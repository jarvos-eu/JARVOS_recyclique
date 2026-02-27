"""Tests API sales — Story 5.2. POST/GET/PUT/PATCH /v1/sales."""

import uuid

import pytest
from fastapi.testclient import TestClient


def test_post_sales_requires_auth(client: TestClient) -> None:
    """POST /v1/sales sans token retourne 401."""
    resp = client.post(
        "/v1/sales",
        json={
            "cash_session_id": str(uuid.uuid4()),
            "items": [{"preset_id": str(uuid.uuid4()), "quantity": 1, "unit_price": 100}],
            "payments": [{"payment_method": "especes", "amount": 100}],
        },
    )
    assert resp.status_code == 401


def test_post_sales_success(
    client: TestClient,
    auth_headers: dict,
    open_cash_session,
    test_preset,
) -> None:
    """POST /v1/sales avec session ouverte et body valide retourne 201 et crée la vente."""
    body = {
        "cash_session_id": str(open_cash_session.id),
        "items": [
            {
                "preset_id": str(test_preset.id),
                "quantity": 1,
                "unit_price": test_preset.preset_price,
                "total_price": test_preset.preset_price,
            }
        ],
        "payments": [{"payment_method": "especes", "amount": test_preset.preset_price}],
        "note": "Test note",
    }
    resp = client.post("/v1/sales", json=body, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["cash_session_id"] == str(open_cash_session.id)
    assert data["total_amount"] == test_preset.preset_price
    assert data["note"] == "Test note"
    assert len(data["items"]) == 1
    assert len(data["payment_transactions"]) == 1
    assert data["items"][0]["preset_id"] == str(test_preset.id)
    assert data["payment_transactions"][0]["amount"] == test_preset.preset_price


def test_post_sales_rejects_closed_session(
    client: TestClient,
    auth_headers: dict,
    open_cash_session,
    test_preset,
    db_session,
) -> None:
    """POST /v1/sales avec session fermée retourne 400."""
    open_cash_session.status = "closed"
    db_session.add(open_cash_session)
    db_session.commit()
    body = {
        "cash_session_id": str(open_cash_session.id),
        "items": [{"preset_id": str(test_preset.id), "quantity": 1, "unit_price": 500}],
        "payments": [{"payment_method": "especes", "amount": 500}],
    }
    resp = client.post("/v1/sales", json=body, headers=auth_headers)
    assert resp.status_code == 400
    assert "closed" in resp.json().get("detail", "").lower()


def test_post_sales_rejects_payment_mismatch(
    client: TestClient,
    auth_headers: dict,
    open_cash_session,
    test_preset,
) -> None:
    """POST /v1/sales avec somme paiements != total lignes retourne 400."""
    body = {
        "cash_session_id": str(open_cash_session.id),
        "items": [{"preset_id": str(test_preset.id), "quantity": 1, "unit_price": 500}],
        "payments": [{"payment_method": "especes", "amount": 300}],
    }
    resp = client.post("/v1/sales", json=body, headers=auth_headers)
    assert resp.status_code == 400
    assert "sum" in resp.json().get("detail", "").lower() or "payment" in resp.json().get("detail", "").lower()


def test_get_sales_list(
    client: TestClient,
    auth_headers: dict,
    open_cash_session,
) -> None:
    """GET /v1/sales retourne 200 et une liste (optionnel filtre cash_session_id)."""
    resp = client.get("/v1/sales", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    resp2 = client.get(
        f"/v1/sales?cash_session_id={open_cash_session.id}",
        headers=auth_headers,
    )
    assert resp2.status_code == 200
    assert isinstance(resp2.json(), list)


def test_get_sales_detail(
    client: TestClient,
    auth_headers: dict,
    open_cash_session,
    test_preset,
) -> None:
    """GET /v1/sales/{id} retourne 200 avec items et payments."""
    body = {
        "cash_session_id": str(open_cash_session.id),
        "items": [{"preset_id": str(test_preset.id), "quantity": 1, "unit_price": 500}],
        "payments": [{"payment_method": "especes", "amount": 500}],
    }
    create = client.post("/v1/sales", json=body, headers=auth_headers)
    assert create.status_code == 201
    sale_id = create.json()["id"]
    resp = client.get(f"/v1/sales/{sale_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == sale_id
    assert len(data["items"]) >= 1
    assert len(data["payment_transactions"]) >= 1


def test_get_sales_detail_404(client: TestClient, auth_headers: dict) -> None:
    """GET /v1/sales/{id} avec id inexistant retourne 404."""
    resp = client.get(f"/v1/sales/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404


def test_put_sales_note(
    client: TestClient,
    auth_headers: dict,
    open_cash_session,
    test_preset,
) -> None:
    """PUT /v1/sales/{id} avec body note met à jour la note."""
    body = {
        "cash_session_id": str(open_cash_session.id),
        "items": [{"preset_id": str(test_preset.id), "quantity": 1, "unit_price": 500}],
        "payments": [{"payment_method": "especes", "amount": 500}],
    }
    create = client.post("/v1/sales", json=body, headers=auth_headers)
    sale_id = create.json()["id"]
    resp = client.put(
        f"/v1/sales/{sale_id}",
        json={"note": "Nouvelle note"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["note"] == "Nouvelle note"


def test_patch_sales_item_weight(
    client: TestClient,
    auth_headers: dict,
    open_cash_session,
    test_preset,
) -> None:
    """PATCH /v1/sales/{id}/items/{item_id}/weight met à jour le poids."""
    body = {
        "cash_session_id": str(open_cash_session.id),
        "items": [{"preset_id": str(test_preset.id), "quantity": 1, "unit_price": 500}],
        "payments": [{"payment_method": "especes", "amount": 500}],
    }
    create = client.post("/v1/sales", json=body, headers=auth_headers)
    data = create.json()
    sale_id = data["id"]
    item_id = data["items"][0]["id"]
    resp = client.patch(
        f"/v1/sales/{sale_id}/items/{item_id}/weight",
        json={"weight": 2.5},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["weight"] == 2.5
