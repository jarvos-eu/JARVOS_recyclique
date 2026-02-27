# RecyClique API — Router admin groups (Story 3.2).
# GET/POST/PUT/DELETE /v1/admin/groups, liaisons groupe-permissions et groupe-utilisateurs.

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import Group, Permission, User, user_groups, group_permissions
from api.schemas.group import (
    GroupCreate,
    GroupDetailResponse,
    GroupPermissionsBody,
    GroupResponse,
    GroupUpdate,
    GroupUsersBody,
)

router = APIRouter()


@router.get("", response_model=list[GroupResponse])
def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> list[Group]:
    """GET /v1/admin/groups — liste des groupes."""
    stmt = select(Group).order_by(Group.name)
    return list(db.execute(stmt).scalars().all())


@router.get("/{group_id}", response_model=GroupDetailResponse)
def get_group(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> GroupDetailResponse:
    """GET /v1/admin/groups/{group_id} — détail (permissions, utilisateurs)."""
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    permission_ids = [p.id for p in group.permissions]
    user_ids = [u.id for u in group.users]
    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_at=group.created_at,
        updated_at=group.updated_at,
        permission_ids=permission_ids,
        user_ids=user_ids,
    )


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    body: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> Group:
    """POST /v1/admin/groups — création d'un groupe."""
    existing = db.execute(select(Group).where(Group.name == body.name)).scalars().one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group name already exists")
    group = Group(name=body.name, description=body.description)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: UUID,
    body: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> Group:
    """PUT /v1/admin/groups/{group_id} — mise à jour."""
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    if body.name is not None:
        other = db.execute(select(Group).where(Group.name == body.name, Group.id != group_id)).scalars().one_or_none()
        if other:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group name already exists")
        group.name = body.name
    if body.description is not None:
        group.description = body.description
    db.commit()
    db.refresh(group)
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> None:
    """DELETE /v1/admin/groups/{group_id}."""
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    db.delete(group)
    db.commit()


@router.post("/{group_id}/permissions", status_code=status.HTTP_204_NO_CONTENT)
def add_group_permissions(
    group_id: UUID,
    body: GroupPermissionsBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> None:
    """POST /v1/admin/groups/{group_id}/permissions — ajouter permission(s) au groupe (body: permission_id ou permission_ids)."""
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    ids_to_add = list(body.permission_ids) if body.permission_ids else []
    if body.permission_id is not None:
        ids_to_add.append(body.permission_id)
    for perm_id in ids_to_add:
        perm = db.get(Permission, perm_id)
        if perm is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Permission {perm_id} not found")
        existing = db.execute(
            select(group_permissions).where(
                group_permissions.c.group_id == group_id,
                group_permissions.c.permission_id == perm_id,
            )
        ).first()
        if not existing:
            db.execute(group_permissions.insert().values(group_id=group_id, permission_id=perm_id))
    db.commit()


@router.delete("/{group_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_group_permission(
    group_id: UUID,
    permission_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> None:
    """DELETE /v1/admin/groups/{group_id}/permissions/{permission_id}."""
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    stmt = delete(group_permissions).where(
        group_permissions.c.group_id == group_id,
        group_permissions.c.permission_id == permission_id,
    )
    db.execute(stmt)
    db.commit()


@router.post("/{group_id}/users", status_code=status.HTTP_204_NO_CONTENT)
def add_group_users(
    group_id: UUID,
    body: GroupUsersBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> None:
    """POST /v1/admin/groups/{group_id}/users — ajouter utilisateur(s) au groupe (body: user_id ou user_ids)."""
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    ids_to_add = list(body.user_ids) if body.user_ids else []
    if body.user_id is not None:
        ids_to_add.append(body.user_id)
    for uid in ids_to_add:
        user = db.get(User, uid)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {uid} not found")
        existing = db.execute(
            select(user_groups).where(
                user_groups.c.group_id == group_id,
                user_groups.c.user_id == uid,
            )
        ).first()
        if not existing:
            db.execute(user_groups.insert().values(user_id=uid, group_id=group_id))
    db.commit()


@router.delete("/{group_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_group_user(
    group_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> None:
    """DELETE /v1/admin/groups/{group_id}/users/{user_id}."""
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    stmt = delete(user_groups).where(
        user_groups.c.group_id == group_id,
        user_groups.c.user_id == user_id,
    )
    db.execute(stmt)
    db.commit()
