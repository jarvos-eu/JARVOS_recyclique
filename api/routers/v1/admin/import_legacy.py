# Story 8.5 — Import legacy : GET llm-models, POST analyze, preview, validate, execute.
# Protégé par permission admin (ou super_admin).

from fastapi import APIRouter, Depends, UploadFile, File

from api.core.deps import require_permissions
from api.models import User

router = APIRouter(prefix="/import/legacy", tags=["admin-import-legacy"])
_Admin = Depends(require_permissions("admin", "super_admin"))


@router.get("/llm-models")
def get_legacy_llm_models(current_user: User = _Admin) -> dict:
    """GET /v1/admin/import/legacy/llm-models — stub v1 : liste vide."""
    return {"models": []}


@router.post("/analyze")
def post_legacy_analyze(
    current_user: User = _Admin,
    file: UploadFile = File(...),
) -> dict:
    """POST /v1/admin/import/legacy/analyze — stub v1 : structure attendue (colonnes, erreurs)."""
    if not file or not file.filename:
        return {"columns": [], "errors": ["Fichier requis"], "warnings": []}
    return {
        "columns": [],
        "row_count": 0,
        "errors": [],
        "warnings": ["Analyse stub v1 : aucun contenu traite"],
    }


@router.post("/preview")
def post_legacy_preview(current_user: User = _Admin) -> dict:
    """POST /v1/admin/import/legacy/preview — stub v1 : aperçu vide."""
    return {"rows": [], "total": 0}


@router.post("/validate")
def post_legacy_validate(current_user: User = _Admin) -> dict:
    """POST /v1/admin/import/legacy/validate — stub v1 : rapport validation."""
    return {"valid": True, "errors": [], "warnings": []}


@router.post("/execute")
def post_legacy_execute(current_user: User = _Admin) -> dict:
    """POST /v1/admin/import/legacy/execute — stub v1 : résumé exécution."""
    return {"imported_count": 0, "errors": [], "message": "Import legacy (stub v1 : aucune ligne importee)"}
