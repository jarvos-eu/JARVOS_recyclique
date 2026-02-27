# Modele LigneDepot — table ligne_depot (Story 6.2).
# AC1 : id, ticket_id FK, poids_kg, category_id nullable FK, destination, notes nullable, is_exit, created_at, updated_at.
# Conventions : snake_case, noms 1.4.4 (audit-reception-poids-recyclic-1.4.4.md, schema-recyclic-dev.md).

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class LigneDepot(Base):
    __tablename__ = "ligne_depot"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ticket_depot.id", ondelete="CASCADE"),
        nullable=False,
    )
    poids_kg = Column(Numeric(12, 3), nullable=False)
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    destination = Column(String(64), nullable=False)  # enum metier (recyclage, revente, destruction, don, autre)
    notes = Column(Text, nullable=True)
    is_exit = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    ticket = relationship("TicketDepot", back_populates="lignes")
    category = relationship("Category", backref="lignes_depot", foreign_keys=[category_id])

    __table_args__ = (
        Index("idx_ligne_depot_ticket_id", "ticket_id"),
        Index("idx_ligne_depot_category_id", "category_id"),
    )
