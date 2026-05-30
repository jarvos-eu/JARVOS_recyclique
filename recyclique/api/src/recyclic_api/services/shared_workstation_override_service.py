"""Override SuperAdmin explicite poste partagé (Epic 27.10)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from recyclic_api.core.audit import (
    log_shared_workstation_override_activated,
    log_shared_workstation_override_activation_refused,
    log_shared_workstation_override_deactivated,
    log_shared_workstation_override_expired,
)
from recyclic_api.core.security import verify_password
from recyclic_api.models.device_operator_session import DeviceOperatorSession
from recyclic_api.models.user import User, UserRole
from recyclic_api.services.device_operator_session_service import DeviceOperatorSessionService
from recyclic_api.services.shared_workstation_effective_modules_service import (
    SharedWorkstationEffectiveModulesService,
)

DEFAULT_OVERRIDE_TTL_SECONDS = 1800

SHARED_WORKSTATION_OPERATOR_REQUIRED = "SHARED_WORKSTATION_OPERATOR_REQUIRED"
SHARED_WORKSTATION_OVERRIDE_FORBIDDEN = "SHARED_WORKSTATION_OVERRIDE_FORBIDDEN"
SHARED_WORKSTATION_OVERRIDE_CONFIRMATION_FAILED = "SHARED_WORKSTATION_OVERRIDE_CONFIRMATION_FAILED"
SHARED_WORKSTATION_OVERRIDE_REQUIRED = "SHARED_WORKSTATION_OVERRIDE_REQUIRED"
SHARED_WORKSTATION_OVERRIDE_EXPIRED = "SHARED_WORKSTATION_OVERRIDE_EXPIRED"

_NEUTRAL_CONFIRMATION_MESSAGE = "Confirmation incorrecte"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def override_seconds_remaining(
    *,
    session: DeviceOperatorSession,
    now: Optional[datetime] = None,
    ttl_seconds: int = DEFAULT_OVERRIDE_TTL_SECONDS,
) -> Optional[int]:
    if not session.override_active or session.override_started_at is None:
        return None
    now = now or _utc_now()
    started = _ensure_aware(session.override_started_at)
    elapsed = (now - started).total_seconds()
    return max(0, int(ttl_seconds - elapsed))


def override_expires_at(
    *,
    session: DeviceOperatorSession,
    ttl_seconds: int = DEFAULT_OVERRIDE_TTL_SECONDS,
) -> Optional[datetime]:
    if not session.override_active or session.override_started_at is None:
        return None
    started = _ensure_aware(session.override_started_at)
    return started + timedelta(seconds=ttl_seconds)


def can_activate_super_admin_override(
    *,
    session: Optional[DeviceOperatorSession],
    operator: Optional[User],
) -> bool:
    if session is None or operator is None:
        return False
    return (
        operator.role == UserRole.SUPER_ADMIN
        and not session.override_active
    )


@dataclass(frozen=True)
class OverrideActivateResult:
    override_active: bool
    override_started_at: datetime
    override_expires_at: datetime


@dataclass(frozen=True)
class OverrideError:
    code: str
    message: str
    http_status: int


class SharedWorkstationOverrideService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._sessions = DeviceOperatorSessionService(db)
        self._effective = SharedWorkstationEffectiveModulesService(db)

    def _get_active_session(self, *, device_id: str) -> Optional[DeviceOperatorSession]:
        return self._sessions.get_active_for_device(device_id=device_id)

    def _get_operator(self, operator_user_id: str) -> Optional[User]:
        try:
            uid = UUID(str(operator_user_id))
        except ValueError:
            return None
        return self._db.get(User, uid)

    def expire_override_if_needed(
        self,
        *,
        session: DeviceOperatorSession,
        now: Optional[datetime] = None,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> bool:
        """Désactive override si TTL dépassé. Retourne True si expiré traité."""
        if not session.override_active or session.override_started_at is None:
            return False
        now = now or _utc_now()
        remaining = override_seconds_remaining(session=session, now=now)
        if remaining is not None and remaining > 0:
            return False
        session.override_active = False
        session.override_started_at = None
        self._db.add(session)
        self._db.commit()
        self._db.refresh(session)
        log_shared_workstation_override_expired(
            db=self._db,
            session_id=str(session.id),
            device_id=str(session.device_id),
            site_id=str(session.site_id),
            operator_user_id=str(session.operator_user_id),
            module_key=session.active_module_key,
            override_active=False,
            user_id=actor_user_id,
            request_id=request_id,
        )
        self._effective.invalidate_on_context_change(
            device_id=str(session.device_id),
            reason="override_expired",
            actor_user_id=actor_user_id,
        )
        return True

    def activate_override(
        self,
        *,
        device_id: str,
        confirmation_pin: str,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> OverrideActivateResult | OverrideError:
        now = now or _utc_now()
        session = self._get_active_session(device_id=device_id)
        if session is None:
            log_shared_workstation_override_activation_refused(
                db=self._db,
                device_id=device_id,
                reason="no_active_session",
                request_id=request_id,
                user_id=actor_user_id,
            )
            return OverrideError(
                code=SHARED_WORKSTATION_OPERATOR_REQUIRED,
                message="Session opérateur active requise",
                http_status=403,
            )

        operator = self._get_operator(str(session.operator_user_id))
        if operator is None or operator.role != UserRole.SUPER_ADMIN:
            log_shared_workstation_override_activation_refused(
                db=self._db,
                session_id=str(session.id),
                device_id=str(session.device_id),
                site_id=str(session.site_id),
                operator_user_id=str(session.operator_user_id),
                module_key=session.active_module_key,
                override_active=session.override_active,
                reason="not_super_admin",
                request_id=request_id,
                user_id=actor_user_id,
            )
            return OverrideError(
                code=SHARED_WORKSTATION_OVERRIDE_FORBIDDEN,
                message="Override réservé aux SuperAdmin",
                http_status=403,
            )

        if session.override_active:
            expires = override_expires_at(session=session)
            started = session.override_started_at
            if started is None or expires is None:
                started = now
                expires = now + timedelta(seconds=DEFAULT_OVERRIDE_TTL_SECONDS)
            return OverrideActivateResult(
                override_active=True,
                override_started_at=_ensure_aware(started),
                override_expires_at=expires,
            )

        if not operator.hashed_pin or not verify_password(confirmation_pin, operator.hashed_pin):
            log_shared_workstation_override_activation_refused(
                db=self._db,
                session_id=str(session.id),
                device_id=str(session.device_id),
                site_id=str(session.site_id),
                operator_user_id=str(session.operator_user_id),
                module_key=session.active_module_key,
                override_active=False,
                reason="confirmation_failed",
                request_id=request_id,
                user_id=actor_user_id,
            )
            return OverrideError(
                code=SHARED_WORKSTATION_OVERRIDE_CONFIRMATION_FAILED,
                message=_NEUTRAL_CONFIRMATION_MESSAGE,
                http_status=403,
            )

        session.override_active = True
        session.override_started_at = now
        self._db.add(session)
        self._db.commit()
        self._db.refresh(session)

        log_shared_workstation_override_activated(
            db=self._db,
            session_id=str(session.id),
            device_id=str(session.device_id),
            site_id=str(session.site_id),
            operator_user_id=str(session.operator_user_id),
            module_key=session.active_module_key,
            override_active=True,
            user_id=actor_user_id,
            request_id=request_id,
        )
        self._effective.invalidate_on_context_change(
            device_id=str(session.device_id),
            reason="override_activated",
            actor_user_id=actor_user_id,
        )

        expires = override_expires_at(session=session)
        assert expires is not None
        return OverrideActivateResult(
            override_active=True,
            override_started_at=now,
            override_expires_at=expires,
        )

    def deactivate_override(
        self,
        *,
        device_id: str,
        reason: str = "user_exit",
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> bool:
        """
        Désactive override si actif. Retourne True si override était actif et a été désactivé.
        Idempotent si déjà inactif (retourne False).
        """
        session = self._get_active_session(device_id=device_id)
        if session is None or not session.override_active:
            return False

        session.override_active = False
        session.override_started_at = None
        self._db.add(session)
        self._db.commit()
        self._db.refresh(session)

        log_shared_workstation_override_deactivated(
            db=self._db,
            session_id=str(session.id),
            device_id=str(session.device_id),
            site_id=str(session.site_id),
            operator_user_id=str(session.operator_user_id),
            module_key=session.active_module_key,
            override_active=False,
            user_id=actor_user_id,
            request_id=request_id,
            reason=reason,
        )
        self._effective.invalidate_on_context_change(
            device_id=str(session.device_id),
            reason="override_deactivated",
            actor_user_id=actor_user_id,
        )
        return True
