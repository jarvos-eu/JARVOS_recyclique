"""Story 27.1 — table registered_devices (postes partagés enrôlés).

Revision ID: s27_1_registered_devices
Revises: s9_10_cash_variance_accounts
Create Date: 2026-05-30

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "s27_1_registered_devices"
down_revision = "s9_10_cash_variance_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "registered_devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("device_type", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("allowed_module_keys", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("inactivity_timeout_seconds", sa.Integer(), nullable=True),
        sa.Column("last_contact_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["site_id"],
            ["sites.id"],
            name="fk_registered_devices_site_id_sites",
        ),
    )
    op.create_index(
        "ix_registered_devices_device_type",
        "registered_devices",
        ["device_type"],
    )
    op.create_index(
        "ix_registered_devices_name",
        "registered_devices",
        ["name"],
    )
    op.create_index(
        "ix_registered_devices_site_id",
        "registered_devices",
        ["site_id"],
    )
    op.create_index(
        "ix_registered_devices_status",
        "registered_devices",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index("ix_registered_devices_status", table_name="registered_devices")
    op.drop_index("ix_registered_devices_site_id", table_name="registered_devices")
    op.drop_index("ix_registered_devices_name", table_name="registered_devices")
    op.drop_index("ix_registered_devices_device_type", table_name="registered_devices")
    op.drop_table("registered_devices")
