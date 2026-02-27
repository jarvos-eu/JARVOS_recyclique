"""Tests API cash-sessions — Story 5.1."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


def test_cash_sessions_list_requires_auth(client: TestClient):
    """GET /v1/cash-sessions sans token → 401."""
    r = client.get("/v1/cash-sessions")
    assert r.status_code == 401


def test_cash_sessions_current_requires_auth(client: TestClient):
    """GET /v1/cash-sessions/current sans token → 401."""
    r = client.get("/v1/cash-sessions/current")
    assert r.status_code == 401


def test_cash_sessions_status_requires_auth(client: TestClient):
    """GET /v1/cash-sessions/status/{id} sans token → 401."""
    r = client.get(f"/v1/cash-sessions/status/{uuid4()}")
    assert r.status_code == 401


def test_cash_sessions_deferred_check_requires_auth(client: TestClient):
    """GET /v1/cash-sessions/deferred/check sans token → 401."""
    r = client.get("/v1/cash-sessions/deferred/check?date=2026-02-27")
    assert r.status_code == 401


def test_cash_sessions_post_requires_auth(client: TestClient):
    """POST /v1/cash-sessions sans token → 401."""
    r = client.post(
        "/v1/cash-sessions",
        json={"initial_amount": 0, "register_id": str(uuid4())},
    )
    assert r.status_code == 401


def test_cash_sessions_close_requires_auth(client: TestClient):
    """POST /v1/cash-sessions/{id}/close sans token → 401."""
    r = client.post(
        f"/v1/cash-sessions/{uuid4()}/close",
        json={},
    )
    assert r.status_code == 401


def test_cash_sessions_get_by_id_requires_auth(client: TestClient):
    """GET /v1/cash-sessions/{id} sans token → 401."""
    r = client.get(f"/v1/cash-sessions/{uuid4()}")
    assert r.status_code == 401


def test_cash_sessions_step_get_requires_auth(client: TestClient):
    """GET /v1/cash-sessions/{id}/step sans token → 401."""
    r = client.get(f"/v1/cash-sessions/{uuid4()}/step")
    assert r.status_code == 401


def test_cash_sessions_step_put_requires_auth(client: TestClient):
    """PUT /v1/cash-sessions/{id}/step sans token → 401."""
    r = client.put(
        f"/v1/cash-sessions/{uuid4()}/step",
        json={"step": "sale"},
    )
    assert r.status_code == 401
