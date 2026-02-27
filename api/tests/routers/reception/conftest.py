# Fixtures partagées pour les tests API réception (Story 6.3).
# Fournit un utilisateur avec reception.access, un ticket avec lignes, et un token JWT.

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from api.db import get_db
from api.db.session import Base, engine
from api.models import (
    Group,
    LigneDepot,
    Permission,
    PosteReception,
    TicketDepot,
    User,
    group_permissions,
    user_groups,
)
from api.services.auth import AuthService

# S'assurer que les modeles sont enregistres et que les tables existent (SQLite test).
import api.models  # noqa: F401
Base.metadata.create_all(bind=engine)


def _get_db_session() -> Session:
    gen = get_db()
    return next(gen)


@pytest.fixture
def reception_db_session():
    """Session DB pour créer les données réception ; commit pour que l'API les voie."""
    db = _get_db_session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def reception_user_with_ticket_and_lignes(reception_db_session: Session):
    """
    Crée : Permission reception.access, Group, User (actif) avec ce groupe,
    PosteReception, TicketDepot, 2 LigneDepot. Commit. Retourne token JWT, ticket_id, etc.
    """
    db = reception_db_session
    now = datetime.now(timezone.utc)

    # Permission et groupe
    perm = db.execute(select(Permission).where(Permission.code == "reception.access")).scalars().one_or_none()
    if perm is None:
        perm = Permission(code="reception.access", label="Accès réception")
        db.add(perm)
        db.flush()
    group_name = f"test_reception_export_{uuid.uuid4().hex[:8]}"
    group = Group(name=group_name, description="Test 6.3")
    db.add(group)
    db.flush()
    db.execute(insert(group_permissions).values(group_id=group.id, permission_id=perm.id))

    # User avec mot de passe hashé
    auth = AuthService(db)
    username = f"test_reception_{uuid.uuid4().hex[:8]}"
    user = User(
        username=username,
        email=f"{username}@test.local",
        password_hash=auth.hash_password("test"),
        status="active",
        role="operator",
    )
    db.add(user)
    db.flush()
    db.execute(insert(user_groups).values(user_id=user.id, group_id=group.id))

    # Poste, ticket, lignes
    poste = PosteReception(
        opened_by_user_id=user.id,
        opened_at=now,
        status="opened",
    )
    db.add(poste)
    db.flush()
    ticket = TicketDepot(
        poste_id=poste.id,
        benevole_user_id=user.id,
        status="opened",
    )
    db.add(ticket)
    db.flush()
    ligne1 = LigneDepot(
        ticket_id=ticket.id,
        poids_kg=10.5,
        destination="recyclage",
        notes="Ligne 1 test",
        is_exit=False,
    )
    ligne2 = LigneDepot(
        ticket_id=ticket.id,
        poids_kg=2.25,
        destination="revente",
        notes=None,
        is_exit=False,
    )
    db.add(ligne1)
    db.add(ligne2)
    db.commit()

    token = auth.create_access_token(user.id)
    yield {
        "token": token,
        "user": user,
        "ticket_id": ticket.id,
        "poste_id": poste.id,
        "ligne_ids": [ligne1.id, ligne2.id],
        "db": db,
    }
