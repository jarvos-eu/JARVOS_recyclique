# Story 5.1 — table cash_sessions (ouverture/fermeture session caisse).
# Colonnes alignées sur api/models/cash_session.py et audit 1.4.4.

"""add cash_sessions table (story 5.1)

Revision ID: 2026_02_27_5_1
Revises: 008
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2026_02_27_5_1"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cash_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("register_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("initial_amount", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("current_amount", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_step", sa.String(32), nullable=False, server_default="entry"),
        sa.Column("closing_amount", sa.BigInteger(), nullable=True),
        sa.Column("actual_amount", sa.BigInteger(), nullable=True),
        sa.Column("variance", sa.BigInteger(), nullable=True),
        sa.Column("variance_comment", sa.Text(), nullable=True),
        sa.Column("session_type", sa.String(32), nullable=False, server_default="real"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["operator_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["register_id"],
            ["cash_registers.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["site_id"],
            ["sites.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "idx_cash_sessions_register_id",
        "cash_sessions",
        ["register_id"],
        unique=False,
    )
    op.create_index(
        "idx_cash_sessions_operator_id",
        "cash_sessions",
        ["operator_id"],
        unique=False,
    )
    op.create_index(
        "idx_cash_sessions_status",
        "cash_sessions",
        ["status"],
        unique=False,
    )
    op.create_index(
        "idx_cash_sessions_opened_at",
        "cash_sessions",
        ["opened_at"],
        unique=False,
    )
    op.create_index(
        "idx_cash_sessions_site_id",
        "cash_sessions",
        ["site_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_cash_sessions_site_id", table_name="cash_sessions")
    op.drop_index("idx_cash_sessions_opened_at", table_name="cash_sessions")
    op.drop_index("idx_cash_sessions_status", table_name="cash_sessions")
    op.drop_index("idx_cash_sessions_operator_id", table_name="cash_sessions")
    op.drop_index("idx_cash_sessions_register_id", table_name="cash_sessions")
    op.drop_table("cash_sessions")
