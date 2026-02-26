# Modele PresetButton — table preset_buttons (RecyClique, Story 2.4).
# Boutons rapides caisse : name, category_id (FK nullable), preset_price (centimes),
# button_type (Don, Recyclage, Decheterie, etc.), sort_order, is_active.
# Conventions : snake_case, timestamps with timezone.

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class PresetButton(Base):
    __tablename__ = "preset_buttons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    preset_price = Column(Integer, nullable=False, default=0)  # centimes
    button_type = Column(String(64), nullable=False, default="")
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category = relationship("Category", backref="preset_buttons")

    __table_args__ = (
        Index("idx_preset_buttons_category_id", "category_id"),
        Index("idx_preset_buttons_is_active", "is_active"),
        Index("idx_preset_buttons_sort_order", "sort_order"),
    )
