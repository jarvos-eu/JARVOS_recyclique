# Modele CashRegister — table cash_registers (RecyClique, Story 2.2).
# Colonnes : id, site_id (FK sites), name, location, is_active, enable_virtual, enable_deferred, created_at, updated_at.
# Conventions : snake_case, timestamps with timezone.

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class CashRegister(Base):
    __tablename__ = "cash_registers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    enable_virtual = Column(Boolean, nullable=False, default=False)
    enable_deferred = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    site = relationship("Site", back_populates="cash_registers")

    __table_args__ = (
        Index("idx_cash_registers_site_id", "site_id"),
        Index("idx_cash_registers_is_active", "is_active"),
    )
