# Schemas Pydantic — Group (Story 3.2). Admin CRUD groupes.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = Field(None, max_length=512)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = Field(None, max_length=512)


class GroupResponse(GroupBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GroupDetailResponse(GroupResponse):
    permission_ids: list[UUID] = []
    user_ids: list[UUID] = []


class GroupPermissionsBody(BaseModel):
    permission_id: UUID | None = None
    permission_ids: list[UUID] = Field(default_factory=list, max_length=100)


class GroupUsersBody(BaseModel):
    user_id: UUID | None = None
    user_ids: list[UUID] = Field(default_factory=list, max_length=100)
