"""Tests API CRUD presets + GET /active, validation category_id — Story 2.4. Routes protégées RBAC (Story 3.2) : caisse.access | admin."""

import pytest
from fastapi.testclient import TestClient


def _create_category(
    client: TestClient,
    auth_headers: dict,
    name: str = "Cat Test",
) -> str:
    resp = client.post(
        "/v1/categories",
        json={"name": name, "is_visible_sale": True, "is_visible_reception": True},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _create_preset(
    client: TestClient,
    auth_headers: dict,
    name: str = "Preset Test",
    category_id: str | None = None,
    preset_price: int = 0,
    button_type: str = "Don",
    sort_order: int = 0,
    is_active: bool = True,
) -> str:
    body = {
        "name": name,
        "preset_price": preset_price,
        "button_type": button_type,
        "sort_order": sort_order,
        "is_active": is_active,
    }
    if category_id is not None:
        body["category_id"] = category_id
    resp = client.post("/v1/presets", json=body, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()["id"]


def test_list_presets_empty(client: TestClient, auth_headers: dict):
    """GET /v1/presets retourne 200 et liste vide quand aucun preset."""
    resp = client.get("/v1/presets", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_presets_returns_created(client: TestClient, auth_headers: dict):
    """GET /v1/presets retourne les presets crees."""
    _create_preset(client, auth_headers, name="P A", button_type="Don")
    _create_preset(client, auth_headers, name="P B", button_type="Recyclage")
    resp = client.get("/v1/presets", headers=auth_headers)
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert "P A" in names
    assert "P B" in names


def test_list_presets_filter_category_id(client: TestClient, auth_headers: dict):
    """GET /v1/presets?category_id=... filtre par categorie."""
    cat_id = _create_category(client, auth_headers, name="Cat Presets")
    _create_preset(client, auth_headers, name="P Linked", category_id=cat_id)
    _create_preset(client, auth_headers, name="P No Cat")  # no category
    resp = client.get("/v1/presets", params={"category_id": cat_id}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "P Linked"
    assert data[0]["category_id"] == cat_id


def test_get_presets_active_only_active_sorted(client: TestClient, auth_headers: dict):
    """GET /v1/presets/active retourne seulement is_active=true, tri par sort_order."""
    _create_preset(client, auth_headers, name="Inactive", is_active=False, sort_order=0)
    _create_preset(client, auth_headers, name="Active 2", is_active=True, sort_order=20)
    _create_preset(client, auth_headers, name="Active 1", is_active=True, sort_order=10)
    resp = client.get("/v1/presets/active", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["name"] == "Active 1"
    assert data[1]["name"] == "Active 2"
    assert all(p["is_active"] is True for p in data)


def test_get_presets_active_route_before_id(client: TestClient, auth_headers: dict):
    """GET /v1/presets/active ne doit pas etre capture par /{id} (ordre des routes)."""
    resp = client.get("/v1/presets/active", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_preset_not_found(client: TestClient, auth_headers: dict):
    """GET /v1/presets/{id} inexistant retourne 404 et detail."""
    resp = client.get("/v1/presets/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404
    assert "detail" in resp.json()
    assert resp.json()["detail"] == "Preset not found"


def test_get_preset_after_create(client: TestClient, auth_headers: dict):
    """GET /v1/presets/{id} retourne le preset cree."""
    preset_id = _create_preset(
        client,
        auth_headers,
        name="Detail Preset",
        preset_price=500,
        button_type="Recyclage",
        sort_order=5,
    )
    resp = client.get(f"/v1/presets/{preset_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Detail Preset"
    assert data["preset_price"] == 500
    assert data["button_type"] == "Recyclage"
    assert data["sort_order"] == 5
    assert "created_at" in data
    assert "updated_at" in data


def test_create_preset_201(client: TestClient, auth_headers: dict):
    """POST /v1/presets cree un preset et retourne 201 avec corps snake_case."""
    resp = client.post(
        "/v1/presets",
        json={
            "name": "New Preset",
            "preset_price": 1000,
            "button_type": "Decheterie",
            "sort_order": 1,
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "New Preset"
    assert data["preset_price"] == 1000
    assert data["button_type"] == "Decheterie"
    assert data["category_id"] is None
    assert "T" in data["created_at"]


def test_create_preset_with_category_id(client: TestClient, auth_headers: dict):
    """POST /v1/presets avec category_id valide lie la categorie."""
    cat_id = _create_category(client, auth_headers, name="Cat For Preset")
    resp = client.post(
        "/v1/presets",
        json={
            "name": "Preset With Cat",
            "category_id": cat_id,
            "preset_price": 0,
            "button_type": "Don",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["category_id"] == cat_id


def test_create_preset_category_not_found_400(client: TestClient, auth_headers: dict):
    """POST /v1/presets avec category_id inexistant retourne 400."""
    resp = client.post(
        "/v1/presets",
        json={
            "name": "Preset",
            "category_id": "00000000-0000-0000-0000-000000000000",
            "preset_price": 0,
            "button_type": "Don",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()
    assert "Category" in resp.json()["detail"] or "category" in resp.json()["detail"].lower()


def test_patch_preset(client: TestClient, auth_headers: dict):
    """PATCH /v1/presets/{id} met a jour partiellement."""
    preset_id = _create_preset(client, auth_headers, name="Original", preset_price=0)
    resp = client.patch(
        f"/v1/presets/{preset_id}",
        json={"name": "Updated", "preset_price": 200, "is_active": False},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated"
    assert data["preset_price"] == 200
    assert data["is_active"] is False


def test_patch_preset_category_id_valid(client: TestClient, auth_headers: dict):
    """PATCH /v1/presets/{id} avec category_id existant met a jour."""
    cat_id = _create_category(client, auth_headers, name="Cat Patch")
    preset_id = _create_preset(client, auth_headers, name="P", category_id=None)
    resp = client.patch(
        f"/v1/presets/{preset_id}",
        json={"category_id": cat_id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["category_id"] == cat_id


def test_patch_preset_category_id_unset_null(client: TestClient, auth_headers: dict):
    """PATCH /v1/presets/{id} avec category_id: null decroche la categorie."""
    cat_id = _create_category(client, auth_headers, name="Cat To Unset")
    preset_id = _create_preset(client, auth_headers, name="P With Cat", category_id=cat_id)
    resp = client.patch(
        f"/v1/presets/{preset_id}",
        json={"category_id": None},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["category_id"] is None


def test_patch_preset_category_not_found_400(client: TestClient, auth_headers: dict):
    """PATCH /v1/presets/{id} avec category_id inexistant retourne 400."""
    preset_id = _create_preset(client, auth_headers, name="P")
    resp = client.patch(
        f"/v1/presets/{preset_id}",
        json={"category_id": "00000000-0000-0000-0000-000000000000"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


def test_patch_preset_not_found(client: TestClient, auth_headers: dict):
    """PATCH /v1/presets/{id} inexistant retourne 404."""
    resp = client.patch(
        "/v1/presets/00000000-0000-0000-0000-000000000000",
        json={"name": "X"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_delete_preset_204(client: TestClient, auth_headers: dict):
    """DELETE /v1/presets/{id} suppression definitive (204), preset absent de la liste."""
    preset_id = _create_preset(client, auth_headers, name="To delete")
    resp = client.delete(f"/v1/presets/{preset_id}", headers=auth_headers)
    assert resp.status_code == 204
    list_resp = client.get("/v1/presets", headers=auth_headers)
    names = [p["name"] for p in list_resp.json()]
    assert "To delete" not in names
    get_resp = client.get(f"/v1/presets/{preset_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_delete_preset_not_found(client: TestClient, auth_headers: dict):
    """DELETE /v1/presets/{id} inexistant retourne 404."""
    resp = client.delete("/v1/presets/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404


def test_error_format_has_detail(client: TestClient, auth_headers: dict):
    """Erreurs au format { \"detail\": \"...\" }."""
    resp = client.get("/v1/presets/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)
