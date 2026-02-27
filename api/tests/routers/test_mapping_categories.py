"""Tests API CRUD /api/mapping/categories — Story 7.1. Routes protegees RBAC : admin."""

import pytest
from fastapi.testclient import TestClient


def _create_category(client: TestClient, auth_headers: dict, name: str = "Cat Mapping") -> str:
    resp = client.post(
        "/v1/categories",
        json={
            "name": name,
            "is_visible_sale": True,
            "is_visible_reception": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_list_category_mappings_empty(client: TestClient, auth_headers: dict):
    """GET /api/mapping/categories retourne 200 et liste vide."""
    resp = client.get("/api/mapping/categories", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_category_mapping_201(client: TestClient, auth_headers: dict):
    """POST /api/mapping/categories cree un mapping (category doit exister)."""
    cat_id = _create_category(client, auth_headers, name="Cat A")
    resp = client.post(
        "/api/mapping/categories",
        json={
            "category_id": cat_id,
            "paheko_category_id": 10,
            "paheko_code": "CAT-A",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["category_id"] == cat_id
    assert data["paheko_category_id"] == 10
    assert data["paheko_code"] == "CAT-A"
    assert "created_at" in data


def test_create_category_mapping_category_not_found_404(client: TestClient, auth_headers: dict):
    """POST avec category_id inexistant retourne 404."""
    resp = client.post(
        "/api/mapping/categories",
        json={
            "category_id": "00000000-0000-0000-0000-000000000000",
            "paheko_category_id": 1,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_create_category_mapping_duplicate_409(client: TestClient, auth_headers: dict):
    """POST avec category_id deja mappe retourne 409."""
    cat_id = _create_category(client, auth_headers, name="Cat B")
    client.post(
        "/api/mapping/categories",
        json={"category_id": cat_id, "paheko_category_id": 1},
        headers=auth_headers,
    )
    resp = client.post(
        "/api/mapping/categories",
        json={"category_id": cat_id, "paheko_category_id": 2},
        headers=auth_headers,
    )
    assert resp.status_code == 409


def test_get_category_mapping(client: TestClient, auth_headers: dict):
    """GET /api/mapping/categories/{id} retourne le mapping."""
    cat_id = _create_category(client, auth_headers, name="Cat C")
    create = client.post(
        "/api/mapping/categories",
        json={"category_id": cat_id, "paheko_category_id": 20},
        headers=auth_headers,
    )
    mapping_id = create.json()["id"]
    resp = client.get(f"/api/mapping/categories/{mapping_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["paheko_category_id"] == 20


def test_patch_category_mapping(client: TestClient, auth_headers: dict):
    """PATCH /api/mapping/categories/{id} met a jour."""
    cat_id = _create_category(client, auth_headers, name="Cat D")
    create = client.post(
        "/api/mapping/categories",
        json={"category_id": cat_id, "paheko_category_id": 30},
        headers=auth_headers,
    )
    mapping_id = create.json()["id"]
    resp = client.patch(
        f"/api/mapping/categories/{mapping_id}",
        json={"paheko_category_id": 31, "paheko_code": "D"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["paheko_category_id"] == 31
    assert resp.json()["paheko_code"] == "D"


def test_error_format_has_detail(client: TestClient, auth_headers: dict):
    """Erreurs au format { \"detail\": \"...\" }."""
    resp = client.get(
        "/api/mapping/categories/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404
    assert "detail" in resp.json()
