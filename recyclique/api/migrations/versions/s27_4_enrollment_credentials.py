"""Story 27.4 — credentials device + codes d'enrôlement.

Revision ID: s27_4_enrollment_credentials
Revises: s27_2_device_operator_sessions
Create Date: 2026-05-30

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "s27_4_enrollment_credentials"
down_revision = "s27_2_device_operator_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "registered_device_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("secret_hash", sa.String(length=255), nullable=False),
        sa.Column("secret_prefix", sa.String(length=8), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["registered_devices.id"],
            name="fk_registered_device_credentials_device_id",
        ),
    )
    op.create_index(
        "ix_registered_device_credentials_device_id",
        "registered_device_credentials",
        ["device_id"],
    )
    op.create_index(
        "ix_registered_device_credentials_status",
        "registered_device_credentials",
        ["status"],
    )
    op.create_index(
        "uq_registered_device_credentials_one_active",
        "registered_device_credentials",
        ["device_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
        sqlite_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "device_enrollment_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=12), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["registered_devices.id"],
            name="fk_device_enrollment_codes_device_id",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_device_enrollment_codes_created_by_user_id",
        ),
    )
    op.create_index(
        "ix_device_enrollment_codes_device_id",
        "device_enrollment_codes",
        ["device_id"],
    )
    op.create_index(
        "ix_device_enrollment_codes_code",
        "device_enrollment_codes",
        ["code"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_device_enrollment_codes_code", table_name="device_enrollment_codes")
    op.drop_index("ix_device_enrollment_codes_device_id", table_name="device_enrollment_codes")
    op.drop_table("device_enrollment_codes")
    op.drop_index(
        "uq_registered_device_credentials_one_active",
        table_name="registered_device_credentials",
    )
    op.drop_index(
        "ix_registered_device_credentials_status",
        table_name="registered_device_credentials",
    )
    op.drop_index(
        "ix_registered_device_credentials_device_id",
        table_name="registered_device_credentials",
    )
    op.drop_table("registered_device_credentials")
