# Modele Sale — table sales (Story 5.2, audit 1.4.4).
# Story 5.4 : offline_id optionnel pour idempotence (tickets crees hors ligne).
# Colonnes : id, cash_session_id, operator_id, total_amount, note, sale_date,
# donation (legacy), payment_method (legacy), offline_id, created_at, updated_at.
# Conventions : snake_case, montants en centimes, dates with timezone.

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cash_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cash_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    operator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )
    total_amount = Column(BigInteger, nullable=False, default=0)  # centimes
    note = Column(Text, nullable=True)
    sale_date = Column(DateTime(timezone=True), nullable=True)  # date reelle ticket (differee)
    donation = Column(BigInteger, nullable=True, default=0)  # legacy, centimes
    payment_method = Column(String(64), nullable=True)  # legacy / resume
    offline_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        unique=True,
        index=True,
        comment="Idempotence: ticket cree hors ligne (Story 5.4)",
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    cash_session = relationship("CashSession", back_populates="sales")
    operator = relationship("User", backref="sales_operated", foreign_keys=[operator_id])
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payment_transactions = relationship(
        "PaymentTransaction", back_populates="sale", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_sales_cash_session_id", "cash_session_id"),
        Index("idx_sales_operator_id", "operator_id"),
        Index("idx_sales_sale_date", "sale_date"),
    )
