# Schemas Pydantic — Sales (Story 5.2). Montants en centimes, snake_case, poids en kg.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SaleItemCreate(BaseModel):
    """Une ligne de vente (body POST /v1/sales)."""

    category_id: UUID | None = None
    preset_id: UUID | None = None
    quantity: int = Field(1, ge=1)
    unit_price: int | None = Field(None, ge=0, description="Centimes (optionnel si total_price)")
    total_price: int | None = Field(None, ge=0, description="Centimes (optionnel si unit_price)")
    weight: float | None = Field(None, ge=0, description="Poids en kg")


class PaymentCreate(BaseModel):
    """Un paiement (body POST /v1/sales)."""

    payment_method: str = Field(..., min_length=1, max_length=64)
    amount: int = Field(..., ge=0, description="Centimes")


class SaleCreate(BaseModel):
    """Body POST /v1/sales — creation ticket. offline_id optionnel (Story 5.4, idempotence)."""

    cash_session_id: UUID
    items: list[SaleItemCreate] = Field(..., min_length=1)
    payments: list[PaymentCreate] = Field(..., min_length=1)
    note: str | None = None
    sale_date: datetime | None = None
    offline_id: UUID | None = Field(None, description="Idempotence: ticket cree hors ligne")


class SaleItemResponse(BaseModel):
    id: UUID
    sale_id: UUID
    category_id: UUID | None = None
    preset_id: UUID | None = None
    quantity: int
    unit_price: int
    total_price: int
    weight: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentTransactionResponse(BaseModel):
    id: UUID
    sale_id: UUID
    payment_method: str
    amount: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SaleResponse(BaseModel):
    """Reponse vente (détail avec lignes et paiements)."""

    id: UUID
    cash_session_id: UUID
    operator_id: UUID
    total_amount: int
    note: str | None = None
    sale_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
    items: list[SaleItemResponse] = []
    payment_transactions: list[PaymentTransactionResponse] = []

    model_config = {"from_attributes": True}


class SaleListResponse(BaseModel):
    """Reponse liste (sans items/payments detail)."""

    id: UUID
    cash_session_id: UUID
    operator_id: UUID
    total_amount: int
    note: str | None = None
    sale_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SaleNoteUpdate(BaseModel):
    """Body PUT /v1/sales/{sale_id} — mise a jour note."""

    note: str | None = None


class SaleItemUpdate(BaseModel):
    """Body PATCH /v1/sales/{sale_id}/items/{item_id} — preset_id, unit_price."""

    preset_id: UUID | None = None
    unit_price: int | None = Field(None, ge=0)


class SaleItemWeightUpdate(BaseModel):
    """Body PATCH /v1/sales/{sale_id}/items/{item_id}/weight."""

    weight: float | None = Field(None, ge=0)
