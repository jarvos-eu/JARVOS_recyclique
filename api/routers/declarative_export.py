# Router export agrégats déclaratifs (Story 9.2 post-MVP).
# Exposé uniquement lorsque le module "decla" est activé dans modules.toml.
# GET /v1/declarative/export : téléchargement CSV ou JSON des agrégats pour une période.

import csv
import io
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.schemas.declarative import DeclarativeAggregateResponse
from api.services.declarative_service import (
    FLOW_CAISSE,
    FLOW_RECEPTION,
    get_aggregates,
    VALID_FLOW_TYPES,
    YEAR_MIN,
    YEAR_MAX,
)

router = APIRouter(prefix="/declarative", tags=["declarative"])
_Admin = Depends(require_permissions("admin"))

EXPORT_FORMAT_CSV = "csv"
EXPORT_FORMAT_JSON = "json"
VALID_EXPORT_FORMATS = frozenset({EXPORT_FORMAT_CSV, EXPORT_FORMAT_JSON})


@router.get(
    "/export",
    summary="Export des agrégats déclaratifs (module décla)",
    description="Export CSV ou JSON des agrégats pour une période (year, quarter). Optionnel : flow_type, category_id, eco_organism (réservé multi-éco). Permission admin.",
)
def export_declarative_aggregates(
    db: Session = Depends(get_db),
    year: int = Query(..., ge=YEAR_MIN, le=YEAR_MAX, description="Année (ex. 2026)"),
    quarter: int = Query(..., ge=1, le=4, description="Trimestre 1–4"),
    format: str = Query(
        EXPORT_FORMAT_CSV,
        alias="format",
        description="Format d'export : csv | json",
    ),
    flow_type: str | None = Query(None, description="caisse | reception"),
    category_id: UUID | None = Query(None, description="Filtre par catégorie"),
    eco_organism: str | None = Query(
        None,
        description="Éco-organisme cible (réservé multi-éco-organismes, ignoré en v1)",
    ),
    _: None = _Admin,
) -> StreamingResponse:
    if format.lower() not in VALID_EXPORT_FORMATS:
        raise HTTPException(
            status_code=422,
            detail=f"format must be one of: {', '.join(sorted(VALID_EXPORT_FORMATS))}",
        )
    if flow_type is not None and flow_type not in VALID_FLOW_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"flow_type must be one of: {', '.join(sorted(VALID_FLOW_TYPES))}",
        )
    rows = get_aggregates(
        db,
        year=year,
        quarter=quarter,
        flow_type=flow_type,
        category_id=category_id,
    )
    payloads = [DeclarativeAggregateResponse.model_validate(r) for r in rows]

    if format.lower() == EXPORT_FORMAT_JSON:
        body = json.dumps(
            [p.model_dump(mode="json") for p in payloads],
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8")
        return StreamingResponse(
            io.BytesIO(body),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=declarative_aggregates.json"},
        )

    # CSV
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "year", "quarter", "category_id", "flow_type", "weight_kg", "quantity", "created_at", "updated_at"])
    for p in payloads:
        writer.writerow([
            str(p.id),
            p.year,
            p.quarter,
            str(p.category_id) if p.category_id else "",
            p.flow_type,
            p.weight_kg,
            p.quantity,
            p.created_at.isoformat() if p.created_at else "",
            p.updated_at.isoformat() if p.updated_at else "",
        ])
    body = buf.getvalue().encode("utf-8-sig")
    return StreamingResponse(
        io.BytesIO(body),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=declarative_aggregates.csv"},
    )
