"""Story 27.3 — audit mutations admin RegisteredDevice + non-régression auth."""

from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.models.audit_log import AuditActionType
from recyclic_api.models.cash_register import CashRegister
from recyclic_api.models.registered_device import RegisteredDeviceStatus
from recyclic_api.models.site import Site
from recyclic_api.modules.module_config.registry import MODULE_KEY_KPI_LIVE_BANNER
from tests.api_v1_paths import v1

_REGISTERED_DEVICES = "/registered-devices"


def _make_site(db: Session) -> Site:
    site = Site(id=uuid4(), name="Site 27.3", is_active=True)
    db.add(site)
    db.commit()
    return site


def _device_payload(site_id: str, **overrides) -> dict:
    base = {
        "name": "Poste Accueil",
        "site_id": site_id,
        "allowed_module_keys": [MODULE_KEY_KPI_LIVE_BANNER],
    }
    base.update(overrides)
    return base


class TestRegisteredDeviceAdminAudit:
    @patch("recyclic_api.core.audit.log_audit")
    def test_create_emits_registered_device_created_audit(
        self, mock_log_audit, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        resp = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(site.id)),
        )
        assert resp.status_code == 201
        body = resp.json()
        device_id = body["device_id"]

        mock_log_audit.assert_called()
        create_calls = [
            c
            for c in mock_log_audit.call_args_list
            if c.kwargs.get("action_type") == AuditActionType.REGISTERED_DEVICE_CREATED
        ]
        assert len(create_calls) >= 1
        kwargs = create_calls[-1].kwargs
        assert kwargs.get("target_type") == "registered_device"
        details = kwargs.get("details") or {}
        assert details.get("device_id") == device_id
        assert details.get("operation") == "registered_device.create"
        assert details.get("outcome") == "success"
        assert "pin" not in str(details).lower()
        assert "secret" not in str(details).lower()

        cash = db_session.query(CashRegister).first()
        if cash:
            assert str(cash.id) != device_id

    @patch("recyclic_api.core.audit.log_audit")
    def test_patch_emits_registered_device_updated_with_changed_fields(
        self, mock_log_audit, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        create = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(site.id)),
        )
        device_id = create.json()["device_id"]
        mock_log_audit.reset_mock()

        patch_resp = super_admin_client.patch(
            v1(f"{_REGISTERED_DEVICES}/{device_id}"),
            json={
                "name": "Poste Renommé",
                "allowed_module_keys": [MODULE_KEY_KPI_LIVE_BANNER],
                "inactivity_timeout_seconds": 600,
            },
        )
        assert patch_resp.status_code == 200

        update_calls = [
            c
            for c in mock_log_audit.call_args_list
            if c.kwargs.get("action_type") == AuditActionType.REGISTERED_DEVICE_UPDATED
        ]
        assert len(update_calls) >= 1
        details = update_calls[-1].kwargs.get("details") or {}
        changed = details.get("changed_fields") or {}
        assert changed.get("name") == "Poste Renommé"
        assert changed.get("inactivity_timeout_seconds") == 600
        assert "allowed_module_keys" in changed

    @patch("recyclic_api.core.audit.log_audit")
    def test_revoke_emits_registered_device_revoked_and_status_revoked(
        self, mock_log_audit, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        create = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(site.id)),
        )
        device_id = create.json()["device_id"]
        mock_log_audit.reset_mock()

        revoke = super_admin_client.post(
            v1(f"{_REGISTERED_DEVICES}/{device_id}/revoke"),
            json={"reason": "maintenance"},
        )
        assert revoke.status_code == 200
        assert revoke.json()["status"] == RegisteredDeviceStatus.REVOKED.value

        revoke_calls = [
            c
            for c in mock_log_audit.call_args_list
            if c.kwargs.get("action_type") == AuditActionType.REGISTERED_DEVICE_REVOKED
        ]
        assert len(revoke_calls) >= 1
        details = revoke_calls[-1].kwargs.get("details") or {}
        assert details.get("reason") == "maintenance"
        assert details.get("device_id") == device_id

    def test_non_super_admin_still_forbidden(
        self, admin_client: TestClient, user_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        payload = _device_payload(str(site.id))
        assert admin_client.post(v1(_REGISTERED_DEVICES), json=payload).status_code == 403
        assert user_client.post(v1(_REGISTERED_DEVICES), json=payload).status_code == 403
        assert admin_client.get(v1(_REGISTERED_DEVICES)).status_code == 403
