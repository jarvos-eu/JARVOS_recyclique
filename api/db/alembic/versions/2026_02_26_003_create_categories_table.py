"""create_categories_table

Revision ID: 003
Revises: 002
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, Sequence[str], None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("official_name", sa.String(512), nullable=True),
        sa.Column("is_visible_sale", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_visible_reception", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("display_order_entry", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["parent_id"], ["categories.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "idx_categories_parent_id", "categories", ["parent_id"], unique=False
    )
    op.create_index(
        "idx_categories_deleted_at", "categories", ["deleted_at"], unique=False
    )
    op.create_index(
        "idx_categories_is_visible_sale", "categories", ["is_visible_sale"], unique=False
    )
    op.create_index(
        "idx_categories_is_visible_reception", "categories", ["is_visible_reception"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_categories_is_visible_reception", table_name="categories")
    op.drop_index("idx_categories_is_visible_sale", table_name="categories")
    op.drop_index("idx_categories_deleted_at", table_name="categories")
    op.drop_index("idx_categories_parent_id", table_name="categories")
    op.drop_table("categories")
