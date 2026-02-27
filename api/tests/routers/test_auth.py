"""Tests API auth et users/me — Story 3.1, 3.3. Login, refresh, logout, signup, pin, /users/me. Pas de secrets en dur."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.models import User, Group, Permission, user_groups, group_permissions, AuditEvent
from api.services.auth import AuthService


@pytest.fixture
def active_user(db_session: Session):
    """Utilisateur actif avec mot de passe connu (pour tests login)."""
    auth = AuthService(db_session)
    user = User(
        id=uuid.uuid4(),
        username="testoperator",
        email="test@example.com",
        password_hash=auth.hash_password("secret123"),
        first_name="Test",
        last_name="User",
        role="operator",
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def active_user_with_pin(db_session: Session):
    """Utilisateur actif avec PIN, SANS permission caisse (Story 3.3 : POST /pin → 403)."""
    auth = AuthService(db_session)
    user = User(
        id=uuid.uuid4(),
        username="pinuser",
        email="pin@example.com",
        password_hash=auth.hash_password("pass"),
        first_name="Pin",
        last_name="User",
        role="operator",
        status="active",
        pin_hash=auth.hash_pin("1234"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def active_user_with_pin_and_caisse(db_session: Session):
    """Utilisateur actif avec PIN et permission caisse.access (Story 3.3 : POST /pin → 200)."""
    auth = AuthService(db_session)
    user = User(
        id=uuid.uuid4(),
        username="caissepin",
        email="caissepin@example.com",
        password_hash=auth.hash_password("pass"),
        first_name="Caisse",
        last_name="Pin",
        role="operator",
        status="active",
        pin_hash=auth.hash_pin("1234"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    perm = Permission(code="caisse.access", label="Accès caisse")
    db_session.add(perm)
    db_session.commit()
    db_session.refresh(perm)
    group = Group(name="caisse_ops", description="Opérateurs caisse")
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)
    db_session.execute(group_permissions.insert().values(group_id=group.id, permission_id=perm.id))
    db_session.execute(user_groups.insert().values(user_id=user.id, group_id=group.id))
    db_session.commit()
    return user


def test_login_success(client: TestClient, active_user):
    """POST /v1/auth/login avec identifiants valides retourne 200, access_token, refresh_token, user."""
    resp = client.post(
        "/v1/auth/login",
        json={"username": "testoperator", "password": "secret123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testoperator"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["status"] == "active"


def test_login_invalid_password(client: TestClient, active_user):
    """POST /v1/auth/login avec mauvais mot de passe retourne 401."""
    resp = client.post(
        "/v1/auth/login",
        json={"username": "testoperator", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_login_invalid_username(client: TestClient):
    """POST /v1/auth/login avec utilisateur inexistant retourne 401."""
    resp = client.post(
        "/v1/auth/login",
        json={"username": "nobody", "password": "any"},
    )
    assert resp.status_code == 401


def test_refresh_success(client: TestClient, active_user):
    """POST /v1/auth/refresh avec refresh_token valide retourne nouveaux tokens."""
    login_resp = client.post(
        "/v1/auth/login",
        json={"username": "testoperator", "password": "secret123"},
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]
    resp = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token


def test_refresh_invalid(client: TestClient):
    """POST /v1/auth/refresh avec token invalide retourne 401."""
    resp = client.post("/v1/auth/refresh", json={"refresh_token": "invalid-token"})
    assert resp.status_code == 401


def test_logout(client: TestClient, active_user):
    """POST /v1/auth/logout avec refresh_token invalide la session (204)."""
    login_resp = client.post(
        "/v1/auth/login",
        json={"username": "testoperator", "password": "secret123"},
    )
    refresh_token = login_resp.json()["refresh_token"]
    resp = client.post("/v1/auth/logout", json={"refresh_token": refresh_token})
    assert resp.status_code == 204
    # Après logout, le refresh ne doit plus marcher
    ref_resp = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_resp.status_code == 401


def test_get_me_unauthorized(client: TestClient):
    """GET /v1/users/me sans token retourne 401."""
    resp = client.get("/v1/users/me")
    assert resp.status_code == 401


def test_get_me_success(client: TestClient, active_user):
    """GET /v1/users/me avec Bearer token retourne 200 et profil."""
    login_resp = client.post(
        "/v1/auth/login",
        json={"username": "testoperator", "password": "secret123"},
    )
    token = login_resp.json()["access_token"]
    resp = client.get("/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testoperator"
    assert data["email"] == "test@example.com"
    assert data["status"] == "active"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_put_me_success(client: TestClient, active_user):
    """PUT /v1/users/me met à jour first_name, last_name, email."""
    login_resp = client.post(
        "/v1/auth/login",
        json={"username": "testoperator", "password": "secret123"},
    )
    token = login_resp.json()["access_token"]
    resp = client.put(
        "/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Updated", "last_name": "Name", "email": "new@example.com"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"
    assert data["email"] == "new@example.com"


def test_put_me_email_already_taken_400(client: TestClient, active_user, db_session: Session):
    """PUT /v1/users/me avec email déjà utilisé par un autre user retourne 400."""
    auth = AuthService(db_session)
    other = User(
        id=uuid.uuid4(),
        username="otheruser",
        email="other@example.com",
        password_hash=auth.hash_password("x"),
        role="operator",
        status="active",
    )
    db_session.add(other)
    db_session.commit()
    login_resp = client.post(
        "/v1/auth/login",
        json={"username": "testoperator", "password": "secret123"},
    )
    token = login_resp.json()["access_token"]
    resp = client.put(
        "/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "other@example.com"},
    )
    assert resp.status_code == 400
    assert "already" in resp.json().get("detail", "").lower()


def test_put_me_password_success(client: TestClient, active_user):
    """PUT /v1/users/me/password change le mot de passe."""
    login_resp = client.post(
        "/v1/auth/login",
        json={"username": "testoperator", "password": "secret123"},
    )
    token = login_resp.json()["access_token"]
    resp = client.put(
        "/v1/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "secret123", "new_password": "newsecret456"},
    )
    assert resp.status_code == 204
    # Ancien MDP ne marche plus
    bad = client.post(
        "/v1/auth/login",
        json={"username": "testoperator", "password": "secret123"},
    )
    assert bad.status_code == 401
    # Nouveau MDP marche
    good = client.post(
        "/v1/auth/login",
        json={"username": "testoperator", "password": "newsecret456"},
    )
    assert good.status_code == 200


def test_put_me_pin_success(client: TestClient, active_user_with_pin_and_caisse):
    """PUT /v1/users/me/pin définit un PIN ; POST /v1/auth/pin avec ce PIN (permission caisse) → 200."""
    login_resp = client.post(
        "/v1/auth/login",
        json={"username": "caissepin", "password": "pass"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    resp = client.put(
        "/v1/users/me/pin",
        headers={"Authorization": f"Bearer {token}"},
        json={"new_pin": "5678"},
    )
    assert resp.status_code == 204
    pin_resp = client.post("/v1/auth/pin", json={"pin": "5678"})
    assert pin_resp.status_code == 200
    assert pin_resp.json()["user"]["username"] == "caissepin"


def test_signup_201(client: TestClient):
    """POST /v1/auth/signup crée une registration_request et retourne 201."""
    resp = client.post(
        "/v1/auth/signup",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "message" in data
    assert "approval" in data["message"].lower() or "submitted" in data["message"].lower()


def test_signup_duplicate_username(client: TestClient, active_user):
    """POST /v1/auth/signup avec username existant retourne 400."""
    resp = client.post(
        "/v1/auth/signup",
        json={
            "username": "testoperator",
            "email": "other@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 400
    assert "detail" in resp.json()


def test_pin_login_success(client: TestClient, active_user_with_pin_and_caisse):
    """POST /v1/auth/pin avec PIN valide et permission caisse retourne 200 et tokens (Story 3.3)."""
    resp = client.post("/v1/auth/pin", json={"pin": "1234"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["username"] == "caissepin"
    assert "pin" not in data.get("user", {})
    assert "pin" not in data


def test_pin_login_403_without_caisse_permission(client: TestClient, active_user_with_pin):
    """POST /v1/auth/pin avec utilisateur sans permission caisse retourne 403 (Story 3.3)."""
    resp = client.post("/v1/auth/pin", json={"pin": "1234"})
    assert resp.status_code == 403
    data = resp.json()
    assert "detail" in data


def test_pin_login_invalid(client: TestClient, active_user_with_pin_and_caisse):
    """POST /v1/auth/pin avec mauvais PIN retourne 401."""
    resp = client.post("/v1/auth/pin", json={"pin": "9999"})
    assert resp.status_code == 401
    data = resp.json()
    assert "detail" in data
    assert "pin" not in data


def test_pin_login_creates_audit_event(
    client: TestClient, active_user_with_pin_and_caisse, db_session: Session
):
    """POST /v1/auth/pin réussi enregistre un événement audit session_unlocked (Story 3.3)."""
    resp = client.post("/v1/auth/pin", json={"pin": "1234"})
    assert resp.status_code == 200
    from sqlalchemy import select
    events = db_session.execute(
        select(AuditEvent).where(AuditEvent.action == "session_unlocked")
    ).scalars().all()
    assert len(events) >= 1
    assert events[0].user_id == active_user_with_pin_and_caisse.id


def test_forgot_password_200(client: TestClient):
    """POST /v1/auth/forgot-password accepte et retourne 200 (stub)."""
    resp = client.post("/v1/auth/forgot-password", json={"email": "any@example.com"})
    assert resp.status_code == 200


def test_error_format_has_detail(client: TestClient):
    """Les erreurs auth renvoient un champ detail (convention API)."""
    resp = client.post("/v1/auth/login", json={"username": "x", "password": "y"})
    assert resp.status_code == 401
    data = resp.json()
    assert "detail" in data
