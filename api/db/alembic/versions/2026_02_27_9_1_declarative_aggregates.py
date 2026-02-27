# Story 9.1 — table declarative_aggregates (agrégats déclaratifs éco-organismes).
# Tables additives uniquement ; conventions snake_case, index idx_{table}_{colonne}.

"""declarative_aggregates (story 9.1)

Revision ID: 2026_02_27_9_1
Revises: 2026_02_27_7_1
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "2026_02_27_9_1"
down_revision: Union[str, None] = "2026_02_27_7_1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "declarative_aggregates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("quarter", sa.Integer(), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("flow_type", sa.String(32), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "year", "quarter", "category_id", "flow_type",
            name="uq_declarative_aggregates_period_category_flow",
        ),
    )
    op.create_index(
        "idx_declarative_aggregates_year_quarter",
        "declarative_aggregates",
        ["year", "quarter"],
        unique=False,
    )
    op.create_index(
        "idx_declarative_aggregates_category_id",
        "declarative_aggregates",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        "idx_declarative_aggregates_flow_type",
        "declarative_aggregates",
        ["flow_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_declarative_aggregates_flow_type", table_name="declarative_aggregates")
    op.drop_index("idx_declarative_aggregates_category_id", table_name="declarative_aggregates")
    op.drop_index("idx_declarative_aggregates_year_quarter", table_name="declarative_aggregates")
    op.drop_table("declarative_aggregates")
