"""Tests des routers métier sous /api (stubs Story 1.2)."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_api_auth_root():
    """GET /api/auth/ retourne le stub auth."""
    resp = client.get("/api/auth/")
    assert resp.status_code == 200
    assert resp.json() == {"module": "auth"}


def test_api_pos_root():
    """GET /api/pos/ retourne le stub pos."""
    resp = client.get("/api/pos/")
    assert resp.status_code == 200
    assert resp.json() == {"module": "pos"}


def test_api_reception_root():
    """GET /api/reception/ retourne le stub reception."""
    resp = client.get("/api/reception/")
    assert resp.status_code == 200
    assert resp.json() == {"module": "reception"}


def test_api_admin_root():
    """GET /api/admin/ retourne le stub admin."""
    resp = client.get("/api/admin/")
    assert resp.status_code == 200
    assert resp.json() == {"module": "admin"}


def test_catch_all_when_dist_absent_returns_json_message():
    """Catch-all : route non-API retourne soit index.html (si dist présent), soit JSON explicite (build absent)."""
    resp = client.get("/any-spa-path")
    assert resp.status_code == 200
    if "application/json" in resp.headers.get("content-type", ""):
        data = resp.json()
        assert "message" in data
        assert "detail" in data
    else:
        # frontend/dist présent : on reçoit index.html
        assert "text/html" in resp.headers.get("content-type", "")
        assert b"<!doctype html>" in resp.content or b"<html" in resp.content.lower()
