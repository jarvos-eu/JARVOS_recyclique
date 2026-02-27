"""Tests API GET/POST/PATCH /api/mapping/locations (Story 7.1)."""

import pytest
from fastapi.testclient import TestClient


def _create_site(client: TestClient, auth_headers: dict, name: str = "Site Map") -> str:
    r = client.post("/v1/sites", json={"name": name, "is_active": True}, headers=auth_headers)
    assert r.status_code == 201
    return r.json()["id"]


def _create_register(client: TestClient, auth_headers: dict, site_id: str, name: str = "Caisse 1") -> str:
    r = client.post(
        "/v1/cash-registers",
        json={
            "site_id": site_id,
            "name": name,
            "location": "Bureau",
            "is_active": True,
            "enable_virtual": False,
            "enable_deferred": False,
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_list_location_mappings_empty(client: TestClient, auth_headers: dict) -> None:
    """GET /api/mapping/locations retourne 200 et liste vide."""
    r = client.get("/api/mapping/locations", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_create_location_mapping_by_site_201(client: TestClient, auth_headers: dict) -> None:
    """POST /api/mapping/locations avec site_id cree un mapping, 201 snake_case."""
    site_id = _create_site(client, auth_headers)
    r = client.post(
        "/api/mapping/locations",
        json={"site_id": site_id, "paheko_id_location": 1},
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["site_id"] == site_id
    assert data["register_id"] is None
    assert data["paheko_id_location"] == 1
    assert "id" in data
    assert "created_at" in data
    assert "T" in data["created_at"]


def test_create_location_mapping_by_register_201(client: TestClient, auth_headers: dict) -> None:
    """POST /api/mapping/locations avec register_id cree un mapping."""
    site_id = _create_site(client, auth_headers)
    register_id = _create_register(client, auth_headers, site_id)
    r = client.post(
        "/api/mapping/locations",
        json={"register_id": register_id, "paheko_id_location": 2},
        headers=auth_headers,
    )
    assert r.status_code == 201
    assert r.json()["register_id"] == register_id
    assert r.json()["site_id"] is None
    assert r.json()["paheko_id_location"] == 2


def test_create_location_mapping_both_site_and_register_422(client: TestClient, auth_headers: dict) -> None:
    """POST avec site_id et register_id tous les deux retourne 422."""
    site_id = _create_site(client, auth_headers)
    register_id = _create_register(client, auth_headers, site_id)
    r = client.post(
        "/api/mapping/locations",
        json={
            "site_id": site_id,
            "register_id": register_id,
            "paheko_id_location": 1,
        },
        headers=auth_headers,
    )
    assert r.status_code == 422
    assert "detail" in r.json()


def test_create_location_mapping_neither_site_nor_register_422(client: TestClient, auth_headers: dict) -> None:
    """POST sans site_id ni register_id retourne 422."""
    r = client.post(
        "/api/mapping/locations",
        json={"paheko_id_location": 1},
        headers=auth_headers,
    )
    assert r.status_code == 422
    assert "detail" in r.json()


def test_get_location_mapping_200(client: TestClient, auth_headers: dict) -> None:
    """GET /api/mapping/locations/{id} retourne le mapping."""
    site_id = _create_site(client, auth_headers)
    create = client.post(
        "/api/mapping/locations",
        json={"site_id": site_id, "paheko_id_location": 5},
        headers=auth_headers,
    )
    assert create.status_code == 201
    mid = create.json()["id"]
    r = client.get(f"/api/mapping/locations/{mid}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["paheko_id_location"] == 5


def test_get_location_mapping_not_found_404(client: TestClient, auth_headers: dict) -> None:
    """GET /api/mapping/locations/{id} inexistant retourne 404."""
    r = client.get(
        "/api/mapping/locations/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert r.status_code == 404
    assert "detail" in r.json()


def test_patch_location_mapping_200(client: TestClient, auth_headers: dict) -> None:
    """PATCH /api/mapping/locations/{id} met a jour paheko_id_location."""
    site_id = _create_site(client, auth_headers)
    create = client.post(
        "/api/mapping/locations",
        json={"site_id": site_id, "paheko_id_location": 1},
        headers=auth_headers,
    )
    assert create.status_code == 201
    mid = create.json()["id"]
    r = client.patch(
        f"/api/mapping/locations/{mid}",
        json={"paheko_id_location": 42},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["paheko_id_location"] == 42


def test_patch_location_mapping_not_found_404(client: TestClient, auth_headers: dict) -> None:
    """PATCH /api/mapping/locations/{id} inexistant retourne 404."""
    r = client.patch(
        "/api/mapping/locations/00000000-0000-0000-0000-000000000000",
        json={"paheko_id_location": 1},
        headers=auth_headers,
    )
    assert r.status_code == 404
