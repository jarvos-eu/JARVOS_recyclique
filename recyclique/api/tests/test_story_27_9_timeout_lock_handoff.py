"""Story 27.9 — timeout inactivité, verrouillage, passage de main poste partagé."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.core.audit import sanitize_audit_details
from recyclic_api.core.redis import get_redis
from recyclic_api.core.security import create_access_token, hash_password
from recyclic_api.models.device_operator_session import (
    DeviceOperatorSession,
    DeviceOperatorSessionStatus,
)
from recyclic_api.models.registered_device import DEFAULT_INACTIVITY_TIMEOUT_SECONDS, RegisteredDevice
from recyclic_api.models.user import User, UserRole, UserStatus
from recyclic_api.modules.module_config.registry import MODULE_KEY_RECEPTION
from recyclic_api.services.device_operator_session_service import DeviceOperatorSessionService
from tests.api_v1_paths import v1
from tests.reception_story72_eligibility import grant_user_reception_eligibility
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
    _make_operator,
    _verify_pin,
)

_OPERATOR_SESSION_STATUS = f"{_SHARED_WS}/operator-session/status"
_OPERATOR_SESSION_END = f"{_SHARED_WS}/operator-session/end"
_OPERATOR_SESSION_ACTIVITY = f"{_SHARED_WS}/operator-session/activity"
_SHARED_WS_CONTEXT = f"{_SHARED_WS}/context"
_RECEPTION_DRAFT = f"{_SHARED_WS}/reception-draft"


def _auth_headers(user_id) -> dict:
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


def _device_auth_headers(user_id, device_id: str, secret: str, **extra) -> dict:
    headers = _auth_headers(user_id)
    headers.update(_device_headers(device_id, secret))
    headers.update(extra)
    return headers


def _enrolled_device(client: TestClient, db: Session) -> tuple[str, str]:
    site = _make_site(db)
    device_id = _create_pending_device(client, str(site.id))
    db_device = db.get(RegisteredDevice, UUID(device_id))
    assert db_device is not None
    db_device.allowed_module_keys = [MODULE_KEY_RECEPTION]
    db.commit()
    code = _issue_code(client, device_id, "initial_enrollment")
    body = _complete_enrollment(client, code)
    return device_id, body["device_secret"]


def _start_session(
    ws_client: TestClient,
    *,
    device_id: str,
    secret: str,
    operator: User,
) -> None:
    resp = _verify_pin(
        ws_client,
        device_id=device_id,
        secret=secret,
        operator_user_id=str(operator.id),
    )
    assert resp.status_code == 200, resp.text


def _set_last_activity(
    db: Session,
    device_id: str,
    *,
    seconds_ago: int,
) -> DeviceOperatorSession:
    session = (
        db.query(DeviceOperatorSession)
        .filter(
            DeviceOperatorSession.device_id == UUID(device_id),
            DeviceOperatorSession.status == DeviceOperatorSessionStatus.ACTIVE.value,
        )
        .first()
    )
    assert session is not None
    session.last_activity_at = datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@pytest.fixture
def fake_redis():
    return _FakeRedis()


@pytest.fixture
def ws_client(super_admin_client: TestClient, fake_redis: _FakeRedis):
    super_admin_client.app.dependency_overrides[get_redis] = lambda: fake_redis
    yield super_admin_client
    super_admin_client.app.dependency_overrides.pop(get_redis, None)


@pytest.mark.story_27_9
class TestStory279ServerGuardExpire:
    def test_expired_session_context_403_and_audit_timeout(
        self,
        ws_client: TestClient,
        super_admin_client: TestClient,
        db_session: Session,
        admin_client: TestClient,
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        site = _make_site(db_session)
        operator = _make_operator(db_session)
        operator.site_id = site.id
        db_session.commit()
        grant_user_reception_eligibility(db_session, operator, site.id)
        _start_session(ws_client, device_id=device_id, secret=secret, operator=operator)
        _set_last_activity(
            db_session,
            device_id,
            seconds_ago=DEFAULT_INACTIVITY_TIMEOUT_SECONDS + 10,
        )

        with patch(
            "recyclic_api.services.device_operator_session_service.log_shared_workstation_operator_locked_timeout"
        ) as log_timeout:
            resp = admin_client.get(
                v1(_SHARED_WS_CONTEXT),
                headers=_device_auth_headers(operator.id, device_id, secret),
            )
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_SESSION_EXPIRED"
        log_timeout.assert_called_once()
        assert "pin" not in log_timeout.call_args.kwargs


@pytest.mark.story_27_9
class TestStory279EndSession:
    def test_manual_lock_ends_session_and_audit(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)
        _start_session(ws_client, device_id=device_id, secret=secret, operator=operator)

        with patch(
            "recyclic_api.services.device_operator_session_service.log_shared_workstation_operator_locked_manual"
        ) as log_manual:
            end = ws_client.post(
                v1(_OPERATOR_SESSION_END),
                headers=_device_headers(device_id, secret),
                json={"reason": "manual_lock"},
            )
        assert end.status_code == 200, end.text
        body = end.json()
        assert body["ended"] is True
        assert body["session_id"]
        assert end.headers.get("cache-control") == "no-store"
        log_manual.assert_called_once()
        assert log_manual.call_args.kwargs.get("reason") == "manual_lock"

        status = ws_client.get(
            v1(_OPERATOR_SESSION_STATUS),
            headers=_device_headers(device_id, secret),
        )
        assert status.json()["active"] is False

    def test_end_idempotent_without_double_audit(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)
        _start_session(ws_client, device_id=device_id, secret=secret, operator=operator)

        ws_client.post(
            v1(_OPERATOR_SESSION_END),
            headers=_device_headers(device_id, secret),
            json={"reason": "handoff"},
        )
        with patch(
            "recyclic_api.services.device_operator_session_service.log_shared_workstation_operator_locked_manual"
        ) as log_manual:
            again = ws_client.post(
                v1(_OPERATOR_SESSION_END),
                headers=_device_headers(device_id, secret),
                json={"reason": "handoff"},
            )
        assert again.status_code == 200
        assert again.json()["ended"] is False
        log_manual.assert_not_called()

    def test_end_without_session_200_not_403(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        resp = ws_client.post(
            v1(_OPERATOR_SESSION_END),
            headers=_device_headers(device_id, secret),
            json={"reason": "manual_lock"},
        )
        assert resp.status_code == 200
        assert resp.json()["ended"] is False


@pytest.mark.story_27_9
class TestStory279Activity:
    def test_activity_updates_last_activity_throttled(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)
        _start_session(ws_client, device_id=device_id, secret=secret, operator=operator)
        session = DeviceOperatorSessionService(db_session).get_active_for_device(device_id=device_id)
        assert session is not None
        before = session.last_activity_at

        touch1 = ws_client.post(
            v1(_OPERATOR_SESSION_ACTIVITY),
            headers=_device_headers(device_id, secret),
        )
        assert touch1.status_code == 204
        db_session.refresh(session)
        after1 = session.last_activity_at
        assert after1 >= before

        touch2 = ws_client.post(
            v1(_OPERATOR_SESSION_ACTIVITY),
            headers=_device_headers(device_id, secret),
        )
        assert touch2.status_code == 204
        db_session.refresh(session)
        assert session.last_activity_at == after1

    def test_activity_without_session_403(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        resp = ws_client.post(
            v1(_OPERATOR_SESSION_ACTIVITY),
            headers=_device_headers(device_id, secret),
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"


@pytest.mark.story_27_9
class TestStory279EnrichedStatus:
    def test_status_includes_timeout_fields(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)
        _start_session(ws_client, device_id=device_id, secret=secret, operator=operator)
        _set_last_activity(db_session, device_id, seconds_ago=120)

        status = ws_client.get(
            v1(_OPERATOR_SESSION_STATUS),
            headers=_device_headers(device_id, secret),
        )
        assert status.status_code == 200
        body = status.json()
        assert body["active"] is True
        assert body["inactivity_timeout_seconds"] == DEFAULT_INACTIVITY_TIMEOUT_SECONDS
        assert body["last_activity_at"]
        assert abs(body["seconds_until_lock"] - (DEFAULT_INACTIVITY_TIMEOUT_SECONDS - 120)) <= 2


@pytest.mark.story_27_9
class TestStory279Audit:
    def test_timeout_vs_manual_reason_in_audit(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)
        _start_session(ws_client, device_id=device_id, secret=secret, operator=operator)

        with patch(
            "recyclic_api.services.device_operator_session_service.log_shared_workstation_operator_locked_timeout"
        ) as log_timeout:
            ws_client.post(
                v1(_OPERATOR_SESSION_END),
                headers=_device_headers(device_id, secret),
                json={"reason": "timeout"},
            )
        log_timeout.assert_called_once()

        _start_session(ws_client, device_id=device_id, secret=secret, operator=operator)
        with patch(
            "recyclic_api.services.device_operator_session_service.log_shared_workstation_operator_locked_manual"
        ) as log_manual:
            ws_client.post(
                v1(_OPERATOR_SESSION_END),
                headers=_device_headers(device_id, secret),
                json={"reason": "handoff"},
            )
        log_manual.assert_called_once()
        assert log_manual.call_args.kwargs.get("reason") == "handoff"

    def test_sanitize_no_pin_in_audit_details(self):
        out = sanitize_audit_details({"pin": "9999", "reason": "timeout"})
        assert out["pin"] == "[REDACTED]"
        assert out["reason"] == "timeout"


@pytest.mark.story_27_9
class TestStory279Regression276:
    def test_pin_session_end_lock_path(
        self, ws_client: TestClient, super_admin_client: TestClient, db_session: Session
    ):
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = _make_operator(db_session)
        _start_session(ws_client, device_id=device_id, secret=secret, operator=operator)
        ws_client.post(
            v1(_OPERATOR_SESSION_END),
            headers=_device_headers(device_id, secret),
            json={"reason": "manual_lock"},
        )
        status = ws_client.get(
            v1(_OPERATOR_SESSION_STATUS),
            headers=_device_headers(device_id, secret),
        )
        assert status.json()["active"] is False


@pytest.mark.story_27_9
class TestStory279Regression278:
    def test_reception_draft_403_after_end_session(
        self,
        ws_client: TestClient,
        super_admin_client: TestClient,
        db_session: Session,
        admin_client: TestClient,
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session)
        operator = User(
            id=uuid4(),
            username=f"op279_{uuid4().hex[:8]}",
            hashed_password=hash_password("Test1234!"),
            hashed_pin=hash_password(_TEST_PIN),
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            is_active=True,
            site_id=site.id,
        )
        db_session.add(operator)
        db_session.commit()
        grant_user_reception_eligibility(db_session, operator, site.id)
        _start_session(ws_client, device_id=device_id, secret=secret, operator=operator)

        ws_client.post(
            v1(_OPERATOR_SESSION_END),
            headers=_device_headers(device_id, secret),
            json={"reason": "handoff"},
        )

        draft = admin_client.get(
            v1(_RECEPTION_DRAFT),
            headers=_device_auth_headers(operator.id, device_id, secret),
        )
        assert draft.status_code == 403
        assert _api_error_code(draft) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"
