# RecyClique API — Router users v1 (Story 3.1, 3.2, 8.1).
# GET/PUT /v1/users/me, PUT /v1/users/me/password, PUT /v1/users/me/pin, GET /v1/users/me/permissions.
# POST /v1/users — création utilisateur par admin (Story 8.1).
# Préfixe monté : /v1

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from api.core.deps import get_current_user, require_permissions
from api.models import User
from api.schemas.user import UserMeResponse, UserMeUpdate, UserMePasswordUpdate, UserMePinUpdate
from api.schemas.admin_user import AdminUserCreate, AdminUserListResponse
from api.db import get_db
from sqlalchemy.orm import Session
from api.services.auth import AuthService
from api.services.permissions import get_user_permission_codes_from_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=AdminUserListResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("admin")),
) -> AdminUserListResponse:
    """POST /v1/users — création utilisateur par admin (Story 8.1)."""
    auth = AuthService(db)
    if auth.get_user_by_username(body.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if auth.get_user_by_email(body.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        username=body.username,
        email=body.email,
        password_hash=auth.hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
        role=body.role,
        status=body.status,
        site_id=body.site_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
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


@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """GET /v1/users/me — profil utilisateur connecté."""
    return current_user


@router.get("/me/permissions", response_model=list[str])
def get_me_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[str]:
    """GET /v1/users/me/permissions — liste des codes de permission de l'utilisateur connecté (pour le front)."""
    codes = get_user_permission_codes_from_user(db, current_user)
    return sorted(codes)


@router.put("/me", response_model=UserMeResponse)
def update_me(
    body: UserMeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """PUT /v1/users/me — mise à jour profil (first_name, last_name, email)."""
    if body.first_name is not None:
        current_user.first_name = body.first_name
    if body.last_name is not None:
        current_user.last_name = body.last_name
    if body.email is not None:
        # Vérifier unicité de l'email avant mise à jour (évite IntegrityError → 500).
        auth = AuthService(db)
        existing = auth.get_user_by_email(body.email)
        if existing is not None and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use by another account",
            )
        current_user.email = body.email
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def update_me_password(
    body: UserMePasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """PUT /v1/users/me/password — changement mot de passe (current + new)."""
    auth = AuthService(db)
    if not auth.verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    current_user.password_hash = auth.hash_password(body.new_password)
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()


@router.put("/me/pin", status_code=status.HTTP_204_NO_CONTENT)
def update_me_pin(
    body: UserMePinUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """PUT /v1/users/me/pin — définition/mise à jour PIN caisse."""
    auth = AuthService(db)
    current_user.pin_hash = auth.hash_pin(body.new_pin)
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
