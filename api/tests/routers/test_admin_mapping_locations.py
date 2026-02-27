"""Tests API admin mapping locations (Story 7.2). GET/POST/DELETE /v1/admin/mapping/locations."""

import pytest
from fastapi.testclient import TestClient


def test_admin_list_location_mappings_empty(client: TestClient, auth_headers: dict):
    """GET /v1/admin/mapping/locations retourne 200 et liste vide."""
    resp = client.get("/v1/admin/mapping/locations", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_admin_create_location_mapping_by_site_201(client: TestClient, auth_headers: dict):
    """POST /v1/admin/mapping/locations avec site_id cree un mapping."""
    site = client.post("/v1/sites", json={"name": "Site Admin", "is_active": True}, headers=auth_headers)
    assert site.status_code == 201
    site_id = site.json()["id"]
    resp = client.post(
        "/v1/admin/mapping/locations",
        json={"site_id": site_id, "paheko_id_location": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["site_id"] == site_id
    assert resp.json()["paheko_id_location"] == 1


def test_admin_delete_location_mapping_204(client: TestClient, auth_headers: dict):
    """DELETE /v1/admin/mapping/locations/{id} retourne 204."""
    site = client.post("/v1/sites", json={"name": "Site Del", "is_active": True}, headers=auth_headers)
    site_id = site.json()["id"]
    create = client.post(
        "/v1/admin/mapping/locations",
        json={"site_id": site_id, "paheko_id_location": 2},
        headers=auth_headers,
    )
    mapping_id = create.json()["id"]
    resp = client.delete(f"/v1/admin/mapping/locations/{mapping_id}", headers=auth_headers)
    assert resp.status_code == 204
