"""Service session opérateur poste partagé (Epic 27.2) — PIN 27.6, timeout 27.9."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from recyclic_api.core.audit import (
    log_device_operator_session_ended,
    log_device_operator_session_started,
    log_shared_workstation_operator_locked_manual,
    log_shared_workstation_operator_locked_timeout,
)
from recyclic_api.core.exceptions import NotFoundError, ValidationError
from recyclic_api.models.device_operator_session import (
    DeviceOperatorSession,
    DeviceOperatorSessionStatus,
)
from recyclic_api.models.registered_device import (
    DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
    RegisteredDevice,
    RegisteredDeviceStatus,
    RegisteredDeviceType,
)
from recyclic_api.models.user import User
from recyclic_api.modules.module_config.registry import is_active_module_key
from recyclic_api.services.registered_device_service import RegisteredDeviceService

HEARTBEAT_MIN_INTERVAL_SECONDS = 30


def _as_uuid(value: Union[str, UUID, None]) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def effective_inactivity_timeout_seconds(device: RegisteredDevice) -> int:
    timeout = device.inactivity_timeout_seconds
    if timeout is None:
        return DEFAULT_INACTIVITY_TIMEOUT_SECONDS
    return int(timeout)


def idle_seconds_since_activity(*, session: DeviceOperatorSession, now: datetime) -> float:
    last = session.last_activity_at
    if last is None:
        return 0.0
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return max(0.0, (now - last).total_seconds())


def seconds_until_lock(
    *,
    session: DeviceOperatorSession,
    timeout_seconds: int,
    now: Optional[datetime] = None,
) -> int:
    now = now or _utc_now()
    idle = idle_seconds_since_activity(session=session, now=now)
    remaining = int(timeout_seconds - idle)
    return max(0, remaining)


def is_session_expired(
    *,
    session: DeviceOperatorSession,
    timeout_seconds: int,
    now: Optional[datetime] = None,
) -> bool:
    return seconds_until_lock(session=session, timeout_seconds=timeout_seconds, now=now) <= 0


@dataclass(frozen=True)
class OperatorSessionStatusEnriched:
    active: bool
    operator_user_id: Optional[str]
    session_id: Optional[str]
    last_activity_at: Optional[datetime]
    inactivity_timeout_seconds: Optional[int]
    seconds_until_lock: Optional[int]


class DeviceOperatorSessionService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _require_operator(self, operator_user_id: str) -> User:
        user = self._db.query(User).filter(User.id == _as_uuid(operator_user_id)).first()
        if not user:
            raise NotFoundError("Opérateur introuvable")
        return user

    def _require_active_device(self, device_id: str) -> RegisteredDevice:
        device = RegisteredDeviceService(self._db).get_required(device_id=device_id)
        if device.device_type != RegisteredDeviceType.SHARED_WORKSTATION.value:
            raise ValidationError("device_type incorrect pour une session opérateur")
        if device.status != RegisteredDeviceStatus.ACTIVE.value:
            raise ValidationError("Poste partagé indisponible")
        return device

    def get_active_for_device(self, *, device_id: str) -> Optional[DeviceOperatorSession]:
        return (
            self._db.query(DeviceOperatorSession)
            .filter(
                DeviceOperatorSession.device_id == _as_uuid(device_id),
                DeviceOperatorSession.status == DeviceOperatorSessionStatus.ACTIVE.value,
            )
            .first()
        )

    def _log_session_end(
        self,
        *,
        session: DeviceOperatorSession,
        reason: str,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        common = dict(
            db=self._db,
            session_id=str(session.id),
            device_id=str(session.device_id),
            site_id=str(session.site_id),
            operator_user_id=str(session.operator_user_id),
            module_key=session.active_module_key,
            override_active=session.override_active,
            user_id=actor_user_id,
            request_id=request_id,
            reason=reason,
        )
        if reason in ("manual_lock", "handoff"):
            log_shared_workstation_operator_locked_manual(**common)
        elif reason == "timeout":
            log_shared_workstation_operator_locked_timeout(**common)
        else:
            log_device_operator_session_ended(**common)

    def _supersede_active(self, *, device_id: str, now: datetime) -> None:
        active = self.get_active_for_device(device_id=device_id)
        if active is None:
            return
        active.status = DeviceOperatorSessionStatus.SUPERSEDED.value
        active.ended_at = now
        self._db.add(active)
        self._log_session_end(session=active, reason="superseded")

    def start_session(
        self,
        *,
        device_id: str,
        operator_user_id: str,
        active_module_key: Optional[str] = None,
        override_active: bool = False,
        actor_user_id: Optional[str] = None,
    ) -> DeviceOperatorSession:
        """
        Démarre une session opérateur — appel interne / tests ; PIN public en story 27.6.
        """
        device = self._require_active_device(device_id)
        self._require_operator(operator_user_id)
        if active_module_key is not None and not is_active_module_key(active_module_key):
            raise ValidationError(f"module_key inconnu ou inactif : {active_module_key!r}")

        now = _utc_now()
        self._supersede_active(device_id=device_id, now=now)

        session = DeviceOperatorSession(
            device_id=device.id,
            operator_user_id=_as_uuid(operator_user_id),
            site_id=device.site_id,
            active_module_key=active_module_key,
            override_active=override_active,
            status=DeviceOperatorSessionStatus.ACTIVE.value,
            started_at=now,
            last_activity_at=now,
        )
        self._db.add(session)
        self._db.commit()
        self._db.refresh(session)

        log_device_operator_session_started(
            db=self._db,
            device_id=str(device.id),
            operator_user_id=operator_user_id,
            site_id=str(device.site_id),
            module_key=active_module_key,
            override_active=override_active,
            user_id=actor_user_id,
            session_id=str(session.id),
        )
        return session

    def end_session(
        self,
        *,
        session: DeviceOperatorSession,
        actor_user_id: Optional[str] = None,
        reason: str = "ended",
        request_id: Optional[str] = None,
    ) -> DeviceOperatorSession:
        if session.status != DeviceOperatorSessionStatus.ACTIVE.value:
            return session
        now = _utc_now()
        session.status = DeviceOperatorSessionStatus.ENDED.value
        session.ended_at = now
        session.last_activity_at = now
        self._db.add(session)
        self._db.commit()
        self._db.refresh(session)

        self._log_session_end(
            session=session,
            reason=reason,
            actor_user_id=actor_user_id,
            request_id=request_id,
        )
        return session

    def end_active_session_for_device(
        self,
        *,
        device_id: str,
        reason: str,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Termine la session ACTIVE du poste. Retourne (ended, session_id).
        Idempotent si aucune session active (ended=False).
        """
        active = self.get_active_for_device(device_id=device_id)
        if active is None:
            return False, None
        ended = self.end_session(
            session=active,
            actor_user_id=actor_user_id,
            reason=reason,
            request_id=request_id,
        )
        return True, str(ended.id)

    def record_activity(
        self,
        *,
        device_id: str,
        now: Optional[datetime] = None,
    ) -> bool:
        """
        Met à jour last_activity_at si intervalle min écoulé.
        Retourne True si touché, False si throttled. Lève ValidationError si pas de session.
        """
        session = self.get_active_for_device(device_id=device_id)
        if session is None:
            raise ValidationError("Session opérateur active requise")
        now = now or _utc_now()
        last = session.last_activity_at
        if last is not None:
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            if (now - last).total_seconds() < HEARTBEAT_MIN_INTERVAL_SECONDS:
                return False
        session.last_activity_at = now
        self._db.add(session)
        self._db.commit()
        return True

    def expire_active_session_if_idle(
        self,
        *,
        device_id: str,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> bool:
        """Auto-invalide session expirée. Retourne True si session terminée."""
        active = self.get_active_for_device(device_id=device_id)
        if active is None:
            return False
        device = RegisteredDeviceService(self._db).get_required(device_id=device_id)
        timeout = effective_inactivity_timeout_seconds(device)
        now = now or _utc_now()
        if not is_session_expired(session=active, timeout_seconds=timeout, now=now):
            return False
        self.end_session(
            session=active,
            actor_user_id=actor_user_id,
            reason="timeout",
            request_id=request_id,
        )
        return True

    def get_enriched_session_status(
        self,
        *,
        device_id: str,
        now: Optional[datetime] = None,
    ) -> OperatorSessionStatusEnriched:
        now = now or _utc_now()
        active = self.get_active_for_device(device_id=device_id)
        if active is None:
            return OperatorSessionStatusEnriched(
                active=False,
                operator_user_id=None,
                session_id=None,
                last_activity_at=None,
                inactivity_timeout_seconds=None,
                seconds_until_lock=None,
            )
        device = RegisteredDeviceService(self._db).get_required(device_id=device_id)
        timeout = effective_inactivity_timeout_seconds(device)
        return OperatorSessionStatusEnriched(
            active=True,
            operator_user_id=str(active.operator_user_id),
            session_id=str(active.id),
            last_activity_at=active.last_activity_at,
            inactivity_timeout_seconds=timeout,
            seconds_until_lock=seconds_until_lock(
                session=active,
                timeout_seconds=timeout,
                now=now,
            ),
        )

    def invalidate_sessions_for_device(
        self,
        *,
        device_id: str,
        reason: str = "device_change",
        actor_user_id: Optional[str] = None,
    ) -> List[DeviceOperatorSession]:
        now = _utc_now()
        sessions = (
            self._db.query(DeviceOperatorSession)
            .filter(
                DeviceOperatorSession.device_id == _as_uuid(device_id),
                DeviceOperatorSession.status == DeviceOperatorSessionStatus.ACTIVE.value,
            )
            .all()
        )
        for session in sessions:
            session.status = DeviceOperatorSessionStatus.INVALIDATED.value
            session.ended_at = now
            session.last_activity_at = now
            self._db.add(session)
            self._log_session_end(session=session, reason=reason, actor_user_id=actor_user_id)
        if sessions:
            self._db.commit()
        return sessions

    def invalidate_on_device_or_operator_change(
        self,
        *,
        device_id: Optional[str] = None,
        operator_user_id: Optional[str] = None,
        reason: str = "context_change",
        actor_user_id: Optional[str] = None,
    ) -> List[DeviceOperatorSession]:
        now = _utc_now()
        query = self._db.query(DeviceOperatorSession).filter(
            DeviceOperatorSession.status == DeviceOperatorSessionStatus.ACTIVE.value,
        )
        if device_id is not None:
            query = query.filter(DeviceOperatorSession.device_id == _as_uuid(device_id))
        if operator_user_id is not None:
            query = query.filter(
                DeviceOperatorSession.operator_user_id == _as_uuid(operator_user_id)
            )
        sessions = query.all()
        for session in sessions:
            session.status = DeviceOperatorSessionStatus.INVALIDATED.value
            session.ended_at = now
            session.last_activity_at = now
            self._db.add(session)
            self._log_session_end(session=session, reason=reason, actor_user_id=actor_user_id)
        if sessions:
            self._db.commit()
        return sessions

    def touch_activity(self, *, session: DeviceOperatorSession) -> None:
        session.last_activity_at = _utc_now()
        self._db.add(session)
        self._db.commit()
