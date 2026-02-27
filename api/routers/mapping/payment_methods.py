"""Router mapping moyens de paiement RecyClique -> Paheko (Story 7.1). GET/POST/PATCH /api/mapping/payment_methods. RBAC: admin."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import PaymentMethodMapping, User
from api.schemas.mapping import (
    PaymentMethodMappingCreate,
    PaymentMethodMappingResponse,
    PaymentMethodMappingUpdate,
)

router = APIRouter(prefix="/payment_methods", tags=["mapping-payment-methods"])
_Admin = Depends(require_permissions("admin"))


@router.get("", response_model=list[PaymentMethodMappingResponse])
def list_payment_method_mappings(
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> list[PaymentMethodMapping]:
    """GET /api/mapping/payment_methods — liste des mappings."""
    q = select(PaymentMethodMapping).order_by(PaymentMethodMapping.recyclic_code)
    return list(db.execute(q).scalars().all())


@router.get("/{mapping_id}", response_model=PaymentMethodMappingResponse)
def get_payment_method_mapping(
    mapping_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> PaymentMethodMapping:
    """GET /api/mapping/payment_methods/{id} — détail."""
    row = db.execute(
        select(PaymentMethodMapping).where(PaymentMethodMapping.id == mapping_id)
    ).scalars().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Payment method mapping not found")
    return row


@router.post("", response_model=PaymentMethodMappingResponse, status_code=201)
def create_payment_method_mapping(
    body: PaymentMethodMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> PaymentMethodMapping:
    """POST /api/mapping/payment_methods — création."""
    existing = db.execute(
        select(PaymentMethodMapping).where(PaymentMethodMapping.recyclic_code == body.recyclic_code)
    ).scalars().one_or_none()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="A mapping for this recyclic_code already exists",
        )
    mapping = PaymentMethodMapping(
        recyclic_code=body.recyclic_code,
        paheko_id_method=body.paheko_id_method,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.patch("/{mapping_id}", response_model=PaymentMethodMappingResponse)
def update_payment_method_mapping(
    mapping_id: UUID,
    body: PaymentMethodMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> PaymentMethodMapping:
    """PATCH /api/mapping/payment_methods/{id} — mise à jour partielle."""
    mapping = db.execute(
        select(PaymentMethodMapping).where(PaymentMethodMapping.id == mapping_id)
    ).scalars().one_or_none()
    if mapping is None:
        raise HTTPException(status_code=404, detail="Payment method mapping not found")
    if body.paheko_id_method is not None and body.paheko_id_method != mapping.paheko_id_method:
        mapping.paheko_id_method = body.paheko_id_method
    mapping.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(mapping)
    return mapping
