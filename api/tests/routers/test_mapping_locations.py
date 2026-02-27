"""Tests API CRUD /api/mapping/locations — Story 7.1. Routes protegees RBAC : admin."""

import pytest
from fastapi.testclient import TestClient


def test_list_location_mappings_empty(client: TestClient, auth_headers: dict):
    """GET /api/mapping/locations retourne 200 et liste vide."""
    resp = client.get("/api/mapping/locations", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_location_mapping_by_site_201(client: TestClient, auth_headers: dict):
    """POST /api/mapping/locations avec site_id cree un mapping."""
    site_resp = client.post("/v1/sites", json={"name": "Site Map", "is_active": True}, headers=auth_headers)
    assert site_resp.status_code == 201
    site_id = site_resp.json()["id"]
    resp = client.post(
        "/api/mapping/locations",
        json={"site_id": site_id, "paheko_id_location": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["site_id"] == site_id
    assert data["register_id"] is None
    assert data["paheko_id_location"] == 1


def test_create_location_mapping_site_not_found_404(client: TestClient, auth_headers: dict):
    """POST avec site_id inexistant retourne 404."""
    resp = client.post(
        "/api/mapping/locations",
        json={
            "site_id": "00000000-0000-0000-0000-000000000000",
            "paheko_id_location": 1,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_create_location_mapping_neither_site_nor_register_422(client: TestClient, auth_headers: dict):
    """POST sans site_id ni register_id (ou les deux) retourne 422."""
    resp = client.post(
        "/api/mapping/locations",
        json={"paheko_id_location": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_create_location_mapping_both_site_and_register_422(client: TestClient, auth_headers: dict):
    """POST avec site_id et register_id tous les deux retourne 422."""
    site_resp = client.post("/v1/sites", json={"name": "S", "is_active": True}, headers=auth_headers)
    site_id = site_resp.json()["id"]
    reg_resp = client.post(
        "/v1/cash-registers",
        json={"site_id": site_id, "name": "R", "is_active": True},
        headers=auth_headers,
    )
    register_id = reg_resp.json()["id"]
    resp = client.post(
        "/api/mapping/locations",
        json={
            "site_id": site_id,
            "register_id": register_id,
            "paheko_id_location": 1,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_create_location_mapping_by_register_201(client: TestClient, auth_headers: dict):
    """POST /api/mapping/locations avec register_id cree un mapping."""
    site_resp = client.post("/v1/sites", json={"name": "Site R", "is_active": True}, headers=auth_headers)
    site_id = site_resp.json()["id"]
    reg_resp = client.post(
        "/v1/cash-registers",
        json={"site_id": site_id, "name": "Caisse 1", "is_active": True},
        headers=auth_headers,
    )
    register_id = reg_resp.json()["id"]
    resp = client.post(
        "/api/mapping/locations",
        json={"register_id": register_id, "paheko_id_location": 2},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["site_id"] is None
    assert data["register_id"] == register_id
    assert data["paheko_id_location"] == 2


def test_get_location_mapping(client: TestClient, auth_headers: dict):
    """GET /api/mapping/locations/{id} retourne le mapping."""
    site_resp = client.post("/v1/sites", json={"name": "Site G", "is_active": True}, headers=auth_headers)
    site_id = site_resp.json()["id"]
    create = client.post(
        "/api/mapping/locations",
        json={"site_id": site_id, "paheko_id_location": 3},
        headers=auth_headers,
    )
    mapping_id = create.json()["id"]
    resp = client.get(f"/api/mapping/locations/{mapping_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["paheko_id_location"] == 3


def test_patch_location_mapping(client: TestClient, auth_headers: dict):
    """PATCH /api/mapping/locations/{id} met a jour paheko_id_location."""
    site_resp = client.post("/v1/sites", json={"name": "Site P", "is_active": True}, headers=auth_headers)
    site_id = site_resp.json()["id"]
    create = client.post(
        "/api/mapping/locations",
        json={"site_id": site_id, "paheko_id_location": 4},
        headers=auth_headers,
    )
    mapping_id = create.json()["id"]
    resp = client.patch(
        f"/api/mapping/locations/{mapping_id}",
        json={"paheko_id_location": 5},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["paheko_id_location"] == 5


def test_error_format_has_detail(client: TestClient, auth_headers: dict):
    """Erreurs au format { \"detail\": \"...\" }."""
    resp = client.get(
        "/api/mapping/locations/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404
    assert "detail" in resp.json()
