"""CRUD registre postes partagés — SUPER_ADMIN uniquement (Epic 27.1)."""



from __future__ import annotations



from typing import Any, Dict, List, Optional



from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from sqlalchemy.orm import Session



from recyclic_api.core.audit import (
    log_device_conflict_resolved,
    log_device_enrollment_code_issued,
    log_device_identity_lost_marked,
    log_registered_device_created,
    log_registered_device_revoked,
    log_registered_device_updated,
)

from recyclic_api.core.auth import require_role_strict

from recyclic_api.core.database import get_db

from recyclic_api.core.exceptions import NotFoundError, ValidationError

from recyclic_api.models.user import User, UserRole

from recyclic_api.core.redis import get_redis
from recyclic_api.schemas.device_enrollment import (
    DeviceEnrollmentCodeIssueRequest,
    DeviceEnrollmentCodeIssueResponse,
    RegisteredDeviceConflictResolveRequest,
    RegisteredDeviceConflictResolveResponse,
)
from recyclic_api.schemas.shared_workstation_operator_pin import ClearOperatorPinLockoutRequest
from recyclic_api.services.shared_workstation_operator_pin_service import (
    SharedWorkstationOperatorPinService,
)
from recyclic_api.core.audit import log_shared_workstation_pin_lockout_cleared
from recyclic_api.schemas.registered_device import (

    RegisteredDeviceCreate,

    RegisteredDeviceResponse,

    RegisteredDeviceRevokeRequest,

    RegisteredDeviceUpdate,

)

from recyclic_api.services.device_enrollment_service import DeviceEnrollmentService, EnrollmentError
from recyclic_api.services.registered_device_service import RegisteredDeviceService



router = APIRouter()





def _no_store(response: Response) -> None:

    response.headers["Cache-Control"] = "no-store"





def _update_changed_fields(payload: RegisteredDeviceUpdate) -> Dict[str, Any]:

    """Champs effectivement fournis dans le PATCH (pour audit)."""

    data = payload.model_dump(exclude_unset=True)

    data.pop("last_contact_at", None)

    return data





@router.get(

    "/",

    response_model=List[RegisteredDeviceResponse],

    summary="Lister les postes partagés enregistrés",

    openapi_extra={"operationId": "recyclique_registeredDevices_listRegisteredDevices"},

)

async def list_registered_devices(

    response: Response,

    skip: int = Query(0, ge=0),

    limit: int = Query(100, ge=1, le=200),

    site_id: Optional[str] = Query(None, description="Filtrer par site"),

    status: Optional[str] = Query(None, description="Filtrer par statut administratif"),

    include_revoked: bool = Query(

        False, description="Inclure les postes révoqués dans la liste"

    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),

):

    _no_store(response)

    service = RegisteredDeviceService(db)

    return service.list(

        skip=skip,

        limit=limit,

        site_id=site_id,

        status=status,

        include_revoked=include_revoked,

    )





@router.get(

    "/{device_id}",

    response_model=RegisteredDeviceResponse,

    summary="Détail d'un poste partagé par device_id",

    openapi_extra={"operationId": "recyclique_registeredDevices_getRegisteredDeviceById"},

)

async def get_registered_device(

    device_id: str,

    response: Response,

    db: Session = Depends(get_db),

    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),

):

    _no_store(response)

    service = RegisteredDeviceService(db)

    try:

        return service.get_required(device_id=device_id)

    except NotFoundError as exc:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=str(exc),

        ) from exc





@router.post(

    "/",

    response_model=RegisteredDeviceResponse,

    status_code=status.HTTP_201_CREATED,

    summary="Créer un poste partagé (shared_workstation)",

    openapi_extra={"operationId": "recyclique_registeredDevices_createRegisteredDevice"},

)

async def create_registered_device(

    payload: RegisteredDeviceCreate,

    response: Response,

    db: Session = Depends(get_db),

    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),

):

    _no_store(response)

    service = RegisteredDeviceService(db)

    try:

        device = service.create(data=payload)

    except NotFoundError as exc:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=str(exc),

        ) from exc

    except ValidationError as exc:

        raise HTTPException(

            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,

            detail=str(exc),

        ) from exc



    log_registered_device_created(

        db=db,

        actor=current_user,

        device_id=str(device.id),

        site_id=str(device.site_id) if device.site_id is not None else None,

        module_keys=list(device.allowed_module_keys or []),

    )

    return device





@router.patch(

    "/{device_id}",

    response_model=RegisteredDeviceResponse,

    summary="Mettre à jour un poste partagé",

    openapi_extra={"operationId": "recyclique_registeredDevices_updateRegisteredDevice"},

)

async def update_registered_device(

    device_id: str,

    payload: RegisteredDeviceUpdate,

    response: Response,

    db: Session = Depends(get_db),

    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),

):

    _no_store(response)

    service = RegisteredDeviceService(db)

    changed_fields = _update_changed_fields(payload)

    try:

        device = service.get_required(device_id=device_id)

        updated = service.update(device=device, data=payload)

    except NotFoundError as exc:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=str(exc),

        ) from exc

    except ValidationError as exc:

        raise HTTPException(

            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,

            detail=str(exc),

        ) from exc



    if changed_fields:

        log_registered_device_updated(

            db=db,

            actor=current_user,

            device_id=str(updated.id),

            site_id=str(updated.site_id) if updated.site_id is not None else None,

            module_keys=list(updated.allowed_module_keys or []),

            changed_fields=changed_fields,

        )

    return updated





@router.post(

    "/{device_id}/revoke",

    response_model=RegisteredDeviceResponse,

    summary="Révoquer un poste partagé",

    openapi_extra={"operationId": "recyclique_registeredDevices_revokeRegisteredDevice"},

)

async def revoke_registered_device(

    device_id: str,

    response: Response,

    payload: Optional[RegisteredDeviceRevokeRequest] = None,

    db: Session = Depends(get_db),

    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),

):

    _no_store(response)

    service = RegisteredDeviceService(db)

    reason = payload.reason if payload else None

    try:

        device = service.get_required(device_id=device_id)

        revoked = service.revoke(device=device)

    except NotFoundError as exc:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=str(exc),

        ) from exc



    log_registered_device_revoked(

        db=db,

        actor=current_user,

        device_id=str(revoked.id),

        site_id=str(revoked.site_id) if revoked.site_id is not None else None,

        reason=reason,

    )

    return revoked


@router.post(
    "/{device_id}/clear-operator-pin-lockout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Débloquer lockout PIN opérateur (device + opérateur)",
    openapi_extra={"operationId": "recyclique_registeredDevices_clearOperatorPinLockout"},
)
async def clear_operator_pin_lockout(
    device_id: str,
    payload: ClearOperatorPinLockoutRequest,
    response: Response,
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),
):
    _no_store(response)
    service = RegisteredDeviceService(db)
    try:
        device = service.get_required(device_id=device_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    operator_id = str(payload.operator_user_id)
    SharedWorkstationOperatorPinService(db).clear_lockout(
        device_id=device_id,
        operator_user_id=operator_id,
        redis_client=redis_client,
    )
    log_shared_workstation_pin_lockout_cleared(
        db=db,
        actor=current_user,
        device_id=device_id,
        operator_user_id=operator_id,
        site_id=str(device.site_id),
    )
    return None


@router.post(
    "/{device_id}/enrollment-codes",
    response_model=DeviceEnrollmentCodeIssueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Générer un code d'enrôlement",
    openapi_extra={"operationId": "recyclique_registeredDevices_issueEnrollmentCode"},
)
async def issue_enrollment_code(
    device_id: str,
    payload: DeviceEnrollmentCodeIssueRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),
):
    _no_store(response)
    service = RegisteredDeviceService(db)
    enrollment = DeviceEnrollmentService(db)
    try:
        device = service.get_required(device_id=device_id)
        result = enrollment.issue_code(
            device_id=device_id,
            purpose=payload.purpose,
            created_by_user_id=str(current_user.id),
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except EnrollmentError as exc:
        raise HTTPException(
            status_code=exc.http_status,
            detail={"code": exc.code, "message": exc.message},
        ) from exc

    log_device_enrollment_code_issued(
        db=db,
        actor=current_user,
        device_id=str(device.id),
        site_id=str(device.site_id),
        purpose=payload.purpose,
    )
    return DeviceEnrollmentCodeIssueResponse(
        code=result.code,
        expires_at=result.expires_at,
        purpose=result.purpose,
    )


@router.post(
    "/{device_id}/mark-identity-lost",
    response_model=RegisteredDeviceResponse,
    summary="Marquer identité locale perdue",
    openapi_extra={"operationId": "recyclique_registeredDevices_markIdentityLost"},
)
async def mark_identity_lost(
    device_id: str,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),
):
    _no_store(response)
    enrollment = DeviceEnrollmentService(db)
    try:
        device = enrollment.mark_identity_lost(device_id=device_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    log_device_identity_lost_marked(
        db=db,
        actor=current_user,
        device_id=str(device.id),
        site_id=str(device.site_id),
    )
    return device


@router.post(
    "/{device_id}/resolve-conflict",
    response_model=RegisteredDeviceConflictResolveResponse,
    summary="Résoudre un conflit d'identité poste",
    openapi_extra={"operationId": "recyclique_registeredDevices_resolveConflict"},
)
async def resolve_conflict(
    device_id: str,
    payload: RegisteredDeviceConflictResolveRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),
):
    _no_store(response)
    enrollment = DeviceEnrollmentService(db)
    try:
        result = enrollment.resolve_conflict(
            device_id=device_id,
            action=payload.action,
            created_by_user_id=str(current_user.id),
            name=payload.name,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except EnrollmentError as exc:
        raise HTTPException(
            status_code=exc.http_status,
            detail={"code": exc.code, "message": exc.message},
        ) from exc

    device = result.device
    distinct_id = result.distinct_device_id

    log_device_conflict_resolved(
        db=db,
        actor=current_user,
        device_id=str(device.id),
        site_id=str(device.site_id),
        action=payload.action,
        distinct_device_id=distinct_id,
    )
    if result.enrollment_code is not None:
        log_device_enrollment_code_issued(
            db=db,
            actor=current_user,
            device_id=str(device.id),
            site_id=str(device.site_id),
            purpose=result.enrollment_code.purpose,
        )
    return RegisteredDeviceConflictResolveResponse(
        device_id=str(device.id),
        status=device.status,
        distinct_device_id=distinct_id,
        enrollment_code=(
            result.enrollment_code.code if result.enrollment_code else None
        ),
        enrollment_code_expires_at=(
            result.enrollment_code.expires_at if result.enrollment_code else None
        ),
        enrollment_code_purpose=(
            result.enrollment_code.purpose if result.enrollment_code else None
        ),
    )

