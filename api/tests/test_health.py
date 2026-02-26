"""Tests de l'endpoint GET /health (Story 1.2)."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_returns_200_and_snake_case():
    """GET /health retourne 200 et un corps JSON en snake_case (status, database, redis)."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data
    assert data["status"] in ("ok", "degraded")
    assert data["database"] in ("ok", "unconfigured", "error")
    assert data["redis"] in ("ok", "unconfigured", "error")


def test_health_no_camel_case():
    """Réponse health ne contient pas de clés camelCase."""
    resp = client.get("/health")
    data = resp.json()
    for key in data:
        assert "_" in key or key.islower(), f"Clé attendue en snake_case: {key}"
