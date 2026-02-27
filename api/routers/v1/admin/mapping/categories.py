"""Admin API mapping categories (Story 7.2). GET/POST/PATCH/DELETE /v1/admin/mapping/categories. RBAC: admin ou compta.responsable ; audit sur CUD."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import CategoryMapping, User
from api.schemas.mapping import (
    CategoryMappingCreate,
    CategoryMappingResponse,
    CategoryMappingUpdate,
)
from api.services.audit import write_audit_event
from api.services.mapping_service import (
    create_category_mapping as svc_create,
    update_category_mapping as svc_update,
    delete_category_mapping as svc_delete,
)

router = APIRouter(prefix="/categories", tags=["admin-mapping-categories"])
_AdminOrCompta = Depends(require_permissions("admin", "compta.responsable"))

RESOURCE_TYPE = "category_mapping"


@router.get("", response_model=list[CategoryMappingResponse])
def list_category_mappings(
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> list[CategoryMapping]:
    """GET /v1/admin/mapping/categories — liste des mappings."""
    q = select(CategoryMapping).order_by(CategoryMapping.category_id)
    return list(db.execute(q).scalars().all())


@router.get("/{mapping_id}", response_model=CategoryMappingResponse)
def get_category_mapping(
    mapping_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> CategoryMapping:
    """GET /v1/admin/mapping/categories/{id} — detail."""
    row = db.execute(
        select(CategoryMapping).where(CategoryMapping.id == mapping_id)
    ).scalars().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Category mapping not found")
    return row


@router.post("", response_model=CategoryMappingResponse, status_code=201)
def create_category_mapping(
    body: CategoryMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> CategoryMapping:
    """POST /v1/admin/mapping/categories — creation + audit."""
    try:
        mapping = svc_create(
            db,
            category_id=body.category_id,
            paheko_category_id=body.paheko_category_id,
            paheko_code=body.paheko_code,
        )
    except ValueError as e:
        err = str(e)
        if "not found" in err.lower():
            raise HTTPException(status_code=404, detail=err)
        raise HTTPException(status_code=409, detail=err)
    write_audit_event(
        db,
        user_id=current_user.id,
        action="mapping.category.created",
        resource_type=RESOURCE_TYPE,
        resource_id=str(mapping.id),
        details=f"category_id={body.category_id}",
    )
    db.commit()
    db.refresh(mapping)
    return mapping


@router.patch("/{mapping_id}", response_model=CategoryMappingResponse)
def update_category_mapping(
    mapping_id: UUID,
    body: CategoryMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> CategoryMapping:
    """PATCH /v1/admin/mapping/categories/{id} — mise a jour + audit."""
    mapping = svc_update(
        db,
        mapping_id,
        paheko_category_id=body.paheko_category_id,
        paheko_code=body.paheko_code,
    )
    if mapping is None:
        raise HTTPException(status_code=404, detail="Category mapping not found")
    write_audit_event(
        db,
        user_id=current_user.id,
        action="mapping.category.updated",
        resource_type=RESOURCE_TYPE,
        resource_id=str(mapping_id),
        details=None,
    )
    db.commit()
    db.refresh(mapping)
    return mapping


@router.delete("/{mapping_id}", status_code=204)
def delete_category_mapping(
    mapping_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> None:
    """DELETE /v1/admin/mapping/categories/{id} — suppression + audit."""
    deleted = svc_delete(db, mapping_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category mapping not found")
    write_audit_event(
        db,
        user_id=current_user.id,
        action="mapping.category.deleted",
        resource_type=RESOURCE_TYPE,
        resource_id=str(mapping_id),
        details=None,
    )
    db.commit()

