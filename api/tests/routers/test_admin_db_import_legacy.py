# Story 8.5 — Tests POST /v1/admin/db/* et GET/POST /v1/admin/import/legacy/*.

import pytest
from fastapi.testclient import TestClient


class TestAdminDb:
    """POST /v1/admin/db/export, purge-transactions, import (admin ou super_admin)."""

    def test_db_export_returns_200_and_sql_content(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST /v1/admin/db/export avec admin : 200 et contenu SQL."""
        r = client.post("/v1/admin/db/export", headers=auth_headers)
        assert r.status_code == 200
        assert "recyclique" in r.headers.get("content-disposition", "").lower() or "sql" in r.headers.get("content-type", "").lower()
        assert b"RecyClique" in r.content or b"stub" in r.content

    def test_db_purge_transactions_returns_200(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST /v1/admin/db/purge-transactions avec admin : 200 et message, deleted_count."""
        r = client.post("/v1/admin/db/purge-transactions", headers=auth_headers, json={})
        assert r.status_code == 200
        data = r.json()
        assert "message" in data
        assert "deleted_count" in data

    def test_db_import_returns_200_with_file(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST /v1/admin/db/import avec fichier : 200 et ok/message."""
        files = {"file": ("backup.sql", b"-- stub", "application/sql")}
        r = client.post("/v1/admin/db/import", headers=auth_headers, files=files)
        assert r.status_code == 200
        data = r.json()
        assert data.get("ok") is True
        assert "filename" in data or "message" in data


class TestAdminImportLegacy:
    """GET llm-models, POST analyze, preview, validate, execute."""

    def test_llm_models_returns_200_and_list(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """GET /v1/admin/import/legacy/llm-models : 200 et models (liste vide stub)."""
        r = client.get("/v1/admin/import/legacy/llm-models", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "models" in data
        assert isinstance(data["models"], list)

    def test_legacy_analyze_returns_200_with_file(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST /v1/admin/import/legacy/analyze avec CSV : 200 et columns, errors, warnings."""
        files = {"file": ("data.csv", b"a,b,c\n1,2,3", "text/csv")}
        r = client.post("/v1/admin/import/legacy/analyze", headers=auth_headers, files=files)
        assert r.status_code == 200
        data = r.json()
        assert "columns" in data
        assert "errors" in data
        assert "warnings" in data

    def test_legacy_preview_returns_200(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST /v1/admin/import/legacy/preview : 200 et rows, total."""
        r = client.post("/v1/admin/import/legacy/preview", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "rows" in data
        assert "total" in data

    def test_legacy_validate_returns_200(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST /v1/admin/import/legacy/validate : 200 et valid, errors, warnings."""
        r = client.post("/v1/admin/import/legacy/validate", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "valid" in data
        assert "errors" in data
        assert "warnings" in data

    def test_legacy_execute_returns_200(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST /v1/admin/import/legacy/execute : 200 et imported_count, errors."""
        r = client.post("/v1/admin/import/legacy/execute", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "imported_count" in data
        assert "errors" in data
