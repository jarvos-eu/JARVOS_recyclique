# Story 8.4 — GET/PUT /v1/admin/settings (stub v1 minimal).

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.core.deps import require_permissions
from api.models import User

router = APIRouter(prefix="/settings", tags=["admin-settings"])
_Admin = Depends(require_permissions("admin"))


class SettingsResponse(BaseModel):
    """Stub : paramètres opérationnels (lecture)."""
    alert_thresholds: dict | None = None
    session: dict | None = None
    email: dict | None = None
    activity_threshold: float | None = None


class SettingsUpdateBody(BaseModel):
    """Body partiel pour PUT /v1/admin/settings."""
    alert_thresholds: dict | None = None
    session: dict | None = None
    email: dict | None = None
    activity_threshold: float | None = None


@router.get("", response_model=SettingsResponse)
def get_settings(current_user: User = _Admin) -> SettingsResponse:
    """GET /v1/admin/settings — lecture paramètres (stub v1)."""
    return SettingsResponse(
        alert_thresholds={},
        session={},
        email={},
        activity_threshold=None,
    )


@router.put("", response_model=SettingsResponse)
def put_settings(
    body: SettingsUpdateBody,
    current_user: User = _Admin,
) -> SettingsResponse:
    """PUT /v1/admin/settings — mise à jour (stub v1, pas de persistance)."""
    return SettingsResponse(
        alert_thresholds=body.alert_thresholds,
        session=body.session,
        email=body.email,
        activity_threshold=body.activity_threshold,
    )


@router.post("/email/test")
def post_settings_email_test(current_user: User = _Admin) -> dict:
    """POST /v1/admin/settings/email/test — envoi email de test (stub v1)."""
    return {"message": "Email de test envoyé (stub v1)"}
