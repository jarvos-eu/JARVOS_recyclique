# Story 8.6 — Tests GET /v1/admin/paheko-compta-url.

import pytest
from fastapi.testclient import TestClient


class TestPahekoComptaUrl:
    """GET /v1/admin/paheko-compta-url (admin only)."""

    def test_paheko_compta_url_404_when_not_configured(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """Sans PAHEKO_PLUGIN_URL : 404."""
        r = client.get("/v1/admin/paheko-compta-url", headers=auth_headers)
        assert r.status_code == 404
        data = r.json()
        assert "detail" in data

    def test_paheko_compta_url_200_when_configured(
        self,
        client: TestClient,
        auth_headers: dict,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Avec PAHEKO_PLUGIN_URL : 200 et url = base + /admin/."""
        monkeypatch.setenv("PAHEKO_PLUGIN_URL", "https://paheko.example/plugin/recyclic/push")
        # Recharger les settings pour prendre la nouvelle env
        from api.config.settings import get_settings
        get_settings.cache_clear()
        try:
            r = client.get("/v1/admin/paheko-compta-url", headers=auth_headers)
            assert r.status_code == 200
            data = r.json()
            assert data["url"] == "https://paheko.example/admin/"
        finally:
            get_settings.cache_clear()
