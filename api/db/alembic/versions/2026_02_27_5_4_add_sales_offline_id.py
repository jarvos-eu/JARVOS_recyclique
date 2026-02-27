# Story 5.4 — colonne sales.offline_id (idempotence tickets hors ligne).
# Convention projet : api/db/alembic/versions/.

"""add sales.offline_id (story 5.4)

Revision ID: 2026_02_27_5_4
Revises: 2026_02_27_5_3
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "2026_02_27_5_4"
down_revision: Union[str, None] = "2026_02_27_5_3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sales",
        sa.Column(
            "offline_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="Idempotence: ticket cree hors ligne (Story 5.4)",
        ),
    )
    op.create_index(
        "ix_sales_offline_id",
        "sales",
        ["offline_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_sales_offline_id", table_name="sales")
    op.drop_column("sales", "offline_id")
