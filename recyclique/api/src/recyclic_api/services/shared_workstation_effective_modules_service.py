"""
Intersection serveur modules poste partagé (Story 27.7).

Formule : config module site × allowlist poste × permissions opérateur.
Recalcul stateless à chaque appel — pas de cache autoritaire.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from recyclic_api.core.audit import log_shared_workstation_access_refused
from recyclic_api.core.auth import get_user_permissions
from recyclic_api.models.registered_device import RegisteredDeviceStatus, RegisteredDeviceType
from recyclic_api.models.user import User
from recyclic_api.modules.module_config.access_registry import (
    get_module_access_entry,
    iter_intersectable_module_keys,
    is_site_module_enabled,
)
from recyclic_api.services.device_operator_session_service import DeviceOperatorSessionService
from recyclic_api.services.registered_device_service import RegisteredDeviceService

SHARED_WORKSTATION_MODULE_FORBIDDEN = "SHARED_WORKSTATION_MODULE_FORBIDDEN"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class EffectiveModulesResult:
    module_keys: list[str]
    computed_at: datetime
    site_id: str
    device_id: str
    operator_user_id: str


class SharedWorkstationEffectiveModulesService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._devices = RegisteredDeviceService(db)
        self._sessions = DeviceOperatorSessionService(db)

    def compute_effective_module_keys(
        self,
        *,
        device_id: str,
        operator_user_id: str,
    ) -> EffectiveModulesResult:
        device = self._devices.get_required(device_id=device_id)
        if device.device_type != RegisteredDeviceType.SHARED_WORKSTATION.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "SHARED_WORKSTATION_DEVICE_INVALID",
                    "message": "Poste non partagé",
                },
            )
        if device.status != RegisteredDeviceStatus.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "SHARED_WORKSTATION_DEVICE_INVALID",
                    "message": "Poste partagé indisponible",
                },
            )

        session = self._sessions.get_active_for_device(device_id=str(device.id))
        if session is None or str(session.operator_user_id) != str(operator_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "SHARED_WORKSTATION_OPERATOR_REQUIRED",
                    "message": "Session opérateur active requise",
                },
            )

        try:
            operator_uuid = uuid.UUID(str(operator_user_id))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "SHARED_WORKSTATION_OPERATOR_REQUIRED",
                    "message": "Opérateur invalide",
                },
            ) from exc

        operator = self._db.get(User, operator_uuid)
        if operator is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "SHARED_WORKSTATION_OPERATOR_REQUIRED",
                    "message": "Opérateur introuvable",
                },
            )

        permission_keys = set(get_user_permissions(operator, self._db))
        allowlist = set(device.allowed_module_keys or [])
        site_id = device.site_id

        effective: list[str] = []
        for module_key in iter_intersectable_module_keys():
            entry = get_module_access_entry(module_key)
            if entry is None:
                continue
            if module_key not in allowlist:
                continue
            if not is_site_module_enabled(self._db, site_id=site_id, module_key=module_key):
                continue
            if not all(p in permission_keys for p in entry.required_permission_keys):
                continue
            # override_active : pas d'élargissement implicite en 27.7 (story 27.10).
            effective.append(module_key)

        return EffectiveModulesResult(
            module_keys=effective,
            computed_at=_utc_now(),
            site_id=str(site_id),
            device_id=str(device.id),
            operator_user_id=str(operator_user_id),
        )

    def assert_module_in_effective_set(
        self,
        *,
        device_id: str,
        operator_user_id: str,
        module_key: str,
        request_id: Optional[str] = None,
        actor_user_id: Optional[str] = None,
    ) -> None:
        result = self.compute_effective_module_keys(
            device_id=device_id,
            operator_user_id=operator_user_id,
        )
        if module_key not in result.module_keys:
            log_shared_workstation_access_refused(
                db=self._db,
                device_id=result.device_id,
                site_id=result.site_id,
                operator_user_id=result.operator_user_id,
                module_key=module_key,
                outcome="module_not_effective",
                operation="shared_workstation.assert_effective_module",
                user_id=actor_user_id,
                request_id=request_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": SHARED_WORKSTATION_MODULE_FORBIDDEN,
                    "message": "Module non autorisé sur ce poste pour cet opérateur",
                },
            )

    def invalidate_on_context_change(
        self,
        *,
        device_id: str,
        reason: str = "context_change",
        actor_user_id: Optional[str] = None,
    ) -> None:
        """Hook recalcul — MVP stateless ; journalise invalidation pour audit."""
        from recyclic_api.core.audit import log_shared_workstation_context_invalidated

        session = self._sessions.get_active_for_device(device_id=device_id)
        if session is None:
            return
        log_shared_workstation_context_invalidated(
            db=self._db,
            device_id=str(session.device_id),
            operator_user_id=str(session.operator_user_id),
            site_id=str(session.site_id),
            module_key=session.active_module_key,
            override_active=session.override_active,
            user_id=actor_user_id,
            reason=reason,
        )
