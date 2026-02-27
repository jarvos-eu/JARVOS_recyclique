# Story 8.4 — GET /v1/admin/email-logs (stub v1, liste vide).

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from api.core.deps import require_permissions
from api.models import User

router = APIRouter(prefix="/email-logs", tags=["admin-email-logs"])
_Admin = Depends(require_permissions("admin"))


class EmailLogItem(BaseModel):
    id: str
    sent_at: str
    recipient: str
    subject: str
    status: str


class EmailLogsListResponse(BaseModel):
    items: list[EmailLogItem]
    total: int
    page: int
    page_size: int


@router.get("", response_model=EmailLogsListResponse)
def list_email_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = _Admin,
) -> EmailLogsListResponse:
    """GET /v1/admin/email-logs — stub v1 (pas de table email_logs)."""
    return EmailLogsListResponse(items=[], total=0, page=page, page_size=page_size)
