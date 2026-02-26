# Schemas Pydantic — Presets (boutons rapides caisse, Story 2.4). Requêtes/réponses en snake_case.
# button_type : Don, Recyclage, Decheterie, etc. (1.4.4). preset_price en centimes.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PresetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category_id: UUID | None = None
    preset_price: int = Field(0, ge=0, description="Prix prédéfini en centimes")
    button_type: str = Field("", max_length=64)
    sort_order: int = 0
    is_active: bool = True


class PresetCreate(PresetBase):
    pass


class PresetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    category_id: UUID | None = None
    preset_price: int | None = Field(None, ge=0)
    button_type: str | None = Field(None, max_length=64)
    sort_order: int | None = None
    is_active: bool | None = None


class PresetResponse(PresetBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
