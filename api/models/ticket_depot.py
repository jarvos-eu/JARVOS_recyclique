# Modele TicketDepot — table ticket_depot (Story 6.1).
# AC2/3 : id, poste_id FK, benevole_user_id FK users, created_at, closed_at nullable, status = 'opened', updated_at.
# Conventions : snake_case, noms 1.4.4 (audit-reception-poids-recyclic-1.4.4.md).

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class TicketDepot(Base):
    __tablename__ = "ticket_depot"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    poste_id = Column(
        UUID(as_uuid=True),
        ForeignKey("poste_reception.id", ondelete="CASCADE"),
        nullable=False,
    )
    benevole_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    closed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), nullable=False, default="opened")
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    poste = relationship("PosteReception", back_populates="tickets")
    benevole_user = relationship("User", backref="tickets_depot", foreign_keys=[benevole_user_id])
    lignes = relationship("LigneDepot", back_populates="ticket", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_ticket_depot_poste_id", "poste_id"),
        Index("idx_ticket_depot_benevole_user_id", "benevole_user_id"),
    )
