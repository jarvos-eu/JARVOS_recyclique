"""Tests API admin mapping (Story 7.2). GET/POST/PATCH/DELETE /v1/admin/mapping/payment_methods avec audit."""

import pytest
from fastapi.testclient import TestClient


def test_admin_list_payment_method_mappings_empty(client: TestClient, auth_headers: dict):
    """GET /v1/admin/mapping/payment_methods retourne 200 et liste vide."""
    resp = client.get("/v1/admin/mapping/payment_methods", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_admin_create_payment_method_mapping_201(client: TestClient, auth_headers: dict):
    """POST /v1/admin/mapping/payment_methods cree un mapping et retourne 201."""
    resp = client.post(
        "/v1/admin/mapping/payment_methods",
        json={"recyclic_code": "especes", "paheko_id_method": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["recyclic_code"] == "especes"
    assert data["paheko_id_method"] == 1


def test_admin_create_payment_method_mapping_reusable_code_per_type(client: TestClient, auth_headers: dict):
    """POST avec un recyclic_code unique cree bien le mapping (audit ecrit en prod)."""
    resp = client.post(
        "/v1/admin/mapping/payment_methods",
        json={"recyclic_code": "audit_test", "paheko_id_method": 99},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["recyclic_code"] == "audit_test"


def test_admin_list_payment_method_mappings_returns_created(client: TestClient, auth_headers: dict):
    """GET /v1/admin/mapping/payment_methods retourne les mappings crees."""
    client.post(
        "/v1/admin/mapping/payment_methods",
        json={"recyclic_code": "cheque", "paheko_id_method": 2},
        headers=auth_headers,
    )
    resp = client.get("/v1/admin/mapping/payment_methods", headers=auth_headers)
    assert resp.status_code == 200
    codes = [m["recyclic_code"] for m in resp.json()]
    assert "cheque" in codes


def test_admin_get_payment_method_mapping(client: TestClient, auth_headers: dict):
    """GET /v1/admin/mapping/payment_methods/{id} retourne le mapping."""
    create = client.post(
        "/v1/admin/mapping/payment_methods",
        json={"recyclic_code": "cb", "paheko_id_method": 3},
        headers=auth_headers,
    )
    assert create.status_code == 201
    mapping_id = create.json()["id"]
    resp = client.get(f"/v1/admin/mapping/payment_methods/{mapping_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["recyclic_code"] == "cb"


def test_admin_get_payment_method_mapping_not_found(client: TestClient, auth_headers: dict):
    """GET /v1/admin/mapping/payment_methods/{id} inexistant retourne 404."""
    resp = client.get(
        "/v1/admin/mapping/payment_methods/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_admin_patch_payment_method_mapping(client: TestClient, auth_headers: dict):
    """PATCH /v1/admin/mapping/payment_methods/{id} met a jour + audit."""
    create = client.post(
        "/v1/admin/mapping/payment_methods",
        json={"recyclic_code": "virement", "paheko_id_method": 4},
        headers=auth_headers,
    )
    mapping_id = create.json()["id"]
    resp = client.patch(
        f"/v1/admin/mapping/payment_methods/{mapping_id}",
        json={"paheko_id_method": 5},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["paheko_id_method"] == 5


def test_admin_delete_payment_method_mapping_204(client: TestClient, auth_headers: dict):
    """DELETE /v1/admin/mapping/payment_methods/{id} retourne 204."""
    create = client.post(
        "/v1/admin/mapping/payment_methods",
        json={"recyclic_code": "to_delete", "paheko_id_method": 10},
        headers=auth_headers,
    )
    mapping_id = create.json()["id"]
    resp = client.delete(
        f"/v1/admin/mapping/payment_methods/{mapping_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 204
    assert resp.content == b""


def test_admin_get_after_delete_404(client: TestClient, auth_headers: dict):
    """GET apres DELETE retourne 404."""
    create = client.post(
        "/v1/admin/mapping/payment_methods",
        json={"recyclic_code": "deleted_after", "paheko_id_method": 11},
        headers=auth_headers,
    )
    mapping_id = create.json()["id"]
    client.delete(f"/v1/admin/mapping/payment_methods/{mapping_id}", headers=auth_headers)
    resp = client.get(f"/v1/admin/mapping/payment_methods/{mapping_id}", headers=auth_headers)
    assert resp.status_code == 404
