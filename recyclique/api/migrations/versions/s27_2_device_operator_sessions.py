"""Story 27.2 — table device_operator_sessions (session opérateur poste partagé).

Revision ID: s27_2_device_operator_sessions
Revises: s27_1_registered_devices
Create Date: 2026-05-30

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "s27_2_device_operator_sessions"
down_revision = "s27_1_registered_devices"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "device_operator_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operator_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("active_module_key", sa.String(length=64), nullable=True),
        sa.Column(
            "override_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "last_activity_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["registered_devices.id"],
            name="fk_device_operator_sessions_device_id",
        ),
        sa.ForeignKeyConstraint(
            ["operator_user_id"],
            ["users.id"],
            name="fk_device_operator_sessions_operator_user_id",
        ),
        sa.ForeignKeyConstraint(
            ["site_id"],
            ["sites.id"],
            name="fk_device_operator_sessions_site_id",
        ),
    )
    op.create_index(
        "ix_device_operator_sessions_device_id",
        "device_operator_sessions",
        ["device_id"],
    )
    op.create_index(
        "ix_device_operator_sessions_operator_user_id",
        "device_operator_sessions",
        ["operator_user_id"],
    )
    op.create_index(
        "ix_device_operator_sessions_site_id",
        "device_operator_sessions",
        ["site_id"],
    )
    op.create_index(
        "ix_device_operator_sessions_status",
        "device_operator_sessions",
        ["status"],
    )
    # Une seule session active par device (Postgres).
    op.create_index(
        "uq_device_operator_sessions_active_device",
        "device_operator_sessions",
        ["device_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_device_operator_sessions_active_device",
        table_name="device_operator_sessions",
    )
    op.drop_index(
        "ix_device_operator_sessions_status",
        table_name="device_operator_sessions",
    )
    op.drop_index(
        "ix_device_operator_sessions_site_id",
        table_name="device_operator_sessions",
    )
    op.drop_index(
        "ix_device_operator_sessions_operator_user_id",
        table_name="device_operator_sessions",
    )
    op.drop_index(
        "ix_device_operator_sessions_device_id",
        table_name="device_operator_sessions",
    )
    op.drop_table("device_operator_sessions")
