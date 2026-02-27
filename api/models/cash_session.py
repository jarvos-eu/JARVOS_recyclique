# Modele CashSession — table cash_sessions (Story 5.1, audit 1.4.4).
# Colonnes : id, operator_id, register_id, site_id, initial_amount, current_amount, status,
# opened_at, closed_at, current_step, closing_amount, actual_amount, variance, variance_comment,
# session_type, created_at, updated_at.
# Conventions : snake_case, montants en centimes, dates with timezone.

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class CashSession(Base):
    __tablename__ = "cash_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )
    register_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cash_registers.id", ondelete="CASCADE"),
        nullable=False,
    )
    site_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    initial_amount = Column(BigInteger, nullable=False, default=0)  # centimes
    current_amount = Column(BigInteger, nullable=False, default=0)  # centimes
    status = Column(String(32), nullable=False, default="open")  # open | closed
    opened_at = Column(DateTime(timezone=True), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    current_step = Column(String(32), nullable=False, default="entry")  # entry | sale | exit
    closing_amount = Column(BigInteger, nullable=True)  # centimes
    actual_amount = Column(BigInteger, nullable=True)  # centimes
    variance = Column(BigInteger, nullable=True)  # centimes (actual - closing)
    variance_comment = Column(Text, nullable=True)
    session_type = Column(String(32), nullable=False, default="real")  # real | virtual | deferred
    total_sales = Column(BigInteger, nullable=True)  # centimes, somme ventes session (Story 5.3)
    total_items = Column(Integer, nullable=True)  # nombre de lignes (sale_items) session (Story 5.3)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    operator = relationship("User", backref="cash_sessions_operated", foreign_keys=[operator_id])
    register = relationship("CashRegister", back_populates="cash_sessions")
    site = relationship("Site", back_populates="cash_sessions")
    sales = relationship("Sale", back_populates="cash_session", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_cash_sessions_register_id", "register_id"),
        Index("idx_cash_sessions_operator_id", "operator_id"),
        Index("idx_cash_sessions_status", "status"),
        Index("idx_cash_sessions_opened_at", "opened_at"),
        Index("idx_cash_sessions_site_id", "site_id"),
    )
