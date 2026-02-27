"""create_audit_events_table

Revision ID: 006
Revises: 005
Create Date: 2026-02-27

Table audit_events — Story 3.3, architecture § Audit log.
Colonnes: id, timestamp, user_id, action, resource_type, resource_id, details.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, Sequence[str], None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=True),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("idx_audit_events_timestamp", "audit_events", ["timestamp"], unique=False)
    op.create_index("idx_audit_events_user_id", "audit_events", ["user_id"], unique=False)
    op.create_index("idx_audit_events_action", "audit_events", ["action"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_audit_events_action", table_name="audit_events")
    op.drop_index("idx_audit_events_user_id", table_name="audit_events")
    op.drop_index("idx_audit_events_timestamp", table_name="audit_events")
    op.drop_table("audit_events")
