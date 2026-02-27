# Modèle déclaratif — agrégats par période/catégorie/flux (Story 9.1).
# Table additive : ne modifie pas sales, sale_items, ligne_depot, categories.
# Sources : sale_items (weight, category_id; période depuis sales.sale_date/created_at),
#           ligne_depot (poids_kg, category_id; période depuis created_at/ticket).
# Périodes : trimestres T1–T4 (year + quarter). Conventions : snake_case, index idx_{table}_{colonne}.

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.models.base import Base


class DeclarativeAggregate(Base):
    """Agrégats déclaratifs par période (trimestre), catégorie et flux (caisse / réception)."""

    __tablename__ = "declarative_aggregates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)  # 1-4 (T1–T4)
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    flow_type = Column(String(32), nullable=False)  # 'caisse' | 'reception'
    weight_kg = Column(Float, nullable=False, default=0.0)
    quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category = relationship("Category", backref="declarative_aggregates")

    __table_args__ = (
        UniqueConstraint(
            "year", "quarter", "category_id", "flow_type",
            name="uq_declarative_aggregates_period_category_flow",
        ),
        Index("idx_declarative_aggregates_year_quarter", "year", "quarter"),
        Index("idx_declarative_aggregates_category_id", "category_id"),
        Index("idx_declarative_aggregates_flow_type", "flow_type"),
    )
