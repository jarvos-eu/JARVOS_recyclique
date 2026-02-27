# RecyClique API — Router auth v1 (Story 3.1, 3.3).
# POST /v1/auth/login, refresh, logout, signup, forgot-password, reset-password, pin.
# 3.3 : PIN restreint aux utilisateurs avec permission caisse ; audit déverrouillage.

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import User, RegistrationRequest, AuditEvent
from api.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PinLoginRequest,
    SignupRequest,
    UserInToken,
)
from api.services.auth import AuthService
from api.services.permissions import get_user_permission_codes_from_user

router = APIRouter(tags=["auth"])

# Permission requise pour déverrouillage caisse par PIN (Story 3.3)
CAISSE_ACCESS_PERMISSION = "caisse.access"


def _user_to_in_token(user: User) -> UserInToken:
    return UserInToken(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role,
        status=user.status,
        first_name=user.first_name,
        last_name=user.last_name,
    )


def _make_login_response(
    auth: AuthService, user: User, access_token: str, refresh_token: str, db: Session
) -> LoginResponse:
    codes = get_user_permission_codes_from_user(db, user)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=_user_to_in_token(user),
        permissions=list(codes),
    )


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """POST /v1/auth/login — identifiants → JWT access + refresh."""
    auth = AuthService(db)
    user = auth.get_user_by_username(body.username)
    if user is None:
        auth.log_login(
            None, body.username, False,
            request.client.host if request.client else None,
            request.headers.get("user-agent"),
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not auth.verify_password(body.password, user.password_hash):
        auth.log_login(
            user.id, body.username, False,
            request.client.host if request.client else None,
            request.headers.get("user-agent"),
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")
    auth.log_login(
        user.id, body.username, True,
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    access_token = auth.create_access_token(user.id)
    refresh_token = auth.create_refresh_token()
    auth.create_session(user.id, refresh_token)
    return _make_login_response(auth, user, access_token, refresh_token, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    body: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """POST /v1/auth/refresh — refresh_token → nouveaux access + refresh."""
    auth = AuthService(db)
    session = auth.find_session_by_refresh_token(body.refresh_token)
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    user = auth.get_user_by_id(session.user_id)
    if user is None or user.status != "active":
        auth.delete_session(session)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    auth.delete_session(session)
    access_token = auth.create_access_token(user.id)
    new_refresh = auth.create_refresh_token()
    auth.create_session(user.id, new_refresh)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    body: RefreshRequest,
    db: Session = Depends(get_db),
) -> None:
    """POST /v1/auth/logout — invalide la session (refresh_token)."""
    auth = AuthService(db)
    session = auth.find_session_by_refresh_token(body.refresh_token)
    if session is not None:
        auth.delete_session(session)


@router.post("/pin", response_model=LoginResponse)
def login_with_pin(
    body: PinLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """POST /v1/auth/pin — connexion caisse / tablette par PIN → même JWT que login.

    Risque v1 accepté : on charge tous les utilisateurs actifs avec PIN puis on vérifie
    le PIN en boucle → coût O(n) et fuite de timing (réponse plus lente si beaucoup d’users).
    TODO (suite) : ajouter rate limit sur cet endpoint et/ou requête ciblée / index
    pour éviter le scan complet (ex. table dédiée PIN → user_id si besoin).
    """
    auth = AuthService(db)
    users_with_pin = db.execute(
        select(User).where(and_(User.pin_hash.isnot(None), User.status == "active"))
    ).scalars().all()
    found = None
    for u in users_with_pin:
        if auth.verify_pin(body.pin, u.pin_hash):
            found = u
            break
    if found is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid PIN")
    # Story 3.3 : restriction aux opérateurs avec permission caisse
    codes = get_user_permission_codes_from_user(db, found)
    if CAISSE_ACCESS_PERMISSION not in codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    auth.log_login(
        found.id, found.username, True,
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    access_token = auth.create_access_token(found.id)
    refresh_token = auth.create_refresh_token()
    # Une seule transaction : session + audit (éviter session sans événement audit si commit audit échoue)
    auth.add_session_no_commit(found.id, refresh_token)
    # resource_id : null en v1 ; à renseigner avec register_id quand disponible (Story 3.4)
    evt = AuditEvent(
        user_id=found.id,
        action="session_unlocked",
        resource_type="caisse",
        resource_id=None,
        details=None,
    )
    db.add(evt)
    db.commit()
    return _make_login_response(auth, found, access_token, refresh_token, db)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(
    body: SignupRequest,
    db: Session = Depends(get_db),
) -> dict:
    """POST /v1/auth/signup — inscription → registration_request (workflow approbation)."""
    auth = AuthService(db)
    if auth.get_user_by_username(body.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if auth.get_user_by_email(body.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    existing = db.execute(
        select(RegistrationRequest).where(
            RegistrationRequest.status == "pending",
        ).where(
            or_(
                RegistrationRequest.username == body.username,
                RegistrationRequest.email == body.email,
            )
        )
    ).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration already pending")
    password_hash = auth.hash_password(body.password)
    auth.create_registration_request(
        username=body.username,
        email=body.email,
        password_hash=password_hash,
        first_name=body.first_name,
        last_name=body.last_name,
    )
    return {"message": "Registration request submitted. Awaiting approval."}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> dict:
    """POST /v1/auth/forgot-password — demande reset (email Brevo si applicable). Stub v1."""
    auth = AuthService(db)
    user = auth.get_user_by_email(body.email)
    if user is None:
        return {"message": "If the email exists, a reset link will be sent."}
    # TODO: générer token reset, envoyer email via Brevo
    return {"message": "If the email exists, a reset link will be sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> dict:
    """POST /v1/auth/reset-password — nouveau mot de passe avec token (JWT type=reset)."""
    from jose import jwt as jose_jwt, JWTError
    from api.config import get_settings
    auth = AuthService(db)
    settings = get_settings()
    try:
        payload = jose_jwt.decode(
            body.token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "reset":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
        user_id = UUID(payload["sub"])
        user = auth.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
        user.password_hash = auth.hash_password(body.new_password)
        db.commit()
        return {"message": "Password reset successfully."}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
