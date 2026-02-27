"""Tests API GET/POST/PATCH /api/mapping/payment_methods (Story 7.1)."""

import pytest
from fastapi.testclient import TestClient


def test_list_payment_method_mappings_empty(client: TestClient, auth_headers: dict) -> None:
    """GET /api/mapping/payment_methods retourne 200 et liste vide."""
    r = client.get("/api/mapping/payment_methods", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_create_payment_method_mapping_201(client: TestClient, auth_headers: dict) -> None:
    """POST /api/mapping/payment_methods cree un mapping et retourne 201, snake_case."""
    r = client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "especes", "paheko_id_method": 1},
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["recyclic_code"] == "especes"
    assert data["paheko_id_method"] == 1
    assert "created_at" in data
    assert "updated_at" in data
    assert "T" in data["created_at"]


def test_list_payment_method_mappings_returns_created(client: TestClient, auth_headers: dict) -> None:
    """GET /api/mapping/payment_methods retourne les mappings crees."""
    client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "cheque", "paheko_id_method": 2},
        headers=auth_headers,
    )
    r = client.get("/api/mapping/payment_methods", headers=auth_headers)
    assert r.status_code == 200
    codes = [m["recyclic_code"] for m in r.json()]
    assert "cheque" in codes


def test_get_payment_method_mapping_200(client: TestClient, auth_headers: dict) -> None:
    """GET /api/mapping/payment_methods/{id} retourne le mapping."""
    create = client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "cb", "paheko_id_method": 3},
        headers=auth_headers,
    )
    assert create.status_code == 201
    mid = create.json()["id"]
    r = client.get(f"/api/mapping/payment_methods/{mid}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["recyclic_code"] == "cb"
    assert r.json()["paheko_id_method"] == 3


def test_get_payment_method_mapping_not_found_404(client: TestClient, auth_headers: dict) -> None:
    """GET /api/mapping/payment_methods/{id} inexistant retourne 404 et detail."""
    r = client.get(
        "/api/mapping/payment_methods/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert r.status_code == 404
    assert "detail" in r.json()
    assert "not found" in r.json()["detail"].lower()


def test_create_payment_method_mapping_duplicate_code_409(client: TestClient, auth_headers: dict) -> None:
    """POST avec recyclic_code deja existant retourne 409."""
    client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "especes", "paheko_id_method": 1},
        headers=auth_headers,
    )
    r = client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "especes", "paheko_id_method": 2},
        headers=auth_headers,
    )
    assert r.status_code == 409
    assert "detail" in r.json()


def test_patch_payment_method_mapping_200(client: TestClient, auth_headers: dict) -> None:
    """PATCH /api/mapping/payment_methods/{id} met a jour paheko_id_method."""
    create = client.post(
        "/api/mapping/payment_methods",
        json={"recyclic_code": "virement", "paheko_id_method": 5},
        headers=auth_headers,
    )
    assert create.status_code == 201
    mid = create.json()["id"]
    r = client.patch(
        f"/api/mapping/payment_methods/{mid}",
        json={"paheko_id_method": 10},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["paheko_id_method"] == 10
    assert r.json()["recyclic_code"] == "virement"


def test_patch_payment_method_mapping_not_found_404(client: TestClient, auth_headers: dict) -> None:
    """PATCH /api/mapping/payment_methods/{id} inexistant retourne 404."""
    r = client.patch(
        "/api/mapping/payment_methods/00000000-0000-0000-0000-000000000000",
        json={"paheko_id_method": 1},
        headers=auth_headers,
    )
    assert r.status_code == 404
    assert "detail" in r.json()


def test_error_format_has_detail(client: TestClient, auth_headers: dict) -> None:
    """Erreurs au format { \"detail\": \"...\" }."""
    r = client.get(
        "/api/mapping/payment_methods/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert r.status_code == 404
    data = r.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)
