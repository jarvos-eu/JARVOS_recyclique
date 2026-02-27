# RecyClique API — Service permissions (Story 3.2).
# Récupération des codes permission d'un utilisateur via ses groupes.

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import Permission, User, user_groups, group_permissions


def get_user_permission_codes(db: Session, user_id: UUID) -> set[str]:
    """Retourne l'ensemble des codes de permission de l'utilisateur (via ses groupes)."""
    stmt = (
        select(Permission.code)
        .join(group_permissions, group_permissions.c.permission_id == Permission.id)
        .join(user_groups, user_groups.c.group_id == group_permissions.c.group_id)
        .where(user_groups.c.user_id == user_id)
    )
    rows = db.execute(stmt).scalars().all()
    return {r for r in rows} if rows else set()


def get_user_permission_codes_from_user(db: Session, user: User) -> set[str]:
    """Retourne l'ensemble des codes de permission de l'utilisateur (via ses groupes)."""
    return get_user_permission_codes(db, user.id)
