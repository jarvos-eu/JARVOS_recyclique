# Rapports admin — Story 8.2.
# GET /v1/admin/reports/cash-sessions, by-session/{id}, export-bulk.

from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select, nulls_last

from api.core.deps import require_permissions
from api.db import get_db
from api.models import CashSession, User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reports/cash-sessions", tags=["admin-reports"])

_Admin = Depends(require_permissions("admin"))


class ReportListItem(BaseModel):
    session_id: UUID
    closed_at: datetime | None
    opened_at: datetime
    site_id: UUID
    register_id: UUID
    operator_id: UUID
    status: str


class ExportBulkRequest(BaseModel):
    date_from: str | None = None  # YYYY-MM-DD
    date_to: str | None = None
    site_id: UUID | None = None


@router.get("", response_model=list[ReportListItem])
def list_cash_session_reports(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> list[ReportListItem]:
    """GET /v1/admin/reports/cash-sessions — liste des rapports (sessions clôturées)."""
    q = (
        select(CashSession)
        .where(CashSession.status == "closed")
        .order_by(nulls_last(CashSession.closed_at.desc()), CashSession.opened_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = list(db.execute(q).scalars().all())
    return [
        ReportListItem(
            session_id=r.id,
            closed_at=r.closed_at,
            opened_at=r.opened_at,
            site_id=r.site_id,
            register_id=r.register_id,
            operator_id=r.operator_id,
            status=r.status,
        )
        for r in rows
    ]


@router.get("/by-session/{session_id}")
def get_report_by_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> Response:
    """GET /v1/admin/reports/cash-sessions/by-session/{session_id} — téléchargement rapport session."""
    row = (
        db.execute(select(CashSession).where(CashSession.id == session_id))
        .scalars()
        .one_or_none()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if row.status != "closed":
        raise HTTPException(status_code=400, detail="Session not closed, no report yet")
    # v1 minimal : retourner un placeholder texte (pas de génération PDF en scope)
    content = f"Rapport session caisse {session_id}\nOuverte: {row.opened_at}\nClôturée: {row.closed_at}\n"
    return Response(content=content, media_type="text/plain")


@router.post("/export-bulk")
def export_bulk(
    body: ExportBulkRequest,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> dict:
    """POST /v1/admin/reports/cash-sessions/export-bulk — export bulk (filtres période, etc.)."""
    q = select(CashSession).where(CashSession.status == "closed")
    if body.site_id is not None:
        q = q.where(CashSession.site_id == body.site_id)
    if body.date_from is not None:
        try:
            dt_from = datetime.strptime(body.date_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            q = q.where(CashSession.closed_at >= dt_from)
        except ValueError:
            pass
    if body.date_to is not None:
        try:
            dt_to = datetime.strptime(body.date_to, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)
            q = q.where(CashSession.closed_at < dt_to)
        except ValueError:
            pass
    q = q.order_by(CashSession.closed_at.desc())
    sessions = list(db.execute(q).scalars().all())
    # v1 minimal : pas de zip réel, on retourne la liste des session_ids concernées
    return {
        "message": "Export bulk demandé",
        "session_ids": [str(s.id) for s in sessions],
        "count": len(sessions),
    }
