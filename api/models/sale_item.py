# Modele SaleItem — table sale_items (Story 5.2, audit 1.4.4).
# Colonnes : id, sale_id, category_id, preset_id (nullable), quantity, unit_price,
# total_price, weight (nullable). Conventions : snake_case, montants centimes, poids kg.

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sales.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    preset_id = Column(
        UUID(as_uuid=True),
        ForeignKey("preset_buttons.id", ondelete="SET NULL"),
        nullable=True,
    )
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(BigInteger, nullable=False, default=0)  # centimes
    total_price = Column(BigInteger, nullable=False, default=0)  # centimes
    weight = Column(Float, nullable=True)  # kg
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    sale = relationship("Sale", back_populates="items")
    category = relationship("Category", backref="sale_items")
    preset = relationship("PresetButton", backref="sale_items")

    __table_args__ = (
        Index("idx_sale_items_sale_id", "sale_id"),
        Index("idx_sale_items_category_id", "category_id"),
        Index("idx_sale_items_preset_id", "preset_id"),
    )
