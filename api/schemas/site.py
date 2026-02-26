# Schemas Pydantic — Sites (Story 2.1). Réponses et requêtes en snake_case.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SiteBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True


class SiteCreate(SiteBase):
    pass


class SiteUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    is_active: bool | None = None


class SiteResponse(SiteBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
