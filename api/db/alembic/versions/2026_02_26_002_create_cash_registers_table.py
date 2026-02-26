"""create_cash_registers_table

Revision ID: 002
Revises: 001
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cash_registers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("enable_virtual", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("enable_deferred", sa.Boolean(), nullable=False, server_default=sa.false()),
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
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "idx_cash_registers_site_id", "cash_registers", ["site_id"], unique=False
    )
    op.create_index(
        "idx_cash_registers_is_active", "cash_registers", ["is_active"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_cash_registers_is_active", table_name="cash_registers")
    op.drop_index("idx_cash_registers_site_id", table_name="cash_registers")
    op.drop_table("cash_registers")
