# Router agrégats déclaratifs (Story 9.1). API read-only + endpoint calcul (job ou manuel).

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.schemas.declarative import DeclarativeAggregateResponse
from api.services.declarative_service import (
    FLOW_CAISSE,
    FLOW_RECEPTION,
    compute_and_persist_aggregates,
    get_aggregates,
)

router = APIRouter(prefix="/declarative", tags=["declarative"])
_Admin = Depends(require_permissions("admin"))

VALID_FLOW_TYPES = frozenset({FLOW_CAISSE, FLOW_RECEPTION})
YEAR_MIN, YEAR_MAX = 1900, 2100


class ComputeAggregatesBody(BaseModel):
    year: int
    quarter: int


class ComputeAggregatesResponse(BaseModel):
    rows_persisted: int


@router.get(
    "/aggregates",
    response_model=list[DeclarativeAggregateResponse],
    summary="Liste des agrégats déclaratifs",
    description="Données agrégées par période (trimestre), catégorie et flux (caisse / réception). Filtres optionnels.",
)
def list_declarative_aggregates(
    db: Session = Depends(get_db),
    year: int | None = Query(None, description="Année (ex. 2026)"),
    quarter: int | None = Query(None, ge=1, le=4, description="Trimestre 1–4"),
    flow_type: str | None = Query(None, description="caisse | reception"),
    category_id: UUID | None = Query(None, description="Filtre par catégorie"),
    _: None = _Admin,
) -> list[DeclarativeAggregateResponse]:
    if flow_type is not None and flow_type not in VALID_FLOW_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"flow_type must be one of: {', '.join(sorted(VALID_FLOW_TYPES))}",
        )
    rows = get_aggregates(db, year=year, quarter=quarter, flow_type=flow_type, category_id=category_id)
    return [DeclarativeAggregateResponse.model_validate(r) for r in rows]


@router.post(
    "/aggregates/compute",
    response_model=ComputeAggregatesResponse,
    summary="Recalculer les agrégats pour un trimestre",
    description="Réexécutable (backfill/corrections). Appelable par un job planifié ou manuellement.",
)
def compute_aggregates(
    body: ComputeAggregatesBody,
    db: Session = Depends(get_db),
    _: None = _Admin,
) -> ComputeAggregatesResponse:
    if body.year < YEAR_MIN or body.year > YEAR_MAX:
        raise HTTPException(
            status_code=400,
            detail=f"year must be between {YEAR_MIN} and {YEAR_MAX}",
        )
    if body.quarter < 1 or body.quarter > 4:
        raise HTTPException(status_code=400, detail="quarter must be 1-4")
    n = compute_and_persist_aggregates(db, body.year, body.quarter)
    return ComputeAggregatesResponse(rows_persisted=n)
