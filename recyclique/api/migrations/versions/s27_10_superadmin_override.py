"""Story 27.10 — colonne override_started_at pour TTL override SuperAdmin.

Revision ID: s27_10_superadmin_override
Revises: s27_8_poste_reception_registered_device
Create Date: 2026-05-30

"""

from alembic import op
import sqlalchemy as sa

revision = "s27_10_superadmin_override"
down_revision = "s27_8_poste_reception_registered_device"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "device_operator_sessions",
        sa.Column("override_started_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("device_operator_sessions", "override_started_at")
