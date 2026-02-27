# Story 8.4 — GET /v1/admin/audit-log (pagination, filtres date, event_type, user_id).

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import User, AuditEvent

router = APIRouter(prefix="/audit-log", tags=["admin-audit"])
_Admin = Depends(require_permissions("admin"))


class AuditEventItem(BaseModel):
    id: str
    timestamp: datetime
    user_id: str | None
    action: str
    resource_type: str | None
    resource_id: str | None
    details: str | None

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    items: list[AuditEventItem]
    total: int
    page: int
    page_size: int


def _parse_date(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        try:
            dt = datetime.strptime(s[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("", response_model=AuditLogListResponse)
def list_audit_log(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    date_from: str | None = Query(None, description="ISO date or YYYY-MM-DD"),
    date_to: str | None = Query(None, description="ISO date or YYYY-MM-DD"),
    event_type: str | None = Query(None, description="Filter by action"),
    user_id: str | None = Query(None, description="Filter by user_id UUID"),
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> AuditLogListResponse:
    """GET /v1/admin/audit-log — liste paginée et filtrable."""
    q = select(AuditEvent)
    count_q = select(func.count()).select_from(AuditEvent)

    dt_from = _parse_date(date_from)
    dt_to = _parse_date(date_to)
    if dt_from is not None:
        q = q.where(AuditEvent.timestamp >= dt_from)
        count_q = count_q.where(AuditEvent.timestamp >= dt_from)
    if dt_to is not None:
        q = q.where(AuditEvent.timestamp <= dt_to)
        count_q = count_q.where(AuditEvent.timestamp <= dt_to)
    if event_type:
        q = q.where(AuditEvent.action == event_type)
        count_q = count_q.where(AuditEvent.action == event_type)
    if user_id:
        try:
            uid = UUID(user_id)
            q = q.where(AuditEvent.user_id == uid)
            count_q = count_q.where(AuditEvent.user_id == uid)
        except ValueError:
            pass

    total = db.execute(count_q).scalar() or 0
    q = q.order_by(AuditEvent.timestamp.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = list(db.execute(q).scalars().all())
    items = [
        AuditEventItem(
            id=str(r.id),
            timestamp=r.timestamp,
            user_id=str(r.user_id) if r.user_id else None,
            action=r.action,
            resource_type=r.resource_type,
            resource_id=r.resource_id,
            details=r.details,
        )
        for r in rows
    ]
    return AuditLogListResponse(items=items, total=total, page=page, page_size=page_size)
