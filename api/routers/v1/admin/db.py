# Story 8.5 — POST /v1/admin/db/export, purge-transactions, import.
# Permissions (v1) : super_admin OU admin.
# Choix v1 « fallback admin » : tant que la permission super_admin n'existe pas dans le seed
# (api/db/alembic/versions/…_seed_permissions_groups.py), on autorise admin pour ne pas bloquer
# les actions BDD. Quand super_admin sera ajoutée au seed et attribuée à un groupe (ex. admin_technique),
# le code pourra être restreint à super_admin uniquement sans autre changement.

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session

from api.core.deps import require_permissions
from api.db import get_db
from api.models import User
from api.services.audit import write_audit_event

router = APIRouter(prefix="/db", tags=["admin-db"])
# super_admin OU admin (v1 fallback : admin suffit si super_admin absent du seed)
_DbAdmin = Depends(require_permissions("super_admin", "admin"))


@router.post("/export")
def admin_db_export(current_user: User = _DbAdmin) -> Response:
    """POST /v1/admin/db/export — stub v1 : retourne un dump SQL minimal (safe) ou message."""
    # Stub v1 : contenu texte minimal (pas d'exécution BDD réelle pour sécurité tests)
    content = b"-- RecyClique DB export stub v1\n-- Aucune donnee exportee en mode stub.\n"
    return Response(
        content=content,
        media_type="application/sql",
        headers={"Content-Disposition": 'attachment; filename="recyclique-export-stub.sql"'},
    )


@router.post("/purge-transactions")
def admin_db_purge_transactions(
    db: Session = Depends(get_db),
    current_user: User = _DbAdmin,
) -> dict:
    """POST /v1/admin/db/purge-transactions — stub v1 : soft / pas de suppression réelle."""
    # Stub v1 : retourne structure attendue, pas de purge réelle
    result = {
        "message": "Purge transactions (stub v1 : aucune suppression effectuee)",
        "deleted_count": 0,
    }
    write_audit_event(
        db,
        user_id=current_user.id,
        action="admin.db.purge_transactions",
        resource_type="db",
        details="purge-transactions (stub v1)",
    )
    db.commit()
    return result


@router.post("/import")
def admin_db_import(
    db: Session = Depends(get_db),
    current_user: User = _DbAdmin,
    file: UploadFile = File(...),
) -> dict:
    """POST /v1/admin/db/import — stub v1 : validation format uniquement, pas de restauration."""
    # Stub v1 : validation minimale (présence fichier), pas d'exécution
    if not file.filename:
        return {"ok": False, "detail": "Fichier requis"}
    result = {
        "ok": True,
        "message": "Import BDD (stub v1 : validation uniquement, aucune restauration effectuee)",
        "filename": file.filename,
    }
    write_audit_event(
        db,
        user_id=current_user.id,
        action="admin.db.import",
        resource_type="db",
        details=f"import file={file.filename} (stub v1)",
    )
    db.commit()
    return result
