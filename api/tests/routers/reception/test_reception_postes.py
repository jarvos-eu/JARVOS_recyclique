# Tests API réception — postes (Story 6.1).
# pytest, structure miroir api/routers/reception.
# Review : scénarios métier avec client authentifié (fixture client).

import pytest


def test_get_current_poste_sans_auth():
    """GET /v1/reception/postes/current sans token — 401."""
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    r = c.get("/v1/reception/postes/current")
    assert r.status_code == 401


def test_get_current_poste_404_when_none(client):
    """GET /v1/reception/postes/current sans poste ouvert — 404."""
    r = client.get("/v1/reception/postes/current")
    assert r.status_code == 404


def test_open_poste_authenticated(client):
    """POST /v1/reception/postes/open avec auth — 201 et poste créé."""
    r = client.post("/v1/reception/postes/open", json={})
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["status"] == "opened"
    assert data["opened_at"]


def test_get_current_poste_authenticated_after_open(client):
    """GET /v1/reception/postes/current après open — 200 et même poste."""
    open_r = client.post("/v1/reception/postes/open", json={})
    assert open_r.status_code == 201
    poste_id = open_r.json()["id"]

    r = client.get("/v1/reception/postes/current")
    assert r.status_code == 200
    assert r.json()["id"] == poste_id
    assert r.json()["status"] == "opened"


def test_close_poste_authenticated(client):
    """POST /v1/reception/postes/{id}/close avec auth — 200 et status closed."""
    open_r = client.post("/v1/reception/postes/open", json={})
    assert open_r.status_code == 201
    poste_id = open_r.json()["id"]

    r = client.post(f"/v1/reception/postes/{poste_id}/close")
    assert r.status_code == 200
    assert r.json()["status"] == "closed"
    assert r.json()["closed_at"] is not None
    # Si aucun autre poste ouvert (DB isolée), get current renvoie 404
    get_r = client.get("/v1/reception/postes/current")
    if get_r.status_code == 200:
        assert get_r.json()["id"] != poste_id  # pas le poste qu'on vient de fermer
