# Story 8.6 — GET /v1/admin/paheko-compta-url (URL admin Paheko pour compta, admin only).

from urllib.parse import urlparse, urlunparse

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.config.settings import get_settings
from api.core.deps import require_permissions
from api.models import User

router = APIRouter(tags=["admin-paheko-compta"])
_Admin = Depends(require_permissions("admin"))


class PahekoComptaUrlResponse(BaseModel):
    """URL de l'interface d'administration Paheko (section Comptabilité)."""
    url: str


def _paheko_admin_base_url(plugin_url: str | None) -> str | None:
    """Dérive l'URL admin Paheko (origine + /admin/) depuis PAHEKO_PLUGIN_URL."""
    if not plugin_url or not plugin_url.strip():
        return None
    parsed = urlparse(plugin_url)
    # origine = scheme + netloc (sans path)
    base = urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))
    return f"{base.rstrip('/')}/admin/"


@router.get("/paheko-compta-url", response_model=PahekoComptaUrlResponse)
def get_paheko_compta_url(current_user: User = _Admin) -> PahekoComptaUrlResponse:
    """GET /v1/admin/paheko-compta-url — URL pour accéder à l'admin compta Paheko (admin only)."""
    settings = get_settings()
    url = _paheko_admin_base_url(settings.paheko_plugin_url)
    if not url:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Paheko URL not configured")
    return PahekoComptaUrlResponse(url=url)
