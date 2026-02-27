"""Seed permissions et groupes RBAC (Story 3.2).

Revision ID: 002
Revises: 001
Create Date: 2026-02-27

"""
import uuid
from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
from sqlalchemy import delete, insert

from api.db.session import Base
from api.models import Group, Permission

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def upgrade() -> None:
    conn = op.get_bind()
    p_table = Base.metadata.tables["permissions"]
    g_table = Base.metadata.tables["groups"]
    gp_table = Base.metadata.tables["group_permissions"]

    now = _now()
    perms_data = [
        ("caisse.access", "Accès caisse"),
        ("caisse.virtual.access", "Accès caisse virtuelle"),
        ("caisse.deferred.access", "Accès caisse différée"),
        ("reception.access", "Accès réception"),
        ("admin", "Administration"),
        ("vie_asso.access", "Vie associative"),
    ]
    perm_ids = {}
    for code, label in perms_data:
        pid = uuid.uuid4()
        perm_ids[code] = pid
        conn.execute(
            insert(p_table).values(
                id=pid,
                code=code,
                label=label,
                created_at=now,
                updated_at=now,
            )
        )

    groups_data = [
        ("operateur_caisse", "Opérateur caisse", ["caisse.access"]),
        ("operateur_reception", "Opérateur réception", ["reception.access"]),
        ("responsable_compta_admin", "Responsable compta / admin", ["admin"]),
        ("admin_technique", "Admin technique", ["admin"]),
        ("benevole", "Bénévole", ["vie_asso.access"]),
    ]
    group_ids = {}
    for name, description, perm_codes in groups_data:
        gid = uuid.uuid4()
        group_ids[name] = gid
        conn.execute(
            insert(g_table).values(
                id=gid,
                name=name,
                description=description,
                created_at=now,
                updated_at=now,
            )
        )
        for code in perm_codes:
            conn.execute(
                insert(gp_table).values(
                    group_id=gid,
                    permission_id=perm_ids[code],
                )
            )


def downgrade() -> None:
    conn = op.get_bind()
    gp_table = Base.metadata.tables["group_permissions"]
    g_table = Base.metadata.tables["groups"]
    p_table = Base.metadata.tables["permissions"]

    conn.execute(delete(gp_table))
    conn.execute(delete(g_table))
    conn.execute(delete(p_table))
