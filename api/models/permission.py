# Modèle Permission — table permissions (RecyClique, Story 3.2).
# Codes de permission (ex. caisse.access, reception.access, admin).
# Conventions : snake_case, timestamps with timezone.

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(128), nullable=False, unique=True)
    label = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    groups = relationship(
        "Group",
        secondary="group_permissions",
        back_populates="permissions",
    )

    __table_args__ = (Index("idx_permissions_code", "code", unique=True),)
