# Schémas API agrégats déclaratifs (Story 9.1). Read-only, snake_case, dates ISO 8601.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DeclarativeAggregateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    year: int
    quarter: int
    category_id: UUID | None
    flow_type: str
    weight_kg: float
    quantity: int
    created_at: datetime
    updated_at: datetime
