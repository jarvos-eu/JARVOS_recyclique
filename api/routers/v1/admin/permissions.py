# RecyClique API — Router admin permissions (Story 3.2).
# GET/POST/PUT/DELETE /v1/admin/permissions.

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import Permission, User
from api.schemas.permission import PermissionCreate, PermissionResponse, PermissionUpdate

router = APIRouter()


@router.get("", response_model=list[PermissionResponse])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> list[Permission]:
    """GET /v1/admin/permissions — liste des permissions (codes et libellés)."""
    stmt = select(Permission).order_by(Permission.code)
    return list(db.execute(stmt).scalars().all())


@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> Permission:
    """GET /v1/admin/permissions/{permission_id}"""
    perm = db.get(Permission, permission_id)
    if perm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return perm


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    body: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> Permission:
    """POST /v1/admin/permissions"""
    existing = db.execute(select(Permission).where(Permission.code == body.code)).scalars().one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission code already exists")
    perm = Permission(code=body.code, label=body.label)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


@router.put("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: UUID,
    body: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> Permission:
    """PUT /v1/admin/permissions/{permission_id}"""
    perm = db.get(Permission, permission_id)
    if perm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    if body.code is not None:
        existing = db.execute(
            select(Permission).where(Permission.code == body.code, Permission.id != permission_id)
        ).scalars().one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission code already exists")
        perm.code = body.code
    if body.label is not None:
        perm.label = body.label
    db.commit()
    db.refresh(perm)
    return perm


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> None:
    """DELETE /v1/admin/permissions/{permission_id}. Comportement BDD : CASCADE sur group_permissions
    (migration 001) — les lignes group_permissions liées à cette permission sont supprimées
    automatiquement ; les groupes restent inchangés."""
    perm = db.get(Permission, permission_id)
    if perm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    db.delete(perm)
    db.commit()
