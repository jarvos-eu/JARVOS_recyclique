"""
Contexte serveur poste partagé (Epic 27.2).

Invariant autoritaire :
``site_id + device_id + operator_user_id + module_key + override_active``

- ``device_id`` = ``RegisteredDevice.id`` (jamais ``cash_register_id`` ni ``reception_post_id``).
- ``operator_user_id`` provient de la session serveur ``device_operator_sessions``, pas du client.
- Sans opérateur actif : refus par défaut sur routes métier poste partagé.
- Recalcul explicite sur changement poste / opérateur / site / module / droits / override.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from recyclic_api.core.audit import log_shared_workstation_access_refused
from recyclic_api.core.exceptions import NotFoundError, ValidationError
from recyclic_api.models.registered_device import RegisteredDeviceStatus
from recyclic_api.schemas.context_envelope import ContextRuntimeState
from recyclic_api.schemas.shared_workstation_context import SharedWorkstationContextOut
from recyclic_api.services.device_operator_session_service import DeviceOperatorSessionService
from recyclic_api.services.registered_device_service import RegisteredDeviceService


@dataclass(frozen=True)
class SharedWorkstationContextResult:
    context: SharedWorkstationContextOut
    device_found: bool
    device_usable: bool
    has_active_operator: bool


class SharedWorkstationContextService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._devices = RegisteredDeviceService(db)
        self._sessions = DeviceOperatorSessionService(db)

    def resolve_shared_workstation_context(
        self,
        *,
        device_id: str,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> SharedWorkstationContextResult:
        device = self._devices.get(device_id=device_id)
        if device is None:
            ctx = SharedWorkstationContextOut(
                device_id=device_id,
                runtime_state=ContextRuntimeState.forbidden,
                restriction_message="Poste partagé introuvable",
            )
            log_shared_workstation_access_refused(
                db=self._db,
                device_id=device_id,
                outcome="not_found",
                operation="shared_workstation.resolve",
                user_id=actor_user_id,
                request_id=request_id,
            )
            return SharedWorkstationContextResult(
                context=ctx,
                device_found=False,
                device_usable=False,
                has_active_operator=False,
            )

        if device.status != RegisteredDeviceStatus.ACTIVE.value:
            if device.status == RegisteredDeviceStatus.REVOKED.value:
                restriction_message = "Poste partagé révoqué"
                outcome = "device_revoked"
            else:
                restriction_message = "Poste partagé indisponible"
                outcome = "device_inactive"
            ctx = SharedWorkstationContextOut(
                site_id=str(device.site_id),
                device_id=str(device.id),
                runtime_state=ContextRuntimeState.forbidden,
                restriction_message=restriction_message,
            )
            log_shared_workstation_access_refused(
                db=self._db,
                device_id=str(device.id),
                site_id=str(device.site_id),
                outcome=outcome,
                operation="shared_workstation.resolve",
                user_id=actor_user_id,
                request_id=request_id,
            )
            return SharedWorkstationContextResult(
                context=ctx,
                device_found=True,
                device_usable=False,
                has_active_operator=False,
            )

        session = self._sessions.get_active_for_device(device_id=str(device.id))
        if session is None:
            ctx = SharedWorkstationContextOut(
                site_id=str(device.site_id),
                device_id=str(device.id),
                operator_user_id=None,
                module_key=None,
                override_active=False,
                runtime_state=ContextRuntimeState.forbidden,
                restriction_message="Aucun opérateur actif sur ce poste",
            )
            return SharedWorkstationContextResult(
                context=ctx,
                device_found=True,
                device_usable=True,
                has_active_operator=False,
            )

        if session.site_id != device.site_id:
            ctx = SharedWorkstationContextOut(
                site_id=str(device.site_id),
                device_id=str(device.id),
                operator_user_id=str(session.operator_user_id),
                module_key=session.active_module_key,
                override_active=session.override_active,
                runtime_state=ContextRuntimeState.forbidden,
                restriction_message="Session opérateur incohérente avec le site du poste",
            )
            return SharedWorkstationContextResult(
                context=ctx,
                device_found=True,
                device_usable=False,
                has_active_operator=False,
            )

        if session.status != "active":
            ctx = SharedWorkstationContextOut(
                site_id=str(device.site_id),
                device_id=str(device.id),
                runtime_state=ContextRuntimeState.forbidden,
                restriction_message="Session opérateur invalidée",
            )
            return SharedWorkstationContextResult(
                context=ctx,
                device_found=True,
                device_usable=True,
                has_active_operator=False,
            )

        ctx = SharedWorkstationContextOut(
            site_id=str(device.site_id),
            device_id=str(device.id),
            operator_user_id=str(session.operator_user_id),
            module_key=session.active_module_key,
            override_active=session.override_active,
            runtime_state=ContextRuntimeState.ok,
            restriction_message=None,
        )
        return SharedWorkstationContextResult(
            context=ctx,
            device_found=True,
            device_usable=True,
            has_active_operator=True,
        )

    def invalidate_sessions_for_device(
        self,
        *,
        device_id: str,
        reason: str = "device_change",
        actor_user_id: Optional[str] = None,
    ) -> None:
        from recyclic_api.core.audit import log_shared_workstation_context_invalidated

        sessions = self._sessions.invalidate_sessions_for_device(
            device_id=device_id,
            reason=reason,
            actor_user_id=actor_user_id,
        )
        for session in sessions:
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

    def invalidate_on_site_change(self, *, device: "RegisteredDevice") -> None:
        """Invalide les sessions actives si le site du device a changé."""
        self.invalidate_sessions_for_device(
            device_id=str(device.id),
            reason="device_site_change",
        )


def parse_device_uuid(device_id: str) -> UUID:
    try:
        return UUID(str(device_id).strip())
    except ValueError as exc:
        raise ValidationError("device_id doit être un UUID valide") from exc
