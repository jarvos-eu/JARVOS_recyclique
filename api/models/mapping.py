# Modeles mapping RecyClique -> Paheko (Story 7.1).
# Tables : payment_method_mappings, category_mappings, location_mappings.
# Conventions : snake_case, index idx_*, config Paheko = reference (NFR-I2).

import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class PaymentMethodMapping(Base):
    """Mapping code moyen de paiement RecyClique -> id_method Paheko (plugin_pos_methods.id)."""

    __tablename__ = "payment_method_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recyclic_code = Column(String(64), nullable=False, unique=True)  # ex. especes, cheque, cb
    paheko_id_method = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (Index("idx_payment_method_mappings_recyclic_code", "recyclic_code"),)


class CategoryMapping(Base):
    """Mapping category RecyClique (categories.id) -> plugin_pos_categories (id ou code)."""

    __tablename__ = "category_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    paheko_category_id = Column(Integer, nullable=True)
    paheko_code = Column(String(128), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category = relationship("Category", backref="paheko_mapping")

    __table_args__ = (Index("idx_category_mappings_category_id", "category_id"),)


class LocationMapping(Base):
    """Mapping site ou poste caisse RecyClique -> plugin_pos_locations.id Paheko. Exactement un de site_id ou register_id."""

    __tablename__ = "location_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=True,
    )
    register_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cash_registers.id", ondelete="CASCADE"),
        nullable=True,
    )
    paheko_id_location = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    site = relationship("Site", backref="paheko_location_mappings")
    register = relationship("CashRegister", backref="paheko_location_mappings")

    __table_args__ = (
        Index("idx_location_mappings_site_id", "site_id"),
        Index("idx_location_mappings_register_id", "register_id"),
        Index("idx_location_mappings_paheko_id_location", "paheko_id_location"),
        CheckConstraint(
            "(site_id IS NOT NULL AND register_id IS NULL) OR (site_id IS NULL AND register_id IS NOT NULL)",
            name="ck_location_mappings_site_or_register",
        ),
    )
