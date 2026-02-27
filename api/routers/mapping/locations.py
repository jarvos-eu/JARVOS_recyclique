"""Router mapping sites/emplacements RecyClique -> Paheko (Story 7.1). GET/POST/PATCH /api/mapping/locations. RBAC: admin."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import CashRegister, LocationMapping, Site, User
from api.schemas.mapping import (
    LocationMappingCreate,
    LocationMappingResponse,
    LocationMappingUpdate,
)

router = APIRouter(prefix="/locations", tags=["mapping-locations"])
_Admin = Depends(require_permissions("admin"))


def _require_site_or_register(site_id: UUID | None, register_id: UUID | None) -> None:
    if (site_id is None) == (register_id is None):
        raise HTTPException(
            status_code=422,
            detail="Exactly one of site_id or register_id must be set",
        )


@router.get("", response_model=list[LocationMappingResponse])
def list_location_mappings(
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> list[LocationMapping]:
    """GET /api/mapping/locations — liste des mappings."""
    q = select(LocationMapping).order_by(LocationMapping.paheko_id_location)
    return list(db.execute(q).scalars().all())


@router.get("/{mapping_id}", response_model=LocationMappingResponse)
def get_location_mapping(
    mapping_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> LocationMapping:
    """GET /api/mapping/locations/{id} — détail."""
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
    current_user: User = _Admin,
) -> LocationMapping:
    """POST /api/mapping/locations — création (exactement un de site_id ou register_id)."""
    _require_site_or_register(body.site_id, body.register_id)
    if body.site_id is not None:
        site = db.execute(select(Site).where(Site.id == body.site_id)).scalars().one_or_none()
        if site is None:
            raise HTTPException(status_code=404, detail="Site not found")
        existing = db.execute(
            select(LocationMapping).where(LocationMapping.site_id == body.site_id)
        ).scalars().one_or_none()
        if existing:
            raise HTTPException(
                status_code=409,
                detail="A mapping for this site already exists",
            )
        mapping = LocationMapping(site_id=body.site_id, paheko_id_location=body.paheko_id_location)
    else:
        reg = db.execute(
            select(CashRegister).where(CashRegister.id == body.register_id)
        ).scalars().one_or_none()
        if reg is None:
            raise HTTPException(status_code=404, detail="Cash register not found")
        existing = db.execute(
            select(LocationMapping).where(LocationMapping.register_id == body.register_id)
        ).scalars().one_or_none()
        if existing:
            raise HTTPException(
                status_code=409,
                detail="A mapping for this register already exists",
            )
        mapping = LocationMapping(
            register_id=body.register_id,
            paheko_id_location=body.paheko_id_location,
        )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.patch("/{mapping_id}", response_model=LocationMappingResponse)
def update_location_mapping(
    mapping_id: UUID,
    body: LocationMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> LocationMapping:
    """PATCH /api/mapping/locations/{id} — mise à jour partielle."""
    mapping = db.execute(
        select(LocationMapping).where(LocationMapping.id == mapping_id)
    ).scalars().one_or_none()
    if mapping is None:
        raise HTTPException(status_code=404, detail="Location mapping not found")
    if body.paheko_id_location is not None:
        mapping.paheko_id_location = body.paheko_id_location
    mapping.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(mapping)
    return mapping
