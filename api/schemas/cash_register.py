# Schemas Pydantic — Cash registers (Story 2.2). Requêtes/réponses en snake_case.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CashRegisterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location: str | None = Field(None, max_length=255)
    is_active: bool = True
    enable_virtual: bool = False
    enable_deferred: bool = False


class CashRegisterCreate(CashRegisterBase):
    site_id: UUID


class CashRegisterUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    location: str | None = Field(None, max_length=255)
    is_active: bool | None = None
    enable_virtual: bool | None = None
    enable_deferred: bool | None = None


class CashRegisterResponse(CashRegisterBase):
    id: UUID
    site_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CashRegisterStatusItem(BaseModel):
    """Un poste avec son statut (libre/occupé). En v1 sans cash_sessions : toujours libre."""

    register_id: UUID
    status: str = Field(..., description="free | occupied")
