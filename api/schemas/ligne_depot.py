# Schemas Pydantic — Ligne dépôt (Story 6.2). snake_case.

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

# Valeurs métier pour destination (aligné BDD et frontend).
DESTINATION_VALUES = ("recyclage", "revente", "destruction", "don", "autre")
DestinationLiteral = Literal["recyclage", "revente", "destruction", "don", "autre"]


class LigneDepotCreateRequest(BaseModel):
    """Body POST /v1/reception/lignes."""

    ticket_id: UUID
    category_id: UUID | None = None
    poids_kg: Decimal = Field(..., gt=0)
    destination: DestinationLiteral
    notes: str | None = None
    is_exit: bool = False


class LigneDepotUpdateRequest(BaseModel):
    """Body PUT /v1/reception/lignes/{ligne_id} — champs modifiables."""

    poids_kg: Decimal | None = Field(None, gt=0)
    category_id: UUID | None = None
    destination: DestinationLiteral | None = None
    notes: str | None = None
    is_exit: bool | None = None


class LigneDepotWeightUpdateRequest(BaseModel):
    """Body PATCH /v1/reception/tickets/{ticket_id}/lignes/{ligne_id}/weight."""

    weight: Decimal = Field(..., gt=0)

    model_config = {"populate_by_name": True}


class LigneDepotResponse(BaseModel):
    """Réponse détail / création ligne."""

    id: UUID
    ticket_id: UUID
    poids_kg: Decimal
    category_id: UUID | None = None
    destination: str
    notes: str | None = None
    is_exit: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LigneDepotListResponse(BaseModel):
    """GET /v1/reception/lignes — pagination (items, total, page, page_size)."""

    items: list[LigneDepotResponse]
    total: int
    page: int
    page_size: int
