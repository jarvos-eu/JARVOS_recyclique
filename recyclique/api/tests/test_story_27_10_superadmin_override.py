"""Story 27.10 — override SuperAdmin explicite, audité, TTL poste partagé."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.core.audit import sanitize_audit_details
from recyclic_api.core.redis import get_redis
from recyclic_api.core.security import create_access_token, hash_password
from recyclic_api.core.shared_workstation_guard import HEADER_DEVICE_ID
from recyclic_api.models.audit_log import AuditActionType
from recyclic_api.models.registered_device import (
    RegisteredDevice,
    RegisteredDeviceStatus,
    RegisteredDeviceType,
)
from recyclic_api.models.site import Site
from recyclic_api.models.site_module_config import SiteModuleConfig
from recyclic_api.models.user import User, UserRole, UserStatus
from recyclic_api.modules.module_config.access_registry import PERMISSION_VIEW_LIVE_BAND
from recyclic_api.modules.module_config.registry import (
    MODULE_KEY_KPI_LIVE_BANNER,
    MODULE_KEY_RECEPTION,
)
from recyclic_api.services.device_operator_session_service import DeviceOperatorSessionService
from recyclic_api.services.shared_workstation_effective_modules_service import (
    SHARED_WORKSTATION_MODULE_FORBIDDEN,
    SharedWorkstationEffectiveModulesService,
)
from recyclic_api.services.shared_workstation_override_service import (
    DEFAULT_OVERRIDE_TTL_SECONDS,
    SHARED_WORKSTATION_OVERRIDE_CONFIRMATION_FAILED,
    SHARED_WORKSTATION_OVERRIDE_FORBIDDEN,
    SHARED_WORKSTATION_OVERRIDE_REQUIRED,
    SharedWorkstationOverrideService,
)
from tests.api_v1_paths import v1
from tests.test_story_27_4_enrollment_reconnect_replace import (
    _SHARED_WS,
    _api_error_code,
    _complete_enrollment,
    _create_pending_device,
    _device_headers,
    _issue_code,
    _make_site,
)
from tests.test_story_27_6_pin_lock_operator_session import (
    _FakeRedis,
    _TEST_PIN,
    _enrolled_device,
    _make_operator,
    _verify_pin,
)

_OVERRIDE_ACTIVATE = f"{_SHARED_WS}/override/activate"
_OVERRIDE_DEACTIVATE = f"{_SHARED_WS}/override/deactivate"
_OPERATOR_SESSION_STATUS = f"{_SHARED_WS}/operator-session/status"
_OPERATOR_SESSION_END = f"{_SHARED_WS}/operator-session/end"
_PROBE_OVERRIDE = f"{_SHARED_WS}/probe-override"
_EFFECTIVE_MODULES = f"{_SHARED_WS}/effective-modules"
_OPERATOR_PIN_VERIFY = f"{_SHARED_WS}/operator-pin/verify"


def _auth_headers(user_id) -> dict:
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


def _device_auth_headers(user_id, device_id: str, secret: str, **extra) -> dict:
    headers = _auth_headers(user_id)
    headers.update(_device_headers(device_id, secret))
    headers.update(extra)
    return headers


def _make_super_admin(db: Session, *, pin: str | None = _TEST_PIN) -> User:
    user = User(
        id=uuid4(),
        username=f"sa27_{uuid4().hex[:8]}",
        hashed_password=hash_password("Test1234!"),
        hashed_pin=hash_password(pin) if pin else None,
        role=UserRole.SUPER_ADMIN,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db.add(user)
    db.commit()
    return user


def _enable_site_module(db: Session, site: Site, module_key: str) -> None:
    if module_key == MODULE_KEY_RECEPTION:
        return
    cfg = SiteModuleConfig(
        site_id=site.id,
        module_key=module_key,
        schema_version="1.0.0",
        payload={
            "show_on_caisse": True,
            "show_on_reception": True,
            "refresh_interval_seconds": 60,
        },
        version=1,
    )
    db.add(cfg)
    db.commit()


@pytest.fixture
def fake_redis():
    return _FakeRedis()


@pytest.fixture
def ws_client(super_admin_client: TestClient, fake_redis: _FakeRedis):
    super_admin_client.app.dependency_overrides[get_redis] = lambda: fake_redis
    yield super_admin_client
    super_admin_client.app.dependency_overrides.pop(get_redis, None)


def _start_super_admin_session(
    ws_client: TestClient,
    super_admin_client: TestClient,
    db_session: Session,
) -> tuple[str, str, User]:
    device_id, secret = _enrolled_device(super_admin_client, db_session)
    sa = _make_super_admin(db_session)
    resp = _verify_pin(ws_client, device_id=device_id, secret=secret, operator_user_id=str(sa.id))
    assert resp.status_code == 200, resp.text
    return device_id, secret, sa


@pytest.mark.story_27_10
class TestStory2710ActivateOverride:
    @patch("recyclic_api.core.audit.log_audit")
    def test_super_admin_activate_ok_audit_and_status(
        self,
        mock_log_audit,
        ws_client: TestClient,
        super_admin_client: TestClient,
        db_session: Session,
    ):
        device_id, secret, sa = _start_super_admin_session(
            ws_client, super_admin_client, db_session
        )

        resp = ws_client.post(
            v1(_OVERRIDE_ACTIVATE),
            headers=_device_headers(device_id, secret),
            json={"confirmation_pin": _TEST_PIN},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["override_active"] is True
        assert body["override_started_at"]
        assert body["override_expires_at"]

        status = ws_client.get(
            v1(_OPERATOR_SESSION_STATUS),
            headers=_device_headers(device_id, secret),
        )
        assert status.status_code == 200
        st = status.json()
        assert st["override_active"] is True
        assert st["can_activate_super_admin_override"] is False
        assert st["override_seconds_remaining"] is not None
        assert st["override_seconds_remaining"] <= DEFAULT_OVERRIDE_TTL_SECONDS

        activated = [
            c
            for c in mock_log_audit.call_args_list
            if c.kwargs.get("action_type")
            == AuditActionType.SHARED_WORKSTATION_OVERRIDE_ACTIVATED
        ]
        assert len(activated) >= 1
        details = sanitize_audit_details(activated[-1].kwargs.get("details") or {})
        assert details.get("override_active") is True
        assert "pin" not in str(details).lower()

    @patch("recyclic_api.core.audit.log_audit")
    def test_non_super_admin_forbidden(
        self,
        mock_log_audit,
        ws_client: TestClient,
        super_admin_client: TestClient,
        db_session: Session,
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)
        assert _verify_pin(
            ws_client,
            device_id=device_id,
            secret=secret,
            operator_user_id=str(operator.id),
        ).status_code == 200

        resp = ws_client.post(
            v1(_OVERRIDE_ACTIVATE),
            headers=_device_headers(device_id, secret),
            json={"confirmation_pin": _TEST_PIN},
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == SHARED_WORKSTATION_OVERRIDE_FORBIDDEN

        refused = [
            c
            for c in mock_log_audit.call_args_list
            if c.kwargs.get("action_type")
            == AuditActionType.SHARED_WORKSTATION_OVERRIDE_ACTIVATION_REFUSED
        ]
        assert len(refused) >= 1

    def test_wrong_confirmation_pin_refused(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret, sa = _start_super_admin_session(
            ws_client, super_admin_client, db_session
        )

        resp = ws_client.post(
            v1(_OVERRIDE_ACTIVATE),
            headers=_device_headers(device_id, secret),
            json={"confirmation_pin": "9999"},
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == SHARED_WORKSTATION_OVERRIDE_CONFIRMATION_FAILED

        session = DeviceOperatorSessionService(db_session).get_active_for_device(
            device_id=device_id
        )
        assert session is not None
        assert session.override_active is False


@pytest.mark.story_27_10
class TestStory2710PinNonRegression:
    def test_pin_verify_starts_session_without_override(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        sa = _make_super_admin(db_session)
        resp = _verify_pin(
            ws_client, device_id=device_id, secret=secret, operator_user_id=str(sa.id)
        )
        assert resp.status_code == 200
        session = DeviceOperatorSessionService(db_session).get_active_for_device(
            device_id=device_id
        )
        assert session is not None
        assert session.override_active is False


@pytest.mark.story_27_10
class TestStory2710IntersectionOverride:
    def test_override_expands_intersection_without_operator_permission(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = _create_pending_device(super_admin_client, str(site.id))
        super_admin_client.patch(
            v1(f"/registered-devices/{device_id}"),
            json={"allowed_module_keys": [MODULE_KEY_RECEPTION]},
        )
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        secret = _complete_enrollment(super_admin_client, code)["device_secret"]

        sa = _make_super_admin(db_session)
        assert _verify_pin(
            ws_client, device_id=device_id, secret=secret, operator_user_id=str(sa.id)
        ).status_code == 200

        with patch(
            "recyclic_api.services.shared_workstation_effective_modules_service.get_user_permissions",
            return_value=[],
        ):
            before = SharedWorkstationEffectiveModulesService(
                db_session
            ).compute_effective_module_keys(device_id=device_id, operator_user_id=str(sa.id))
        assert MODULE_KEY_RECEPTION not in before.module_keys

        assert (
            ws_client.post(
                v1(_OVERRIDE_ACTIVATE),
                headers=_device_headers(device_id, secret),
                json={"confirmation_pin": _TEST_PIN},
            ).status_code
            == 200
        )
        db_session.expire_all()

        with patch(
            "recyclic_api.services.shared_workstation_effective_modules_service.get_user_permissions",
            return_value=[],
        ):
            after = SharedWorkstationEffectiveModulesService(
                db_session
            ).compute_effective_module_keys(device_id=device_id, operator_user_id=str(sa.id))
        assert MODULE_KEY_RECEPTION in after.module_keys

    def test_without_override_intersection_strict(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        _enable_site_module(db_session, site, MODULE_KEY_KPI_LIVE_BANNER)
        device = RegisteredDevice(
            id=uuid4(),
            device_type=RegisteredDeviceType.SHARED_WORKSTATION.value,
            name="Poste 27.10",
            site_id=site.id,
            status=RegisteredDeviceStatus.ACTIVE.value,
            allowed_module_keys=[MODULE_KEY_KPI_LIVE_BANNER],
        )
        db_session.add(device)
        db_session.commit()
        operator = _make_operator(db_session, pin=_TEST_PIN)
        DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
        )
        result = SharedWorkstationEffectiveModulesService(
            db_session
        ).compute_effective_module_keys(
            device_id=str(device.id), operator_user_id=str(operator.id)
        )
        assert MODULE_KEY_KPI_LIVE_BANNER not in result.module_keys

    def test_module_outside_allowlist_forbidden_even_with_override(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        _enable_site_module(db_session, site, MODULE_KEY_KPI_LIVE_BANNER)
        device_id = _create_pending_device(super_admin_client, str(site.id))
        super_admin_client.patch(
            v1(f"/registered-devices/{device_id}"),
            json={"allowed_module_keys": []},
        )
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        secret = _complete_enrollment(super_admin_client, code)["device_secret"]
        sa = _make_super_admin(db_session)
        _verify_pin(ws_client, device_id=device_id, secret=secret, operator_user_id=str(sa.id))
        ws_client.post(
            v1(_OVERRIDE_ACTIVATE),
            headers=_device_headers(device_id, secret),
            json={"confirmation_pin": _TEST_PIN},
        )

        resp = ws_client.get(
            v1(f"{_SHARED_WS}/probe-module/{MODULE_KEY_KPI_LIVE_BANNER}"),
            headers=_device_auth_headers(sa.id, device_id, secret),
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == SHARED_WORKSTATION_MODULE_FORBIDDEN


@pytest.mark.story_27_10
class TestStory2710DeactivateAndTtl:
    @patch("recyclic_api.core.audit.log_audit")
    def test_deactivate_override(
        self,
        mock_log_audit,
        ws_client: TestClient,
        super_admin_client: TestClient,
        db_session: Session,
    ):
        device_id, secret, sa = _start_super_admin_session(
            ws_client, super_admin_client, db_session
        )
        ws_client.post(
            v1(_OVERRIDE_ACTIVATE),
            headers=_device_headers(device_id, secret),
            json={"confirmation_pin": _TEST_PIN},
        )

        resp = ws_client.post(
            v1(_OVERRIDE_DEACTIVATE),
            headers=_device_headers(device_id, secret),
            json={"reason": "user_exit"},
        )
        assert resp.status_code == 200
        assert resp.json()["override_active"] is False

        session = DeviceOperatorSessionService(db_session).get_active_for_device(
            device_id=device_id
        )
        assert session is not None
        assert session.override_active is False

        deactivated = [
            c
            for c in mock_log_audit.call_args_list
            if c.kwargs.get("action_type")
            == AuditActionType.SHARED_WORKSTATION_OVERRIDE_DEACTIVATED
        ]
        assert len(deactivated) >= 1

    def test_ttl_expired_auto_deactivate_and_probe_403(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret, sa = _start_super_admin_session(
            ws_client, super_admin_client, db_session
        )
        ws_client.post(
            v1(_OVERRIDE_ACTIVATE),
            headers=_device_headers(device_id, secret),
            json={"confirmation_pin": _TEST_PIN},
        )

        session = DeviceOperatorSessionService(db_session).get_active_for_device(
            device_id=device_id
        )
        assert session is not None
        expired_start = datetime.now(timezone.utc) - timedelta(
            seconds=DEFAULT_OVERRIDE_TTL_SECONDS + 10
        )
        session.override_started_at = expired_start
        db_session.add(session)
        db_session.commit()

        with patch(
            "recyclic_api.services.shared_workstation_effective_modules_service.get_user_permissions",
            return_value=[],
        ):
            result = SharedWorkstationEffectiveModulesService(
                db_session
            ).compute_effective_module_keys(device_id=device_id, operator_user_id=str(sa.id))
        assert MODULE_KEY_RECEPTION not in result.module_keys

        status = DeviceOperatorSessionService(db_session).get_enriched_session_status(
            device_id=device_id
        )
        assert status.override_active is False

        resp = ws_client.get(
            v1(f"{_PROBE_OVERRIDE}/{MODULE_KEY_RECEPTION}"),
            headers=_device_auth_headers(sa.id, device_id, secret),
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == SHARED_WORKSTATION_OVERRIDE_REQUIRED


@pytest.mark.story_27_10
class TestStory2710SessionEndAndProbe:
    @patch("recyclic_api.core.audit.log_audit")
    def test_timeout_end_session_clears_override(
        self,
        mock_log_audit,
        ws_client: TestClient,
        super_admin_client: TestClient,
        db_session: Session,
    ):
        device_id, secret, sa = _start_super_admin_session(
            ws_client, super_admin_client, db_session
        )
        ws_client.post(
            v1(_OVERRIDE_ACTIVATE),
            headers=_device_headers(device_id, secret),
            json={"confirmation_pin": _TEST_PIN},
        )

        resp = ws_client.post(
            v1(_OPERATOR_SESSION_END),
            headers=_device_headers(device_id, secret),
            json={"reason": "timeout"},
        )
        assert resp.status_code == 200
        assert resp.json()["ended"] is True

        deactivated = [
            c
            for c in mock_log_audit.call_args_list
            if c.kwargs.get("action_type")
            == AuditActionType.SHARED_WORKSTATION_OVERRIDE_DEACTIVATED
        ]
        assert any(
            sanitize_audit_details(c.kwargs.get("details") or {}).get("reason")
            == "session_ended"
            for c in deactivated
        )

    def test_probe_override_required_without_override(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = _create_pending_device(super_admin_client, str(site.id))
        super_admin_client.patch(
            v1(f"/registered-devices/{device_id}"),
            json={"allowed_module_keys": [MODULE_KEY_RECEPTION]},
        )
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        secret = _complete_enrollment(super_admin_client, code)["device_secret"]
        sa = _make_super_admin(db_session)
        _verify_pin(ws_client, device_id=device_id, secret=secret, operator_user_id=str(sa.id))

        resp = ws_client.get(
            v1(f"{_PROBE_OVERRIDE}/{MODULE_KEY_RECEPTION}"),
            headers=_device_auth_headers(sa.id, device_id, secret),
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == SHARED_WORKSTATION_OVERRIDE_REQUIRED


@pytest.mark.story_27_10
class TestStory2710CanActivateFlag:
    def test_can_activate_only_super_admin_without_override(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret, sa = _start_super_admin_session(
            ws_client, super_admin_client, db_session
        )
        status = ws_client.get(
            v1(_OPERATOR_SESSION_STATUS),
            headers=_device_headers(device_id, secret),
        ).json()
        assert status["can_activate_super_admin_override"] is True
        assert status["override_active"] is False

        device_id2, secret2 = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)
        _verify_pin(
            ws_client,
            device_id=device_id2,
            secret=secret2,
            operator_user_id=str(operator.id),
        )
        status2 = ws_client.get(
            v1(_OPERATOR_SESSION_STATUS),
            headers=_device_headers(device_id2, secret2),
        ).json()
        assert status2["can_activate_super_admin_override"] is False
