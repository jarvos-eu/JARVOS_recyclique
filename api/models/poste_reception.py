# Modele PosteReception — table poste_reception (Story 3.4, 6.1).
# AC1/5 : id, opened_by_user_id, opened_at, closed_at nullable, status = 'opened', created_at, updated_at.
# Conventions : snake_case, noms 1.4.4 (audit-reception-poids-recyclic-1.4.4.md).

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class PosteReception(Base):
    __tablename__ = "poste_reception"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    opened_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    opened_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), nullable=False, default="opened")
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    opened_by_user = relationship("User", backref="opened_reception_posts", foreign_keys=[opened_by_user_id])
    tickets = relationship("TicketDepot", back_populates="poste", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_poste_reception_opened_by_user_id", "opened_by_user_id"),
        Index("idx_poste_reception_status", "status"),
    )
