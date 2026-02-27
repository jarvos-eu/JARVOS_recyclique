# Schemas Pydantic — Poste réception (Story 3.4, 6.1).

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PosteReceptionOpenRequest(BaseModel):
    """Body pour POST /v1/reception/postes/open (opened_at optionnel, saisie différée)."""

    opened_at: datetime | None = None


class PosteReceptionResponse(BaseModel):
    """Réponse création/ouverture/lecture poste réception."""

    id: UUID
    opened_by_user_id: UUID | None
    opened_at: datetime
    closed_at: datetime | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
