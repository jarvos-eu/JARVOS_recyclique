# Tests des routes cash_sessions (Story 5.1).
# POST open, GET list/current/id/status/deferred/check, POST close, GET/PUT step.

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from api.models import CashSession
from api.models.audit_event import AuditEvent
from api.tests.conftest import TestingSessionLocal


def test_open_cash_session(client, auth_headers, test_user, test_site, test_register, db_session):
    """POST /v1/cash-sessions crée une session et un audit_event."""
    r = client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 10000,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["register_id"] == str(test_register.id)
    assert data["operator_id"] == str(test_user.id)
    assert data["site_id"] == str(test_site.id)
    assert data["initial_amount"] == 10000
    assert data["current_amount"] == 10000
    assert data["status"] == "open"
    assert data["current_step"] == "entry"
    session_id = data["id"]

    # Audit enregistré (nouvelle session pour voir les données commitées depuis le thread du request)
    s = TestingSessionLocal()
    try:
        evt = (
            s.execute(
                select(AuditEvent).where(
                    AuditEvent.action == "cash_session_opened",
                    AuditEvent.resource_id == session_id,
                )
            )
            .scalars()
            .one_or_none()
        )
    finally:
        s.close()
    assert evt is not None


def test_open_cash_session_409_if_register_already_open(
    client, auth_headers, test_user, test_site, test_register, db_session
):
    """POST /v1/cash-sessions retourne 409 si le register a déjà une session ouverte."""
    r1 = client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 0,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    assert r1.status_code == 201
    r2 = client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 0,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    assert r2.status_code == 409
    assert "open session" in r2.json().get("detail", "").lower()


def test_list_cash_sessions(client, auth_headers, test_user, test_site, test_register):
    """GET /v1/cash-sessions retourne la liste (filtres optionnels)."""
    client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 5000,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    r = client.get("/v1/cash-sessions", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    r2 = client.get(
        f"/v1/cash-sessions?register_id={test_register.id}",
        headers=auth_headers,
    )
    assert r2.status_code == 200
    assert all(s["register_id"] == str(test_register.id) for s in r2.json())


def test_get_current_session(client, auth_headers, test_user, test_site, test_register):
    """GET /v1/cash-sessions/current retourne la session ouverte de l'opérateur."""
    r_empty = client.get("/v1/cash-sessions/current", headers=auth_headers)
    assert r_empty.status_code == 200
    assert r_empty.json() is None
    client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 0,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    r = client.get("/v1/cash-sessions/current", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data is not None
    assert data["status"] == "open"
    assert data["operator_id"] == str(test_user.id)


def test_get_cash_session_by_id(client, auth_headers, test_user, test_site, test_register):
    """GET /v1/cash-sessions/{id} retourne le détail ou 404."""
    r404 = client.get(f"/v1/cash-sessions/{uuid4()}", headers=auth_headers)
    assert r404.status_code == 404
    create = client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 0,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    session_id = create.json()["id"]
    r = client.get(f"/v1/cash-sessions/{session_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == session_id


def test_get_register_status(client, auth_headers, test_user, test_site, test_register):
    """GET /v1/cash-sessions/status/{register_id} retourne has_open_session."""
    r_before = client.get(
        f"/v1/cash-sessions/status/{test_register.id}",
        headers=auth_headers,
    )
    assert r_before.status_code == 200
    assert r_before.json()["has_open_session"] is False
    client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 0,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    r_after = client.get(
        f"/v1/cash-sessions/status/{test_register.id}",
        headers=auth_headers,
    )
    assert r_after.status_code == 200
    assert r_after.json()["has_open_session"] is True


def test_close_cash_session(client, auth_headers, test_user, test_site, test_register, db_session):
    """POST /v1/cash-sessions/{id}/close ferme la session et enregistre l'audit."""
    create = client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 10000,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    session_id = create.json()["id"]
    r = client.post(
        f"/v1/cash-sessions/{session_id}/close",
        json={
            "closing_amount": 10500,
            "actual_amount": 10500,
            "variance_comment": "OK",
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "closed"
    assert data["closing_amount"] == 10500
    assert data["actual_amount"] == 10500
    assert data["closed_at"] is not None

    s = TestingSessionLocal()
    try:
        evt = (
            s.execute(
                select(AuditEvent).where(
                    AuditEvent.action == "cash_session_closed",
                    AuditEvent.resource_id == session_id,
                )
            )
            .scalars()
            .one_or_none()
        )
    finally:
        s.close()
    assert evt is not None


def test_close_cash_session_400_if_already_closed(
    client, auth_headers, test_user, test_site, test_register
):
    """POST close retourne 400 si la session est déjà fermée."""
    create = client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 0,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    session_id = create.json()["id"]
    client.post(f"/v1/cash-sessions/{session_id}/close", json={}, headers=auth_headers)
    r2 = client.post(f"/v1/cash-sessions/{session_id}/close", json={}, headers=auth_headers)
    assert r2.status_code == 400


def test_deferred_check(client, auth_headers, test_user, test_site, test_register):
    """GET /v1/cash-sessions/deferred/check avec date YYYY-MM-DD."""
    r = client.get(
        "/v1/cash-sessions/deferred/check?date=2026-02-27",
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["date"] == "2026-02-27"
    assert "has_session" in data


def test_get_and_put_step(client, auth_headers, test_user, test_site, test_register):
    """GET et PUT /v1/cash-sessions/{id}/step."""
    create = client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 0,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    session_id = create.json()["id"]
    r_get = client.get(f"/v1/cash-sessions/{session_id}/step", headers=auth_headers)
    assert r_get.status_code == 200
    assert r_get.json()["current_step"] == "entry"
    r_put = client.put(
        f"/v1/cash-sessions/{session_id}/step",
        json={"step": "sale"},
        headers=auth_headers,
    )
    assert r_put.status_code == 200
    assert r_put.json()["current_step"] == "sale"


def test_unauthorized_cash_sessions(client, test_register):
    """Sans token Bearer, les routes protégées retournent 401."""
    r = client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 0,
            "register_id": str(test_register.id),
        },
    )
    assert r.status_code == 401


def test_close_cash_session_with_totals(
    client, auth_headers, test_user, test_site, test_register, test_preset
):
    """POST close après des ventes renvoie total_sales et total_items (Story 5.3)."""
    create = client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 0,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    assert create.status_code == 201
    session_id = create.json()["id"]
    # Une vente (1 ligne, 500 centimes)
    sale_body = {
        "cash_session_id": session_id,
        "items": [
            {
                "preset_id": str(test_preset.id),
                "quantity": 1,
                "unit_price": test_preset.preset_price,
                "total_price": test_preset.preset_price,
            }
        ],
        "payments": [{"payment_method": "especes", "amount": test_preset.preset_price}],
    }
    client.post("/v1/sales", json=sale_body, headers=auth_headers)
    r = client.post(
        f"/v1/cash-sessions/{session_id}/close",
        json={"closing_amount": 500, "actual_amount": 500},
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "closed"
    assert data["total_sales"] == test_preset.preset_price
    assert data["total_items"] == 1


def test_get_current_session_returns_totals(
    client, auth_headers, test_user, test_site, test_register, test_preset
):
    """GET /v1/cash-sessions/current renvoie total_sales et total_items pour session ouverte (Story 5.3)."""
    create = client.post(
        "/v1/cash-sessions",
        json={
            "initial_amount": 0,
            "register_id": str(test_register.id),
            "session_type": "real",
        },
        headers=auth_headers,
    )
    session_id = create.json()["id"]
    sale_body = {
        "cash_session_id": session_id,
        "items": [
            {
                "preset_id": str(test_preset.id),
                "quantity": 2,
                "unit_price": 100,
                "total_price": 200,
            }
        ],
        "payments": [{"payment_method": "especes", "amount": 200}],
    }
    client.post("/v1/sales", json=sale_body, headers=auth_headers)
    r = client.get("/v1/cash-sessions/current", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data is not None
    assert data["total_sales"] == 200
    assert data["total_items"] == 1
