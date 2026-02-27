# RecyClique API — Router admin cash-registers start/stop (Story 3.4).
# POST /v1/admin/cash-registers/start : demarrer un poste caisse (admin).
# Audit : register_started / register_stopped (meme transaction).

import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import AuditEvent, CashRegister, User
from api.schemas.cash_register import CashRegisterStartRequest, CashRegisterResponse

router = APIRouter()


def _get_register_or_404(db: Session, register_id: UUID) -> CashRegister | None:
    return (
        db.execute(select(CashRegister).where(CashRegister.id == register_id))
        .scalars()
        .one_or_none()
    )


@router.post("/start", response_model=CashRegisterResponse)
def start_cash_register(
    body: CashRegisterStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> CashRegister:
    """POST /v1/admin/cash-registers/start — demarrer un poste caisse (admin).
    Verifie que register_id appartient au site_id ; enregistre started_at, started_by_user_id ; audit.
    """
    reg = _get_register_or_404(db, body.register_id)
    if reg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cash register not found")
    if str(reg.site_id) != str(body.site_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Register does not belong to the given site",
        )
    now = datetime.now(timezone.utc)
    reg.started_at = now
    reg.started_by_user_id = current_user.id
    evt = AuditEvent(
        user_id=current_user.id,
        action="register_started",
        resource_type="cash_register",
        resource_id=str(reg.id),
        details=json.dumps({"site_id": str(reg.site_id), "register_id": str(reg.id)}),
    )
    db.add(evt)
    db.commit()
    db.refresh(reg)
    return reg

