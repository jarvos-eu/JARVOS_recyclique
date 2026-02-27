# RecyClique API — Dépendances partagées (Story 3.1, 3.2).
# get_current_user : validation JWT et injection User sur routes protégées.
# require_permissions : vérification RBAC (au moins une des permissions listées).

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import User
from api.services.auth import AuthService
from api.services.permissions import get_user_permission_codes_from_user

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Dépendance : utilisateur connecté via JWT (Bearer). 401 si absent ou invalide."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    auth = AuthService(db)
    user_id_str = auth.decode_access_token(token)
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = auth.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )
    return user


def require_permissions(
    *permission_codes: str,
):
    """Dépendance : utilisateur connecté ET possédant au moins une des permissions (OR). 403 sinon.
    Usage : current_user = Depends(require_permissions(\"admin\")) ou require_permissions(\"caisse.access\", \"admin\").
    """

    def _check(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if not permission_codes:
            return current_user
        codes = get_user_permission_codes_from_user(db, current_user)
        if not codes.intersection(set(permission_codes)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check
