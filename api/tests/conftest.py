# Pytest fixtures pour l'API — DB test (SQLite in-memory), user mock (Story 6.1).
# client : session-scoped pour éviter UNIQUE constraint quand plusieurs modules utilisent le client.

import uuid
from collections.abc import Generator

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import api.models  # noqa: F401 — enregistre tous les modèles avec Base
from api.db import get_db
from api.db.session import Base
from api.main import app
from api.models import User


# Moteur SQLite en mémoire pour les tests (StaticPool = une seule connexion partagée)
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=TEST_ENGINE)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
TestingSessionLocal = TestSessionLocal  # alias for test_cash_sessions


def override_get_db() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Utilisateur factice pour les tests réception (doit exister en BDD pour les FK)
FAKE_USER_ID = uuid.uuid4()
FAKE_SITE_ID = uuid.uuid4()


def _get_fake_user():
    from api.models import Site, User
    u = User(
        id=FAKE_USER_ID,
        username="test_reception",
        email="test@reception.local",
        password_hash="hash",
        role="operator",
        status="active",
        site_id=FAKE_SITE_ID,
    )
    return u


FAKE_USER = _get_fake_user()


def override_get_current_user():
    return FAKE_USER


@pytest.fixture(scope="session")
def _db_with_user():
    """Session-scoped : crée les tables et insère site + user une seule fois."""
    from api.models import Site
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TestSessionLocal()
    try:
        site = Site(id=FAKE_SITE_ID, name="Test Site", is_active=True)
        db.add(site)
        db.add(FAKE_USER)
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client(_db_with_user):
    """Client API authentifié (reception.access) pour tests réception. Function-scoped pour ne pas polluer les tests sans auth."""
    from api.core import deps
    original_get_codes = deps.get_user_permission_codes_from_user

    def mock_get_codes(db, user):
        if user and user.id == FAKE_USER_ID:
            return {"reception.access", "admin"}
        return set()

    deps.get_user_permission_codes_from_user = mock_get_codes
    app.dependency_overrides[get_db] = override_get_db

    def _get_current_user(db: Session = Depends(get_db)):
        user = db.get(User, FAKE_USER_ID)
        if user is None:
            raise RuntimeError("Test user not found in DB")
        return user

    app.dependency_overrides[deps.get_current_user] = _get_current_user

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    deps.get_user_permission_codes_from_user = original_get_codes


@pytest.fixture
def auth_headers() -> dict:
    """Headers pour routes protegees (admin). get_current_user est override par client -> pas de Bearer requis."""
    return {}
