"""Tests API Story 3.4 — demarrer poste caisse (POST start/stop), audit, reception postes/open."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from uuid import UUID

from api.models import AuditEvent, CashRegister, PosteReception, Site


def _create_site(client: TestClient, auth_headers: dict, name: str = "Site Start") -> str:
    resp = client.post("/v1/sites", json={"name": name, "is_active": True}, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()["id"]


def _create_register(client: TestClient, auth_headers: dict, site_id: str, name: str = "Caisse 1") -> str:
    resp = client.post(
        "/v1/cash-registers",
        json={
            "site_id": site_id,
            "name": name,
            "is_active": True,
            "enable_virtual": False,
            "enable_deferred": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_post_admin_cash_registers_start_200_and_state(client: TestClient, auth_headers: dict, db_session):
    """POST /v1/admin/cash-registers/start avec admin -> 200 et etat enregistre."""
    site_id = _create_site(client, auth_headers)
    register_id = _create_register(client, auth_headers, site_id)
    resp = client.post(
        "/v1/admin/cash-registers/start",
        json={"site_id": site_id, "register_id": register_id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == register_id
    assert data["started_at"] is not None
    assert data["started_by_user_id"] is not None
    reg = db_session.execute(
        select(CashRegister).where(CashRegister.id == UUID(register_id))
    ).scalars().one_or_none()
    assert reg is not None
    assert reg.started_at is not None
    assert reg.started_by_user_id is not None


def test_post_admin_cash_registers_start_without_admin_403(client: TestClient, user_without_admin, db_session, site):
    """POST /v1/admin/cash-registers/start sans admin -> 403."""
    _, token = user_without_admin
    site_id = str(site.id)
    reg = CashRegister(site_id=site.id, name="R1", is_active=True)
    db_session.add(reg)
    db_session.commit()
    db_session.refresh(reg)
    resp = client.post(
        "/v1/admin/cash-registers/start",
        json={"site_id": site_id, "register_id": str(reg.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_post_admin_cash_registers_start_site_register_mismatch_400(client: TestClient, auth_headers: dict, db_session, site):
    """POST start avec site_id et register_id incoherents -> 400."""
    site_id = str(site.id)
    other_site = Site(name="Other", is_active=True)
    db_session.add(other_site)
    db_session.commit()
    db_session.refresh(other_site)
    reg = CashRegister(site_id=other_site.id, name="R2", is_active=True)
    db_session.add(reg)
    db_session.commit()
    db_session.refresh(reg)
    resp = client.post(
        "/v1/admin/cash-registers/start",
        json={"site_id": site_id, "register_id": str(reg.id)},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


def test_post_admin_cash_registers_start_creates_audit_event(client: TestClient, auth_headers: dict, db_session):
    """POST start enregistre un evenement audit_events."""
    site_id = _create_site(client, auth_headers)
    register_id = _create_register(client, auth_headers, site_id)
    before = db_session.execute(select(AuditEvent).where(AuditEvent.action == "register_started")).scalars().all()
    resp = client.post(
        "/v1/admin/cash-registers/start",
        json={"site_id": site_id, "register_id": register_id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    after = db_session.execute(select(AuditEvent).where(AuditEvent.action == "register_started")).scalars().all()
    assert len(after) == len(before) + 1
    evt = after[-1]
    assert evt.resource_type == "cash_register"
    assert evt.resource_id == register_id


def test_post_cash_registers_stop_200(client: TestClient, auth_headers: dict, db_session, admin_user_and_token):
    """POST /v1/cash-registers/{id}/stop remet started_at a null et audit."""
    site_id = _create_site(client, auth_headers)
    register_id = _create_register(client, auth_headers, site_id)
    client.post(
        "/v1/admin/cash-registers/start",
        json={"site_id": site_id, "register_id": register_id},
        headers=auth_headers,
    )
    resp = client.post(f"/v1/cash-registers/{register_id}/stop", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["started_at"] is None
    assert data["started_by_user_id"] is None
    stopped = db_session.execute(select(AuditEvent).where(AuditEvent.action == "register_stopped")).scalars().all()
    assert len(stopped) >= 1


def test_get_cash_registers_status_includes_started(client: TestClient, auth_headers: dict):
    """GET /v1/cash-registers/status expose started_at et started_by_user_id."""
    site_id = _create_site(client, auth_headers)
    register_id = _create_register(client, auth_headers, site_id)
    resp = client.get("/v1/cash-registers/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["register_id"] == register_id
    assert data[0]["status"] == "free"
    assert "started_at" in data[0]
    assert "started_by_user_id" in data[0]
    client.post(
        "/v1/admin/cash-registers/start",
        json={"site_id": site_id, "register_id": register_id},
        headers=auth_headers,
    )
    resp2 = client.get("/v1/cash-registers/status", headers=auth_headers)
    assert resp2.status_code == 200
    assert resp2.json()[0]["status"] == "started"
    assert resp2.json()[0]["started_at"] is not None


def test_post_reception_postes_open_201_and_audit(client: TestClient, auth_headers: dict, db_session):
    """POST /v1/reception/postes/open avec admin -> 201 et audit reception_post_opened."""
    before = db_session.execute(select(PosteReception)).scalars().all()
    resp = client.post("/v1/reception/postes/open", json={}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["status"] == "open"
    assert "opened_at" in data
    after = db_session.execute(select(PosteReception)).scalars().all()
    assert len(after) == len(before) + 1
    evts = db_session.execute(select(AuditEvent).where(AuditEvent.action == "reception_post_opened")).scalars().all()
    assert len(evts) >= 1
    assert evts[-1].resource_type == "reception_post"
