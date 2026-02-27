# Modèle User — table users (RecyClique, Story 3.1).
# Utilisateurs terrain : profil, role, status, pin_hash, site_id.
# Conventions : snake_case, timestamps with timezone.

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base
from api.models.group import user_groups


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(128), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    role = Column(String(64), nullable=False, default="operator")
    status = Column(String(32), nullable=False, default="pending")
    pin_hash = Column(String(255), nullable=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    site = relationship("Site", backref="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    groups = relationship("Group", secondary=user_groups, back_populates="users")

    __table_args__ = (
        Index("idx_users_username", "username", unique=True),
        Index("idx_users_email", "email", unique=True),
        Index("idx_users_status", "status"),
        Index("idx_users_site_id", "site_id"),
        Index("idx_users_role", "role"),
    )
