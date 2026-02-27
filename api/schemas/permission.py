# Schemas Pydantic — Permission (Story 3.2). Admin CRUD permissions.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=128)
    label: str | None = Field(None, max_length=255)


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    code: str | None = Field(None, min_length=1, max_length=128)
    label: str | None = Field(None, max_length=255)


class PermissionResponse(PermissionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
