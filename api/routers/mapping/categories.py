"""Router mapping catégories RecyClique -> Paheko (Story 7.1). GET/POST/PATCH /api/mapping/categories. RBAC: admin."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import Category, CategoryMapping, User
from api.schemas.mapping import (
    CategoryMappingCreate,
    CategoryMappingResponse,
    CategoryMappingUpdate,
)

router = APIRouter(prefix="/categories", tags=["mapping-categories"])
_Admin = Depends(require_permissions("admin"))


def _require_paheko_target(paheko_category_id: int | None, paheko_code: str | None) -> None:
    has_id = paheko_category_id is not None
    has_code = paheko_code is not None and len(paheko_code.strip()) > 0
    if not has_id and not has_code:
        raise HTTPException(
            status_code=422,
            detail="At least one of paheko_category_id or paheko_code must be set",
        )


@router.get("", response_model=list[CategoryMappingResponse])
def list_category_mappings(
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> list[CategoryMapping]:
    """GET /api/mapping/categories — liste des mappings."""
    q = select(CategoryMapping).order_by(CategoryMapping.category_id)
    return list(db.execute(q).scalars().all())


@router.get("/{mapping_id}", response_model=CategoryMappingResponse)
def get_category_mapping(
    mapping_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> CategoryMapping:
    """GET /api/mapping/categories/{id} — détail."""
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
    current_user: User = _Admin,
) -> CategoryMapping:
    """POST /api/mapping/categories — création (au moins un de paheko_category_id ou paheko_code)."""
    _require_paheko_target(body.paheko_category_id, body.paheko_code)
    category = db.execute(select(Category).where(Category.id == body.category_id)).scalars().one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    existing = db.execute(
        select(CategoryMapping).where(CategoryMapping.category_id == body.category_id)
    ).scalars().one_or_none()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="A mapping for this category already exists",
        )
    mapping = CategoryMapping(
        category_id=body.category_id,
        paheko_category_id=body.paheko_category_id,
        paheko_code=body.paheko_code,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.patch("/{mapping_id}", response_model=CategoryMappingResponse)
def update_category_mapping(
    mapping_id: UUID,
    body: CategoryMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> CategoryMapping:
    """PATCH /api/mapping/categories/{id} — mise à jour partielle."""
    mapping = db.execute(
        select(CategoryMapping).where(CategoryMapping.id == mapping_id)
    ).scalars().one_or_none()
    if mapping is None:
        raise HTTPException(status_code=404, detail="Category mapping not found")
    if body.paheko_category_id is not None:
        mapping.paheko_category_id = body.paheko_category_id
    if body.paheko_code is not None:
        mapping.paheko_code = body.paheko_code
    mapping.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(mapping)
    return mapping
