# Story 8.4 — POST /v1/admin/reports/reception-tickets/export-bulk.
# Export bulk des tickets de réception (filtres, CSV).

import csv
import io
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select

from api.core.deps import require_permissions
from api.db import get_db
from api.models import TicketDepot, User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reports/reception-tickets", tags=["admin-reports-reception"])
_Admin = Depends(require_permissions("admin"))


class ReceptionExportBulkRequest(BaseModel):
    """Body POST /v1/admin/reports/reception-tickets/export-bulk."""

    date_from: str | None = None  # YYYY-MM-DD
    date_to: str | None = None
    poste_id: UUID | None = None
    status: str | None = None


@router.post("/export-bulk")
def export_bulk(
    body: ReceptionExportBulkRequest,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> StreamingResponse:
    """POST /v1/admin/reports/reception-tickets/export-bulk — export CSV des tickets (filtres)."""
    q = select(TicketDepot).order_by(TicketDepot.created_at.desc())
    if body.poste_id is not None:
        q = q.where(TicketDepot.poste_id == body.poste_id)
    if body.status is not None:
        q = q.where(TicketDepot.status == body.status)
    if body.date_from is not None:
        try:
            dt_from = datetime.strptime(body.date_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            q = q.where(TicketDepot.created_at >= dt_from)
        except ValueError:
            pass
    if body.date_to is not None:
        try:
            dt_to = datetime.strptime(body.date_to, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)
            q = q.where(TicketDepot.created_at < dt_to)
        except ValueError:
            pass
    rows = list(db.execute(q).scalars().all())

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "poste_id", "benevole_user_id", "created_at", "closed_at", "status", "updated_at"])
    for t in rows:
        writer.writerow([
            str(t.id),
            str(t.poste_id),
            str(t.benevole_user_id) if t.benevole_user_id else "",
            t.created_at.isoformat() if t.created_at else "",
            t.closed_at.isoformat() if t.closed_at else "",
            t.status or "",
            t.updated_at.isoformat() if t.updated_at else "",
        ])
    buf.seek(0)
    content = buf.getvalue().encode("utf-8-sig")

    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=reception-tickets-export.csv",
        },
    )
