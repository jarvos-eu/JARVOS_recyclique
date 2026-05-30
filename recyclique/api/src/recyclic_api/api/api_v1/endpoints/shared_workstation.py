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
    require_valid_device_credential,
)
from recyclic_api.schemas.device_enrollment import (
    SharedWorkstationDeviceStatusResponse,
    SharedWorkstationEnrollCompleteRequest,
    SharedWorkstationEnrollCompleteResponse,
)
from recyclic_api.schemas.shared_workstation_context import SharedWorkstationContextOut
from recyclic_api.schemas.shared_workstation_operator_pin import (
    SharedWorkstationOperatorPinVerifyRequest,
    SharedWorkstationOperatorPinVerifyResponse,
    SharedWorkstationOperatorSessionStatusResponse,
)
from recyclic_api.services.device_enrollment_service import DeviceEnrollmentService, EnrollmentError
from recyclic_api.services.registered_device_service import RegisteredDeviceService
from recyclic_api.services.shared_workstation_operator_pin_service import (
    PinVerifyError,
    SharedWorkstationOperatorPinService,
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
    context: SharedWorkstationContextOut = Depends(require_active_operator_context),
):
    """
    Lecture du tuple autoritaire ``site_id + device_id + operator_user_id + module_key + override_active``.

    Story 27.2 — refus 403 sans opérateur actif ; credential invalidé en 27.4 avant résolution.
    """
    _no_store(response)
    return context


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
