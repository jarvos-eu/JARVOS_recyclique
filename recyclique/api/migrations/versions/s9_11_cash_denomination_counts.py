"""Story 9.11 — tables cash_denominations (seed 15) et cash_denomination_counts.

Revision ID: s9_11_cash_denomination_counts
Revises: s27_10_superadmin_override
Create Date: 2026-06-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "s9_11_cash_denomination_counts"
down_revision = "s27_10_superadmin_override"
branch_labels = None
depends_on = None

_DENOMINATIONS = [
    ("EUR_50000", "500 €", "note", 50000, 1, 0),
    ("EUR_20000", "200 €", "note", 20000, 2, 1),
    ("EUR_10000", "100 €", "note", 10000, 3, 1),
    ("EUR_5000", "50 €", "note", 5000, 4, 1),
    ("EUR_2000", "20 €", "note", 2000, 5, 1),
    ("EUR_1000", "10 €", "note", 1000, 6, 1),
    ("EUR_500", "5 €", "note", 500, 7, 1),
    ("EUR_200", "2 €", "coin", 200, 8, 1),
    ("EUR_100", "1 €", "coin", 100, 9, 1),
    ("EUR_050", "50 c", "coin", 50, 10, 1),
    ("EUR_020", "20 c", "coin", 20, 11, 1),
    ("EUR_010", "10 c", "coin", 10, 12, 1),
    ("EUR_005", "5 c", "coin", 5, 13, 1),
    ("EUR_002", "2 c", "coin", 2, 14, 1),
    ("EUR_001", "1 c", "coin", 1, 15, 1),
]


def upgrade() -> None:
    op.create_table(
        "cash_denominations",
        sa.Column("code", sa.String(length=16), primary_key=True),
        sa.Column("label_fr", sa.String(length=32), nullable=False),
        sa.Column("kind", sa.String(length=8), nullable=False),
        sa.Column("unit_value_cents", sa.Integer(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("display_default", sa.Integer(), nullable=False, server_default="1"),
    )

    denom_table = sa.table(
        "cash_denominations",
        sa.column("code", sa.String),
        sa.column("label_fr", sa.String),
        sa.column("kind", sa.String),
        sa.column("unit_value_cents", sa.Integer),
        sa.column("display_order", sa.Integer),
        sa.column("display_default", sa.Integer),
    )
    op.bulk_insert(
        denom_table,
        [
            {
                "code": code,
                "label_fr": label,
                "kind": kind,
                "unit_value_cents": cents,
                "display_order": order,
                "display_default": display_default,
            }
            for code, label, kind, cents, order, display_default in _DENOMINATIONS
        ],
    )

    op.create_table(
        "cash_denomination_counts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("cash_session_id", sa.UUID(), nullable=False),
        sa.Column("site_id", sa.UUID(), nullable=False),
        sa.Column("denomination_code", sa.String(length=16), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unit_value_cents", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("recorded_by_user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["cash_session_id"], ["cash_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["denomination_code"], ["cash_denominations.code"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recorded_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "cash_session_id",
            "denomination_code",
            name="uq_cash_denomination_counts_session_code",
        ),
    )
    op.create_index(
        "ix_cash_denomination_counts_cash_session_id",
        "cash_denomination_counts",
        ["cash_session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_cash_denomination_counts_cash_session_id", table_name="cash_denomination_counts")
    op.drop_table("cash_denomination_counts")
    op.drop_table("cash_denominations")
