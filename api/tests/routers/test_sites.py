"""Tests API CRUD /v1/sites — Story 2.1."""

import pytest
from fastapi.testclient import TestClient


def test_list_sites_empty(client: TestClient):
    """GET /v1/sites retourne 200 et une liste vide quand aucun site."""
    resp = client.get("/v1/sites")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_sites_filter_is_active(client: TestClient):
    """GET /v1/sites?is_active=true retourne 200."""
    resp = client.get("/v1/sites", params={"is_active": True})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_site_not_found(client: TestClient):
    """GET /v1/sites/{id} inexistant retourne 404 et detail."""
    resp = client.get("/v1/sites/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert data["detail"] == "Site not found"


def test_create_site_201(client: TestClient):
    """POST /v1/sites crée un site et retourne 201 avec corps snake_case."""
    resp = client.post(
        "/v1/sites",
        json={"name": "Site A", "is_active": True},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "Site A"
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data
    assert "T" in data["created_at"]  # ISO 8601


def test_get_site_after_create(client: TestClient):
    """GET /v1/sites/{id} retourne le site créé."""
    create = client.post("/v1/sites", json={"name": "Site B", "is_active": False})
    assert create.status_code == 201
    site_id = create.json()["id"]
    resp = client.get(f"/v1/sites/{site_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Site B"
    assert resp.json()["is_active"] is False


def test_list_sites_returns_created(client: TestClient):
    """GET /v1/sites retourne les sites créés."""
    client.post("/v1/sites", json={"name": "Site C", "is_active": True})
    resp = client.get("/v1/sites")
    assert resp.status_code == 200
    names = [s["name"] for s in resp.json()]
    assert "Site C" in names


def test_patch_site(client: TestClient):
    """PATCH /v1/sites/{id} met à jour partiellement."""
    create = client.post("/v1/sites", json={"name": "Original", "is_active": True})
    site_id = create.json()["id"]
    resp = client.patch(
        f"/v1/sites/{site_id}",
        json={"name": "Updated"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"
    assert resp.json()["is_active"] is True


def test_patch_site_empty_body_does_not_update_updated_at(client: TestClient):
    """PATCH /v1/sites/{id} avec body {} ne modifie pas updated_at."""
    create = client.post("/v1/sites", json={"name": "No change", "is_active": True})
    site_id = create.json()["id"]
    updated_before = create.json()["updated_at"]
    resp = client.patch(f"/v1/sites/{site_id}", json={})
    assert resp.status_code == 200
    assert resp.json()["name"] == "No change"
    assert resp.json()["updated_at"] == updated_before


def test_patch_site_not_found(client: TestClient):
    """PATCH /v1/sites/{id} inexistant retourne 404."""
    resp = client.patch(
        "/v1/sites/00000000-0000-0000-0000-000000000000",
        json={"name": "X"},
    )
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_delete_site_204(client: TestClient):
    """DELETE /v1/sites/{id} retourne 204 et supprime."""
    create = client.post("/v1/sites", json={"name": "To delete", "is_active": True})
    site_id = create.json()["id"]
    resp = client.delete(f"/v1/sites/{site_id}")
    assert resp.status_code == 204
    get_resp = client.get(f"/v1/sites/{site_id}")
    assert get_resp.status_code == 404


def test_delete_site_not_found(client: TestClient):
    """DELETE /v1/sites/{id} inexistant retourne 404."""
    resp = client.delete("/v1/sites/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Site not found"


def test_error_format_has_detail(client: TestClient):
    """Erreurs au format { \"detail\": \"...\" }."""
    resp = client.get("/v1/sites/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)
