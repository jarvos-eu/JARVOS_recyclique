# Tests API RecyClique — pytest.
# Fixtures partagées : db_engine, db_session, client.
# Si TEST_DATABASE_URL (postgresql://...) est défini : exécution des migrations
# Alembic sur cette BDD puis tests contre elle. Sinon : SQLite temporaire + create_all
# (voir story 2.1 — pour vérifier les migrations, lancer les tests avec TEST_DATABASE_URL).

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.db import get_db
from api.models import Base


def _use_pg_test_db() -> bool:
    url = os.environ.get("TEST_DATABASE_URL", "").strip()
    return url.startswith("postgresql")


@pytest.fixture(scope="session")
def _pg_engine():
    """Moteur PostgreSQL de test après exécution des migrations Alembic (session-scoped)."""
    if not _use_pg_test_db():
        return None
    from api.config.settings import get_settings

    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
    get_settings.cache_clear()

    import alembic.config
    from alembic import command

    api_dir = Path(__file__).resolve().parent.parent
    cfg = alembic.config.Config(str(api_dir / "alembic.ini"))
    command.upgrade(cfg, "head")

    engine = create_engine(os.environ["DATABASE_URL"])
    return engine


@pytest.fixture(scope="function")
def db_engine(_pg_engine, tmp_path):
    """Moteur BDD pour les tests. PG si TEST_DATABASE_URL, sinon SQLite fichier temporaire."""
    if _pg_engine is not None:
        return _pg_engine
    db_file = tmp_path / "test_sites.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Session de test. Pour PostgreSQL : transaction rollback en fin de test."""
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    if db_engine.url.drivername == "postgresql":
        connection = db_engine.connect()
        transaction = connection.begin()
        session = Session(bind=connection)
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()
            connection.close()
    else:
        session = Session()
        try:
            yield session
        finally:
            session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Client de test avec override get_db vers la session de test."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)
