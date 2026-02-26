"""Tests API CRUD + hierarchy, sale-tickets, entry-tickets, visibility, display-order, soft delete — Story 2.3."""

import pytest
from fastapi.testclient import TestClient


def _create_category(
    client: TestClient,
    name: str = "Cat Test",
    parent_id: str | None = None,
    official_name: str | None = None,
    is_visible_sale: bool = True,
    is_visible_reception: bool = True,
    display_order: int = 0,
    display_order_entry: int = 0,
) -> str:
    body = {
        "name": name,
        "is_visible_sale": is_visible_sale,
        "is_visible_reception": is_visible_reception,
        "display_order": display_order,
        "display_order_entry": display_order_entry,
    }
    if parent_id is not None:
        body["parent_id"] = parent_id
    if official_name is not None:
        body["official_name"] = official_name
    resp = client.post("/v1/categories", json=body)
    assert resp.status_code == 201
    return resp.json()["id"]


def test_list_categories_empty(client: TestClient):
    """GET /v1/categories retourne 200 et liste vide quand aucune categorie."""
    resp = client.get("/v1/categories")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_categories_returns_created(client: TestClient):
    """GET /v1/categories retourne les categories creees (sans supprimees)."""
    _create_category(client, name="Cat A")
    _create_category(client, name="Cat B")
    resp = client.get("/v1/categories")
    assert resp.status_code == 200
    names = [c["name"] for c in resp.json()]
    assert "Cat A" in names
    assert "Cat B" in names


def test_list_categories_filter_parent_id(client: TestClient):
    """GET /v1/categories?parent_id=... filtre par parent."""
    root_id = _create_category(client, name="Root")
    _create_category(client, name="Child", parent_id=root_id)
    resp = client.get("/v1/categories", params={"parent_id": root_id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Child"
    assert data[0]["parent_id"] == root_id


def test_get_categories_hierarchy_empty(client: TestClient):
    """GET /v1/categories/hierarchy retourne 200 et liste vide quand aucune racine."""
    resp = client.get("/v1/categories/hierarchy")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_categories_hierarchy_with_children(client: TestClient):
    """GET /v1/categories/hierarchy retourne arborescence racines + children."""
    root_id = _create_category(client, name="Root", display_order=1)
    _create_category(client, name="Child", parent_id=root_id)
    resp = client.get("/v1/categories/hierarchy")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Root"
    assert len(data[0]["children"]) == 1
    assert data[0]["children"][0]["name"] == "Child"


def test_get_categories_sale_tickets_filtered(client: TestClient):
    """GET /v1/categories/sale-tickets retourne seulement is_visible_sale=true et non supprimees."""
    _create_category(client, name="Visible", is_visible_sale=True)
    _create_category(client, name="Hidden", is_visible_sale=False)
    resp = client.get("/v1/categories/sale-tickets")
    assert resp.status_code == 200
    names = [c["name"] for c in resp.json()]
    assert "Visible" in names
    assert "Hidden" not in names


def test_get_categories_entry_tickets_filtered(client: TestClient):
    """GET /v1/categories/entry-tickets retourne seulement is_visible_reception=true et non supprimees."""
    _create_category(client, name="Visible", is_visible_reception=True)
    _create_category(client, name="Hidden", is_visible_reception=False)
    resp = client.get("/v1/categories/entry-tickets")
    assert resp.status_code == 200
    names = [c["name"] for c in resp.json()]
    assert "Visible" in names
    assert "Hidden" not in names


def test_get_category_not_found(client: TestClient):
    """GET /v1/categories/{id} inexistant retourne 404 et detail."""
    resp = client.get("/v1/categories/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    assert "detail" in resp.json()
    assert resp.json()["detail"] == "Category not found"


def test_get_category_after_create(client: TestClient):
    """GET /v1/categories/{id} retourne la categorie creee."""
    cat_id = _create_category(client, name="Detail Cat", official_name="Official")
    resp = client.get(f"/v1/categories/{cat_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Detail Cat"
    assert resp.json()["official_name"] == "Official"
    assert resp.json()["deleted_at"] is None


def test_create_category_201(client: TestClient):
    """POST /v1/categories cree une categorie et retourne 201 avec corps snake_case."""
    resp = client.post(
        "/v1/categories",
        json={
            "name": "New Cat",
            "official_name": "Official New",
            "is_visible_sale": True,
            "is_visible_reception": False,
            "display_order": 10,
            "display_order_entry": 20,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "New Cat"
    assert data["official_name"] == "Official New"
    assert data["is_visible_sale"] is True
    assert data["is_visible_reception"] is False
    assert data["display_order"] == 10
    assert data["display_order_entry"] == 20
    assert "created_at" in data
    assert "updated_at" in data
    assert "T" in data["created_at"]


def test_create_category_parent_not_found_404(client: TestClient):
    """POST /v1/categories avec parent_id inexistant retourne 404."""
    resp = client.post(
        "/v1/categories",
        json={
            "name": "Child",
            "parent_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Parent category not found"


def test_put_category(client: TestClient):
    """PUT /v1/categories/{id} met a jour."""
    cat_id = _create_category(client, name="Original")
    resp = client.put(
        f"/v1/categories/{cat_id}",
        json={
            "name": "Updated",
            "official_name": "Off",
            "is_visible_sale": False,
            "display_order": 5,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"
    assert resp.json()["official_name"] == "Off"
    assert resp.json()["is_visible_sale"] is False
    assert resp.json()["display_order"] == 5


def test_put_category_not_found(client: TestClient):
    """PUT /v1/categories/{id} inexistant retourne 404."""
    resp = client.put(
        "/v1/categories/00000000-0000-0000-0000-000000000000",
        json={"name": "X"},
    )
    assert resp.status_code == 404


def test_put_category_parent_self_rejected(client: TestClient):
    """PUT /v1/categories/{id} avec parent_id=self retourne 400."""
    cat_id = _create_category(client, name="Self")
    resp = client.put(
        f"/v1/categories/{cat_id}",
        json={"parent_id": cat_id},
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()
    assert "self" in resp.json()["detail"].lower() or "cycle" in resp.json()["detail"].lower()


def test_put_category_parent_cycle_rejected(client: TestClient):
    """PUT /v1/categories/{id} avec parent_id=descendant (cycle) retourne 400."""
    root_id = _create_category(client, name="Root")
    child_id = _create_category(client, name="Child", parent_id=root_id)
    resp = client.put(
        f"/v1/categories/{root_id}",
        json={"parent_id": child_id},
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()
    assert "cycle" in resp.json()["detail"].lower()


def test_delete_category_soft_204(client: TestClient):
    """DELETE /v1/categories/{id} soft delete (204), categorie absente de liste."""
    cat_id = _create_category(client, name="To delete")
    resp = client.delete(f"/v1/categories/{cat_id}")
    assert resp.status_code == 204
    list_resp = client.get("/v1/categories")
    names = [c["name"] for c in list_resp.json()]
    assert "To delete" not in names
    get_resp = client.get(f"/v1/categories/{cat_id}")
    assert get_resp.status_code == 404


def test_delete_category_not_found(client: TestClient):
    """DELETE /v1/categories/{id} inexistant retourne 404."""
    resp = client.delete("/v1/categories/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_restore_category(client: TestClient):
    """POST /v1/categories/{id}/restore remet deleted_at a null."""
    cat_id = _create_category(client, name="To restore")
    client.delete(f"/v1/categories/{cat_id}")
    resp = client.post(f"/v1/categories/{cat_id}/restore")
    assert resp.status_code == 200
    assert resp.json()["deleted_at"] is None
    assert resp.json()["name"] == "To restore"
    list_resp = client.get("/v1/categories")
    names = [c["name"] for c in list_resp.json()]
    assert "To restore" in names


def test_restore_category_not_found(client: TestClient):
    """POST /v1/categories/{id}/restore avec id inexistant retourne 404."""
    resp = client.post("/v1/categories/00000000-0000-0000-0000-000000000000/restore")
    assert resp.status_code == 404


def test_put_visibility(client: TestClient):
    """PUT /v1/categories/{id}/visibility met a jour is_visible_sale et/ou is_visible_reception."""
    cat_id = _create_category(client, name="V", is_visible_sale=True, is_visible_reception=True)
    resp = client.put(
        f"/v1/categories/{cat_id}/visibility",
        json={"is_visible_sale": False, "is_visible_reception": False},
    )
    assert resp.status_code == 200
    assert resp.json()["is_visible_sale"] is False
    assert resp.json()["is_visible_reception"] is False


def test_put_visibility_not_found(client: TestClient):
    """PUT /v1/categories/{id}/visibility avec id inexistant retourne 404."""
    resp = client.put(
        "/v1/categories/00000000-0000-0000-0000-000000000000/visibility",
        json={"is_visible_sale": False},
    )
    assert resp.status_code == 404


def test_put_display_order(client: TestClient):
    """PUT /v1/categories/{id}/display-order met a jour display_order et/ou display_order_entry."""
    cat_id = _create_category(client, name="Ord", display_order=0, display_order_entry=0)
    resp = client.put(
        f"/v1/categories/{cat_id}/display-order",
        json={"display_order": 100, "display_order_entry": 200},
    )
    assert resp.status_code == 200
    assert resp.json()["display_order"] == 100
    assert resp.json()["display_order_entry"] == 200


def test_put_display_order_not_found(client: TestClient):
    """PUT /v1/categories/{id}/display-order avec id inexistant retourne 404."""
    resp = client.put(
        "/v1/categories/00000000-0000-0000-0000-000000000000/display-order",
        json={"display_order": 1},
    )
    assert resp.status_code == 404


def test_error_format_has_detail(client: TestClient):
    """Erreurs au format { \"detail\": \"...\" }."""
    resp = client.get("/v1/categories/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)
