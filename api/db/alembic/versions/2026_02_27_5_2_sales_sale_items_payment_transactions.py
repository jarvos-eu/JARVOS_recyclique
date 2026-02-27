# Story 5.2 — tables sales, sale_items, payment_transactions (migration 1.4.4).
# Convention projet : api/db/alembic/versions/.

"""sales, sale_items, payment_transactions (story 5.2)

Revision ID: 2026_02_27_5_2
Revises: 2026_02_27_5_1
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "2026_02_27_5_2"
down_revision: Union[str, None] = "2026_02_27_5_1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sales",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cash_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_amount", sa.BigInteger(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("sale_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("donation", sa.BigInteger(), nullable=True),
        sa.Column("payment_method", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["cash_session_id"], ["cash_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operator_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_sales_cash_session_id", "sales", ["cash_session_id"], unique=False)
    op.create_index("idx_sales_operator_id", "sales", ["operator_id"], unique=False)
    op.create_index("idx_sales_sale_date", "sales", ["sale_date"], unique=False)

    op.create_table(
        "sale_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sale_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("preset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.BigInteger(), nullable=False),
        sa.Column("total_price", sa.BigInteger(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["preset_id"], ["preset_buttons.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_sale_items_sale_id", "sale_items", ["sale_id"], unique=False)
    op.create_index("idx_sale_items_category_id", "sale_items", ["category_id"], unique=False)
    op.create_index("idx_sale_items_preset_id", "sale_items", ["preset_id"], unique=False)

    op.create_table(
        "payment_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sale_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_method", sa.String(64), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_payment_transactions_sale_id", "payment_transactions", ["sale_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_payment_transactions_sale_id", table_name="payment_transactions")
    op.drop_table("payment_transactions")
    op.drop_index("idx_sale_items_preset_id", table_name="sale_items")
    op.drop_index("idx_sale_items_category_id", table_name="sale_items")
    op.drop_index("idx_sale_items_sale_id", table_name="sale_items")
    op.drop_table("sale_items")
    op.drop_index("idx_sales_sale_date", table_name="sales")
    op.drop_index("idx_sales_operator_id", table_name="sales")
    op.drop_index("idx_sales_cash_session_id", table_name="sales")
    op.drop_table("sales")
