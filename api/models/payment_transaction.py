# Modele PaymentTransaction — table payment_transactions (Story 5.2, audit 1.4.4).
# Paiements multi-moyens par vente : sale_id, payment_method, amount (centimes).

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sales.id", ondelete="CASCADE"),
        nullable=False,
    )
    payment_method = Column(String(64), nullable=False)  # especes, cheque, etc.
    amount = Column(BigInteger, nullable=False)  # centimes
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    sale = relationship("Sale", back_populates="payment_transactions")

    __table_args__ = (Index("idx_payment_transactions_sale_id", "sale_id"),)
