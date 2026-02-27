# Schemas Pydantic — Mapping RecyClique -> Paheko (Story 7.1). snake_case, reponses { "detail": "..." }.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ----- Payment method mapping -----


class PaymentMethodMappingBase(BaseModel):
    recyclic_code: str = Field(..., min_length=1, max_length=64)
    paheko_id_method: int = Field(..., ge=0)


class PaymentMethodMappingCreate(PaymentMethodMappingBase):
    pass


class PaymentMethodMappingUpdate(BaseModel):
    paheko_id_method: int | None = Field(None, ge=0)


class PaymentMethodMappingResponse(PaymentMethodMappingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ----- Category mapping -----


class CategoryMappingBase(BaseModel):
    category_id: UUID
    paheko_category_id: int | None = Field(None, ge=0)
    paheko_code: str | None = Field(None, max_length=128)


class CategoryMappingCreate(BaseModel):
    category_id: UUID
    paheko_category_id: int | None = Field(None, ge=0)
    paheko_code: str | None = Field(None, max_length=128)


class CategoryMappingUpdate(BaseModel):
    paheko_category_id: int | None = Field(None, ge=0)
    paheko_code: str | None = Field(None, max_length=128)


class CategoryMappingResponse(BaseModel):
    id: UUID
    category_id: UUID
    paheko_category_id: int | None
    paheko_code: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ----- Location mapping -----


class LocationMappingBase(BaseModel):
    site_id: UUID | None = None
    register_id: UUID | None = None
    paheko_id_location: int = Field(..., ge=0)


class LocationMappingCreate(BaseModel):
    site_id: UUID | None = None
    register_id: UUID | None = None
    paheko_id_location: int = Field(..., ge=0)


class LocationMappingUpdate(BaseModel):
    paheko_id_location: int | None = Field(None, ge=0)


class LocationMappingResponse(BaseModel):
    id: UUID
    site_id: UUID | None
    register_id: UUID | None
    paheko_id_location: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
