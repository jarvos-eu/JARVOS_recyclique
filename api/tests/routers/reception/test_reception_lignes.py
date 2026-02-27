# Tests API réception — lignes de dépôt (Story 6.2).
# 401 sans auth pour chaque endpoint ; scénarios avec client authentifié (conftest).

import pytest


def test_post_lignes_sans_auth():
    """POST /v1/reception/lignes sans token — 401."""
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    r = c.post(
        "/v1/reception/lignes",
        json={
            "ticket_id": "00000000-0000-0000-0000-000000000001",
            "poids_kg": 10.5,
            "destination": "recyclage",
        },
    )
    assert r.status_code == 401


def test_get_lignes_sans_auth():
    """GET /v1/reception/lignes sans token — 401."""
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    r = c.get("/v1/reception/lignes?ticket_id=00000000-0000-0000-0000-000000000001")
    assert r.status_code == 401


def test_put_lignes_sans_auth():
    """PUT /v1/reception/lignes/{ligne_id} sans token — 401."""
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    r = c.put(
        "/v1/reception/lignes/00000000-0000-0000-0000-000000000001",
        json={"poids_kg": 12},
    )
    assert r.status_code == 401


def test_patch_ligne_weight_sans_auth():
    """PATCH /v1/reception/tickets/{ticket_id}/lignes/{ligne_id}/weight sans token — 401."""
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    r = c.patch(
        "/v1/reception/tickets/00000000-0000-0000-0000-000000000001/lignes/00000000-0000-0000-0000-000000000002/weight",
        json={"weight": 15},
    )
    assert r.status_code == 401


def test_delete_lignes_sans_auth():
    """DELETE /v1/reception/lignes/{ligne_id} sans token — 401."""
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    r = c.delete("/v1/reception/lignes/00000000-0000-0000-0000-000000000001")
    assert r.status_code == 401


def test_create_ligne_authenticated(client):
    """POST /v1/reception/lignes avec auth — 201 et ligne créée."""
    client.post("/v1/reception/postes/open", json={})
    create_ticket = client.post("/v1/reception/tickets", json={})
    assert create_ticket.status_code == 201
    ticket_id = create_ticket.json()["id"]

    r = client.post(
        "/v1/reception/lignes",
        json={
            "ticket_id": ticket_id,
            "poids_kg": 10.5,
            "destination": "recyclage",
            "notes": "test",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["ticket_id"] == ticket_id
    assert float(data["poids_kg"]) == 10.5
    assert data["destination"] == "recyclage"
    assert data["notes"] == "test"
    assert "id" in data


def test_get_lignes_requires_ticket_id(client):
    """GET /v1/reception/lignes sans ticket_id — 400."""
    r = client.get("/v1/reception/lignes")
    assert r.status_code == 400


def test_list_lignes_authenticated(client):
    """GET /v1/reception/lignes?ticket_id= avec auth — 200 et items."""
    client.post("/v1/reception/postes/open", json={})
    create_ticket = client.post("/v1/reception/tickets", json={})
    assert create_ticket.status_code == 201
    ticket_id = create_ticket.json()["id"]
    client.post(
        "/v1/reception/lignes",
        json={"ticket_id": ticket_id, "poids_kg": 5, "destination": "revente"},
    )

    r = client.get(f"/v1/reception/lignes?ticket_id={ticket_id}")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["destination"] == "revente"


def test_get_ticket_includes_lignes(client):
    """GET /v1/reception/tickets/{id} retourne les lignes."""
    client.post("/v1/reception/postes/open", json={})
    create_ticket = client.post("/v1/reception/tickets", json={})
    assert create_ticket.status_code == 201
    ticket_id = create_ticket.json()["id"]
    client.post(
        "/v1/reception/lignes",
        json={"ticket_id": ticket_id, "poids_kg": 3, "destination": "don"},
    )

    r = client.get(f"/v1/reception/tickets/{ticket_id}")
    assert r.status_code == 200
    data = r.json()
    assert "lignes" in data
    assert len(data["lignes"]) == 1
    assert float(data["lignes"][0]["poids_kg"]) == 3
    assert data["lignes"][0]["destination"] == "don"


def test_put_ligne_authenticated(client):
    """PUT /v1/reception/lignes/{id} — 200 et ligne mise à jour."""
    client.post("/v1/reception/postes/open", json={})
    create_ticket = client.post("/v1/reception/tickets", json={})
    assert create_ticket.status_code == 201
    ticket_id = create_ticket.json()["id"]
    create_ligne = client.post(
        "/v1/reception/lignes",
        json={"ticket_id": ticket_id, "poids_kg": 1, "destination": "recyclage"},
    )
    assert create_ligne.status_code == 201
    ligne_id = create_ligne.json()["id"]

    r = client.put(
        f"/v1/reception/lignes/{ligne_id}",
        json={"poids_kg": 2, "destination": "destruction", "notes": "modif"},
    )
    assert r.status_code == 200
    data = r.json()
    assert float(data["poids_kg"]) == 2
    assert data["destination"] == "destruction"
    assert data["notes"] == "modif"


def test_patch_ligne_weight_authenticated(client):
    """PATCH .../weight — 200 et poids mis à jour."""
    client.post("/v1/reception/postes/open", json={})
    create_ticket = client.post("/v1/reception/tickets", json={})
    assert create_ticket.status_code == 201
    ticket_id = create_ticket.json()["id"]
    create_ligne = client.post(
        "/v1/reception/lignes",
        json={"ticket_id": ticket_id, "poids_kg": 7, "destination": "recyclage"},
    )
    assert create_ligne.status_code == 201
    ligne_id = create_ligne.json()["id"]

    r = client.patch(
        f"/v1/reception/tickets/{ticket_id}/lignes/{ligne_id}/weight",
        json={"weight": 8.5},
    )
    assert r.status_code == 200
    data = r.json()
    assert float(data["poids_kg"]) == 8.5


def test_delete_ligne_authenticated(client):
    """DELETE /v1/reception/lignes/{id} — 204 puis ligne absente du ticket."""
    client.post("/v1/reception/postes/open", json={})
    create_ticket = client.post("/v1/reception/tickets", json={})
    assert create_ticket.status_code == 201
    ticket_id = create_ticket.json()["id"]
    create_ligne = client.post(
        "/v1/reception/lignes",
        json={"ticket_id": ticket_id, "poids_kg": 1, "destination": "autre"},
    )
    assert create_ligne.status_code == 201
    ligne_id = create_ligne.json()["id"]

    r = client.delete(f"/v1/reception/lignes/{ligne_id}")
    assert r.status_code == 204

    get_ticket = client.get(f"/v1/reception/tickets/{ticket_id}")
    assert get_ticket.status_code == 200
    assert len(get_ticket.json()["lignes"]) == 0


def test_create_ligne_validation_poids_obligatoire(client):
    """POST /v1/reception/lignes sans poids_kg valide — 422."""
    client.post("/v1/reception/postes/open", json={})
    create_ticket = client.post("/v1/reception/tickets", json={})
    ticket_id = create_ticket.json()["id"]

    r = client.post(
        "/v1/reception/lignes",
        json={"ticket_id": ticket_id, "destination": "recyclage"},
    )
    assert r.status_code == 422


def test_create_ligne_validation_destination_obligatoire(client):
    """POST /v1/reception/lignes sans destination — 422."""
    client.post("/v1/reception/postes/open", json={})
    create_ticket = client.post("/v1/reception/tickets", json={})
    ticket_id = create_ticket.json()["id"]

    r = client.post(
        "/v1/reception/lignes",
        json={"ticket_id": ticket_id, "poids_kg": 10},
    )
    assert r.status_code == 422


def test_create_ligne_validation_destination_valeurs_metier(client):
    """POST /v1/reception/lignes avec destination invalide — 422 (valeurs: recyclage, revente, destruction, don, autre)."""
    client.post("/v1/reception/postes/open", json={})
    create_ticket = client.post("/v1/reception/tickets", json={})
    ticket_id = create_ticket.json()["id"]

    r = client.post(
        "/v1/reception/lignes",
        json={"ticket_id": ticket_id, "poids_kg": 10, "destination": "typo_ou_valeur_invalide"},
    )
    assert r.status_code == 422
