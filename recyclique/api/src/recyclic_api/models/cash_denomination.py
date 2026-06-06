"""Story 9.11 — référentiel dénominations EUR et comptage par session."""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from recyclic_api.core.database import Base


class CashDenomination(Base):
    """Référentiel national des 15 dénominations EUR (seed migration)."""

    __tablename__ = "cash_denominations"

    code = Column(String(16), primary_key=True)
    label_fr = Column(String(32), nullable=False)
    kind = Column(String(8), nullable=False)  # coin | note
    unit_value_cents = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=False)
    display_default = Column(Integer, nullable=False, default=1, server_default="1")


class CashDenominationCount(Base):
    """Quantités comptées par dénomination pour une session ouverte."""

    __tablename__ = "cash_denomination_counts"
    __table_args__ = (
        UniqueConstraint(
            "cash_session_id",
            "denomination_code",
            name="uq_cash_denomination_counts_session_code",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cash_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cash_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    denomination_code = Column(
        String(16),
        ForeignKey("cash_denominations.code", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False, default=0, server_default="0")
    unit_value_cents = Column(Integer, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    recorded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
