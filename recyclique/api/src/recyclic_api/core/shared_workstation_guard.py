"""
Garde API poste partagé (Epic 27.2) — refus frontière sans opérateur actif.

En-têtes optionnels (évolution 25.8) :
- ``X-Recyclique-Device-Id`` : UUID poste annoncé — comparé à la vérité serveur si présent.
- ``X-Recyclique-Context-Module-Key`` : module annoncé — doit matcher ``active_module_key`` si session active.

L'opérateur actif provient uniquement de la session serveur, jamais d'un en-tête client non signé.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from recyclic_api.core.audit import (
    log_device_identity_conflict,
    log_shared_workstation_access_refused,
    log_shared_workstation_context_invalidated,
)
from recyclic_api.core.auth import get_current_user
from recyclic_api.core.context_binding_guard import CONTEXT_STALE_CODE
from recyclic_api.core.database import get_db
from recyclic_api.models.user import User
from recyclic_api.schemas.shared_workstation_context import SharedWorkstationContextOut
from recyclic_api.services.registered_device_credential_service import (
    RegisteredDeviceCredentialService,
)
from recyclic_api.services.shared_workstation_context_service import (
    SharedWorkstationContextService,
)
from recyclic_api.services.shared_workstation_effective_modules_service import (
    SharedWorkstationEffectiveModulesService,
)
from recyclic_api.modules.module_config.registry import MODULE_KEY_RECEPTION
from recyclic_api.services.device_operator_session_service import DeviceOperatorSessionService
from recyclic_api.services.reception_service import SharedWorkstationReceptionScope

HEADER_DEVICE_ID = "X-Recyclique-Device-Id"
HEADER_DEVICE_CREDENTIAL = "X-Recyclique-Device-Credential"
HEADER_CONTEXT_MODULE_KEY = "X-Recyclique-Context-Module-Key"

SHARED_WORKSTATION_OPERATOR_REQUIRED = "SHARED_WORKSTATION_OPERATOR_REQUIRED"
SHARED_WORKSTATION_DEVICE_INVALID = "SHARED_WORKSTATION_DEVICE_INVALID"
DEVICE_CREDENTIAL_REVOKED = "DEVICE_CREDENTIAL_REVOKED"
DEVICE_IDENTITY_CONFLICT = "DEVICE_IDENTITY_CONFLICT"


def _request_id(request: Request) -> Optional[str]:
    return request.headers.get("X-Request-Id") or request.headers.get("X-Correlation-Id")


def _norm(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def extract_device_id(
    *,
    request: Request,
    x_recyclique_device_id: Optional[str] = Header(None, alias=HEADER_DEVICE_ID),
    device_id_query: Optional[str] = None,
) -> str:
    """En-tête prioritaire sur query param."""
    raw = (x_recyclique_device_id or "").strip() or (device_id_query or "").strip()
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": (
                    f"Identifiant poste requis via en-tête {HEADER_DEVICE_ID} "
                    "ou paramètre device_id."
                ),
            },
        )
    try:
        uuid.UUID(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "device_id doit être un UUID valide.",
            },
        ) from exc
    return raw


def verify_device_credential_or_raise(
    *,
    request: Request,
    db: Session,
    device_id: str,
    credential: Optional[str],
    require_credential: bool = True,
) -> None:
    """
    Valide le couple device_id + credential (Epic 27.4).
    Lève HTTPException 403 si révoqué, conflit ou désalignement.
    """
    if not credential or not credential.strip():
        if require_credential:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": DEVICE_CREDENTIAL_REVOKED,
                    "message": "Credential device requis",
                },
            )
        return

    service = RegisteredDeviceCredentialService(db)
    result = service.verify(device_id=device_id, secret=credential.strip())
    req_id = _request_id(request)

    if result.credential is not None and not result.revoked:
        if result.device is not None:
            service.touch_last_contact(device=result.device)
            db.commit()
        return

    if result.conflict_detected and result.device is not None:
        service.mark_device_conflict_if_needed(device=result.device)
        log_device_identity_conflict(
            db=db,
            device_id=str(result.device.id),
            site_id=str(result.device.site_id),
            request_id=req_id,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": DEVICE_IDENTITY_CONFLICT,
                "message": "Identité poste en conflit — contacter un administrateur",
            },
        )

    if result.revoked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": DEVICE_CREDENTIAL_REVOKED,
                "message": "Credential device révoqué ou invalide",
            },
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": DEVICE_IDENTITY_CONFLICT,
            "message": "Credential device invalide pour ce poste",
        },
    )


def require_valid_device_credential(
    request: Request,
    db: Session = Depends(get_db),
    x_recyclique_device_id: Optional[str] = Header(None, alias=HEADER_DEVICE_ID),
    x_recyclique_device_credential: Optional[str] = Header(
        None, alias=HEADER_DEVICE_CREDENTIAL
    ),
    device_id: Optional[str] = None,
) -> str:
    """Dependency : device_id + credential valides (sans session opérateur)."""
    resolved_device_id = extract_device_id(
        request=request,
        x_recyclique_device_id=x_recyclique_device_id,
        device_id_query=device_id,
    )
    verify_device_credential_or_raise(
        request=request,
        db=db,
        device_id=resolved_device_id,
        credential=x_recyclique_device_credential,
        require_credential=True,
    )
    return resolved_device_id


def assert_context_fresh(
    *,
    request: Request,
    db: Session,
    device_id: str,
    resolved: SharedWorkstationContextOut,
    actor_user_id: Optional[str] = None,
) -> None:
    """
    Compare les en-têtes client optionnels à la vérité serveur.
    Lève 409 CONTEXT_STALE si désalignement.
    """
    raw_device = (request.headers.get(HEADER_DEVICE_ID) or "").strip()
    raw_module = (request.headers.get(HEADER_CONTEXT_MODULE_KEY) or "").strip()

    truth_device = _norm(resolved.device_id)
    truth_module = _norm(resolved.module_key)

    stale = False
    if raw_device and _norm(raw_device) != truth_device:
        stale = True
    if raw_module and resolved.operator_user_id and truth_module != _norm(raw_module):
        stale = True

    if stale:
        log_shared_workstation_context_invalidated(
            db=db,
            device_id=resolved.device_id or device_id,
            operator_user_id=resolved.operator_user_id,
            site_id=resolved.site_id,
            module_key=resolved.module_key,
            override_active=resolved.override_active,
            user_id=actor_user_id,
            reason="header_mismatch",
            request_id=_request_id(request),
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": CONTEXT_STALE_CODE,
                "message": (
                    "Le contexte poste partagé annoncé ne correspond plus à la vérité serveur — "
                    "rafraîchir l'enveloppe puis réessayer."
                ),
            },
        )


def require_active_operator_context(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_recyclique_device_id: Optional[str] = Header(None, alias=HEADER_DEVICE_ID),
    x_recyclique_device_credential: Optional[str] = Header(
        None, alias=HEADER_DEVICE_CREDENTIAL
    ),
    device_id: Optional[str] = None,
) -> SharedWorkstationContextOut:
    """
    Dependency FastAPI : exige un poste valide avec session opérateur active.
    """
    resolved_device_id = extract_device_id(
        request=request,
        x_recyclique_device_id=x_recyclique_device_id,
        device_id_query=device_id,
    )
    if x_recyclique_device_credential and x_recyclique_device_credential.strip():
        verify_device_credential_or_raise(
            request=request,
            db=db,
            device_id=resolved_device_id,
            credential=x_recyclique_device_credential,
            require_credential=True,
        )
    service = SharedWorkstationContextService(db)
    result = service.resolve_shared_workstation_context(
        device_id=resolved_device_id,
        actor_user_id=str(current_user.id),
        request_id=_request_id(request),
    )
    ctx = result.context

    if not result.device_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": SHARED_WORKSTATION_DEVICE_INVALID,
                "message": ctx.restriction_message or "Poste partagé introuvable",
            },
        )

    if not result.device_usable:
        log_shared_workstation_access_refused(
            db=db,
            device_id=ctx.device_id,
            site_id=ctx.site_id,
            outcome="device_invalid",
            operation="shared_workstation.require_operator",
            user_id=str(current_user.id),
            request_id=_request_id(request),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": SHARED_WORKSTATION_DEVICE_INVALID,
                "message": ctx.restriction_message or "Poste partagé indisponible",
            },
        )

    if not result.has_active_operator:
        log_shared_workstation_access_refused(
            db=db,
            device_id=ctx.device_id,
            site_id=ctx.site_id,
            outcome="operator_required",
            operation="shared_workstation.require_operator",
            user_id=str(current_user.id),
            request_id=_request_id(request),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": SHARED_WORKSTATION_OPERATOR_REQUIRED,
                "message": ctx.restriction_message or "Opérateur actif requis sur ce poste",
            },
        )

    assert_context_fresh(
        request=request,
        db=db,
        device_id=resolved_device_id,
        resolved=ctx,
        actor_user_id=str(current_user.id),
    )
    return ctx


def require_effective_module(module_key: str):
    """
    Dependency factory : require_active_operator_context + assert_module_in_effective_set.
    Story 27.7 — refus frontière API si module ∉ intersection effective.
    """

    def _dependency(
        request: Request,
        db: Session = Depends(get_db),
        ctx: SharedWorkstationContextOut = Depends(require_active_operator_context),
        current_user: User = Depends(get_current_user),
    ) -> SharedWorkstationContextOut:
        _assert_effective_module_in_context(
            request=request,
            db=db,
            ctx=ctx,
            module_key=module_key,
            current_user=current_user,
        )
        return ctx

    return _dependency


def require_effective_module_from_path(
    module_key: str,
    request: Request,
    db: Session = Depends(get_db),
    ctx: SharedWorkstationContextOut = Depends(require_active_operator_context),
    current_user: User = Depends(get_current_user),
) -> SharedWorkstationContextOut:
    """Dependency pour routes avec ``module_key`` en paramètre de chemin."""
    _assert_effective_module_in_context(
        request=request,
        db=db,
        ctx=ctx,
        module_key=module_key,
        current_user=current_user,
    )
    return ctx


def _assert_effective_module_in_context(
    *,
    request: Request,
    db: Session,
    ctx: SharedWorkstationContextOut,
    module_key: str,
    current_user: User,
) -> None:
    if ctx.operator_user_id is None or ctx.device_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": SHARED_WORKSTATION_OPERATOR_REQUIRED,
                "message": "Opérateur actif requis sur ce poste",
            },
        )
    SharedWorkstationEffectiveModulesService(db).assert_module_in_effective_set(
        device_id=ctx.device_id,
        operator_user_id=ctx.operator_user_id,
        module_key=module_key,
        request_id=_request_id(request),
        actor_user_id=str(current_user.id),
    )


def resolve_shared_workstation_reception_scope_when_device_present(
    *,
    request: Request,
    db: Session,
    current_user: User,
    x_recyclique_device_id: Optional[str] = None,
    x_recyclique_device_credential: Optional[str] = None,
) -> Optional[SharedWorkstationReceptionScope]:
    """
    Si en-têtes device présents : credential + session opérateur + module ``reception``.
    Sinon None (brownfield web).
    """
    raw_device = (x_recyclique_device_id or request.headers.get(HEADER_DEVICE_ID) or "").strip()
    if not raw_device:
        return None
    credential = x_recyclique_device_credential or request.headers.get(HEADER_DEVICE_CREDENTIAL)
    verify_device_credential_or_raise(
        request=request,
        db=db,
        device_id=raw_device,
        credential=credential,
        require_credential=True,
    )
    session = DeviceOperatorSessionService(db).get_active_for_device(device_id=raw_device)
    if session is None:
        log_shared_workstation_access_refused(
            db=db,
            device_id=raw_device,
            outcome="operator_required",
            operation="shared_workstation.reception_guard",
            user_id=str(current_user.id),
            request_id=_request_id(request),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": SHARED_WORKSTATION_OPERATOR_REQUIRED,
                "message": "Opérateur actif requis sur ce poste",
            },
        )
    operator_user_id = str(session.operator_user_id)
    SharedWorkstationEffectiveModulesService(db).assert_module_in_effective_set(
        device_id=raw_device,
        operator_user_id=operator_user_id,
        module_key=MODULE_KEY_RECEPTION,
        request_id=_request_id(request),
        actor_user_id=str(current_user.id),
    )
    return SharedWorkstationReceptionScope(device_id=raw_device)


def get_optional_shared_workstation_reception_scope(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_recyclique_device_id: Optional[str] = Header(None, alias=HEADER_DEVICE_ID),
    x_recyclique_device_credential: Optional[str] = Header(
        None, alias=HEADER_DEVICE_CREDENTIAL
    ),
) -> Optional[SharedWorkstationReceptionScope]:
    return resolve_shared_workstation_reception_scope_when_device_present(
        request=request,
        db=db,
        current_user=current_user,
        x_recyclique_device_id=x_recyclique_device_id,
        x_recyclique_device_credential=x_recyclique_device_credential,
    )


def require_shared_workstation_reception_access(
    ctx: SharedWorkstationContextOut = Depends(require_effective_module(MODULE_KEY_RECEPTION)),
) -> SharedWorkstationContextOut:
    """Dependency — credential + session + module reception effectif (routes shared-workstation)."""
    return ctx
