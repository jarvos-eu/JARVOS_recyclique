# Modèle Site — table sites (RecyClique, Story 2.1).
# Colonnes : id, name, is_active, created_at, updated_at.
# Conventions : snake_case, timestamps with timezone.

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class Site(Base):
    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    cash_registers = relationship("CashRegister", back_populates="site", cascade="all, delete-orphan")
    cash_sessions = relationship("CashSession", back_populates="site")

    __table_args__ = (Index("idx_sites_is_active", "is_active"),)
