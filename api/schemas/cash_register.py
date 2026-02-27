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


class CashRegisterStartRequest(BaseModel):
    """Body pour POST /v1/admin/cash-registers/start (Story 3.4)."""

    site_id: UUID
    register_id: UUID


class CashRegisterResponse(CashRegisterBase):
    id: UUID
    site_id: UUID
    started_at: datetime | None = None
    started_by_user_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CashRegisterStatusItem(BaseModel):
    """Un poste avec son statut (libre/occupé). Inclut started_at / started_by si démarré (Story 3.4)."""

    register_id: UUID
    status: str = Field(..., description="free | started")
    started_at: datetime | None = None
    started_by_user_id: UUID | None = None
