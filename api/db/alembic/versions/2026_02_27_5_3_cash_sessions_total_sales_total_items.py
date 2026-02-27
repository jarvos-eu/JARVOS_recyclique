# Story 5.3 — colonnes total_sales, total_items sur cash_sessions (audit 1.4.4).
# Convention projet : api/db/alembic/versions/.

"""add total_sales total_items to cash_sessions (story 5.3)

Revision ID: 2026_02_27_5_3
Revises: 2026_02_27_5_2
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "2026_02_27_5_3"
down_revision: Union[str, None] = "2026_02_27_5_2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cash_sessions",
        sa.Column("total_sales", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "cash_sessions",
        sa.Column("total_items", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cash_sessions", "total_items")
    op.drop_column("cash_sessions", "total_sales")
