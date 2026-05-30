"""Story 27.4 — enrôlement, reconnexion, remplacement, credential device."""

from __future__ import annotations

from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.core.security import verify_password
from recyclic_api.models.audit_log import AuditActionType
from recyclic_api.models.registered_device import RegisteredDeviceStatus
from recyclic_api.models.registered_device_credential import (
    RegisteredDeviceCredential,
    RegisteredDeviceCredentialStatus,
)
from recyclic_api.models.site import Site
from recyclic_api.modules.module_config.registry import MODULE_KEY_KPI_LIVE_BANNER
from tests.api_v1_paths import v1

_REGISTERED_DEVICES = "/registered-devices"
_SHARED_WS = "/shared-workstation"


def _make_site(db: Session) -> Site:
    site = Site(id=uuid4(), name="Site 27.4", is_active=True)
    db.add(site)
    db.commit()
    return site


def _device_payload(site_id: str, **overrides) -> dict:
    base = {
        "name": "Poste Enroll",
        "site_id": site_id,
        "allowed_module_keys": [MODULE_KEY_KPI_LIVE_BANNER],
    }
    base.update(overrides)
    return base


def _create_pending_device(client: TestClient, site_id: str) -> str:
    resp = client.post(v1(_REGISTERED_DEVICES), json=_device_payload(site_id))
    assert resp.status_code == 201
    return resp.json()["device_id"]


def _issue_code(client: TestClient, device_id: str, purpose: str) -> str:
    resp = client.post(
        v1(f"{_REGISTERED_DEVICES}/{device_id}/enrollment-codes"),
        json={"purpose": purpose},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["code"]


def _complete_enrollment(client: TestClient, code: str) -> dict:
    resp = client.post(
        v1(f"{_SHARED_WS}/enroll/complete"),
        json={"code": code},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _device_headers(device_id: str, secret: str) -> dict:
    return {
        "X-Recyclique-Device-Id": device_id,
        "X-Recyclique-Device-Credential": secret,
    }


def _api_error_code(resp) -> str | None:
    data = resp.json()
    code = data.get("code")
    if isinstance(code, str):
        return code
    detail = data.get("detail")
    if isinstance(detail, dict):
        return detail.get("code")
    return None


@pytest.mark.story_27_4
class TestStory274EnrollmentNominal:
    def test_initial_enrollment_active_credential_hashed(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = _create_pending_device(super_admin_client, str(site.id))
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        body = _complete_enrollment(super_admin_client, code)

        assert body["device_id"] == device_id
        assert body["device_secret"]
        assert body["device_name"] == "Poste Enroll"

        device_resp = super_admin_client.get(v1(f"{_REGISTERED_DEVICES}/{device_id}"))
        assert device_resp.json()["status"] == RegisteredDeviceStatus.ACTIVE.value

        cred = (
            db_session.query(RegisteredDeviceCredential)
            .filter(
                RegisteredDeviceCredential.device_id == UUID(device_id),
                RegisteredDeviceCredential.status
                == RegisteredDeviceCredentialStatus.ACTIVE.value,
            )
            .first()
        )
        assert cred is not None
        assert cred.secret_hash != body["device_secret"]
        assert verify_password(body["device_secret"], cred.secret_hash)

        status_resp = super_admin_client.get(
            v1(f"{_SHARED_WS}/device-status"),
            headers=_device_headers(device_id, body["device_secret"]),
        )
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "active"


@pytest.mark.story_27_4
class TestStory274Reconnect:
    def test_mark_identity_lost_then_reconnect(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = _create_pending_device(super_admin_client, str(site.id))
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        first = _complete_enrollment(super_admin_client, code)
        old_secret = first["device_secret"]

        mark = super_admin_client.post(
            v1(f"{_REGISTERED_DEVICES}/{device_id}/mark-identity-lost")
        )
        assert mark.status_code == 200
        assert mark.json()["status"] == RegisteredDeviceStatus.IDENTITY_LOST.value

        reconnect_code = _issue_code(super_admin_client, device_id, "reconnect")
        second = _complete_enrollment(super_admin_client, reconnect_code)
        assert second["device_secret"] != old_secret

        old_status = super_admin_client.get(
            v1(f"{_SHARED_WS}/device-status"),
            headers=_device_headers(device_id, old_secret),
        )
        assert old_status.status_code == 403
        assert _api_error_code(old_status) in (
            "DEVICE_CREDENTIAL_REVOKED",
            "DEVICE_IDENTITY_CONFLICT",
        )


def _put_device_in_conflict(
    client: TestClient, device_id: str, old_secret: str
) -> str:
    """Replace enrollment puis retry ancien secret → statut conflict ; retourne le nouveau secret actif."""
    replace_code = _issue_code(client, device_id, "replace")
    new_enroll = _complete_enrollment(client, replace_code)
    retry = client.get(
        v1(f"{_SHARED_WS}/device-status"),
        headers=_device_headers(device_id, old_secret),
    )
    assert retry.status_code == 403
    device_resp = client.get(v1(f"{_REGISTERED_DEVICES}/{device_id}"))
    assert device_resp.json()["status"] == RegisteredDeviceStatus.CONFLICT.value
    return new_enroll["device_secret"]


@pytest.mark.story_27_4
class TestStory274ReplaceAndConflict:
    def test_replace_old_secret_refused_and_conflict(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = _create_pending_device(super_admin_client, str(site.id))
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        first = _complete_enrollment(super_admin_client, code)
        old_secret = first["device_secret"]

        replace_code = _issue_code(super_admin_client, device_id, "replace")
        second = _complete_enrollment(super_admin_client, replace_code)
        assert second["device_secret"] != old_secret

        retry = super_admin_client.get(
            v1(f"{_SHARED_WS}/device-status"),
            headers=_device_headers(device_id, old_secret),
        )
        assert retry.status_code == 403
        assert _api_error_code(retry) == "DEVICE_IDENTITY_CONFLICT"

        device_resp = super_admin_client.get(v1(f"{_REGISTERED_DEVICES}/{device_id}"))
        assert device_resp.json()["status"] == RegisteredDeviceStatus.CONFLICT.value

    @patch("recyclic_api.core.audit.log_audit")
    def test_resolve_conflict_actions(
        self, mock_log_audit, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = _create_pending_device(super_admin_client, str(site.id))
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        first = _complete_enrollment(super_admin_client, code)
        replace_code = _issue_code(super_admin_client, device_id, "replace")
        _complete_enrollment(super_admin_client, replace_code)
        super_admin_client.get(
            v1(f"{_SHARED_WS}/device-status"),
            headers=_device_headers(device_id, first["device_secret"]),
        )

        refuse = super_admin_client.post(
            v1(f"{_REGISTERED_DEVICES}/{device_id}/resolve-conflict"),
            json={"action": "refuse"},
        )
        assert refuse.status_code == 200
        assert refuse.json()["status"] == RegisteredDeviceStatus.ACTIVE.value

        # Remettre en conflict pour create_distinct
        replace_code2 = _issue_code(super_admin_client, device_id, "replace")
        new_enroll = _complete_enrollment(super_admin_client, replace_code2)
        super_admin_client.get(
            v1(f"{_SHARED_WS}/device-status"),
            headers=_device_headers(device_id, first["device_secret"]),
        )
        distinct = super_admin_client.post(
            v1(f"{_REGISTERED_DEVICES}/{device_id}/resolve-conflict"),
            json={"action": "create_distinct", "name": "Poste Distinct"},
        )
        assert distinct.status_code == 200
        assert distinct.json()["distinct_device_id"]
        assert distinct.json()["distinct_device_id"] != device_id

        # Nouveau secret actif fonctionne
        ok = super_admin_client.get(
            v1(f"{_SHARED_WS}/device-status"),
            headers=_device_headers(device_id, new_enroll["device_secret"]),
        )
        assert ok.status_code == 200

    def test_replace_definitively_poste_reste_utilisable(
        self, super_admin_client: TestClient, db_session: Session
    ):
        """replace_definitively : credential actif conservé + code replace consommable."""
        site = _make_site(db_session)
        device_id = _create_pending_device(super_admin_client, str(site.id))
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        first = _complete_enrollment(super_admin_client, code)
        active_secret = _put_device_in_conflict(
            super_admin_client, device_id, first["device_secret"]
        )

        resolve = super_admin_client.post(
            v1(f"{_REGISTERED_DEVICES}/{device_id}/resolve-conflict"),
            json={"action": "replace_definitively"},
        )
        assert resolve.status_code == 200, resolve.text
        body = resolve.json()
        assert body["status"] == RegisteredDeviceStatus.ACTIVE.value
        assert body["enrollment_code"]
        assert body["enrollment_code_purpose"] == "replace"

        # Poste reste utilisable avec le credential actif (machine légitime)
        still_ok = super_admin_client.get(
            v1(f"{_SHARED_WS}/device-status"),
            headers=_device_headers(device_id, active_secret),
        )
        assert still_ok.status_code == 200

        # Code replace auto-émis est consommable pour rotation ultérieure
        rotated = _complete_enrollment(super_admin_client, body["enrollment_code"])
        assert rotated["device_secret"] != active_secret
        after_rotate = super_admin_client.get(
            v1(f"{_SHARED_WS}/device-status"),
            headers=_device_headers(device_id, rotated["device_secret"]),
        )
        assert after_rotate.status_code == 200
        old_after = super_admin_client.get(
            v1(f"{_SHARED_WS}/device-status"),
            headers=_device_headers(device_id, active_secret),
        )
        assert old_after.status_code == 403


@pytest.mark.story_27_4
class TestStory274EnrollmentCodes:
    def test_invalid_expired_consumed_codes(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = _create_pending_device(super_admin_client, str(site.id))

        bad = super_admin_client.post(
            v1(f"{_SHARED_WS}/enroll/complete"),
            json={"code": "BADCODE1"},
        )
        assert bad.status_code == 400
        assert _api_error_code(bad) == "ENROLLMENT_CODE_INVALID"

        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        _complete_enrollment(super_admin_client, code)

        consumed = super_admin_client.post(
            v1(f"{_SHARED_WS}/enroll/complete"),
            json={"code": code},
        )
        assert consumed.status_code == 409
        assert _api_error_code(consumed) == "ENROLLMENT_CODE_CONSUMED"


@pytest.mark.story_27_4
class TestStory274AuditSanitize:
    @patch("recyclic_api.core.audit.log_audit")
    def test_audit_never_contains_secret(
        self, mock_log_audit, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = _create_pending_device(super_admin_client, str(site.id))
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        body = _complete_enrollment(super_admin_client, code)

        enrollment_calls = [
            c
            for c in mock_log_audit.call_args_list
            if c.kwargs.get("action_type")
            in (
                AuditActionType.DEVICE_ENROLLED,
                AuditActionType.DEVICE_ENROLLMENT_CODE_ISSUED,
            )
        ]
        assert enrollment_calls
        for call in enrollment_calls:
            details = call.kwargs.get("details") or {}
            blob = str(details).lower()
            assert body["device_secret"] not in blob
            assert "pin" not in blob


@pytest.mark.story_27_4
class TestStory274DeviceIdDistinctFromCashRegister:
    def test_device_id_not_cash_register(
        self, super_admin_client: TestClient, db_session: Session
    ):
        from recyclic_api.models.cash_register import CashRegister

        site = _make_site(db_session)
        device_id = _create_pending_device(super_admin_client, str(site.id))
        cash = CashRegister(id=uuid4(), name="Caisse", site_id=site.id, is_active=True)
        db_session.add(cash)
        db_session.commit()
        assert str(cash.id) != device_id
