"""create_preset_buttons_table

Revision ID: 004
Revises: 003
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, Sequence[str], None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "preset_buttons",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("preset_price", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("button_type", sa.String(64), nullable=False, server_default=sa.text("''")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
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
            ["category_id"], ["categories.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "idx_preset_buttons_category_id",
        "preset_buttons",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        "idx_preset_buttons_is_active",
        "preset_buttons",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        "idx_preset_buttons_sort_order",
        "preset_buttons",
        ["sort_order"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_preset_buttons_sort_order", table_name="preset_buttons")
    op.drop_index("idx_preset_buttons_is_active", table_name="preset_buttons")
    op.drop_index("idx_preset_buttons_category_id", table_name="preset_buttons")
    op.drop_table("preset_buttons")
