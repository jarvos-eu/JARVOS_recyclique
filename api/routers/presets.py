"""Router presets — CRUD + GET /active (Story 2.4). Boutons rapides caisse. Protégé RBAC (Story 3.2) : GET = caisse.access | admin, write = admin."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import Category, PresetButton, User
from api.schemas.preset import PresetCreate, PresetResponse, PresetUpdate

router = APIRouter(prefix="/presets", tags=["presets"])

_CaisseOrAdmin = Depends(require_permissions("caisse.access", "admin"))
_Admin = Depends(require_permissions("admin"))


def _get_preset_or_404(db: Session, preset_id: UUID) -> PresetButton | None:
    return (
        db.execute(select(PresetButton).where(PresetButton.id == preset_id))
        .scalars()
        .one_or_none()
    )


def _get_category_or_404(db: Session, category_id: UUID) -> Category | None:
    return (
        db.execute(select(Category).where(Category.id == category_id))
        .scalars()
        .one_or_none()
    )


# ——— Liste et actifs (avant /{id}) ———

@router.get("", response_model=list[PresetResponse])
def list_presets(
    category_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> list[PresetButton]:
    """GET /v1/presets — liste (filtre optionnel category_id)."""
    q = select(PresetButton)
    if category_id is not None:
        q = q.where(PresetButton.category_id == category_id)
    q = q.order_by(PresetButton.sort_order, PresetButton.name)
    return list(db.execute(q).scalars().all())


@router.get("/active", response_model=list[PresetResponse])
def list_presets_active(
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> list[PresetButton]:
    """GET /v1/presets/active — presets actifs pour la caisse (is_active=true, tri sort_order)."""
    q = (
        select(PresetButton)
        .where(PresetButton.is_active == True)
        .order_by(PresetButton.sort_order, PresetButton.name)
    )
    return list(db.execute(q).scalars().all())


# ——— CRUD par id ———

@router.get("/{preset_id}", response_model=PresetResponse)
def get_preset(
    preset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> PresetButton:
    """GET /v1/presets/{id} — détail (404 si absent)."""
    preset = _get_preset_or_404(db, preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset


@router.post("", response_model=PresetResponse, status_code=201)
def create_preset(
    body: PresetCreate,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> PresetButton:
    """POST /v1/presets — création. category_id optionnel mais doit exister si fourni."""
    if body.category_id is not None:
        cat = _get_category_or_404(db, body.category_id)
        if cat is None:
            raise HTTPException(
                status_code=400,
                detail="Category not found",
            )
    preset = PresetButton(
        name=body.name,
        category_id=body.category_id,
        preset_price=body.preset_price,
        button_type=body.button_type,
        sort_order=body.sort_order,
        is_active=body.is_active,
    )
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset


@router.patch("/{preset_id}", response_model=PresetResponse)
def update_preset(
    preset_id: UUID,
    body: PresetUpdate,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> PresetButton:
    """PATCH /v1/presets/{id} — mise à jour partielle. category_id doit exister si fourni ; peut être remis à null."""
    preset = _get_preset_or_404(db, preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")
    data = body.model_dump(exclude_unset=True)
    if "category_id" in data:
        if data["category_id"] is not None:
            cat = _get_category_or_404(db, data["category_id"])
            if cat is None:
                raise HTTPException(
                    status_code=400,
                    detail="Category not found",
                )
        preset.category_id = data["category_id"]
    if "name" in data and data["name"] != preset.name:
        preset.name = data["name"]
    if "preset_price" in data and data["preset_price"] != preset.preset_price:
        preset.preset_price = data["preset_price"]
    if "button_type" in data and data["button_type"] != preset.button_type:
        preset.button_type = data["button_type"]
    if "sort_order" in data and data["sort_order"] != preset.sort_order:
        preset.sort_order = data["sort_order"]
    if "is_active" in data and data["is_active"] != preset.is_active:
        preset.is_active = data["is_active"]
    if data:
        preset.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(preset)
    return preset


@router.delete("/{preset_id}", status_code=204)
def delete_preset(
    preset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _Admin,
) -> None:
    """DELETE /v1/presets/{id} — suppression définitive (pas de soft delete)."""
    preset = _get_preset_or_404(db, preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")
    db.delete(preset)
    db.commit()
