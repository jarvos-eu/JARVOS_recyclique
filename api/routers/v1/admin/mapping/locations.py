"""Admin API mapping sites/emplacements (Story 7.2). GET/POST/PATCH/DELETE /v1/admin/mapping/locations. RBAC: admin ou compta.responsable ; audit sur CUD."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import LocationMapping, User
from api.schemas.mapping import (
    LocationMappingCreate,
    LocationMappingResponse,
    LocationMappingUpdate,
)
from api.services.audit import write_audit_event
from api.services.mapping_service import (
    create_location_mapping as svc_create,
    update_location_mapping as svc_update,
    delete_location_mapping as svc_delete,
)

router = APIRouter(prefix="/locations", tags=["admin-mapping-locations"])
_AdminOrCompta = Depends(require_permissions("admin", "compta.responsable"))

RESOURCE_TYPE = "location_mapping"


@router.get("", response_model=list[LocationMappingResponse])
def list_location_mappings(
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> list[LocationMapping]:
    """GET /v1/admin/mapping/locations — liste des mappings."""
    q = select(LocationMapping).order_by(LocationMapping.paheko_id_location)
    return list(db.execute(q).scalars().all())


@router.get("/{mapping_id}", response_model=LocationMappingResponse)
def get_location_mapping(
    mapping_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> LocationMapping:
    """GET /v1/admin/mapping/locations/{id} — detail."""
    row = db.execute(
        select(LocationMapping).where(LocationMapping.id == mapping_id)
    ).scalars().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Location mapping not found")
    return row


@router.post("", response_model=LocationMappingResponse, status_code=201)
def create_location_mapping(
    body: LocationMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> LocationMapping:
    """POST /v1/admin/mapping/locations — creation + audit."""
    try:
        mapping = svc_create(
            db,
            site_id=body.site_id,
            register_id=body.register_id,
            paheko_id_location=body.paheko_id_location,
        )
    except ValueError as e:
        err = str(e)
        if "not found" in err.lower():
            raise HTTPException(status_code=404, detail=err)
        raise HTTPException(status_code=422, detail=err)
    write_audit_event(
        db,
        user_id=current_user.id,
        action="mapping.location.created",
        resource_type=RESOURCE_TYPE,
        resource_id=str(mapping.id),
        details=f"site_id={body.site_id} register_id={body.register_id} paheko_id_location={body.paheko_id_location}",
    )
    db.commit()
    db.refresh(mapping)
    return mapping


@router.patch("/{mapping_id}", response_model=LocationMappingResponse)
def update_location_mapping(
    mapping_id: UUID,
    body: LocationMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> LocationMapping:
    """PATCH /v1/admin/mapping/locations/{id} — mise a jour + audit."""
    mapping = svc_update(
        db,
        mapping_id,
        paheko_id_location=body.paheko_id_location,
    )
    if mapping is None:
        raise HTTPException(status_code=404, detail="Location mapping not found")
    write_audit_event(
        db,
        user_id=current_user.id,
        action="mapping.location.updated",
        resource_type=RESOURCE_TYPE,
        resource_id=str(mapping_id),
        details=f"paheko_id_location={mapping.paheko_id_location}",
    )
    db.commit()
    db.refresh(mapping)
    return mapping


@router.delete("/{mapping_id}", status_code=204)
def delete_location_mapping(
    mapping_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _AdminOrCompta,
) -> None:
    """DELETE /v1/admin/mapping/locations/{id} — suppression + audit."""
    deleted = svc_delete(db, mapping_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Location mapping not found")
    write_audit_event(
        db,
        user_id=current_user.id,
        action="mapping.location.deleted",
        resource_type=RESOURCE_TYPE,
        resource_id=str(mapping_id),
        details=None,
    )
    db.commit()
