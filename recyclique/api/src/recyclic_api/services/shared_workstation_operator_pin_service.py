"""Vérification PIN poste partagé + lockout Redis device+opérateur (Epic 27.6)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import redis
from sqlalchemy.orm import Session

from recyclic_api.core.audit import (
    log_shared_workstation_pin_failure,
    log_shared_workstation_pin_lockout,
    log_shared_workstation_pin_success,
)
from recyclic_api.core.exceptions import NotFoundError, ValidationError
from recyclic_api.core.security import verify_password
from uuid import UUID

from recyclic_api.models.device_operator_session import DeviceOperatorSession
from recyclic_api.models.user import User, UserStatus
from recyclic_api.services.device_operator_session_service import DeviceOperatorSessionService
from recyclic_api.services.registered_device_service import RegisteredDeviceService

logger = logging.getLogger(__name__)

SHARED_WS_PIN_MAX_FAILURES = 5
SHARED_WS_PIN_LOCKOUT_SECONDS = 300
SHARED_WS_PIN_FAIL_WINDOW_SECONDS = 300

SHARED_WORKSTATION_PIN_INVALID = "SHARED_WORKSTATION_PIN_INVALID"
SHARED_WORKSTATION_PIN_LOCKED = "SHARED_WORKSTATION_PIN_LOCKED"
SHARED_WORKSTATION_PIN_NOT_CONFIGURED = "SHARED_WORKSTATION_PIN_NOT_CONFIGURED"

_NEUTRAL_PIN_MESSAGE = "Identifiant ou PIN incorrect"
_LOCKOUT_MESSAGE = "Trop de tentatives — réessayez dans quelques minutes"


def _redis_key_fail(device_id: str, operator_user_id: str) -> str:
    return f"shared_ws:pin_fail:{device_id}:{operator_user_id}"


def _redis_key_lockout(device_id: str, operator_user_id: str) -> str:
    return f"shared_ws:pin_lockout:{device_id}:{operator_user_id}"


def _is_locked_out(redis_client: redis.Redis, device_id: str, operator_user_id: str) -> bool:
    try:
        return bool(redis_client.exists(_redis_key_lockout(device_id, operator_user_id)))
    except Exception:
        logger.warning(
            "shared_ws pin lockout check unavailable device_id=%s operator_user_id=%s",
            device_id,
            operator_user_id,
        )
        return False


def _register_failed_attempt(
    redis_client: redis.Redis,
    *,
    device_id: str,
    operator_user_id: str,
    db: Session,
    site_id: Optional[str],
    request_id: Optional[str],
) -> bool:
    """Incrémente les échecs ; retourne True si lockout appliqué."""
    try:
        key = _redis_key_fail(device_id, operator_user_id)
        n = redis_client.incr(key)
        if n == 1:
            redis_client.expire(key, SHARED_WS_PIN_FAIL_WINDOW_SECONDS)
        if n >= SHARED_WS_PIN_MAX_FAILURES:
            redis_client.setex(
                _redis_key_lockout(device_id, operator_user_id),
                SHARED_WS_PIN_LOCKOUT_SECONDS,
                "1",
            )
            log_shared_workstation_pin_lockout(
                db=db,
                device_id=device_id,
                operator_user_id=operator_user_id,
                site_id=site_id,
                request_id=request_id,
            )
            return True
    except Exception as exc:
        logger.warning(
            "shared_ws pin fail counter error device_id=%s operator_user_id=%s err=%s",
            device_id,
            operator_user_id,
            type(exc).__name__,
        )
    return False


def _clear_fail_window(redis_client: redis.Redis, device_id: str, operator_user_id: str) -> None:
    try:
        redis_client.delete(_redis_key_fail(device_id, operator_user_id))
    except Exception:
        pass


@dataclass(frozen=True)
class PinVerifyResult:
    session: DeviceOperatorSession


@dataclass(frozen=True)
class PinVerifyError:
    code: str
    message: str
    http_status: int


class SharedWorkstationOperatorPinService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._sessions = DeviceOperatorSessionService(db)

    def get_session_status(self, *, device_id: str) -> tuple[bool, Optional[str], Optional[str]]:
        active = self._sessions.get_active_for_device(device_id=device_id)
        if active is None:
            return False, None, None
        return True, str(active.operator_user_id), str(active.id)

    def clear_lockout(
        self,
        *,
        device_id: str,
        operator_user_id: str,
        redis_client: redis.Redis,
    ) -> None:
        try:
            redis_client.delete(
                _redis_key_fail(device_id, operator_user_id),
                _redis_key_lockout(device_id, operator_user_id),
            )
        except Exception as exc:
            logger.warning(
                "shared_ws pin clear lockout error device_id=%s operator_user_id=%s err=%s",
                device_id,
                operator_user_id,
                type(exc).__name__,
            )

    def verify_and_start_session(
        self,
        *,
        device_id: str,
        operator_user_id: str,
        pin_plain: str,
        redis_client: redis.Redis,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> PinVerifyResult | PinVerifyError:
        try:
            device = RegisteredDeviceService(self._db).get_required(device_id=device_id)
            site_id_default = str(device.site_id)
        except Exception:
            site_id_default = None

        if _is_locked_out(redis_client, device_id, operator_user_id):
            return PinVerifyError(
                code=SHARED_WORKSTATION_PIN_LOCKED,
                message=_LOCKOUT_MESSAGE,
                http_status=429,
            )

        try:
            operator_uuid = UUID(str(operator_user_id))
        except ValueError:
            operator_uuid = None
        user = (
            self._db.query(User).filter(User.id == operator_uuid).first()
            if operator_uuid is not None
            else None
        )
        if (
            user is None
            or not user.is_active
            or user.status not in (UserStatus.ACTIVE, UserStatus.APPROVED)
        ):
            _register_failed_attempt(
                redis_client,
                device_id=device_id,
                operator_user_id=operator_user_id,
                db=self._db,
                site_id=site_id_default,
                request_id=request_id,
            )
            log_shared_workstation_pin_failure(
                db=self._db,
                device_id=device_id,
                operator_user_id=operator_user_id,
                site_id=site_id_default,
                outcome="invalid",
                request_id=request_id,
            )
            return PinVerifyError(
                code=SHARED_WORKSTATION_PIN_INVALID,
                message=_NEUTRAL_PIN_MESSAGE,
                http_status=403,
            )

        if not user.hashed_pin:
            _register_failed_attempt(
                redis_client,
                device_id=device_id,
                operator_user_id=operator_user_id,
                db=self._db,
                site_id=str(user.site_id) if user.site_id else None,
                request_id=request_id,
            )
            log_shared_workstation_pin_failure(
                db=self._db,
                device_id=device_id,
                operator_user_id=operator_user_id,
                site_id=str(user.site_id) if user.site_id else None,
                outcome="not_configured",
                request_id=request_id,
            )
            return PinVerifyError(
                code=SHARED_WORKSTATION_PIN_NOT_CONFIGURED,
                message=_NEUTRAL_PIN_MESSAGE,
                http_status=403,
            )

        site_id = site_id_default

        if not verify_password(pin_plain, user.hashed_pin):
            locked = _register_failed_attempt(
                redis_client,
                device_id=device_id,
                operator_user_id=operator_user_id,
                db=self._db,
                site_id=site_id,
                request_id=request_id,
            )
            log_shared_workstation_pin_failure(
                db=self._db,
                device_id=device_id,
                operator_user_id=operator_user_id,
                site_id=site_id,
                outcome="lockout" if locked else "invalid",
                request_id=request_id,
            )
            if locked:
                return PinVerifyError(
                    code=SHARED_WORKSTATION_PIN_LOCKED,
                    message=_LOCKOUT_MESSAGE,
                    http_status=429,
                )
            return PinVerifyError(
                code=SHARED_WORKSTATION_PIN_INVALID,
                message=_NEUTRAL_PIN_MESSAGE,
                http_status=403,
            )

        _clear_fail_window(redis_client, device_id, operator_user_id)
        try:
            session = self._sessions.start_session(
                device_id=device_id,
                operator_user_id=operator_user_id,
                actor_user_id=actor_user_id,
            )
        except (NotFoundError, ValidationError):
            return PinVerifyError(
                code=SHARED_WORKSTATION_PIN_INVALID,
                message=_NEUTRAL_PIN_MESSAGE,
                http_status=403,
            )
        log_shared_workstation_pin_success(
            db=self._db,
            device_id=device_id,
            operator_user_id=operator_user_id,
            site_id=site_id,
            session_id=str(session.id),
            request_id=request_id,
            user_id=actor_user_id,
        )
        return PinVerifyResult(session=session)
