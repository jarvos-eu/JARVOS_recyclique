"""create_users_auth_tables

Revision ID: 005
Revises: 004
Create Date: 2026-02-27

Tables: users, user_sessions, login_history, registration_request.
Alignement 1.4.4 + checklist-import-1.4.4 (copy + consolidate + security).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: Union[str, Sequence[str], None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(128), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("last_name", sa.String(128), nullable=True),
        sa.Column("role", sa.String(64), nullable=False, server_default=sa.text("'operator'")),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("pin_hash", sa.String(255), nullable=True),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="SET NULL"),
    )
    op.create_index("idx_users_username", "users", ["username"], unique=True)
    op.create_index("idx_users_email", "users", ["email"], unique=True)
    op.create_index("idx_users_status", "users", ["status"], unique=False)
    op.create_index("idx_users_site_id", "users", ["site_id"], unique=False)
    op.create_index("idx_users_role", "users", ["role"], unique=False)

    op.create_table(
        "user_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("refresh_token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_user_sessions_user_id", "user_sessions", ["user_id"], unique=False)
    op.create_index("idx_user_sessions_expires_at", "user_sessions", ["expires_at"], unique=False)

    op.create_table(
        "login_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("username", sa.String(128), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "logged_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("idx_login_history_user_id", "login_history", ["user_id"], unique=False)
    op.create_index("idx_login_history_logged_at", "login_history", ["logged_at"], unique=False)

    op.create_table(
        "registration_request",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(128), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("last_name", sa.String(128), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'pending'")),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "idx_registration_request_status",
        "registration_request",
        ["status"],
        unique=False,
    )
    op.create_index(
        "idx_registration_request_requested_at",
        "registration_request",
        ["requested_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_registration_request_requested_at", table_name="registration_request")
    op.drop_index("idx_registration_request_status", table_name="registration_request")
    op.drop_table("registration_request")

    op.drop_index("idx_login_history_logged_at", table_name="login_history")
    op.drop_index("idx_login_history_user_id", table_name="login_history")
    op.drop_table("login_history")

    op.drop_index("idx_user_sessions_expires_at", table_name="user_sessions")
    op.drop_index("idx_user_sessions_user_id", table_name="user_sessions")
    op.drop_table("user_sessions")

    op.drop_index("idx_users_role", table_name="users")
    op.drop_index("idx_users_site_id", table_name="users")
    op.drop_index("idx_users_status", table_name="users")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_index("idx_users_username", table_name="users")
    op.drop_table("users")
