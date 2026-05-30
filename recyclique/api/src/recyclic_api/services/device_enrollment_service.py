"""Service — enrôlement, reconnexion, remplacement poste partagé (Epic 27.4)."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from recyclic_api.core.exceptions import NotFoundError, ValidationError
from recyclic_api.models.device_enrollment_code import (
    DeviceEnrollmentCode,
    DeviceEnrollmentPurpose,
)
from recyclic_api.models.registered_device import (
    RegisteredDevice,
    RegisteredDeviceStatus,
    RegisteredDeviceType,
)
from recyclic_api.models.registered_device_credential import (
    RegisteredDeviceCredentialStatus,
)
from recyclic_api.schemas.registered_device import RegisteredDeviceCreate
from recyclic_api.services.device_operator_session_service import DeviceOperatorSessionService
from recyclic_api.services.registered_device_credential_service import (
    RegisteredDeviceCredentialService,
    generate_device_secret,
)
from recyclic_api.services.registered_device_service import RegisteredDeviceService

ENROLLMENT_CODE_TTL_MINUTES = 15
ENROLLMENT_CODE_LENGTH = 8
# Alphabet sans ambiguïté 0/O/1/I
_ENROLLMENT_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class EnrollmentError(Exception):
    def __init__(self, *, code: str, message: str, http_status: int = 400) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(message)


@dataclass(frozen=True)
class EnrollmentCodeIssueResult:
    code: str
    expires_at: datetime
    purpose: str


@dataclass(frozen=True)
class EnrollmentCompleteResult:
    device_id: str
    device_secret: str
    device_name: str
    site_id: str
    purpose: str


@dataclass(frozen=True)
class ConflictResolveResult:
    device: RegisteredDevice
    distinct_device_id: Optional[str] = None
    enrollment_code: Optional[EnrollmentCodeIssueResult] = None


def _as_uuid(value: str | UUID) -> UUID:
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def _generate_enrollment_code() -> str:
    return "".join(
        secrets.choice(_ENROLLMENT_ALPHABET) for _ in range(ENROLLMENT_CODE_LENGTH)
    )


def _expected_status_for_purpose(purpose: str) -> set[str]:
    if purpose == DeviceEnrollmentPurpose.INITIAL_ENROLLMENT.value:
        return {RegisteredDeviceStatus.PENDING_ENROLLMENT.value}
    if purpose == DeviceEnrollmentPurpose.RECONNECT.value:
        return {
            RegisteredDeviceStatus.IDENTITY_LOST.value,
            RegisteredDeviceStatus.PENDING_ENROLLMENT.value,
        }
    if purpose == DeviceEnrollmentPurpose.REPLACE.value:
        return {
            RegisteredDeviceStatus.ACTIVE.value,
            RegisteredDeviceStatus.CONFLICT.value,
        }
    return set()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_utc_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class DeviceEnrollmentService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._devices = RegisteredDeviceService(db)
        self._credentials = RegisteredDeviceCredentialService(db)
        self._sessions = DeviceOperatorSessionService(db)

    def _purge_stale_codes(self, *, device_id: str, purpose: str) -> None:
        now = _utc_now()
        stale = (
            self._db.query(DeviceEnrollmentCode)
            .filter(
                DeviceEnrollmentCode.device_id == _as_uuid(device_id),
                DeviceEnrollmentCode.purpose == purpose,
                DeviceEnrollmentCode.consumed_at.is_(None),
                DeviceEnrollmentCode.expires_at < now,
            )
            .all()
        )
        for row in stale:
            self._db.delete(row)

    def issue_code(
        self,
        *,
        device_id: str,
        purpose: str,
        created_by_user_id: str,
    ) -> EnrollmentCodeIssueResult:
        device = self._devices.get_required(device_id=device_id)
        if device.status == RegisteredDeviceStatus.REVOKED.value:
            raise ValidationError("Poste révoqué — impossible d'émettre un code")

        allowed = _expected_status_for_purpose(purpose)
        if device.status not in allowed:
            raise EnrollmentError(
                code="DEVICE_ENROLLMENT_STATE_INVALID",
                message=f"Statut {device.status!r} incompatible avec purpose {purpose!r}",
                http_status=422,
            )

        self._purge_stale_codes(device_id=device_id, purpose=purpose)

        expires_at = _utc_now() + timedelta(minutes=ENROLLMENT_CODE_TTL_MINUTES)
        for _ in range(10):
            code_value = _generate_enrollment_code()
            existing = (
                self._db.query(DeviceEnrollmentCode)
                .filter(DeviceEnrollmentCode.code == code_value)
                .first()
            )
            if existing:
                continue
            row = DeviceEnrollmentCode(
                device_id=device.id,
                code=code_value,
                purpose=purpose,
                expires_at=expires_at,
                created_by_user_id=_as_uuid(created_by_user_id),
            )
            self._db.add(row)
            self._db.commit()
            return EnrollmentCodeIssueResult(
                code=code_value, expires_at=expires_at, purpose=purpose
            )
        raise ValidationError("Impossible de générer un code unique")

    def complete_enrollment(self, *, code: str) -> EnrollmentCompleteResult:
        normalized = code.strip().upper()
        if not normalized:
            raise EnrollmentError(
                code="ENROLLMENT_CODE_INVALID",
                message="Code d'enrôlement invalide",
            )

        row = (
            self._db.query(DeviceEnrollmentCode)
            .filter(DeviceEnrollmentCode.code == normalized)
            .first()
        )
        if row is None:
            raise EnrollmentError(
                code="ENROLLMENT_CODE_INVALID",
                message="Code d'enrôlement inconnu",
            )

        now = _utc_now()
        if row.consumed_at is not None:
            raise EnrollmentError(
                code="ENROLLMENT_CODE_CONSUMED",
                message="Code déjà utilisé",
                http_status=409,
            )
        if _ensure_utc_aware(row.expires_at) < now:
            raise EnrollmentError(
                code="ENROLLMENT_CODE_EXPIRED",
                message="Code expiré",
                http_status=410,
            )

        device = self._devices.get_required(device_id=str(row.device_id))
        allowed = _expected_status_for_purpose(row.purpose)
        if device.status not in allowed:
            raise EnrollmentError(
                code="DEVICE_ENROLLMENT_STATE_INVALID",
                message=f"Statut device incompatible avec le code",
                http_status=422,
            )

        secret = generate_device_secret()
        self._credentials.create_active_credential(
            device_id=str(device.id), secret=secret
        )

        device.status = RegisteredDeviceStatus.ACTIVE.value
        device.last_contact_at = now
        row.consumed_at = now

        if row.purpose in (
            DeviceEnrollmentPurpose.REPLACE.value,
            DeviceEnrollmentPurpose.RECONNECT.value,
        ):
            self._sessions.invalidate_sessions_for_device(
                device_id=str(device.id),
                reason=row.purpose,
            )

        self._db.add(device)
        self._db.add(row)
        self._db.commit()
        self._db.refresh(device)

        return EnrollmentCompleteResult(
            device_id=str(device.id),
            device_secret=secret,
            device_name=device.name,
            site_id=str(device.site_id),
            purpose=row.purpose,
        )

    def mark_identity_lost(self, *, device_id: str) -> RegisteredDevice:
        device = self._devices.get_required(device_id=device_id)
        if device.status == RegisteredDeviceStatus.REVOKED.value:
            raise ValidationError("Poste révoqué")
        if device.status not in (
            RegisteredDeviceStatus.ACTIVE.value,
            RegisteredDeviceStatus.PENDING_ENROLLMENT.value,
        ):
            raise ValidationError(
                f"Transition identity_lost impossible depuis statut {device.status}"
            )

        self._credentials.supersede_active(
            device_id=str(device.id), reason="identity_lost"
        )
        device.status = RegisteredDeviceStatus.IDENTITY_LOST.value
        self._db.add(device)
        self._db.commit()
        self._db.refresh(device)
        return device

    def resolve_conflict(
        self,
        *,
        device_id: str,
        action: str,
        created_by_user_id: str,
        name: Optional[str] = None,
    ) -> ConflictResolveResult:
        device = self._devices.get_required(device_id=device_id)
        if device.status != RegisteredDeviceStatus.CONFLICT.value:
            raise ValidationError("Le poste n'est pas en statut conflict")

        if action == "refuse":
            device.status = RegisteredDeviceStatus.ACTIVE.value
            self._db.add(device)
            self._db.commit()
            self._db.refresh(device)
            return ConflictResolveResult(device=device)

        if action == "replace_definitively":
            from recyclic_api.models.registered_device_credential import (
                RegisteredDeviceCredential,
            )

            # Option A (story) : conserver le credential actif (machine légitime) ;
            # révoquer uniquement les credentials stale ; émettre un code replace.
            others = (
                self._db.query(RegisteredDeviceCredential)
                .filter(
                    RegisteredDeviceCredential.device_id == device.id,
                    RegisteredDeviceCredential.status
                    != RegisteredDeviceCredentialStatus.ACTIVE.value,
                )
                .all()
            )
            now = _utc_now()
            for cred in others:
                cred.status = RegisteredDeviceCredentialStatus.REVOKED.value
                cred.revoked_at = now
                cred.revocation_reason = "conflict_replace"
                self._db.add(cred)

            device.status = RegisteredDeviceStatus.ACTIVE.value
            self._sessions.invalidate_sessions_for_device(
                device_id=str(device.id), reason="conflict_replace"
            )
            self._db.add(device)
            self._db.commit()
            self._db.refresh(device)

            code_result = self.issue_code(
                device_id=str(device.id),
                purpose=DeviceEnrollmentPurpose.REPLACE.value,
                created_by_user_id=created_by_user_id,
            )
            return ConflictResolveResult(device=device, enrollment_code=code_result)

        if action == "create_distinct":
            if not name or not name.strip():
                raise ValidationError("name requis pour create_distinct")
            new_device = self._devices.create(
                data=RegisteredDeviceCreate(
                    name=name.strip(),
                    site_id=str(device.site_id),
                    location=device.location,
                    device_type=RegisteredDeviceType.SHARED_WORKSTATION.value,
                    status=RegisteredDeviceStatus.PENDING_ENROLLMENT.value,
                    allowed_module_keys=list(device.allowed_module_keys or []),
                    inactivity_timeout_seconds=device.inactivity_timeout_seconds,
                )
            )
            device.status = RegisteredDeviceStatus.ACTIVE.value
            self._db.add(device)
            self._db.commit()
            self._db.refresh(device)
            return ConflictResolveResult(
                device=device, distinct_device_id=str(new_device.id)
            )

        raise ValidationError(f"Action conflict inconnue: {action}")
