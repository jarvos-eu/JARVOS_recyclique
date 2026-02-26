"""Router categories — CRUD, hiérarchie, visibilité, ordre, soft delete (Story 2.3)."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import Category
from api.schemas.category import (
    CategoryCreate,
    CategoryDisplayOrderUpdate,
    CategoryHierarchyNode,
    CategoryResponse,
    CategoryUpdate,
    CategoryVisibilityUpdate,
)

router = APIRouter(prefix="/categories", tags=["categories"])


def _get_category_or_404(db: Session, category_id: UUID, include_deleted: bool = False) -> Category | None:
    q = select(Category).where(Category.id == category_id)
    if not include_deleted:
        q = q.where(Category.deleted_at.is_(None))
    return db.execute(q).scalars().one_or_none()


def _get_descendant_ids(db: Session, category_id: UUID, include_deleted: bool = False) -> set[UUID]:
    """Retourne l'ensemble des ids des descendants (enfants récursifs) pour éviter les cycles."""
    q = select(Category.id).where(Category.parent_id == category_id)
    if not include_deleted:
        q = q.where(Category.deleted_at.is_(None))
    child_ids = {row[0] for row in db.execute(q).all()}
    descendant_ids = set(child_ids)
    for cid in child_ids:
        descendant_ids |= _get_descendant_ids(db, cid, include_deleted)
    return descendant_ids


def _category_to_hierarchy_node(cat: Category, include_deleted: bool = False) -> CategoryHierarchyNode:
    children = [
        _category_to_hierarchy_node(c, include_deleted)
        for c in sorted(cat.children, key=lambda x: (x.display_order, x.name))
        if include_deleted or c.deleted_at is None
    ]
    return CategoryHierarchyNode(
        id=cat.id,
        name=cat.name,
        parent_id=cat.parent_id,
        official_name=cat.official_name,
        is_visible_sale=cat.is_visible_sale,
        is_visible_reception=cat.is_visible_reception,
        display_order=cat.display_order,
        display_order_entry=cat.display_order_entry,
        deleted_at=cat.deleted_at,
        children=children,
    )


# ——— Liste et hiérarchie (avant /{id}) ———

@router.get("", response_model=list[CategoryResponse])
def list_categories(
    include_deleted: bool = False,
    parent_id: UUID | None = None,
    is_visible_sale: bool | None = None,
    is_visible_reception: bool | None = None,
    db: Session = Depends(get_db),
) -> list[Category]:
    """GET /v1/categories — liste (filtres optionnels). Par défaut exclut les supprimées."""
    q = select(Category)
    if not include_deleted:
        q = q.where(Category.deleted_at.is_(None))
    if parent_id is not None:
        q = q.where(Category.parent_id == parent_id)
    if is_visible_sale is not None:
        q = q.where(Category.is_visible_sale == is_visible_sale)
    if is_visible_reception is not None:
        q = q.where(Category.is_visible_reception == is_visible_reception)
    q = q.order_by(Category.display_order, Category.name)
    return list(db.execute(q).scalars().all())


@router.get("/hierarchy", response_model=list[CategoryHierarchyNode])
def get_categories_hierarchy(
    include_deleted: bool = False,
    db: Session = Depends(get_db),
) -> list[CategoryHierarchyNode]:
    """GET /v1/categories/hierarchy — arborescence (racines avec enfants)."""
    q = select(Category).where(Category.parent_id.is_(None))
    if not include_deleted:
        q = q.where(Category.deleted_at.is_(None))
    roots = list(db.execute(q).scalars().all())
    return [_category_to_hierarchy_node(r, include_deleted) for r in sorted(roots, key=lambda x: (x.display_order, x.name))]


@router.get("/sale-tickets", response_model=list[CategoryResponse])
def get_categories_sale_tickets(db: Session = Depends(get_db)) -> list[Category]:
    """GET /v1/categories/sale-tickets — catégories visibles en caisse, non supprimées, tri display_order."""
    q = (
        select(Category)
        .where(Category.is_visible_sale == True)
        .where(Category.deleted_at.is_(None))
        .order_by(Category.display_order, Category.name)
    )
    return list(db.execute(q).scalars().all())


@router.get("/entry-tickets", response_model=list[CategoryResponse])
def get_categories_entry_tickets(db: Session = Depends(get_db)) -> list[Category]:
    """GET /v1/categories/entry-tickets — catégories visibles en réception, non supprimées, tri display_order_entry."""
    q = (
        select(Category)
        .where(Category.is_visible_reception == True)
        .where(Category.deleted_at.is_(None))
        .order_by(Category.display_order_entry, Category.name)
    )
    return list(db.execute(q).scalars().all())


# ——— CRUD par id ———

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: UUID,
    include_deleted: bool = False,
    db: Session = Depends(get_db),
) -> Category:
    """GET /v1/categories/{id} — détail (404 si absent)."""
    cat = _get_category_or_404(db, category_id, include_deleted=include_deleted)
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(body: CategoryCreate, db: Session = Depends(get_db)) -> Category:
    """POST /v1/categories — création."""
    if body.parent_id is not None:
        parent = _get_category_or_404(db, body.parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent category not found")
    cat = Category(
        name=body.name,
        parent_id=body.parent_id,
        official_name=body.official_name,
        is_visible_sale=body.is_visible_sale,
        is_visible_reception=body.is_visible_reception,
        display_order=body.display_order,
        display_order_entry=body.display_order_entry,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: UUID,
    body: CategoryUpdate,
    db: Session = Depends(get_db),
) -> Category:
    """PUT /v1/categories/{id} — mise à jour complète (champs fournis)."""
    cat = _get_category_or_404(db, category_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if body.parent_id is not None:
        if body.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Parent cannot be self")
        if body.parent_id in _get_descendant_ids(db, category_id):
            raise HTTPException(status_code=400, detail="Parent would create a cycle")
        parent = _get_category_or_404(db, body.parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent category not found")
    changed = False
    if body.name is not None and body.name != cat.name:
        cat.name = body.name
        changed = True
    if body.parent_id is not None and body.parent_id != cat.parent_id:
        cat.parent_id = body.parent_id
        changed = True
    if body.official_name is not None and body.official_name != cat.official_name:
        cat.official_name = body.official_name
        changed = True
    if body.is_visible_sale is not None and body.is_visible_sale != cat.is_visible_sale:
        cat.is_visible_sale = body.is_visible_sale
        changed = True
    if body.is_visible_reception is not None and body.is_visible_reception != cat.is_visible_reception:
        cat.is_visible_reception = body.is_visible_reception
        changed = True
    if body.display_order is not None and body.display_order != cat.display_order:
        cat.display_order = body.display_order
        changed = True
    if body.display_order_entry is not None and body.display_order_entry != cat.display_order_entry:
        cat.display_order_entry = body.display_order_entry
        changed = True
    if changed:
        cat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: UUID, db: Session = Depends(get_db)) -> None:
    """DELETE /v1/categories/{id} — soft delete (deleted_at)."""
    cat = _get_category_or_404(db, category_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.deleted_at = datetime.now(timezone.utc)
    cat.updated_at = datetime.now(timezone.utc)
    db.commit()


@router.post("/{category_id}/restore", response_model=CategoryResponse)
def restore_category(category_id: UUID, db: Session = Depends(get_db)) -> Category:
    """POST /v1/categories/{id}/restore — remet deleted_at à null."""
    cat = db.execute(select(Category).where(Category.id == category_id)).scalars().one_or_none()
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.deleted_at is None:
        raise HTTPException(status_code=400, detail="Category is not deleted")
    cat.deleted_at = None
    cat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{category_id}/visibility", response_model=CategoryResponse)
def update_category_visibility(
    category_id: UUID,
    body: CategoryVisibilityUpdate,
    db: Session = Depends(get_db),
) -> Category:
    """PUT /v1/categories/{id}/visibility — met à jour is_visible_sale / is_visible_reception."""
    cat = _get_category_or_404(db, category_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if body.is_visible_sale is not None:
        cat.is_visible_sale = body.is_visible_sale
    if body.is_visible_reception is not None:
        cat.is_visible_reception = body.is_visible_reception
    cat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{category_id}/display-order", response_model=CategoryResponse)
def update_category_display_order(
    category_id: UUID,
    body: CategoryDisplayOrderUpdate,
    db: Session = Depends(get_db),
) -> Category:
    """PUT /v1/categories/{id}/display-order — met à jour display_order et/ou display_order_entry."""
    cat = _get_category_or_404(db, category_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if body.display_order is not None:
        cat.display_order = body.display_order
    if body.display_order_entry is not None:
        cat.display_order_entry = body.display_order_entry
    cat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cat)
    return cat
