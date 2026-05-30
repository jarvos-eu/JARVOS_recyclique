"""Endpoints poste partagé — contexte, enrôlement, statut device, PIN opérateur (Epic 27)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from recyclic_api.core.auth import resolve_access_token
from recyclic_api.core.database import get_db
from recyclic_api.core.redis import get_redis
from recyclic_api.core.security import verify_token
from recyclic_api.core.shared_workstation_guard import (
    require_active_operator_context,
    require_effective_module_from_path,
    require_shared_workstation_reception_access,
    require_valid_device_credential,
)
from recyclic_api.schemas.device_enrollment import (
    SharedWorkstationDeviceStatusResponse,
    SharedWorkstationEnrollCompleteRequest,
    SharedWorkstationEnrollCompleteResponse,
)
from recyclic_api.schemas.shared_workstation_context import SharedWorkstationContextOut
from recyclic_api.schemas.shared_workstation_effective_modules import (
    SharedWorkstationEffectiveModulesOut,
    SharedWorkstationProbeModuleOut,
)
from recyclic_api.schemas.shared_workstation_operator_pin import (
    SharedWorkstationOperatorPinVerifyRequest,
    SharedWorkstationOperatorPinVerifyResponse,
    SharedWorkstationOperatorSessionStatusResponse,
)
from recyclic_api.schemas.shared_workstation_reception_draft import (
    SharedWorkstationReceptionDraftAbandonOut,
    SharedWorkstationReceptionDraftConfirmRequest,
    SharedWorkstationReceptionDraftGetOut,
    SharedWorkstationReceptionDraftResumeOut,
)
from recyclic_api.services.shared_workstation_reception_draft_service import (
    SharedWorkstationReceptionDraftService,
)
from recyclic_api.services.device_enrollment_service import DeviceEnrollmentService, EnrollmentError
from recyclic_api.services.registered_device_service import RegisteredDeviceService
from recyclic_api.services.shared_workstation_operator_pin_service import (
    PinVerifyError,
    SharedWorkstationOperatorPinService,
)
from recyclic_api.services.shared_workstation_effective_modules_service import (
    SharedWorkstationEffectiveModulesService,
)
from recyclic_api.utils.rate_limit import conditional_rate_limit

router = APIRouter()
_security = HTTPBearer(auto_error=False)


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"


def _request_id(request: Request) -> Optional[str]:
    return request.headers.get("X-Request-Id") or request.headers.get("X-Correlation-Id")


async def _optional_actor_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_security),
) -> Optional[str]:
    """JWT utilisateur optionnel (acteur audit) — sans exiger l'authentification."""
    token = resolve_access_token(request, credentials)
    if not token:
        return None
    try:
        payload = verify_token(token)
        sub = payload.get("sub")
        return str(sub) if sub else None
    except JWTError:
        return None


@router.get(
    "/context",
    response_model=SharedWorkstationContextOut,
    summary="Contexte poste partagé résolu (vérité serveur)",
    openapi_extra={"operationId": "recyclique_sharedWorkstation_getContext"},
)
async def get_shared_workstation_context(
    response: Response,
    db: Session = Depends(get_db),
    context: SharedWorkstationContextOut = Depends(require_active_operator_context),
):
    """
    Lecture du tuple autoritaire ``site_id + device_id + operator_user_id + module_key + override_active``.

    Story 27.2 — refus 403 sans opérateur actif ; credential invalidé en 27.4 avant résolution.
    Story 27.7 — enrichit ``effective_module_keys`` si session active.
    """
    _no_store(response)
    out = context.model_copy()
    if context.device_id and context.operator_user_id:
        eff = SharedWorkstationEffectiveModulesService(db).compute_effective_module_keys(
            device_id=context.device_id,
            operator_user_id=context.operator_user_id,
        )
        out = out.model_copy(update={"effective_module_keys": list(eff.module_keys)})
        from recyclic_api.modules.module_config.registry import MODULE_KEY_RECEPTION

        if MODULE_KEY_RECEPTION in eff.module_keys:
            summary = SharedWorkstationReceptionDraftService(db).get_draft_for_device(
                device_id=context.device_id,
                operator_user_id=context.operator_user_id,
                actor_user_id=context.operator_user_id,
            )
            if summary is not None:
                out = out.model_copy(update={"reception_draft_summary": summary.model_dump()})
    return out


@router.get(
    "/effective-modules",
    response_model=SharedWorkstationEffectiveModulesOut,
    summary="Modules effectifs poste partagé (intersection serveur)",
    openapi_extra={"operationId": "recyclique_sharedWorkstation_getEffectiveModules"},
)
async def get_effective_modules(
    response: Response,
    db: Session = Depends(get_db),
    context: SharedWorkstationContextOut = Depends(require_active_operator_context),
):
    """Story 27.7 — intersection site × allowlist × permissions opérateur."""
    _no_store(response)
    if context.operator_user_id is None or context.device_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "SHARED_WORKSTATION_OPERATOR_REQUIRED",
                "message": "Session opérateur active requise",
            },
        )
    result = SharedWorkstationEffectiveModulesService(db).compute_effective_module_keys(
        device_id=context.device_id,
        operator_user_id=context.operator_user_id,
    )
    return SharedWorkstationEffectiveModulesOut(
        module_keys=list(result.module_keys),
        computed_at=result.computed_at,
        site_id=result.site_id,
        device_id=result.device_id,
        operator_user_id=result.operator_user_id,
    )


@router.get(
    "/probe-module/{module_key}",
    response_model=SharedWorkstationProbeModuleOut,
    summary="Probe garde module effectif (tests + preuve refus 403)",
    openapi_extra={"operationId": "recyclique_sharedWorkstation_probeModule"},
)
async def probe_effective_module(
    module_key: str,
    response: Response,
    _ctx: SharedWorkstationContextOut = Depends(require_effective_module_from_path),
):
    """Route minimale sans données métier — preuve garde require_effective_module."""
    _no_store(response)
    return SharedWorkstationProbeModuleOut(module_key=module_key, effective=True)


@router.post(
    "/enroll/complete",
    response_model=SharedWorkstationEnrollCompleteResponse,
    summary="Compléter l'enrôlement poste (semi-public)",
    openapi_extra={"operationId": "recyclique_sharedWorkstation_completeEnrollment"},
)
async def complete_enrollment(
    payload: SharedWorkstationEnrollCompleteRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Route semi-publique — pas de JWT utilisateur requis."""
    _no_store(response)
    from recyclic_api.core.audit import log_device_enrolled

    enrollment = DeviceEnrollmentService(db)
    try:
        result = enrollment.complete_enrollment(code=payload.code)
    except EnrollmentError as exc:
        raise HTTPException(
            status_code=exc.http_status,
            detail={"code": exc.code, "message": exc.message},
        ) from exc

    log_device_enrolled(
        db=db,
        device_id=result.device_id,
        site_id=result.site_id,
        purpose=result.purpose,
    )
    return SharedWorkstationEnrollCompleteResponse(
        device_id=result.device_id,
        device_secret=result.device_secret,
        device_name=result.device_name,
        site_id=result.site_id,
    )


@router.get(
    "/device-status",
    response_model=SharedWorkstationDeviceStatusResponse,
    summary="Statut poste avec credential device valide",
    openapi_extra={"operationId": "recyclique_sharedWorkstation_getDeviceStatus"},
)
async def get_device_status(
    response: Response,
    device_id: str = Depends(require_valid_device_credential),
    db: Session = Depends(get_db),
):
    from recyclic_api.models.registered_device import DEFAULT_INACTIVITY_TIMEOUT_SECONDS

    _no_store(response)
    device = RegisteredDeviceService(db).get_required(device_id=device_id)
    timeout = device.inactivity_timeout_seconds
    if timeout is None:
        timeout = DEFAULT_INACTIVITY_TIMEOUT_SECONDS
    return SharedWorkstationDeviceStatusResponse(
        device_id=str(device.id),
        device_name=device.name,
        site_id=str(device.site_id),
        status=device.status,
        allowed_module_keys=list(device.allowed_module_keys or []),
        inactivity_timeout_seconds=timeout,
    )


@router.get(
    "/operator-session/status",
    response_model=SharedWorkstationOperatorSessionStatusResponse,
    summary="Statut session opérateur sur le poste",
    openapi_extra={"operationId": "recyclique_sharedWorkstation_getOperatorSessionStatus"},
)
async def get_operator_session_status(
    response: Response,
    device_id: str = Depends(require_valid_device_credential),
    db: Session = Depends(get_db),
):
    _no_store(response)
    active, operator_id, session_id = SharedWorkstationOperatorPinService(db).get_session_status(
        device_id=device_id
    )
    return SharedWorkstationOperatorSessionStatusResponse(
        active=active,
        operator_user_id=operator_id,
        session_id=session_id,
    )


@router.post(
    "/operator-pin/verify",
    response_model=SharedWorkstationOperatorPinVerifyResponse,
    summary="Vérifier PIN opérateur et démarrer session",
    openapi_extra={"operationId": "recyclique_sharedWorkstation_verifyOperatorPin"},
)
@conditional_rate_limit("10/minute")
async def verify_operator_pin(
    payload: SharedWorkstationOperatorPinVerifyRequest,
    request: Request,
    response: Response,
    device_id: str = Depends(require_valid_device_credential),
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
    actor_user_id: Optional[str] = Depends(_optional_actor_user_id),
):
    _no_store(response)
    service = SharedWorkstationOperatorPinService(db)
    result = service.verify_and_start_session(
        device_id=device_id,
        operator_user_id=str(payload.operator_user_id),
        pin_plain=payload.pin,
        redis_client=redis_client,
        actor_user_id=actor_user_id,
        request_id=_request_id(request),
    )
    if isinstance(result, PinVerifyError):
        from recyclic_api.services.shared_workstation_operator_pin_service import (
            SHARED_WS_PIN_LOCKOUT_SECONDS,
        )

        headers = (
            {"Retry-After": str(SHARED_WS_PIN_LOCKOUT_SECONDS)}
            if result.http_status == 429
            else None
        )
        raise HTTPException(
            status_code=result.http_status,
            detail={"code": result.code, "message": result.message},
            headers=headers,
        )
    session = result.session
    return SharedWorkstationOperatorPinVerifyResponse(
        session_id=session.id,
        device_id=session.device_id,
        operator_user_id=session.operator_user_id,
        site_id=session.site_id,
        started_at=session.started_at,
    )


@router.get(
    "/reception-draft",
    response_model=SharedWorkstationReceptionDraftGetOut,
    summary="Résumé brouillon réception poste partagé",
    openapi_extra={"operationId": "recyclique_sharedWorkstation_getReceptionDraft"},
    responses={204: {"description": "Aucun brouillon actif"}},
)
async def get_reception_draft(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    context: SharedWorkstationContextOut = Depends(require_shared_workstation_reception_access),
):
    _no_store(response)
    if context.device_id is None or context.operator_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "SHARED_WORKSTATION_OPERATOR_REQUIRED",
                "message": "Session opérateur active requise",
            },
        )
    summary = SharedWorkstationReceptionDraftService(db).get_draft_for_device(
        device_id=context.device_id,
        operator_user_id=context.operator_user_id,
        actor_user_id=context.operator_user_id,
        request_id=_request_id(request),
    )
    if summary is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return SharedWorkstationReceptionDraftGetOut(summary=summary)


@router.post(
    "/reception-draft/resume",
    response_model=SharedWorkstationReceptionDraftResumeOut,
    summary="Reprendre brouillon réception (confirmation explicite)",
    openapi_extra={"operationId": "recyclique_sharedWorkstation_resumeReceptionDraft"},
)
async def resume_reception_draft(
    payload: SharedWorkstationReceptionDraftConfirmRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    context: SharedWorkstationContextOut = Depends(require_shared_workstation_reception_access),
):
    _no_store(response)
    if context.device_id is None or context.operator_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "SHARED_WORKSTATION_OPERATOR_REQUIRED",
                "message": "Session opérateur active requise",
            },
        )
    poste_id, ticket_id = SharedWorkstationReceptionDraftService(db).resume_draft(
        device_id=context.device_id,
        operator_user_id=context.operator_user_id,
        confirm=payload.confirm,
        actor_user_id=context.operator_user_id,
        request_id=_request_id(request),
    )
    return SharedWorkstationReceptionDraftResumeOut(poste_id=poste_id, ticket_id=ticket_id)


@router.post(
    "/reception-draft/abandon",
    response_model=SharedWorkstationReceptionDraftAbandonOut,
    summary="Abandonner brouillon réception (confirmation explicite)",
    openapi_extra={"operationId": "recyclique_sharedWorkstation_abandonReceptionDraft"},
)
async def abandon_reception_draft(
    payload: SharedWorkstationReceptionDraftConfirmRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    context: SharedWorkstationContextOut = Depends(require_shared_workstation_reception_access),
):
    _no_store(response)
    if context.device_id is None or context.operator_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "SHARED_WORKSTATION_OPERATOR_REQUIRED",
                "message": "Session opérateur active requise",
            },
        )
    SharedWorkstationReceptionDraftService(db).abandon_draft(
        device_id=context.device_id,
        operator_user_id=context.operator_user_id,
        confirm=payload.confirm,
        actor_user_id=context.operator_user_id,
        request_id=_request_id(request),
    )
    return SharedWorkstationReceptionDraftAbandonOut()
