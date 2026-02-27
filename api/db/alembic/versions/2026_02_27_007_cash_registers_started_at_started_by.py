"""add started_at and started_by_user_id to cash_registers

Revision ID: 007
Revises: 006
Create Date: 2026-02-27

Story 3.4: etat poste caisse demarre (started_at, started_by_user_id).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, Sequence[str], None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cash_registers",
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "cash_registers",
        sa.Column(
            "started_by_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_cash_registers_started_by_user_id",
        "cash_registers",
        "users",
        ["started_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "idx_cash_registers_started_at",
        "cash_registers",
        ["started_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_cash_registers_started_at", table_name="cash_registers")
    op.drop_constraint(
        "fk_cash_registers_started_by_user_id",
        "cash_registers",
        type_="foreignkey",
    )
    op.drop_column("cash_registers", "started_by_user_id")
    op.drop_column("cash_registers", "started_at")
