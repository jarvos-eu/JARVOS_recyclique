# RecyClique API — Router admin users (Story 8.1).
# GET/POST/PUT /v1/admin/users (liste, détail, pending, approve/reject, role, status, groupes, history, reset-password, reset-pin).

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, or_, delete
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import (
    User,
    Group,
    RegistrationRequest,
    AuditEvent,
    UserSession,
    user_groups,
)
from api.schemas.admin_user import (
    AdminUserListResponse,
    AdminUserDetailResponse,
    AdminPendingUserResponse,
    AdminUserRoleUpdate,
    AdminUserStatusUpdate,
    AdminUserProfileUpdate,
    AdminUserGroupsUpdate,
    AdminApproveRejectBody,
    AuditEventResponse,
    AdminUsersStatusesResponse,
    AdminResetPasswordBody,
    AdminResetPinBody,
)
from api.services.audit import write_audit_event
from api.services.auth import AuthService

router = APIRouter()


def _user_list_from_orm(user: User) -> AdminUserListResponse:
    return AdminUserListResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        status=user.status,
        site_id=user.site_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("", response_model=list[AdminUserListResponse])
def list_users(
    role: str | None = Query(None, alias="role"),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1, alias="page"),
    page_size: int = Query(20, ge=1, le=100, alias="page_size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> list[AdminUserListResponse]:
    """GET /v1/admin/users — liste avec filtres rôle, statut, pagination (query snake_case)."""
    stmt = select(User).order_by(User.username)
    if role is not None:
        stmt = stmt.where(User.role == role)
    if status_filter is not None:
        stmt = stmt.where(User.status == status_filter)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    users = list(db.execute(stmt).scalars().all())
    return [_user_list_from_orm(u) for u in users]


@router.get("/statuses", response_model=AdminUsersStatusesResponse)
def get_users_statuses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> AdminUsersStatusesResponse:
    """GET /v1/admin/users/statuses — ids des utilisateurs avec session active (en ligne)."""
    now = datetime.now(timezone.utc)
    subq = (
        select(UserSession.user_id)
        .where(UserSession.expires_at > now)
        .distinct()
    )
    rows = db.execute(subq).all()
    online_user_ids = [r[0] for r in rows]
    return AdminUsersStatusesResponse(online_user_ids=online_user_ids)


@router.get("/pending", response_model=list[AdminPendingUserResponse])
def list_pending(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> list[AdminPendingUserResponse]:
    """GET /v1/admin/users/pending — inscriptions en attente (registration_request)."""
    stmt = (
        select(RegistrationRequest)
        .where(RegistrationRequest.status == "pending")
        .order_by(RegistrationRequest.requested_at.desc())
    )
    reqs = list(db.execute(stmt).scalars().all())
    return [
        AdminPendingUserResponse(
            id=r.id,
            username=r.username,
            email=r.email,
            first_name=r.first_name,
            last_name=r.last_name,
            status=r.status,
            requested_at=r.requested_at,
        )
        for r in reqs
    ]


@router.post("/approve", status_code=status.HTTP_201_CREATED)
def approve_registration(
    body: AdminApproveRejectBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> dict:
    """POST /v1/admin/users/approve — approuver une inscription (crée l'utilisateur)."""
    req = db.get(RegistrationRequest, body.registration_request_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration request not found")
    if req.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already processed")
    auth = AuthService(db)
    if auth.get_user_by_username(req.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    if auth.get_user_by_email(req.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        username=req.username,
        email=req.email,
        password_hash=req.password_hash,
        first_name=req.first_name,
        last_name=req.last_name,
        role="operator",
        status="active",
    )
    db.add(user)
    db.flush()
    req.status = "approved"
    req.reviewed_at = datetime.now(timezone.utc)
    req.reviewed_by_id = current_user.id
    write_audit_event(
        db,
        user_id=current_user.id,
        action="user_approved",
        resource_type="registration_request",
        resource_id=str(req.id),
        details=f"Created user {user.id}",
    )
    db.commit()
    db.refresh(user)
    return {"message": "User approved", "user_id": str(user.id)}


@router.post("/reject", status_code=status.HTTP_200_OK)
def reject_registration(
    body: AdminApproveRejectBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> dict:
    """POST /v1/admin/users/reject — rejeter une inscription."""
    req = db.get(RegistrationRequest, body.registration_request_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration request not found")
    if req.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already processed")
    req.status = "rejected"
    req.reviewed_at = datetime.now(timezone.utc)
    req.reviewed_by_id = current_user.id
    write_audit_event(
        db,
        user_id=current_user.id,
        action="registration_rejected",
        resource_type="registration_request",
        resource_id=str(req.id),
        details=None,
    )
    db.commit()
    return {"message": "Registration rejected"}


@router.get("/{user_id}", response_model=AdminUserDetailResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> AdminUserDetailResponse:
    """GET /v1/admin/users/{user_id} — détail utilisateur avec group_ids."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    group_ids = [g.id for g in user.groups]
    return AdminUserDetailResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        status=user.status,
        site_id=user.site_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        group_ids=group_ids,
    )


@router.get("/{user_id}/history", response_model=list[AuditEventResponse])
def get_user_history(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> list[AuditEventResponse]:
    """GET /v1/admin/users/{user_id}/history — historique des actions sur l'utilisateur."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    stmt = (
        select(AuditEvent)
        .where(
            or_(
                AuditEvent.user_id == user_id,
                and_(
                    AuditEvent.resource_type == "user",
                    AuditEvent.resource_id == str(user_id),
                ),
            )
        )
        .order_by(AuditEvent.timestamp.desc())
        .limit(100)
    )
    events = list(db.execute(stmt).scalars().all())
    return [AuditEventResponse.model_validate(e) for e in events]


@router.put("/{user_id}/role", response_model=AdminUserListResponse)
def update_user_role(
    user_id: UUID,
    body: AdminUserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> AdminUserListResponse:
    """PUT /v1/admin/users/{user_id}/role — modifier le rôle."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    old_role = user.role
    user.role = body.role
    user.updated_at = datetime.now(timezone.utc)
    write_audit_event(
        db,
        user_id=current_user.id,
        action="user_role_updated",
        resource_type="user",
        resource_id=str(user_id),
        details=f"role {old_role} -> {body.role}",
    )
    db.commit()
    db.refresh(user)
    return _user_list_from_orm(user)


@router.put("/{user_id}/status", response_model=AdminUserListResponse)
def update_user_status(
    user_id: UUID,
    body: AdminUserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> AdminUserListResponse:
    """PUT /v1/admin/users/{user_id}/status — modifier le statut."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    old_status = user.status
    user.status = body.status
    user.updated_at = datetime.now(timezone.utc)
    write_audit_event(
        db,
        user_id=current_user.id,
        action="user_status_updated",
        resource_type="user",
        resource_id=str(user_id),
        details=f"status {old_status} -> {body.status}",
    )
    db.commit()
    db.refresh(user)
    return _user_list_from_orm(user)


@router.put("/{user_id}", response_model=AdminUserDetailResponse)
def update_user_profile(
    user_id: UUID,
    body: AdminUserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> AdminUserDetailResponse:
    """PUT /v1/admin/users/{user_id} — mise à jour profil (first_name, last_name, email, role, status, site_id)."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    auth = AuthService(db)
    if body.email is not None:
        existing = auth.get_user_by_email(body.email)
        if existing is not None and existing.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        user.email = body.email
    if body.first_name is not None:
        user.first_name = body.first_name
    if body.last_name is not None:
        user.last_name = body.last_name
    if body.role is not None:
        user.role = body.role
    if body.status is not None:
        user.status = body.status
    if body.site_id is not None:
        user.site_id = body.site_id
    user.updated_at = datetime.now(timezone.utc)
    write_audit_event(
        db,
        user_id=current_user.id,
        action="user_profile_updated",
        resource_type="user",
        resource_id=str(user_id),
        details=None,
    )
    db.commit()
    db.refresh(user)
    group_ids = [g.id for g in user.groups]
    return AdminUserDetailResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        status=user.status,
        site_id=user.site_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        group_ids=group_ids,
    )


@router.put("/{user_id}/groups", response_model=AdminUserDetailResponse)
def update_user_groups(
    user_id: UUID,
    body: AdminUserGroupsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> AdminUserDetailResponse:
    """PUT /v1/admin/users/{user_id}/groups — affectation groupes (remplace la liste)."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    for gid in body.group_ids:
        if db.get(Group, gid) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Group {gid} not found")
    db.execute(delete(user_groups).where(user_groups.c.user_id == user_id))
    for gid in body.group_ids:
        db.execute(user_groups.insert().values(user_id=user_id, group_id=gid))
    write_audit_event(
        db,
        user_id=current_user.id,
        action="user_groups_updated",
        resource_type="user",
        resource_id=str(user_id),
        details=f"group_ids={[str(g) for g in body.group_ids]}",
    )
    db.commit()
    db.refresh(user)
    group_ids = [g.id for g in user.groups]
    return AdminUserDetailResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        status=user.status,
        site_id=user.site_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        group_ids=group_ids,
    )


@router.post("/{user_id}/reset-password", status_code=status.HTTP_200_OK)
def reset_user_password(
    user_id: UUID,
    body: AdminResetPasswordBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> dict:
    """POST /v1/admin/users/{user_id}/reset-password — forcer un nouveau mot de passe (admin)."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    auth = AuthService(db)
    user.password_hash = auth.hash_password(body.new_password)
    user.updated_at = datetime.now(timezone.utc)
    write_audit_event(
        db,
        user_id=current_user.id,
        action="user_password_reset",
        resource_type="user",
        resource_id=str(user_id),
        details=None,
    )
    db.commit()
    return {"message": "Password reset"}


@router.post("/{user_id}/reset-pin", status_code=status.HTTP_200_OK)
def reset_user_pin(
    user_id: UUID,
    body: AdminResetPinBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> dict:
    """POST /v1/admin/users/{user_id}/reset-pin — réinitialiser le PIN caisse."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    auth = AuthService(db)
    user.pin_hash = auth.hash_pin(body.new_pin)
    user.updated_at = datetime.now(timezone.utc)
    write_audit_event(
        db,
        user_id=current_user.id,
        action="user_pin_reset",
        resource_type="user",
        resource_id=str(user_id),
        details=None,
    )
    db.commit()
    return {"message": "PIN reset"}
