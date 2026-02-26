"""Tests du loader de modules (TOML, ModuleBase) — Story 1.4."""

from fastapi.testclient import TestClient

from api.main import app
from api.core.modules.base import ModuleBase


def test_diagnostic_modules_returns_200_and_list():
    """GET /api/admin/diagnostic/modules retourne 200 et une liste de modules chargés."""
    with TestClient(app) as client:
        resp = client.get("/api/admin/diagnostic/modules")
    assert resp.status_code == 200
    data = resp.json()
    assert "modules" in data
    assert isinstance(data["modules"], list)
    # Avec modules.toml présent et enabled = ["stub"], le stub doit être chargé
    assert "stub" in data["modules"]


def test_module_base_interface():
    """ModuleBase définit name, register, startup, shutdown."""
    from api.core.modules.stub_module import StubModule
    m = StubModule()
    assert m.name == "stub"
    assert callable(getattr(m, "register", None))
    assert callable(getattr(m, "startup", None))
    assert callable(getattr(m, "shutdown", None))
