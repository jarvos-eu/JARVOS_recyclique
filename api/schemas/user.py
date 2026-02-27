# Schemas Pydantic — User / profil (Story 3.1). GET/PUT /v1/users/me, password, PIN.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserMeResponse(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    role: str
    status: str
    site_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserMeUpdate(BaseModel):
    first_name: str | None = Field(None, max_length=128)
    last_name: str | None = Field(None, max_length=128)
    email: str | None = Field(None, min_length=1)


class UserMePasswordUpdate(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class UserMePinUpdate(BaseModel):
    new_pin: str = Field(..., min_length=4, max_length=8)
