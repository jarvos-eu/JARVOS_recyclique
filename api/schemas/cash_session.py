# Schemas Pydantic — Cash sessions (Story 5.1). Montants en centimes, snake_case.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CashSessionCreate(BaseModel):
    """Body POST /v1/cash-sessions — ouverture session."""

    initial_amount: int = Field(..., ge=0, description="Fond de caisse en centimes")
    register_id: UUID
    opened_at: datetime | None = Field(None, description="Pour saisie différée (date réelle)")
    session_type: str = Field("real", description="real | virtual | deferred")


class CashSessionClose(BaseModel):
    """Body POST /v1/cash-sessions/{id}/close — fermeture."""

    closing_amount: int | None = Field(None, ge=0, description="Montant clôture en centimes")
    actual_amount: int | None = Field(None, description="Montant compté en centimes")
    variance_comment: str | None = None


class CashSessionStepUpdate(BaseModel):
    """Body PUT /v1/cash-sessions/{id}/step."""

    step: str = Field(..., description="entry | sale | exit")


class CashSessionResponse(BaseModel):
    """Réponse session (détail, current, liste)."""

    id: UUID
    operator_id: UUID
    register_id: UUID
    site_id: UUID
    initial_amount: int
    current_amount: int
    status: str
    opened_at: datetime
    closed_at: datetime | None = None
    current_step: str
    closing_amount: int | None = None
    actual_amount: int | None = None
    variance: int | None = None
    variance_comment: str | None = None
    session_type: str
    total_sales: int | None = None  # centimes, somme ventes (Story 5.3)
    total_items: int | None = None  # nombre de lignes (Story 5.3)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CashSessionStatusResponse(BaseModel):
    """GET /v1/cash-sessions/status/{register_id} — occupé / libre."""

    register_id: UUID
    has_open_session: bool
    session_id: UUID | None = None
    opened_at: datetime | None = None


class CashSessionDeferredCheckResponse(BaseModel):
    """GET /v1/cash-sessions/deferred/check — évitement doublon différée."""

    date: str  # YYYY-MM-DD
    has_session: bool
    session_id: UUID | None = None
