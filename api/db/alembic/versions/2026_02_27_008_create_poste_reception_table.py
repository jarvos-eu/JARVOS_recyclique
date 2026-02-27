"""create_poste_reception_table

Revision ID: 008
Revises: 007
Create Date: 2026-02-27

Story 3.4 / Epic 6 stub : table poste_reception (ouverture poste par admin).
Colonnes: id, opened_by_user_id, opened_at, status.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "008"
down_revision: Union[str, Sequence[str], None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "poste_reception",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("opened_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'open'")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["opened_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "idx_poste_reception_opened_at",
        "poste_reception",
        ["opened_at"],
        unique=False,
    )
    op.create_index(
        "idx_poste_reception_status",
        "poste_reception",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_poste_reception_status", table_name="poste_reception")
    op.drop_index("idx_poste_reception_opened_at", table_name="poste_reception")
    op.drop_table("poste_reception")
