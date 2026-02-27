"""Admin API mapping moyens de paiement (Story 7.2). GET/POST/PATCH/DELETE /v1/admin/mapping/payment_methods. RBAC: admin ou compta.responsable ; audit sur CUD."""

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
from api.services.audit import write_audit_event
from api.services.mapping_service import (
    create_payment_method_mapping as svc_create,
    update_payment_method_mapping as svc_update,
    delete_payment_method_mapping as svc_delete,
)

router = APIRouter(prefix="/payment_methods", tags=["admin-mapping-payment-methods"])
_AdminOrCompta = Depends(require_permissions("admin", "compta.responsable"))

RESOURCE_TYPE = "payment_method_mapping"


@router.get("", response_model=list[PaymentMethodMappingResponse])
def list_payment_method_mappings(
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> list[PaymentMethodMapping]:
    """GET /v1/admin/mapping/payment_methods — liste des mappings."""
    q = select(PaymentMethodMapping).order_by(PaymentMethodMapping.recyclic_code)
    return list(db.execute(q).scalars().all())


@router.get("/{mapping_id}", response_model=PaymentMethodMappingResponse)
def get_payment_method_mapping(
    mapping_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> PaymentMethodMapping:
    """GET /v1/admin/mapping/payment_methods/{id} — detail."""
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
    current_user: User = _AdminOrCompta,
) -> PaymentMethodMapping:
    """POST /v1/admin/mapping/payment_methods — creation + audit."""
    try:
        mapping = svc_create(
            db,
            recyclic_code=body.recyclic_code,
            paheko_id_method=body.paheko_id_method,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    write_audit_event(
        db,
        user_id=current_user.id,
        action="mapping.payment_method.created",
        resource_type=RESOURCE_TYPE,
        resource_id=str(mapping.id),
        details=f"recyclic_code={body.recyclic_code} paheko_id_method={body.paheko_id_method}",
    )
    db.commit()
    db.refresh(mapping)
    return mapping


@router.patch("/{mapping_id}", response_model=PaymentMethodMappingResponse)
def update_payment_method_mapping(
    mapping_id: UUID,
    body: PaymentMethodMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> PaymentMethodMapping:
    """PATCH /v1/admin/mapping/payment_methods/{id} — mise a jour + audit."""
    mapping = svc_update(
        db,
        mapping_id,
        paheko_id_method=body.paheko_id_method,
    )
    if mapping is None:
        raise HTTPException(status_code=404, detail="Payment method mapping not found")
    write_audit_event(
        db,
        user_id=current_user.id,
        action="mapping.payment_method.updated",
        resource_type=RESOURCE_TYPE,
        resource_id=str(mapping_id),
        details=f"paheko_id_method={mapping.paheko_id_method}",
    )
    db.commit()
    db.refresh(mapping)
    return mapping


@router.delete("/{mapping_id}", status_code=204)
def delete_payment_method_mapping(
    mapping_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> None:
    """DELETE /v1/admin/mapping/payment_methods/{id} — suppression + audit."""
    deleted = svc_delete(db, mapping_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment method mapping not found")
    write_audit_event(
        db,
        user_id=current_user.id,
        action="mapping.payment_method.deleted",
        resource_type=RESOURCE_TYPE,
        resource_id=str(mapping_id),
        details=None,
    )
    db.commit()
