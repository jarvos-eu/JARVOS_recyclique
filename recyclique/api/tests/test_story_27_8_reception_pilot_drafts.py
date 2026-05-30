"""Story 27.8 — brouillon réception pilote poste partagé (masquage, reprise, abandon)."""

from __future__ import annotations

from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.core.security import create_access_token, hash_password
from recyclic_api.models.registered_device import RegisteredDevice
from recyclic_api.models.category import Category
from recyclic_api.models.site import Site
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

_RECEPTION_DRAFT = f"{_SHARED_WS}/reception-draft"
_RECEPTION_DRAFT_RESUME = f"{_RECEPTION_DRAFT}/resume"
_RECEPTION_DRAFT_ABANDON = f"{_RECEPTION_DRAFT}/abandon"
_RECEPTION = "/reception"


def _auth_headers(user_id) -> dict:
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


def _device_auth_headers(user_id, device_id: str, secret: str, **extra) -> dict:
    headers = _auth_headers(user_id)
    headers.update(_device_headers(device_id, secret))
    headers.update(extra)
    return headers


def _make_user(db: Session, *, site: Site, with_reception: bool = True) -> User:
    user = User(
        id=uuid4(),
        username=f"op278_{uuid4().hex[:8]}",
        hashed_password=hash_password("Test1234!"),
        hashed_pin=hash_password("4242"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_active=True,
        site_id=site.id,
    )
    db.add(user)
    db.commit()
    if with_reception:
        grant_user_reception_eligibility(db, user, site.id)
    return user


def _create_pending_device_modules(client: TestClient, site_id: str, allowed: list[str]) -> str:
    resp = client.post(
        v1("/registered-devices"),
        json={"name": "Poste 27.8", "site_id": site_id, "allowed_module_keys": allowed},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["device_id"]


def _enrolled_device(client: TestClient, db: Session, site: Site) -> tuple[str, str]:
    device_id = _create_pending_device(client, str(site.id))
    db_device = db.get(RegisteredDevice, UUID(device_id))
    assert db_device is not None
    db_device.allowed_module_keys = [MODULE_KEY_RECEPTION]
    db.commit()
    code = _issue_code(client, device_id, "initial_enrollment")
    body = _complete_enrollment(client, code)
    return device_id, body["device_secret"]


def _clear_device_session(db: Session, device_id: str) -> None:
    """Simule fin de session sans écriture audit (isolation SQLite tests)."""
    from recyclic_api.models.device_operator_session import (
        DeviceOperatorSession,
        DeviceOperatorSessionStatus,
    )

    (
        db.query(DeviceOperatorSession)
        .filter(
            DeviceOperatorSession.device_id == UUID(device_id),
            DeviceOperatorSession.status == DeviceOperatorSessionStatus.ACTIVE.value,
        )
        .update(
            {
                DeviceOperatorSession.status: DeviceOperatorSessionStatus.ENDED.value,
            },
            synchronize_session=False,
        )
    )
    db.commit()


def _end_device_session(db: Session, device_id: str) -> None:
    _clear_device_session(db, device_id)


def _start_session(db: Session, device_id: str, operator: User) -> None:
    DeviceOperatorSessionService(db).start_session(
        device_id=device_id,
        operator_user_id=str(operator.id),
        active_module_key=MODULE_KEY_RECEPTION,
    )


def _make_category(db: Session) -> Category:
    category = Category(
        id=uuid4(),
        name=f"cat278_{uuid4().hex[:8]}",
        is_active=True,
        is_visible=True,
    )
    db.add(category)
    db.commit()
    return category


def _open_poste_and_ticket(
    client: TestClient,
    *,
    operator: User,
    device_id: str,
    secret: str,
) -> tuple[str, str]:
    headers = _device_auth_headers(operator.id, device_id, secret)
    r_poste = client.post(v1(f"{_RECEPTION}/postes/open"), headers=headers)
    assert r_poste.status_code == 200, r_poste.text
    poste_id = r_poste.json()["id"]
    r_ticket = client.post(
        v1(f"{_RECEPTION}/tickets"),
        headers=headers,
        json={"poste_id": poste_id},
    )
    assert r_ticket.status_code == 200, r_ticket.text
    return poste_id, r_ticket.json()["id"]


@pytest.mark.story_27_8
class TestStory278DraftLocked:
    def test_get_draft_without_pin_403(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        headers = _device_auth_headers(operator.id, device_id, secret)
        resp = super_admin_client.get(v1(_RECEPTION_DRAFT), headers=headers)
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"


@pytest.mark.story_27_8
class TestStory278DraftSummary:
    def test_authorized_summary_without_lines(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        resp = super_admin_client.get(
            v1(_RECEPTION_DRAFT),
            headers=_device_auth_headers(operator.id, device_id, secret),
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "summary" in body
        summary = body["summary"]
        assert "poste_id" in summary
        assert "ticket_id" in summary
        assert "started_by_display" in summary
        assert summary["line_count"] == 0
        assert "lignes" not in body
        assert resp.headers.get("cache-control") == "no-store"


@pytest.mark.story_27_8
class TestStory278Forbidden:
    def test_operator_without_reception_access_403(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site, with_reception=False)
        _start_session(db_session, device_id, operator)
        resp = super_admin_client.get(
            v1(_RECEPTION_DRAFT),
            headers=_device_auth_headers(operator.id, device_id, secret),
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) in (
            "SHARED_WORKSTATION_RECEPTION_DRAFT_FORBIDDEN",
            "SHARED_WORKSTATION_MODULE_FORBIDDEN",
        )

    def test_reception_not_in_allowlist_403(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = _create_pending_device_modules(super_admin_client, str(site.id), [])
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        body = _complete_enrollment(super_admin_client, code)
        secret = body["device_secret"]
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        resp = super_admin_client.get(
            v1(_RECEPTION_DRAFT),
            headers=_device_auth_headers(operator.id, device_id, secret),
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_MODULE_FORBIDDEN"


@pytest.mark.story_27_8
class TestStory278TicketLeak:
    def test_get_ticket_without_pin_403(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator_a = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator_a)
        _, ticket_id = _open_poste_and_ticket(
            super_admin_client, operator=operator_a, device_id=device_id, secret=secret
        )
        _end_device_session(db_session, device_id)
        headers = _device_auth_headers(operator_a.id, device_id, secret)
        resp = super_admin_client.get(v1(f"{_RECEPTION}/tickets/{ticket_id}"), headers=headers)
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"


@pytest.mark.story_27_8
class TestStory278InterOperator:
    def test_resume_by_operator_b_audit_and_ticket_access(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator_a = _make_user(db_session, site=site)
        operator_b = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator_a)
        poste_id, ticket_id = _open_poste_and_ticket(
            super_admin_client, operator=operator_a, device_id=device_id, secret=secret
        )
        _clear_device_session(db_session, device_id)
        _start_session(db_session, device_id, operator_b)
        headers_b = _device_auth_headers(operator_b.id, device_id, secret)
        with patch(
            "recyclic_api.services.shared_workstation_reception_draft_service.log_shared_workstation_reception_draft_resumed"
        ) as log_resumed:
            resume = super_admin_client.post(
                v1(_RECEPTION_DRAFT_RESUME),
                headers=headers_b,
                json={"confirm": True},
            )
        assert resume.status_code == 200, resume.text
        assert resume.json()["poste_id"] == poste_id
        assert resume.json()["ticket_id"] == ticket_id
        log_resumed.assert_called_once()
        assert "pin" not in str(log_resumed.call_args.kwargs).lower()

        detail = super_admin_client.get(
            v1(f"{_RECEPTION}/tickets/{ticket_id}"),
            headers=headers_b,
        )
        assert detail.status_code == 200, detail.text

        category = _make_category(db_session)
        r_ligne = super_admin_client.post(
            v1(f"{_RECEPTION}/lignes"),
            headers=headers_b,
            json={
                "ticket_id": ticket_id,
                "category_id": str(category.id),
                "poids_kg": 2.5,
                "destination": "MAGASIN",
            },
        )
        assert r_ligne.status_code == 200, r_ligne.text
        ligne_id = r_ligne.json()["id"]

        r_update = super_admin_client.put(
            v1(f"{_RECEPTION}/lignes/{ligne_id}"),
            headers=headers_b,
            json={"poids_kg": 3.0},
        )
        assert r_update.status_code == 200, r_update.text
        assert float(r_update.json()["poids_kg"]) == 3.0

        r_delete = super_admin_client.delete(
            v1(f"{_RECEPTION}/lignes/{ligne_id}"),
            headers=headers_b,
        )
        assert r_delete.status_code == 200, r_delete.text


@pytest.mark.story_27_8
class TestStory278Abandon:
    def test_abandon_closes_and_audits(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        with patch(
            "recyclic_api.services.shared_workstation_reception_draft_service.log_shared_workstation_reception_draft_abandoned"
        ) as log_abandoned:
            resp = super_admin_client.post(
                v1(_RECEPTION_DRAFT_ABANDON),
                headers=_device_auth_headers(operator.id, device_id, secret),
                json={"confirm": True},
            )
        assert resp.status_code == 200, resp.text
        log_abandoned.assert_called_once()
        draft = super_admin_client.get(
            v1(_RECEPTION_DRAFT),
            headers=_device_auth_headers(operator.id, device_id, secret),
        )
        assert draft.status_code == 204


@pytest.mark.story_27_8
class TestStory278Confirm:
    def test_resume_without_confirm_422(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        resp = super_admin_client.post(
            v1(_RECEPTION_DRAFT_RESUME),
            headers=_device_auth_headers(operator.id, device_id, secret),
            json={"confirm": False},
        )
        assert resp.status_code == 422

    def test_abandon_without_confirm_422(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        resp = super_admin_client.post(
            v1(_RECEPTION_DRAFT_ABANDON),
            headers=_device_auth_headers(operator.id, device_id, secret),
            json={"confirm": False},
        )
        assert resp.status_code == 422


@pytest.mark.story_27_8
class TestStory278SingleDraft:
    def test_second_open_poste_same_device_409(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        headers = _device_auth_headers(operator.id, device_id, secret)
        resp = super_admin_client.post(v1(f"{_RECEPTION}/postes/open"), headers=headers)
        assert resp.status_code == 409
        assert _api_error_code(resp) == "SHARED_WORKSTATION_RECEPTION_DRAFT_ALREADY_ACTIVE"


@pytest.mark.story_27_8
class TestStory278ReceptionGuardM1:
    """CR loop 1 — garde PIN complète routes nominaux (M1)."""

    def test_put_ligne_without_pin_403(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        _, ticket_id = _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        category = _make_category(db_session)
        headers = _device_auth_headers(operator.id, device_id, secret)
        r_ligne = super_admin_client.post(
            v1(f"{_RECEPTION}/lignes"),
            headers=headers,
            json={
                "ticket_id": ticket_id,
                "category_id": str(category.id),
                "poids_kg": 1.0,
                "destination": "MAGASIN",
            },
        )
        assert r_ligne.status_code == 200, r_ligne.text
        ligne_id = r_ligne.json()["id"]
        _end_device_session(db_session, device_id)
        resp = super_admin_client.put(
            v1(f"{_RECEPTION}/lignes/{ligne_id}"),
            headers=headers,
            json={"poids_kg": 2.0},
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"

    def test_close_poste_without_pin_403(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        poste_id, _ = _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        headers = _device_auth_headers(operator.id, device_id, secret)
        _end_device_session(db_session, device_id)
        resp = super_admin_client.post(
            v1(f"{_RECEPTION}/postes/{poste_id}/close"),
            headers=headers,
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"

    def test_close_ticket_without_pin_403(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        _, ticket_id = _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        headers = _device_auth_headers(operator.id, device_id, secret)
        _end_device_session(db_session, device_id)
        resp = super_admin_client.post(
            v1(f"{_RECEPTION}/tickets/{ticket_id}/close"),
            headers=headers,
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"

    def test_delete_ligne_without_pin_403(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        _, ticket_id = _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        category = _make_category(db_session)
        headers = _device_auth_headers(operator.id, device_id, secret)
        r_ligne = super_admin_client.post(
            v1(f"{_RECEPTION}/lignes"),
            headers=headers,
            json={
                "ticket_id": ticket_id,
                "category_id": str(category.id),
                "poids_kg": 1.0,
                "destination": "MAGASIN",
            },
        )
        assert r_ligne.status_code == 200, r_ligne.text
        ligne_id = r_ligne.json()["id"]
        _end_device_session(db_session, device_id)
        resp = super_admin_client.delete(
            v1(f"{_RECEPTION}/lignes/{ligne_id}"),
            headers=headers,
        )
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"

    def test_get_ticket_brownfield_without_device_headers_403(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        _, ticket_id = _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        _start_session(db_session, device_id, operator)
        jwt_only = _auth_headers(operator.id)
        resp = super_admin_client.get(v1(f"{_RECEPTION}/tickets/{ticket_id}"), headers=jwt_only)
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"

    def test_get_tickets_list_hides_enrolled_draft_without_device(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id, secret = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        _, ticket_id = _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_id, secret=secret
        )
        category = _make_category(db_session)
        headers = _device_auth_headers(operator.id, device_id, secret)
        r_ligne = super_admin_client.post(
            v1(f"{_RECEPTION}/lignes"),
            headers=headers,
            json={
                "ticket_id": ticket_id,
                "category_id": str(category.id),
                "poids_kg": 1.0,
                "destination": "MAGASIN",
            },
        )
        assert r_ligne.status_code == 200, r_ligne.text
        jwt_only = _auth_headers(operator.id)
        resp = super_admin_client.get(v1(f"{_RECEPTION}/tickets"), headers=jwt_only)
        assert resp.status_code == 200, resp.text
        ids = [t["id"] for t in resp.json().get("tickets", [])]
        assert ticket_id not in ids

    def test_get_ticket_wrong_device_scope_403(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_a, secret_a = _enrolled_device(super_admin_client, db_session, site)
        device_b, secret_b = _enrolled_device(super_admin_client, db_session, site)
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_a, operator)
        _, ticket_id = _open_poste_and_ticket(
            super_admin_client, operator=operator, device_id=device_a, secret=secret_a
        )
        _clear_device_session(db_session, device_a)
        _start_session(db_session, device_b, operator)
        headers_b = _device_auth_headers(operator.id, device_b, secret_b)
        resp = super_admin_client.get(v1(f"{_RECEPTION}/tickets/{ticket_id}"), headers=headers_b)
        assert resp.status_code == 403
        assert _api_error_code(resp) == "SHARED_WORKSTATION_OPERATOR_REQUIRED"


@pytest.mark.story_27_8
class TestStory278Brownfield:
    def test_web_user_without_device_unchanged(self, user_client: TestClient):
        resp = user_client.post(v1(f"{_RECEPTION}/postes/open"))
        assert resp.status_code in (200, 403)


@pytest.mark.story_27_8
class TestStory278Context:
    def test_no_draft_summary_when_module_not_effective(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = _create_pending_device_modules(super_admin_client, str(site.id), [])
        code = _issue_code(super_admin_client, device_id, "initial_enrollment")
        body = _complete_enrollment(super_admin_client, code)
        secret = body["device_secret"]
        operator = _make_user(db_session, site=site)
        _start_session(db_session, device_id, operator)
        resp = super_admin_client.get(
            v1(f"{_SHARED_WS}/context"),
            headers=_device_auth_headers(operator.id, device_id, secret),
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data.get("reception_draft_summary") is None
