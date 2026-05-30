"""Service session opérateur poste partagé (Epic 27.2) — préparation PIN story 27.6."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from recyclic_api.core.audit import log_device_operator_session_ended, log_device_operator_session_started
from recyclic_api.core.exceptions import NotFoundError, ValidationError
from recyclic_api.models.device_operator_session import (
    DeviceOperatorSession,
    DeviceOperatorSessionStatus,
)
from recyclic_api.models.registered_device import (
    RegisteredDevice,
    RegisteredDeviceStatus,
    RegisteredDeviceType,
)
from recyclic_api.models.user import User
from recyclic_api.modules.module_config.registry import is_active_module_key
from recyclic_api.services.registered_device_service import RegisteredDeviceService


def _as_uuid(value: Union[str, UUID, None]) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


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

    def _supersede_active(self, *, device_id: str, now: datetime) -> None:
        active = self.get_active_for_device(device_id=device_id)
        if active is None:
            return
        active.status = DeviceOperatorSessionStatus.SUPERSEDED.value
        active.ended_at = now
        self._db.add(active)
        log_device_operator_session_ended(
            db=self._db,
            device_id=str(active.device_id),
            operator_user_id=str(active.operator_user_id),
            site_id=str(active.site_id),
            module_key=active.active_module_key,
            override_active=active.override_active,
            session_id=str(active.id),
            reason="superseded",
        )

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

        log_device_operator_session_ended(
            db=self._db,
            device_id=str(session.device_id),
            operator_user_id=str(session.operator_user_id),
            site_id=str(session.site_id),
            module_key=session.active_module_key,
            override_active=session.override_active,
            user_id=actor_user_id,
            session_id=str(session.id),
            reason="ended",
        )
        return session

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
            log_device_operator_session_ended(
                db=self._db,
                device_id=str(session.device_id),
                operator_user_id=str(session.operator_user_id),
                site_id=str(session.site_id),
                module_key=session.active_module_key,
                override_active=session.override_active,
                user_id=actor_user_id,
                session_id=str(session.id),
                reason=reason,
            )
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
            log_device_operator_session_ended(
                db=self._db,
                device_id=str(session.device_id),
                operator_user_id=str(session.operator_user_id),
                site_id=str(session.site_id),
                module_key=session.active_module_key,
                override_active=session.override_active,
                user_id=actor_user_id,
                session_id=str(session.id),
                reason=reason,
            )
        if sessions:
            self._db.commit()
        return sessions

    def touch_activity(self, *, session: DeviceOperatorSession) -> None:
        session.last_activity_at = _utc_now()
        self._db.add(session)
        self._db.commit()
