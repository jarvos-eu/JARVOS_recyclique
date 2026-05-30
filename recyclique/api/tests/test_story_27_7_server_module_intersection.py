"""Story 27.7 — intersection serveur modules × allowlist poste × permissions opérateur."""

from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.core.audit import sanitize_audit_details
from recyclic_api.core.security import create_access_token, hash_password
from recyclic_api.core.shared_workstation_guard import (
    HEADER_CONTEXT_MODULE_KEY,
    HEADER_DEVICE_ID,
)
from recyclic_api.models.audit_log import AuditActionType
from recyclic_api.models.permission import Group, Permission
from recyclic_api.models.registered_device import (
    RegisteredDevice,
    RegisteredDeviceStatus,
    RegisteredDeviceType,
)
from recyclic_api.models.site import Site
from recyclic_api.models.site_module_config import SiteModuleConfig
from recyclic_api.models.user import User, UserRole, UserStatus
from recyclic_api.modules.module_config.access_registry import PERMISSION_VIEW_LIVE_BAND
from recyclic_api.modules.module_config.registry import MODULE_KEY_KPI_LIVE_BANNER
from recyclic_api.services.context_envelope_service import build_context_envelope
from recyclic_api.services.device_operator_session_service import DeviceOperatorSessionService
from recyclic_api.services.shared_workstation_effective_modules_service import (
    SHARED_WORKSTATION_MODULE_FORBIDDEN,
    SharedWorkstationEffectiveModulesService,
)
from tests.api_v1_paths import v1

_SHARED_WS = "/shared-workstation"
_EFFECTIVE_MODULES = f"{_SHARED_WS}/effective-modules"
_PROBE = f"{_SHARED_WS}/probe-module"
_REGISTERED_DEVICES = "/registered-devices"


def _auth_headers(user_id) -> dict:
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


def _device_auth_headers(user_id, device_id: str, **extra) -> dict:
    headers = _auth_headers(user_id)
    headers[HEADER_DEVICE_ID] = device_id
    headers.update(extra)
    return headers


def _make_site(db: Session) -> Site:
    site = Site(id=uuid4(), name="Site 27.7", is_active=True)
    db.add(site)
    db.commit()
    return site


def _make_user(db: Session, *, site: Site | None = None, with_live_band: bool = False) -> User:
    user = User(
        id=uuid4(),
        username=f"op27_{uuid4().hex[:8]}",
        hashed_password=hash_password("Test1234!"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_active=True,
        site_id=site.id if site else None,
    )
    if with_live_band:
        perm = (
            db.query(Permission)
            .filter(Permission.name == PERMISSION_VIEW_LIVE_BAND)
            .one_or_none()
        )
        if perm is None:
            perm = Permission(name=PERMISSION_VIEW_LIVE_BAND, description="Bandeau live")
            db.add(perm)
            db.flush()
        group = Group(name="G Live Band", description="", key=f"g-live-{uuid4().hex[:6]}")
        group.permissions = [perm]
        db.add(group)
        user.groups = [group]
    db.add(user)
    db.commit()
    return user


def _make_device(
    db: Session,
    site: Site,
    *,
    allowed_module_keys: list[str] | None = None,
) -> RegisteredDevice:
    device = RegisteredDevice(
        id=uuid4(),
        device_type=RegisteredDeviceType.SHARED_WORKSTATION.value,
        name="Poste 27.7",
        site_id=site.id,
        status=RegisteredDeviceStatus.ACTIVE.value,
        allowed_module_keys=allowed_module_keys
        if allowed_module_keys is not None
        else [MODULE_KEY_KPI_LIVE_BANNER],
    )
    db.add(device)
    db.commit()
    return device


def _start_session(db: Session, device: RegisteredDevice, operator: User) -> None:
    DeviceOperatorSessionService(db).start_session(
        device_id=str(device.id),
        operator_user_id=str(operator.id),
        active_module_key=MODULE_KEY_KPI_LIVE_BANNER,
    )


@pytest.mark.story_27_7
class TestStory277IntersectionNominal:
    def test_intersection_ok_all_factors(self, client: TestClient, db_session: Session):
        site = _make_site(db_session)
        device = _make_device(db_session, site)
        operator = _make_user(db_session, site=site, with_live_band=True)
        _start_session(db_session, device, operator)

        result = SharedWorkstationEffectiveModulesService(db_session).compute_effective_module_keys(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
        )
        assert MODULE_KEY_KPI_LIVE_BANNER in result.module_keys

        resp = client.get(
            v1(_EFFECTIVE_MODULES),
            headers=_device_auth_headers(operator.id, str(device.id)),
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert MODULE_KEY_KPI_LIVE_BANNER in body["module_keys"]
        assert resp.headers.get("cache-control") == "no-store"


@pytest.mark.story_27_7
class TestStory277Allowlist:
    def test_allowlist_excludes_module(self, client: TestClient, db_session: Session):
        site = _make_site(db_session)
        device = _make_device(db_session, site, allowed_module_keys=[])
        operator = _make_user(db_session, site=site, with_live_band=True)
        _start_session(db_session, device, operator)

        result = SharedWorkstationEffectiveModulesService(db_session).compute_effective_module_keys(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
        )
        assert MODULE_KEY_KPI_LIVE_BANNER not in result.module_keys


@pytest.mark.story_27_7
class TestStory277Permissions:
    def test_operator_without_permission_excluded(self, db_session: Session):
        site = _make_site(db_session)
        device = _make_device(db_session, site)
        operator = _make_user(db_session, site=site, with_live_band=False)
        _start_session(db_session, device, operator)

        result = SharedWorkstationEffectiveModulesService(db_session).compute_effective_module_keys(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
        )
        assert MODULE_KEY_KPI_LIVE_BANNER not in result.module_keys


@pytest.mark.story_27_7
class TestStory277SiteConfig:
    def test_site_config_disables_module(self, db_session: Session):
        site = _make_site(db_session)
        device = _make_device(db_session, site)
        operator = _make_user(db_session, site=site, with_live_band=True)
        _start_session(db_session, device, operator)

        row = SiteModuleConfig(
            site_id=site.id,
            module_key=MODULE_KEY_KPI_LIVE_BANNER,
            schema_version="1.0.0",
            payload={"show_on_caisse": False, "show_on_reception": False, "refresh_interval_seconds": 60},
            version=1,
        )
        db_session.add(row)
        db_session.commit()

        result = SharedWorkstationEffectiveModulesService(db_session).compute_effective_module_keys(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
        )
        assert MODULE_KEY_KPI_LIVE_BANNER not in result.module_keys


@pytest.mark.story_27_7
class TestStory277OperatorRequired:
    def test_effective_modules_without_session_403(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_device(db_session, site)
        operator = _make_user(db_session, site=site, with_live_band=True)

        resp = client.get(
            v1(_EFFECTIVE_MODULES),
            headers=_device_auth_headers(operator.id, str(device.id)),
        )
        assert resp.status_code == 403


@pytest.mark.story_27_7
class TestStory277ProbeGuard:
    def test_probe_403_when_not_in_intersection(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_device(db_session, site, allowed_module_keys=[])
        operator = _make_user(db_session, site=site, with_live_band=True)
        _start_session(db_session, device, operator)

        resp = client.get(
            v1(f"{_PROBE}/{MODULE_KEY_KPI_LIVE_BANNER}"),
            headers=_device_auth_headers(operator.id, str(device.id)),
        )
        assert resp.status_code == 403
        assert resp.json()["code"] == SHARED_WORKSTATION_MODULE_FORBIDDEN

    def test_probe_200_when_effective(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_device(db_session, site)
        operator = _make_user(db_session, site=site, with_live_band=True)
        _start_session(db_session, device, operator)

        resp = client.get(
            v1(f"{_PROBE}/{MODULE_KEY_KPI_LIVE_BANNER}"),
            headers=_device_auth_headers(operator.id, str(device.id)),
        )
        assert resp.status_code == 200
        assert resp.json()["module_key"] == MODULE_KEY_KPI_LIVE_BANNER


@pytest.mark.story_27_7
class TestStory277StaleUi:
    def test_stale_module_header_409(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_device(db_session, site)
        operator = _make_user(db_session, site=site, with_live_band=True)
        _start_session(db_session, device, operator)

        resp = client.get(
            v1(f"{_PROBE}/{MODULE_KEY_KPI_LIVE_BANNER}"),
            headers=_device_auth_headers(
                operator.id,
                str(device.id),
                **{HEADER_CONTEXT_MODULE_KEY: "unknown-module-key"},
            ),
        )
        assert resp.status_code == 409
        assert resp.json()["code"] == "CONTEXT_STALE"


@pytest.mark.story_27_7
class TestStory277RecalcAfterAllowlistPatch:
    def test_patch_allowlist_recalc(
        self, super_admin_client: TestClient, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_device(db_session, site)
        operator = _make_user(db_session, site=site, with_live_band=True)
        _start_session(db_session, device, operator)

        before = SharedWorkstationEffectiveModulesService(db_session).compute_effective_module_keys(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
        )
        assert MODULE_KEY_KPI_LIVE_BANNER in before.module_keys

        patch = super_admin_client.patch(
            v1(f"{_REGISTERED_DEVICES}/{device.id}"),
            json={"allowed_module_keys": []},
        )
        assert patch.status_code == 200, patch.text
        db_session.expire_all()

        after = SharedWorkstationEffectiveModulesService(db_session).compute_effective_module_keys(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
        )
        assert MODULE_KEY_KPI_LIVE_BANNER not in after.module_keys


@pytest.mark.story_27_7
class TestStory277ContextEnvelope:
    def test_envelope_with_device_session_has_effective_keys(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_device(db_session, site)
        operator = _make_user(db_session, site=site, with_live_band=True)
        _start_session(db_session, device, operator)

        env = build_context_envelope(
            db_session,
            operator.id,
            device_id=device.id,
        )
        assert env.effective_module_keys is not None
        assert MODULE_KEY_KPI_LIVE_BANNER in env.effective_module_keys

        resp = client.get(
            f"/v1/users/me/context?device_id={device.id}",
            headers=_auth_headers(operator.id),
        )
        assert resp.status_code == 200
        assert MODULE_KEY_KPI_LIVE_BANNER in resp.json().get("effective_module_keys", [])

    def test_envelope_web_without_device_no_effective_keys(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        user = _make_user(db_session, site=site)

        env = build_context_envelope(db_session, user.id)
        assert env.effective_module_keys is None

        resp = client.get("/v1/users/me/context", headers=_auth_headers(user.id))
        assert resp.status_code == 200
        assert resp.json().get("effective_module_keys") is None


@pytest.mark.story_27_7
class TestStory277Registry:
    def test_invalid_module_key_never_effective(self, db_session: Session):
        site = _make_site(db_session)
        device = _make_device(db_session, site)
        operator = _make_user(db_session, site=site, with_live_band=True)
        _start_session(db_session, device, operator)

        result = SharedWorkstationEffectiveModulesService(db_session).compute_effective_module_keys(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
        )
        assert "reception" not in result.module_keys
        assert "not-a-module" not in result.module_keys


@pytest.mark.story_27_7
class TestStory277Audit:
    @patch(
        "recyclic_api.services.shared_workstation_effective_modules_service.log_shared_workstation_access_refused"
    )
    def test_audit_refusal_no_pin(
        self, mock_refused, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_device(db_session, site, allowed_module_keys=[])
        operator = _make_user(db_session, site=site, with_live_band=True)
        _start_session(db_session, device, operator)

        service = SharedWorkstationEffectiveModulesService(db_session)
        with pytest.raises(Exception):
            service.assert_module_in_effective_set(
                device_id=str(device.id),
                operator_user_id=str(operator.id),
                module_key=MODULE_KEY_KPI_LIVE_BANNER,
            )
        mock_refused.assert_called_once()
        kwargs = mock_refused.call_args.kwargs
        assert kwargs["device_id"] == str(device.id)
        assert kwargs["module_key"] == MODULE_KEY_KPI_LIVE_BANNER
        assert kwargs["outcome"] == "module_not_effective"
        assert "pin" not in str(kwargs).lower()

    def test_audit_refusal_details_contain_module_key_no_pin(self):
        from recyclic_api.core.audit import merge_critical_audit_fields

        details = merge_critical_audit_fields(
            {},
            device_id="dev-1",
            module_key=MODULE_KEY_KPI_LIVE_BANNER,
            outcome="module_not_effective",
        )
        sanitized = sanitize_audit_details(details)
        assert sanitized.get("module_key") == MODULE_KEY_KPI_LIVE_BANNER
        assert sanitized.get("device_id") == "dev-1"
        assert "pin" not in str(sanitized).lower()
