"""Router admin — stub pour Story 1.2. Health check est dans admin/health.py, monté à la racine (GET /health)."""

from fastapi import APIRouter

from api.core.modules.loader import get_loaded_modules

router = APIRouter(tags=["admin"])


@router.get("/")
def admin_root() -> dict:
    """Stub : module admin monté sous /api/admin."""
    return {"module": "admin"}


@router.get("/diagnostic/modules")
def diagnostic_modules() -> dict:
    """Liste des modules chargés au démarrage (loader TOML / ModuleBase). Optionnel pour diagnostic."""
    modules = list(get_loaded_modules().keys())
    return {"modules": modules}
