"""Tests API GET/POST/PATCH /api/mapping/categories (Story 7.1)."""

import pytest
from fastapi.testclient import TestClient


def _create_category(client: TestClient, auth_headers: dict, name: str = "Cat Test") -> str:
    r = client.post(
        "/v1/categories",
        json={"name": name, "is_visible_sale": True, "is_visible_reception": True},
        headers=auth_headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_list_category_mappings_empty(client: TestClient, auth_headers: dict) -> None:
    """GET /api/mapping/categories retourne 200 et liste vide."""
    r = client.get("/api/mapping/categories", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_create_category_mapping_201(client: TestClient, auth_headers: dict) -> None:
    """POST /api/mapping/categories avec paheko_category_id cree un mapping, 201 snake_case."""
    category_id = _create_category(client, auth_headers, "Cat A")
    r = client.post(
        "/api/mapping/categories",
        json={"category_id": category_id, "paheko_category_id": 10},
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["category_id"] == category_id
    assert data["paheko_category_id"] == 10
    assert data["paheko_code"] is None
    assert "id" in data
    assert "created_at" in data
    assert "T" in data["created_at"]


def test_create_category_mapping_with_paheko_code(client: TestClient, auth_headers: dict) -> None:
    """POST /api/mapping/categories avec paheko_code uniquement (sans envoyer paheko_category_id)."""
    category_id = _create_category(client, auth_headers, "Cat B")
    r = client.post(
        "/api/mapping/categories",
        json={"category_id": category_id, "paheko_code": "RECYCLAGE"},
        headers=auth_headers,
    )
    assert r.status_code == 201, r.json()
    assert r.json()["paheko_code"] == "RECYCLAGE"


def test_create_category_mapping_no_paheko_target_422(client: TestClient, auth_headers: dict) -> None:
    """POST sans paheko_category_id ni paheko_code retourne 422."""
    category_id = _create_category(client, auth_headers, "Cat C")
    r = client.post(
        "/api/mapping/categories",
        json={"category_id": category_id},
        headers=auth_headers,
    )
    assert r.status_code == 422
    assert "detail" in r.json()


def test_create_category_mapping_duplicate_category_409(client: TestClient, auth_headers: dict) -> None:
    """POST avec category_id deja mappe retourne 409."""
    category_id = _create_category(client, auth_headers, "Cat D")
    r1 = client.post(
        "/api/mapping/categories",
        json={"category_id": category_id, "paheko_category_id": 1},
        headers=auth_headers,
    )
    assert r1.status_code == 201
    r = client.post(
        "/api/mapping/categories",
        json={"category_id": category_id, "paheko_code": "X"},
        headers=auth_headers,
    )
    assert r.status_code == 409
    assert "detail" in r.json()


def test_get_category_mapping_200(client: TestClient, auth_headers: dict) -> None:
    """GET /api/mapping/categories/{id} retourne le mapping."""
    category_id = _create_category(client, auth_headers, "Cat E")
    create = client.post(
        "/api/mapping/categories",
        json={"category_id": category_id, "paheko_category_id": 20},
        headers=auth_headers,
    )
    assert create.status_code == 201
    mid = create.json()["id"]
    r = client.get(f"/api/mapping/categories/{mid}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["category_id"] == category_id
    assert r.json()["paheko_category_id"] == 20


def test_get_category_mapping_not_found_404(client: TestClient, auth_headers: dict) -> None:
    """GET /api/mapping/categories/{id} inexistant retourne 404."""
    r = client.get(
        "/api/mapping/categories/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert r.status_code == 404
    assert "detail" in r.json()


def test_patch_category_mapping_200(client: TestClient, auth_headers: dict) -> None:
    """PATCH /api/mapping/categories/{id} met a jour paheko_category_id et paheko_code."""
    category_id = _create_category(client, auth_headers, "Cat F")
    create = client.post(
        "/api/mapping/categories",
        json={"category_id": category_id, "paheko_category_id": 1},
        headers=auth_headers,
    )
    assert create.status_code == 201
    mid = create.json()["id"]
    r = client.patch(
        f"/api/mapping/categories/{mid}",
        json={"paheko_category_id": 99, "paheko_code": "UPD"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["paheko_category_id"] == 99
    assert r.json()["paheko_code"] == "UPD"


def test_patch_category_mapping_not_found_404(client: TestClient, auth_headers: dict) -> None:
    """PATCH /api/mapping/categories/{id} inexistant retourne 404."""
    r = client.patch(
        "/api/mapping/categories/00000000-0000-0000-0000-000000000000",
        json={"paheko_code": "X"},
        headers=auth_headers,
    )
    assert r.status_code == 404
