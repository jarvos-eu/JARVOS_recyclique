"""Tests API CRUD /api/mapping/payment_methods — Story 7.1. Routes protegees RBAC : admin."""

import pytest
from fastapi.testclient import TestClient


def test_list_payment_method_mappings_empty(client: TestClient, auth_headers: dict):
    """GET /api/mapping/payment_methods retourne 200 et liste vide."""
    resp = client.get("/api/mapping/payment_methods", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_payment_method_mapping_201(client: TestClient, auth_headers: dict):
    """POST /api/mapping/payment_methods cree un mapping et retourne 201."""
    resp = client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "especes", "paheko_id_method": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["recyclic_code"] == "especes"
    assert data["paheko_id_method"] == 1
    assert "created_at" in data
    assert "updated_at" in data
    assert "T" in data["created_at"]


def test_list_payment_method_mappings_returns_created(client: TestClient, auth_headers: dict):
    """GET /api/mapping/payment_methods retourne les mappings crees."""
    client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "cheque", "paheko_id_method": 2},
        headers=auth_headers,
    )
    resp = client.get("/api/mapping/payment_methods", headers=auth_headers)
    assert resp.status_code == 200
    codes = [m["recyclic_code"] for m in resp.json()]
    assert "cheque" in codes


def test_get_payment_method_mapping(client: TestClient, auth_headers: dict):
    """GET /api/mapping/payment_methods/{id} retourne le mapping."""
    create = client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "cb", "paheko_id_method": 3},
        headers=auth_headers,
    )
    assert create.status_code == 201
    mapping_id = create.json()["id"]
    resp = client.get(f"/api/mapping/payment_methods/{mapping_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["recyclic_code"] == "cb"
    assert resp.json()["paheko_id_method"] == 3


def test_get_payment_method_mapping_not_found(client: TestClient, auth_headers: dict):
    """GET /api/mapping/payment_methods/{id} inexistant retourne 404."""
    resp = client.get(
        "/api/mapping/payment_methods/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_create_payment_method_mapping_duplicate_code_409(client: TestClient, auth_headers: dict):
    """POST avec recyclic_code deja existant retourne 409."""
    client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "especes", "paheko_id_method": 1},
        headers=auth_headers,
    )
    resp = client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "especes", "paheko_id_method": 2},
        headers=auth_headers,
    )
    assert resp.status_code == 409
    assert "detail" in resp.json()


def test_patch_payment_method_mapping(client: TestClient, auth_headers: dict):
    """PATCH /api/mapping/payment_methods/{id} met a jour."""
    create = client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "virement", "paheko_id_method": 4},
        headers=auth_headers,
    )
    mapping_id = create.json()["id"]
    resp = client.patch(
        f"/api/mapping/payment_methods/{mapping_id}",
        json={"paheko_id_method": 5},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["recyclic_code"] == "virement"
    assert resp.json()["paheko_id_method"] == 5


def test_patch_payment_method_mapping_not_found(client: TestClient, auth_headers: dict):
    """PATCH /api/mapping/payment_methods/{id} inexistant retourne 404."""
    resp = client.patch(
        "/api/mapping/payment_methods/00000000-0000-0000-0000-000000000000",
        json={"paheko_id_method": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_error_format_has_detail(client: TestClient, auth_headers: dict):
    """Erreurs au format { \"detail\": \"...\" }."""
    resp = client.get(
        "/api/mapping/payment_methods/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404
    assert "detail" in resp.json()
    assert isinstance(resp.json()["detail"], str)
