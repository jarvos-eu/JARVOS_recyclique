"""Tests API CRUD + GET /status /v1/cash-registers — Story 2.2. Routes protégées RBAC (Story 3.2) : caisse.access | admin."""

import pytest
from fastapi.testclient import TestClient


def _create_site(client: TestClient, auth_headers: dict, name: str = "Site Test", is_active: bool = True):
    resp = client.post("/v1/sites", json={"name": name, "is_active": is_active}, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()["id"]


def test_list_cash_registers_empty(client: TestClient, auth_headers: dict):
    """GET /v1/cash-registers retourne 200 et une liste vide quand aucun poste."""
    resp = client.get("/v1/cash-registers", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_cash_registers_filter_site_id(client: TestClient, auth_headers: dict):
    """GET /v1/cash-registers?site_id=... retourne 200."""
    site_id = _create_site(client, auth_headers)
    resp = client.get("/v1/cash-registers", params={"site_id": site_id}, headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_cash_registers_filter_is_active(client: TestClient, auth_headers: dict):
    """GET /v1/cash-registers?is_active=true retourne 200."""
    resp = client.get("/v1/cash-registers", params={"is_active": True}, headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_cash_registers_status_empty(client: TestClient, auth_headers: dict):
    """GET /v1/cash-registers/status retourne 200 et liste vide quand aucun poste."""
    resp = client.get("/v1/cash-registers/status", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_cash_registers_status_with_registers(client: TestClient, auth_headers: dict):
    """GET /v1/cash-registers/status retourne un item libre par poste."""
    site_id = _create_site(client, auth_headers)
    client.post(
        "/v1/cash-registers",
        json={
            "site_id": site_id,
            "name": "Caisse 1",
            "location": "Rez-de-chaussee",
            "is_active": True,
            "enable_virtual": False,
            "enable_deferred": False,
        },
        headers=auth_headers,
    )
    resp = client.get("/v1/cash-registers/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "free"
    assert "register_id" in data[0]


def test_get_cash_registers_status_filter_site_id(client: TestClient, auth_headers: dict):
    """GET /v1/cash-registers/status?site_id=... filtre par site."""
    site_id = _create_site(client, auth_headers)
    resp = client.get("/v1/cash-registers/status", params={"site_id": site_id}, headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_cash_register_not_found(client: TestClient, auth_headers: dict):
    """GET /v1/cash-registers/{id} inexistant retourne 404 et detail."""
    resp = client.get(
        "/v1/cash-registers/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert data["detail"] == "Cash register not found"


def test_create_cash_register_201(client: TestClient, auth_headers: dict):
    """POST /v1/cash-registers cree un poste et retourne 201 avec corps snake_case."""
    site_id = _create_site(client, auth_headers)
    resp = client.post(
        "/v1/cash-registers",
        json={
            "site_id": site_id,
            "name": "Caisse A",
            "location": "Bureau 1",
            "is_active": True,
            "enable_virtual": True,
            "enable_deferred": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["site_id"] == site_id
    assert data["name"] == "Caisse A"
    assert data["location"] == "Bureau 1"
    assert data["is_active"] is True
    assert data["enable_virtual"] is True
    assert data["enable_deferred"] is False
    assert "created_at" in data
    assert "updated_at" in data
    assert "T" in data["created_at"]


def test_create_cash_register_site_not_found_404(client: TestClient, auth_headers: dict):
    """POST /v1/cash-registers avec site_id inexistant retourne 404."""
    resp = client.post(
        "/v1/cash-registers",
        json={
            "site_id": "00000000-0000-0000-0000-000000000000",
            "name": "Caisse X",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Site not found"


def test_get_cash_register_after_create(client: TestClient, auth_headers: dict):
    """GET /v1/cash-registers/{id} retourne le poste cree."""
    site_id = _create_site(client, auth_headers)
    create = client.post(
        "/v1/cash-registers",
        json={"site_id": site_id, "name": "Caisse B", "is_active": False},
        headers=auth_headers,
    )
    assert create.status_code == 201
    register_id = create.json()["id"]
    resp = client.get(f"/v1/cash-registers/{register_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Caisse B"
    assert resp.json()["is_active"] is False


def test_list_cash_registers_returns_created(client: TestClient, auth_headers: dict):
    """GET /v1/cash-registers retourne les postes crees."""
    site_id = _create_site(client, auth_headers)
    client.post(
        "/v1/cash-registers",
        json={"site_id": site_id, "name": "Caisse C", "is_active": True},
        headers=auth_headers,
    )
    resp = client.get("/v1/cash-registers", headers=auth_headers)
    assert resp.status_code == 200
    names = [r["name"] for r in resp.json()]
    assert "Caisse C" in names


def test_patch_cash_register(client: TestClient, auth_headers: dict):
    """PATCH /v1/cash-registers/{id} met a jour partiellement."""
    site_id = _create_site(client, auth_headers)
    create = client.post(
        "/v1/cash-registers",
        json={"site_id": site_id, "name": "Original", "is_active": True},
        headers=auth_headers,
    )
    register_id = create.json()["id"]
    resp = client.patch(
        f"/v1/cash-registers/{register_id}",
        json={"name": "Updated", "location": "Hall"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"
    assert resp.json()["location"] == "Hall"
    assert resp.json()["is_active"] is True


def test_patch_cash_register_empty_body_does_not_update_updated_at(client: TestClient, auth_headers: dict):
    """PATCH /v1/cash-registers/{id} avec body {} ne modifie pas updated_at."""
    site_id = _create_site(client, auth_headers)
    create = client.post(
        "/v1/cash-registers",
        json={"site_id": site_id, "name": "No change", "is_active": True},
        headers=auth_headers,
    )
    register_id = create.json()["id"]
    updated_before = create.json()["updated_at"]
    resp = client.patch(f"/v1/cash-registers/{register_id}", json={}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "No change"
    assert resp.json()["updated_at"] == updated_before


def test_patch_cash_register_not_found(client: TestClient, auth_headers: dict):
    """PATCH /v1/cash-registers/{id} inexistant retourne 404."""
    resp = client.patch(
        "/v1/cash-registers/00000000-0000-0000-0000-000000000000",
        json={"name": "X"},
        headers=auth_headers,
    )
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_delete_cash_register_204(client: TestClient, auth_headers: dict):
    """DELETE /v1/cash-registers/{id} retourne 204 et supprime."""
    site_id = _create_site(client, auth_headers)
    create = client.post(
        "/v1/cash-registers",
        json={"site_id": site_id, "name": "To delete", "is_active": True},
        headers=auth_headers,
    )
    register_id = create.json()["id"]
    resp = client.delete(f"/v1/cash-registers/{register_id}", headers=auth_headers)
    assert resp.status_code == 204
    get_resp = client.get(f"/v1/cash-registers/{register_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_delete_cash_register_not_found(client: TestClient, auth_headers: dict):
    """DELETE /v1/cash-registers/{id} inexistant retourne 404."""
    resp = client.delete(
        "/v1/cash-registers/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Cash register not found"


def test_error_format_has_detail(client: TestClient, auth_headers: dict):
    """Erreurs au format { \"detail\": \"...\" }."""
    resp = client.get(
        "/v1/cash-registers/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)
