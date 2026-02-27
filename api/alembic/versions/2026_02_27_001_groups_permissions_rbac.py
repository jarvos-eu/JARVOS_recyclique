"""Groupes, permissions et tables association RBAC (Story 3.2).

Revision ID: 001
Revises:
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(128), nullable=False),
        sa.Column("label", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_permissions_code", "permissions", ["code"], unique=True)

    op.create_table(
        "groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_groups_name", "groups", ["name"], unique=True)

    op.create_table(
        "user_groups",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "group_id"),
    )
    op.create_index("idx_user_groups_user_id", "user_groups", ["user_id"], unique=False)
    op.create_index("idx_user_groups_group_id", "user_groups", ["group_id"], unique=False)

    op.create_table(
        "group_permissions",
        sa.Column("group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("group_id", "permission_id"),
    )
    op.create_index("idx_group_permissions_group_id", "group_permissions", ["group_id"], unique=False)
    op.create_index("idx_group_permissions_permission_id", "group_permissions", ["permission_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_group_permissions_permission_id", table_name="group_permissions")
    op.drop_index("idx_group_permissions_group_id", table_name="group_permissions")
    op.drop_table("group_permissions")
    op.drop_index("idx_user_groups_group_id", table_name="user_groups")
    op.drop_index("idx_user_groups_user_id", table_name="user_groups")
    op.drop_table("user_groups")
    op.drop_index("idx_groups_name", table_name="groups")
    op.drop_table("groups")
    op.drop_index("idx_permissions_code", table_name="permissions")
    op.drop_table("permissions")
