# Story 7.1 — tables mapping RecyClique -> Paheko (payment_method_mappings, category_mappings, location_mappings).
# Convention : snake_case pluriel, index idx_*.

"""mapping tables (story 7.1)

Revision ID: 2026_02_27_7_1
Revises: 2026_02_27_5_4
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "2026_02_27_7_1"
down_revision: Union[str, None] = "2026_02_27_5_4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payment_method_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recyclic_code", sa.String(64), nullable=False),
        sa.Column("paheko_id_method", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_payment_method_mappings_recyclic_code",
        "payment_method_mappings",
        ["recyclic_code"],
        unique=True,
    )
    op.create_index(
        "idx_payment_method_mappings_paheko_id_method",
        "payment_method_mappings",
        ["paheko_id_method"],
        unique=False,
    )

    op.create_table(
        "category_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paheko_category_id", sa.Integer(), nullable=True),
        sa.Column("paheko_code", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("category_id", name="uq_category_mappings_category_id"),
    )
    op.create_index(
        "idx_category_mappings_category_id",
        "category_mappings",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        "idx_category_mappings_paheko_category_id",
        "category_mappings",
        ["paheko_category_id"],
        unique=False,
    )
    op.create_index(
        "idx_category_mappings_paheko_code",
        "category_mappings",
        ["paheko_code"],
        unique=False,
    )

    op.create_table(
        "location_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("register_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("paheko_id_location", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["register_id"], ["cash_registers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "(site_id IS NOT NULL AND register_id IS NULL) OR (site_id IS NULL AND register_id IS NOT NULL)",
            name="ck_location_mappings_site_or_register",
        ),
    )
    op.create_index(
        "idx_location_mappings_site_id",
        "location_mappings",
        ["site_id"],
        unique=False,
    )
    op.create_index(
        "idx_location_mappings_register_id",
        "location_mappings",
        ["register_id"],
        unique=False,
    )
    op.create_index(
        "idx_location_mappings_paheko_id_location",
        "location_mappings",
        ["paheko_id_location"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_location_mappings_paheko_id_location", table_name="location_mappings")
    op.drop_index("idx_location_mappings_register_id", table_name="location_mappings")
    op.drop_index("idx_location_mappings_site_id", table_name="location_mappings")
    op.drop_table("location_mappings")
    op.drop_index("idx_category_mappings_paheko_code", table_name="category_mappings")
    op.drop_index("idx_category_mappings_paheko_category_id", table_name="category_mappings")
    op.drop_index("idx_category_mappings_category_id", table_name="category_mappings")
    op.drop_table("category_mappings")
    op.drop_index(
        "idx_payment_method_mappings_paheko_id_method",
        table_name="payment_method_mappings",
    )
    op.drop_index("idx_payment_method_mappings_recyclic_code", table_name="payment_method_mappings")
    op.drop_table("payment_method_mappings")
