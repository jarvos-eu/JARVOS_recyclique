"""Router cash-registers — CRUD + GET /status (Story 2.2) + start/stop (Story 3.4). Protégé RBAC (Story 3.2) : GET = caisse.access | admin, write = admin."""

import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import AuditEvent, CashRegister, Site, User
from api.schemas.cash_register import (
    CashRegisterCreate,
    CashRegisterResponse,
    CashRegisterStatusItem,
    CashRegisterUpdate,
)

router = APIRouter(prefix="/cash-registers", tags=["cash-registers"])

_CaisseOrAdmin = Depends(require_permissions("caisse.access", "admin"))
_Admin = Depends(require_permissions("admin"))


def _get_site_or_404(db: Session, site_id: UUID) -> Site | None:
    return db.execute(select(Site).where(Site.id == site_id)).scalars().one_or_none()


@router.get("", response_model=list[CashRegisterResponse])
def list_cash_registers(
    site_id: UUID | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> list[CashRegister]:
    """GET /v1/cash-registers — liste des postes (filtres optionnels site_id, is_active)."""
    q = select(CashRegister)
    if site_id is not None:
        q = q.where(CashRegister.site_id == site_id)
    if is_active is not None:
        q = q.where(CashRegister.is_active == is_active)
    return list(db.execute(q).scalars().all())


@router.get("/status", response_model=list[CashRegisterStatusItem])
def get_cash_registers_status(
    site_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> list[CashRegisterStatusItem]:
    """GET /v1/cash-registers/status — statut global (libre/démarré). Story 3.4 : started_at / started_by exposés."""
    q = select(CashRegister)
    if site_id is not None:
        q = q.where(CashRegister.site_id == site_id)
    registers = list(db.execute(q).scalars().all())
    return [
        CashRegisterStatusItem(
            register_id=r.id,
            status="started" if r.started_at else "free",
            started_at=r.started_at,
            started_by_user_id=r.started_by_user_id,
        )
        for r in registers
    ]


@router.get("/{register_id}", response_model=CashRegisterResponse)
def get_cash_register(
    register_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> CashRegister:
    """GET /v1/cash-registers/{register_id} — détail d'un poste (404 si absent)."""
    row = (
        db.execute(select(CashRegister).where(CashRegister.id == register_id))
        .scalars()
        .one_or_none()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Cash register not found")
    return row


@router.post("", response_model=CashRegisterResponse, status_code=201)
def create_cash_register(
    body: CashRegisterCreate,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> CashRegister:
    """POST /v1/cash-registers — création (site_id requis, site existant)."""
    site = _get_site_or_404(db, body.site_id)
    if site is None:
        raise HTTPException(
            status_code=404, detail="Site not found"
        )
    reg = CashRegister(
        site_id=body.site_id,
        name=body.name,
        location=body.location,
        is_active=body.is_active,
        enable_virtual=body.enable_virtual,
        enable_deferred=body.enable_deferred,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


@router.patch("/{register_id}", response_model=CashRegisterResponse)
def update_cash_register(
    register_id: UUID,
    body: CashRegisterUpdate,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> CashRegister:
    """PATCH /v1/cash-registers/{register_id} — mise à jour partielle."""
    reg = (
        db.execute(select(CashRegister).where(CashRegister.id == register_id))
        .scalars()
        .one_or_none()
    )
    if reg is None:
        raise HTTPException(status_code=404, detail="Cash register not found")
    changed = False
    if body.name is not None and body.name != reg.name:
        reg.name = body.name
        changed = True
    if body.location is not None and body.location != reg.location:
        reg.location = body.location
        changed = True
    if body.is_active is not None and body.is_active != reg.is_active:
        reg.is_active = body.is_active
        changed = True
    if body.enable_virtual is not None and body.enable_virtual != reg.enable_virtual:
        reg.enable_virtual = body.enable_virtual
        changed = True
    if body.enable_deferred is not None and body.enable_deferred != reg.enable_deferred:
        reg.enable_deferred = body.enable_deferred
        changed = True
    if changed:
        reg.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(reg)
    return reg


@router.delete("/{register_id}", status_code=204)
def delete_cash_register(
    register_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> None:
    """DELETE /v1/cash-registers/{register_id} — suppression (204 ou 404)."""
    reg = (
        db.execute(select(CashRegister).where(CashRegister.id == register_id))
        .scalars()
        .one_or_none()
    )
    if reg is None:
        raise HTTPException(status_code=404, detail="Cash register not found")
    db.delete(reg)
    db.commit()


@router.post("/{register_id}/stop", response_model=CashRegisterResponse)
def stop_cash_register(
    register_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> CashRegister:
    """POST /v1/cash-registers/{register_id}/stop — arreter un poste caisse (admin). Story 3.4."""
    reg = (
        db.execute(select(CashRegister).where(CashRegister.id == register_id))
        .scalars()
        .one_or_none()
    )
    if reg is None:
        raise HTTPException(status_code=404, detail="Cash register not found")
    if reg.started_at is None:
        db.refresh(reg)
        return reg
    evt = AuditEvent(
        user_id=current_user.id,
        action="register_stopped",
        resource_type="cash_register",
        resource_id=str(reg.id),
        details=json.dumps({"site_id": str(reg.site_id), "register_id": str(reg.id)}),
    )
    db.add(evt)
    reg.started_at = None
    reg.started_by_user_id = None
    db.commit()
    db.refresh(reg)
    return reg
