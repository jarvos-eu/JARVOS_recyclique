"""Tests API admin mapping categories (Story 7.2). GET/POST/PATCH/DELETE /v1/admin/mapping/categories."""

import pytest
from fastapi.testclient import TestClient


def test_admin_list_category_mappings_empty(client: TestClient, auth_headers: dict):
    """GET /v1/admin/mapping/categories retourne 200 et liste vide."""
    resp = client.get("/v1/admin/mapping/categories", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_admin_create_category_mapping_201(client: TestClient, auth_headers: dict):
    """POST /v1/admin/mapping/categories cree un mapping."""
    cat = client.post(
        "/v1/categories",
        json={
            "name": "Cat Map",
            "is_visible_sale": True,
            "is_visible_reception": True,
            "display_order": 0,
            "display_order_entry": 0,
        },
        headers=auth_headers,
    )
    assert cat.status_code == 201
    category_id = cat.json()["id"]
    resp = client.post(
        "/v1/admin/mapping/categories",
        json={"category_id": category_id, "paheko_category_id": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["category_id"] == category_id
    assert resp.json()["paheko_category_id"] == 1


def test_admin_delete_category_mapping_204(client: TestClient, auth_headers: dict):
    """DELETE /v1/admin/mapping/categories/{id} retourne 204."""
    cat = client.post(
        "/v1/categories",
        json={
            "name": "Cat Del",
            "is_visible_sale": True,
            "is_visible_reception": True,
            "display_order": 0,
            "display_order_entry": 0,
        },
        headers=auth_headers,
    )
    category_id = cat.json()["id"]
    create = client.post(
        "/v1/admin/mapping/categories",
        json={"category_id": category_id, "paheko_code": "DEL"},
        headers=auth_headers,
    )
    mapping_id = create.json()["id"]
    resp = client.delete(f"/v1/admin/mapping/categories/{mapping_id}", headers=auth_headers)
    assert resp.status_code == 204
