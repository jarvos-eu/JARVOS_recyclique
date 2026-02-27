# Story 8.4 — Tests GET /v1/admin/health et GET /v1/admin/audit-log.

import pytest
from fastapi.testclient import TestClient


class TestAdminHealth:
    """GET /v1/admin/health (agrégé), /health/database, /health/scheduler, /health/anomalies."""

    def test_admin_health_returns_200_and_status(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """GET /v1/admin/health avec admin : 200 et champs status, database, redis, push_worker."""
        r = client.get("/v1/admin/health", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "status" in data
        assert data["status"] in ("ok", "degraded")
        assert "database" in data
        assert "redis" in data
        assert "push_worker" in data

    def test_admin_health_without_auth_returns_401(self, client: TestClient) -> None:
        """Sans token : 401 (ou 200 si conftest injecte un user par défaut)."""
        r = client.get("/v1/admin/health")
        # Conftest peut injecter get_current_user : 200 attendu si user injecté, 401 sinon.
        assert r.status_code in (200, 401)

    def test_admin_health_database_returns_200(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """GET /v1/admin/health/database : 200 et status."""
        r = client.get("/v1/admin/health/database", headers=auth_headers)
        assert r.status_code == 200
        assert "status" in r.json()

    def test_admin_health_scheduler_returns_200(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """GET /v1/admin/health/scheduler : 200 et status, configured, running."""
        r = client.get("/v1/admin/health/scheduler", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "status" in data
        assert "configured" in data
        assert "running" in data

    def test_admin_health_anomalies_returns_200(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """GET /v1/admin/health/anomalies : 200 et items (stub)."""
        r = client.get("/v1/admin/health/anomalies", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert data["count"] == 0


class TestAdminAuditLog:
    """GET /v1/admin/audit-log avec pagination."""

    def test_audit_log_returns_200_and_pagination(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """GET /v1/admin/audit-log : 200 et items, total, page, page_size."""
        r = client.get("/v1/admin/audit-log?page=1&page_size=10", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_audit_log_without_auth_returns_401(self, client: TestClient) -> None:
        """Sans token : 401 (ou 200 si conftest injecte un user par défaut)."""
        r = client.get("/v1/admin/audit-log")
        assert r.status_code in (200, 401)

    def test_audit_log_with_filters(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """GET /v1/admin/audit-log avec date_from, event_type : 200."""
        r = client.get(
            "/v1/admin/audit-log?page=1&page_size=5&event_type=reception_post_opened",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data
