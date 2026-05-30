"""Epic 27.2 / story_27_2 — contexte serveur poste partagé, session opérateur, audit."""

from __future__ import annotations

from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.core.audit import (
    log_shared_workstation_access_refused,
    merge_critical_audit_fields,
    sanitize_audit_details,
)
from recyclic_api.core.security import create_access_token, hash_password
from recyclic_api.core.shared_workstation_guard import (
    HEADER_CONTEXT_MODULE_KEY,
    HEADER_DEVICE_ID,
    SHARED_WORKSTATION_DEVICE_INVALID,
    SHARED_WORKSTATION_OPERATOR_REQUIRED,
)
from recyclic_api.models.audit_log import AuditActionType
from recyclic_api.models.cash_register import CashRegister
from recyclic_api.models.device_operator_session import (
    DeviceOperatorSession,
    DeviceOperatorSessionStatus,
)
from recyclic_api.models.registered_device import (
    RegisteredDevice,
    RegisteredDeviceStatus,
    RegisteredDeviceType,
)
from recyclic_api.models.site import Site
from recyclic_api.models.user import User, UserRole, UserStatus
from recyclic_api.modules.module_config.registry import MODULE_KEY_KPI_LIVE_BANNER
from recyclic_api.services.device_operator_session_service import DeviceOperatorSessionService
from recyclic_api.schemas.registered_device import RegisteredDeviceUpdate
from recyclic_api.services.registered_device_service import RegisteredDeviceService
from tests.api_v1_paths import v1

_SHARED_WORKSTATION_CONTEXT = "/shared-workstation/context"


def _auth_headers(user_id: UUID) -> dict:
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


def _device_headers(user_id: UUID, device_id: str, **extra) -> dict:
    headers = _auth_headers(user_id)
    headers[HEADER_DEVICE_ID] = device_id
    headers.update(extra)
    return headers


def _make_site(db: Session) -> Site:
    site = Site(id=uuid4(), name="Site SW 27.2", is_active=True)
    db.add(site)
    db.commit()
    return site


def _make_user(db: Session, *, site: Site | None = None) -> User:
    user = User(
        id=uuid4(),
        username=f"op_{uuid4().hex[:8]}",
        hashed_password=hash_password("Test1234!"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_active=True,
        site_id=site.id if site else None,
    )
    db.add(user)
    db.commit()
    return user


def _make_active_device(db: Session, site: Site) -> RegisteredDevice:
    device = RegisteredDevice(
        id=uuid4(),
        device_type=RegisteredDeviceType.SHARED_WORKSTATION.value,
        name="Poste SW",
        site_id=site.id,
        status=RegisteredDeviceStatus.ACTIVE.value,
        allowed_module_keys=[MODULE_KEY_KPI_LIVE_BANNER],
    )
    db.add(device)
    db.commit()
    return device


class TestDeviceOperatorSessionStory272:
    def test_start_get_active_end_single_active_per_device(self, db_session: Session):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        operator = _make_user(db_session, site=site)
        service = DeviceOperatorSessionService(db_session)

        s1 = service.start_session(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
            active_module_key=MODULE_KEY_KPI_LIVE_BANNER,
        )
        assert s1.status == DeviceOperatorSessionStatus.ACTIVE.value

        active = service.get_active_for_device(device_id=str(device.id))
        assert active is not None
        assert active.id == s1.id
        assert str(active.operator_user_id) == str(operator.id)

        operator2 = _make_user(db_session, site=site)
        s2 = service.start_session(
            device_id=str(device.id),
            operator_user_id=str(operator2.id),
        )
        db_session.refresh(s1)
        assert s1.status == DeviceOperatorSessionStatus.SUPERSEDED.value
        assert service.get_active_for_device(device_id=str(device.id)).id == s2.id

        service.end_session(session=s2)
        db_session.refresh(s2)
        assert s2.status == DeviceOperatorSessionStatus.ENDED.value
        assert service.get_active_for_device(device_id=str(device.id)) is None


class TestSharedWorkstationRouteStory272:
    @patch("recyclic_api.core.shared_workstation_guard.log_shared_workstation_access_refused")
    def test_refusal_without_operator_403_and_audit(
        self,
        mock_refused,
        client: TestClient,
        db_session: Session,
    ):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        user = _make_user(db_session, site=site)

        resp = client.get(
            v1(_SHARED_WORKSTATION_CONTEXT),
            headers=_device_headers(user.id, str(device.id)),
        )
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == SHARED_WORKSTATION_OPERATOR_REQUIRED
        mock_refused.assert_called()
        kwargs = mock_refused.call_args.kwargs
        assert kwargs["device_id"] == str(device.id)
        assert kwargs["outcome"] == "operator_required"
        assert "pin" not in str(kwargs).lower()

    def test_success_with_active_session(self, client: TestClient, db_session: Session):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        user = _make_user(db_session, site=site)
        DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(user.id),
            active_module_key=MODULE_KEY_KPI_LIVE_BANNER,
        )

        resp = client.get(
            v1(_SHARED_WORKSTATION_CONTEXT),
            headers=_device_headers(
                user.id,
                str(device.id),
                **{HEADER_CONTEXT_MODULE_KEY: MODULE_KEY_KPI_LIVE_BANNER},
            ),
        )
        assert resp.status_code == 200
        assert resp.headers.get("cache-control") == "no-store"
        body = resp.json()
        assert body["device_id"] == str(device.id)
        assert body["operator_user_id"] == str(user.id)
        assert body["module_key"] == MODULE_KEY_KPI_LIVE_BANNER
        assert body["runtime_state"] == "ok"

    @patch("recyclic_api.core.shared_workstation_guard.log_shared_workstation_access_refused")
    def test_revoked_device_refused_and_audit(
        self,
        mock_refused,
        client: TestClient,
        db_session: Session,
    ):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        user = _make_user(db_session, site=site)
        DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(user.id),
        )
        device.status = RegisteredDeviceStatus.REVOKED.value
        db_session.add(device)
        db_session.commit()

        resp = client.get(
            v1(_SHARED_WORKSTATION_CONTEXT),
            headers=_device_headers(user.id, str(device.id)),
        )
        assert resp.status_code == 403
        assert resp.json()["code"] == SHARED_WORKSTATION_DEVICE_INVALID
        mock_refused.assert_called()
        assert mock_refused.call_args.kwargs["outcome"] == "device_invalid"
        assert mock_refused.call_args.kwargs["device_id"] == str(device.id)

    def test_unknown_device_404(self, client: TestClient, db_session: Session):
        site = _make_site(db_session)
        user = _make_user(db_session, site=site)
        unknown_id = str(uuid4())

        resp = client.get(
            v1(_SHARED_WORKSTATION_CONTEXT),
            headers=_device_headers(user.id, unknown_id),
        )
        assert resp.status_code == 404
        assert resp.json()["code"] == SHARED_WORKSTATION_DEVICE_INVALID

    def test_header_module_mismatch_409_context_stale(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        user = _make_user(db_session, site=site)
        DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(user.id),
            active_module_key=MODULE_KEY_KPI_LIVE_BANNER,
        )

        resp = client.get(
            v1(_SHARED_WORKSTATION_CONTEXT),
            headers=_device_headers(
                user.id,
                str(device.id),
                **{HEADER_CONTEXT_MODULE_KEY: "wrong-module"},
            ),
        )
        assert resp.status_code == 409
        assert resp.json()["code"] == "CONTEXT_STALE"


class TestContextEnvelopeSharedWorkstationStory272:
    def test_envelope_without_device_fields_null(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        user = _make_user(db_session, site=site)
        resp = client.get("/v1/users/me/context", headers=_auth_headers(user.id))
        assert resp.status_code == 200
        ctx = resp.json()["context"]
        assert ctx.get("device_id") is None
        assert ctx.get("operator_user_id") is None
        assert ctx.get("module_key") is None
        assert ctx.get("override_active") is None

    def test_envelope_with_device_session_merges_fields(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        user = _make_user(db_session, site=site)
        DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(user.id),
            active_module_key=MODULE_KEY_KPI_LIVE_BANNER,
        )

        resp = client.get(
            f"/v1/users/me/context?device_id={device.id}",
            headers=_auth_headers(user.id),
        )
        assert resp.status_code == 200
        ctx = resp.json()["context"]
        assert ctx["device_id"] == str(device.id)
        assert ctx["operator_user_id"] == str(user.id)
        assert ctx["module_key"] == MODULE_KEY_KPI_LIVE_BANNER

    def test_envelope_refresh_post_with_device_merges_fields(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        user = _make_user(db_session, site=site)
        DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(user.id),
            active_module_key=MODULE_KEY_KPI_LIVE_BANNER,
        )

        resp = client.post(
            f"/v1/users/me/context/refresh?device_id={device.id}",
            headers=_auth_headers(user.id),
        )
        assert resp.status_code == 200
        ctx = resp.json()["context"]
        assert ctx["device_id"] == str(device.id)
        assert ctx["operator_user_id"] == str(user.id)
        assert ctx["module_key"] == MODULE_KEY_KPI_LIVE_BANNER

    def test_envelope_with_device_header_merges_fields(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        user = _make_user(db_session, site=site)
        DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(user.id),
            active_module_key=MODULE_KEY_KPI_LIVE_BANNER,
        )

        headers = _auth_headers(user.id)
        headers[HEADER_DEVICE_ID] = str(device.id)
        resp = client.get("/v1/users/me/context", headers=headers)
        assert resp.status_code == 200
        ctx = resp.json()["context"]
        assert ctx["device_id"] == str(device.id)
        assert ctx["operator_user_id"] == str(user.id)


class TestAuditSharedWorkstationStory272:
    def test_merge_critical_audit_fields_device_module_override(self):
        d = merge_critical_audit_fields(
            {},
            device_id="dev-1",
            module_key=MODULE_KEY_KPI_LIVE_BANNER,
            override_active=True,
            operator_user_id="op-1",
            user_id="jwt-1",
        )
        assert d["device_id"] == "dev-1"
        assert d["module_key"] == MODULE_KEY_KPI_LIVE_BANNER
        assert d["override_active"] is True
        assert d["operator_user_id"] == "op-1"
        assert d["user_id"] == "jwt-1"

    @patch("recyclic_api.core.audit.log_audit")
    def test_sanitize_pin_on_shared_workstation_audit(self, mock_log_audit):
        out = sanitize_audit_details({"pin": "1234", "device_id": "d1"})
        assert out["pin"] == "[REDACTED]"
        assert out["device_id"] == "d1"

        log_shared_workstation_access_refused(
            db=pytest.importorskip("unittest.mock").MagicMock(),
            device_id=str(uuid4()),
        )
        mock_log_audit.assert_called_once()
        action = mock_log_audit.call_args.kwargs["action_type"]
        assert action == AuditActionType.SHARED_WORKSTATION_ACCESS_REFUSED
        details = mock_log_audit.call_args.kwargs["details"]
        assert "1234" not in str(details)

    def test_sanitize_step_up_pin_derivative(self):
        out = sanitize_audit_details({"step_up_pin": "9999", "device_id": "d1"})
        assert out["step_up_pin"] == "[REDACTED]"
        assert out["device_id"] == "d1"


class TestDeviceOperatorSessionAuditStory272:
    @patch("recyclic_api.core.audit.log_audit")
    def test_start_session_emits_started_audit(
        self, mock_log_audit, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        operator = _make_user(db_session, site=site)
        session = DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
            active_module_key=MODULE_KEY_KPI_LIVE_BANNER,
        )
        mock_log_audit.assert_called()
        kwargs = mock_log_audit.call_args.kwargs
        assert kwargs["action_type"] == AuditActionType.DEVICE_OPERATOR_SESSION_STARTED
        details = kwargs["details"]
        assert details["device_id"] == str(device.id)
        assert details["operator_user_id"] == str(operator.id)
        assert details["session_id"] == str(session.id)
        assert "pin" not in str(details).lower()

    @patch("recyclic_api.core.audit.log_audit")
    def test_end_session_emits_ended_audit(self, mock_log_audit, db_session: Session):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        operator = _make_user(db_session, site=site)
        service = DeviceOperatorSessionService(db_session)
        session = service.start_session(
            device_id=str(device.id),
            operator_user_id=str(operator.id),
        )
        mock_log_audit.reset_mock()
        service.end_session(session=session)
        mock_log_audit.assert_called_once()
        kwargs = mock_log_audit.call_args.kwargs
        assert kwargs["action_type"] == AuditActionType.DEVICE_OPERATOR_SESSION_ENDED
        assert kwargs["details"]["device_id"] == str(device.id)


class TestIdentifierSeparationStory272:
    def test_device_id_distinct_from_cash_register_in_context(
        self, client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        user = _make_user(db_session, site=site)
        cash_reg = CashRegister(id=uuid4(), name="Caisse A", site_id=site.id)
        db_session.add(cash_reg)
        db_session.commit()

        DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(user.id),
        )

        resp = client.get(
            v1(_SHARED_WORKSTATION_CONTEXT),
            headers=_device_headers(user.id, str(device.id)),
        )
        body = resp.json()
        assert body["device_id"] == str(device.id)
        assert body["device_id"] != str(cash_reg.id)
        assert body.get("cash_register_id") is None

    @patch("recyclic_api.core.audit.log_audit")
    def test_audit_device_id_not_cash_register_id(self, mock_log_audit):
        device_id = str(uuid4())
        cash_id = str(uuid4())
        log_shared_workstation_access_refused(
            db=pytest.importorskip("unittest.mock").MagicMock(),
            device_id=device_id,
        )
        mock_log_audit.assert_called_once()
        details = mock_log_audit.call_args.kwargs["details"]
        assert details["device_id"] == device_id
        assert details.get("cash_register_id") != cash_id


class TestInvalidationStory272:
    @patch("recyclic_api.core.audit.log_shared_workstation_context_invalidated")
    def test_site_change_emits_context_invalidated_audit(
        self,
        mock_invalidated,
        db_session: Session,
        super_admin_client: TestClient,
    ):
        site_a = _make_site(db_session)
        site_b = _make_site(db_session)
        device = _make_active_device(db_session, site_a)
        user = _make_user(db_session, site=site_a)
        DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(user.id),
        )

        patch_resp = super_admin_client.patch(
            v1(f"/registered-devices/{device.id}"),
            json={"site_id": str(site_b.id)},
        )
        assert patch_resp.status_code == 200
        mock_invalidated.assert_called()
        kwargs = mock_invalidated.call_args.kwargs
        assert kwargs["device_id"] == str(device.id)
        assert kwargs["reason"] == "device_site_change"

    def test_site_change_invalidates_session_then_403(
        self, client: TestClient, db_session: Session, super_admin_client: TestClient
    ):
        site_a = _make_site(db_session)
        site_b = _make_site(db_session)
        device = _make_active_device(db_session, site_a)
        user = _make_user(db_session, site=site_a)
        DeviceOperatorSessionService(db_session).start_session(
            device_id=str(device.id),
            operator_user_id=str(user.id),
        )

        patch_resp = super_admin_client.patch(
            v1(f"/registered-devices/{device.id}"),
            json={"site_id": str(site_b.id)},
        )
        assert patch_resp.status_code == 200

        active = DeviceOperatorSessionService(db_session).get_active_for_device(
            device_id=str(device.id)
        )
        assert active is None

        resp = client.get(
            v1(_SHARED_WORKSTATION_CONTEXT),
            headers=_device_headers(user.id, str(device.id)),
        )
        assert resp.status_code == 403

    @patch("recyclic_api.core.audit.log_shared_workstation_context_invalidated")
    def test_update_status_revoked_invalidates_session_and_audit(
        self,
        mock_invalidated,
        db_session: Session,
    ):
        site = _make_site(db_session)
        device = _make_active_device(db_session, site)
        user = _make_user(db_session, site=site)
        session_service = DeviceOperatorSessionService(db_session)
        session_service.start_session(
            device_id=str(device.id),
            operator_user_id=str(user.id),
        )
        assert session_service.get_active_for_device(device_id=str(device.id)) is not None

        updated = RegisteredDeviceService(db_session).update(
            device=device,
            data=RegisteredDeviceUpdate.model_construct(
                status=RegisteredDeviceStatus.REVOKED.value
            ),
        )
        assert updated.status == RegisteredDeviceStatus.REVOKED.value
        assert updated.revoked_at is not None

        assert session_service.get_active_for_device(device_id=str(device.id)) is None
        mock_invalidated.assert_called()
        kwargs = mock_invalidated.call_args.kwargs
        assert kwargs["device_id"] == str(device.id)
        assert kwargs["reason"] == "device_revoked"
