# Modèle Group — table groups (RecyClique, Story 3.2).
# Groupes RBAC (ex. opérateur caisse, admin technique).
# Conventions : snake_case, timestamps with timezone.

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


# Tables d'association many-to-many (snake_case, idx_*)
user_groups = Table(
    "user_groups",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    Index("idx_user_groups_user_id", "user_id"),
    Index("idx_user_groups_group_id", "group_id"),
)

group_permissions = Table(
    "group_permissions",
    Base.metadata,
    Column("group_id", UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    Index("idx_group_permissions_group_id", "group_id"),
    Index("idx_group_permissions_permission_id", "permission_id"),
)


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    users = relationship(
        "User",
        secondary=user_groups,
        back_populates="groups",
    )
    permissions = relationship(
        "Permission",
        secondary=group_permissions,
        back_populates="groups",
    )

    __table_args__ = (Index("idx_groups_name", "name", unique=True),)
