"""Story 27.6 — lock screen PIN, session opérateur, lockout Redis device+opérateur."""

from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.core.audit import sanitize_audit_details
from recyclic_api.core.redis import get_redis
from recyclic_api.core.security import hash_password
from recyclic_api.models.user import User, UserRole, UserStatus
from recyclic_api.services.shared_workstation_operator_pin_service import (
    SHARED_WORKSTATION_PIN_INVALID,
    SHARED_WORKSTATION_PIN_LOCKED,
    SHARED_WORKSTATION_PIN_NOT_CONFIGURED,
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

_OPERATOR_PIN_VERIFY = f"{_SHARED_WS}/operator-pin/verify"
_OPERATOR_SESSION_STATUS = f"{_SHARED_WS}/operator-session/status"
_SHARED_WS_CONTEXT = f"{_SHARED_WS}/context"
_CLEAR_LOCKOUT = "/registered-devices/{device_id}/clear-operator-pin-lockout"

_TEST_PIN = "4242"


class _FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, int | str] = {}

    def exists(self, key: str) -> bool:
        return key in self._data

    def incr(self, key: str) -> int:
        self._data[key] = int(self._data.get(key, 0)) + 1
        return int(self._data[key])

    def expire(self, key: str, ttl: int) -> None:
        pass

    def setex(self, key: str, ttl: int, value: str) -> None:
        self._data[key] = value

    def delete(self, *keys: str) -> None:
        for key in keys:
            self._data.pop(key, None)


@pytest.fixture
def fake_redis():
    return _FakeRedis()


@pytest.fixture
def ws_client(super_admin_client: TestClient, fake_redis: _FakeRedis):
    """Client API avec Redis in-memory pour lockout PIN."""
    super_admin_client.app.dependency_overrides[get_redis] = lambda: fake_redis
    yield super_admin_client
    super_admin_client.app.dependency_overrides.pop(get_redis, None)


def _make_operator(db: Session, *, pin: str | None = _TEST_PIN) -> User:
    user = User(
        id=uuid4(),
        username=f"op27_{uuid4().hex[:8]}",
        hashed_password=hash_password("Test1234!"),
        hashed_pin=hash_password(pin) if pin else None,
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db.add(user)
    db.commit()
    return user


def _enrolled_device(super_admin_client: TestClient, db_session: Session) -> tuple[str, str]:
    site = _make_site(db_session)
    device_id = _create_pending_device(super_admin_client, str(site.id))
    code = _issue_code(super_admin_client, device_id, "initial_enrollment")
    body = _complete_enrollment(super_admin_client, code)
    return device_id, body["device_secret"]


def _verify_pin(
    client: TestClient,
    *,
    device_id: str,
    secret: str,
    operator_user_id: str,
    pin: str = _TEST_PIN,
):
    return client.post(
        v1(_OPERATOR_PIN_VERIFY),
        headers=_device_headers(device_id, secret),
        json={"operator_user_id": operator_user_id, "pin": pin},
    )


@pytest.mark.story_27_6
class TestStory276PinVerifyNominal:
    def test_valid_pin_starts_session_audit_success(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)

        with patch(
            "recyclic_api.services.shared_workstation_operator_pin_service.log_shared_workstation_pin_success"
        ) as log_success:
            resp = _verify_pin(
                ws_client,
                device_id=device_id,
                secret=secret,
                operator_user_id=str(operator.id),
            )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["device_id"] == device_id
        assert body["operator_user_id"] == str(operator.id)
        assert resp.headers.get("cache-control") == "no-store"
        log_success.assert_called_once()
        call_kw = log_success.call_args.kwargs
        assert "pin" not in call_kw

        status = ws_client.get(
            v1(_OPERATOR_SESSION_STATUS),
            headers=_device_headers(device_id, secret),
        )
        assert status.json()["active"] is True


@pytest.mark.story_27_6
class TestStory276PinInvalid:
    def test_invalid_pin_403_neutral_no_pin_in_audit(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)

        with patch(
            "recyclic_api.services.shared_workstation_operator_pin_service.log_shared_workstation_pin_failure"
        ) as log_failure:
            resp = _verify_pin(
                ws_client,
                device_id=device_id,
                secret=secret,
                operator_user_id=str(operator.id),
                pin="0000",
            )
        assert resp.status_code == 403
        assert _api_error_code(resp) == SHARED_WORKSTATION_PIN_INVALID
        log_failure.assert_called_once()
        fail_kw = log_failure.call_args.kwargs
        assert "pin" not in fail_kw
        assert fail_kw.get("outcome") == "invalid"


@pytest.mark.story_27_6
class TestStory276PinLockout:
    def test_five_failures_then_lockout_429(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)

        for _ in range(5):
            r = _verify_pin(
                ws_client,
                device_id=device_id,
                secret=secret,
                operator_user_id=str(operator.id),
                pin="0000",
            )
            assert r.status_code in (403, 429)

        locked = _verify_pin(
            ws_client,
            device_id=device_id,
            secret=secret,
            operator_user_id=str(operator.id),
            pin=_TEST_PIN,
        )
        assert locked.status_code == 429
        assert _api_error_code(locked) == SHARED_WORKSTATION_PIN_LOCKED


@pytest.mark.story_27_6
class TestStory276SuperAdminClearLockout:
    def test_clear_lockout_then_pin_ok(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)

        for _ in range(5):
            _verify_pin(
                ws_client,
                device_id=device_id,
                secret=secret,
                operator_user_id=str(operator.id),
                pin="0000",
            )

        clear = super_admin_client.post(
            v1(_CLEAR_LOCKOUT.format(device_id=device_id)),
            json={"operator_user_id": str(operator.id)},
        )
        assert clear.status_code == 204

        ok = _verify_pin(
            ws_client,
            device_id=device_id,
            secret=secret,
            operator_user_id=str(operator.id),
        )
        assert ok.status_code == 200


@pytest.mark.story_27_6
class TestStory276ContextRegression:
    def test_context_403_without_operator_session(
        self, super_admin_client: TestClient, db_session: Session, admin_client: TestClient
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        resp = admin_client.get(
            v1(_SHARED_WS_CONTEXT),
            headers=_device_headers(device_id, secret),
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"


@pytest.mark.story_27_6
class TestStory276OperatorChange:
    def test_two_operators_superseded_audits(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        op1 = _make_operator(db_session, pin="1111")
        op2 = _make_operator(db_session, pin="2222")

        with patch(
            "recyclic_api.services.device_operator_session_service.log_device_operator_session_ended"
        ) as log_ended:
            r1 = _verify_pin(
                ws_client,
                device_id=device_id,
                secret=secret,
                operator_user_id=str(op1.id),
                pin="1111",
            )
            assert r1.status_code == 200
            r2 = _verify_pin(
                ws_client,
                device_id=device_id,
                secret=secret,
                operator_user_id=str(op2.id),
                pin="2222",
            )
            assert r2.status_code == 200

        assert any(
            call.kwargs.get("reason") == "superseded" for call in log_ended.call_args_list
        )


@pytest.mark.story_27_6
class TestStory276SanitizeAudit:
    def test_sanitize_audit_details_redacts_pin(self):
        out = sanitize_audit_details({"pin": "1234", "device_id": "d1"})
        assert out["pin"] == "[REDACTED]"
        assert out["device_id"] == "d1"


@pytest.mark.story_27_6
class TestStory276CredentialBeforePin:
    def test_invalid_credential_403_before_pin(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)

        resp = _verify_pin(
            ws_client,
            device_id=device_id,
            secret="wrong-secret",
            operator_user_id=str(operator.id),
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) in ("DEVICE_CREDENTIAL_REVOKED", "DEVICE_IDENTITY_CONFLICT")


@pytest.mark.story_27_6
class TestStory276PinNotConfigured:
    def test_no_hashed_pin_returns_not_configured_code(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session, pin=None)

        resp = _verify_pin(
            ws_client,
            device_id=device_id,
            secret=secret,
            operator_user_id=str(operator.id),
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == SHARED_WORKSTATION_PIN_NOT_CONFIGURED
