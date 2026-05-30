"""Service — credentials device poste partagé (Epic 27.4)."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from recyclic_api.core.security import hash_password, verify_password
from recyclic_api.models.registered_device import RegisteredDevice, RegisteredDeviceStatus
from recyclic_api.models.registered_device_credential import (
    RegisteredDeviceCredential,
    RegisteredDeviceCredentialStatus,
)


def generate_device_secret() -> str:
    """Secret aléatoire url-safe (32 bytes)."""
    return secrets.token_urlsafe(32)


def _secret_prefix(secret: str) -> str:
    return secret[:6]


def _as_uuid(value: str | UUID) -> UUID:
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


class CredentialVerifyResult:
    __slots__ = ("credential", "device", "conflict_detected", "revoked")

    def __init__(
        self,
        *,
        credential: Optional[RegisteredDeviceCredential] = None,
        device: Optional[RegisteredDevice] = None,
        conflict_detected: bool = False,
        revoked: bool = False,
    ) -> None:
        self.credential = credential
        self.device = device
        self.conflict_detected = conflict_detected
        self.revoked = revoked


class RegisteredDeviceCredentialService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_active_for_device(
        self, *, device_id: str
    ) -> Optional[RegisteredDeviceCredential]:
        return (
            self._db.query(RegisteredDeviceCredential)
            .filter(
                RegisteredDeviceCredential.device_id == _as_uuid(device_id),
                RegisteredDeviceCredential.status
                == RegisteredDeviceCredentialStatus.ACTIVE.value,
            )
            .first()
        )

    def supersede_active(
        self,
        *,
        device_id: str,
        reason: str,
    ) -> None:
        now = datetime.now(timezone.utc)
        active = self.get_active_for_device(device_id=device_id)
        if active is None:
            return
        active.status = RegisteredDeviceCredentialStatus.SUPERSEDED.value
        active.revoked_at = now
        active.revocation_reason = reason
        self._db.add(active)

    def create_active_credential(
        self,
        *,
        device_id: str,
        secret: str,
    ) -> RegisteredDeviceCredential:
        self.supersede_active(device_id=device_id, reason="replaced")
        cred = RegisteredDeviceCredential(
            device_id=_as_uuid(device_id),
            secret_hash=hash_password(secret),
            secret_prefix=_secret_prefix(secret),
            status=RegisteredDeviceCredentialStatus.ACTIVE.value,
        )
        self._db.add(cred)
        return cred

    def verify(
        self,
        *,
        device_id: str,
        secret: str,
    ) -> CredentialVerifyResult:
        """Valide possession secret ; détecte conflit si ancien credential révoqué."""
        device = (
            self._db.query(RegisteredDevice)
            .filter(RegisteredDevice.id == _as_uuid(device_id))
            .first()
        )
        if device is None:
            return CredentialVerifyResult(device=None)

        active = self.get_active_for_device(device_id=device_id)
        if active and verify_password(secret, active.secret_hash):
            if device.status != RegisteredDeviceStatus.ACTIVE.value:
                return CredentialVerifyResult(
                    device=device, credential=active, revoked=True
                )
            return CredentialVerifyResult(credential=active, device=device)

        # Chercher un credential non-actif correspondant (ancien secret)
        stale_matches = (
            self._db.query(RegisteredDeviceCredential)
            .filter(
                RegisteredDeviceCredential.device_id == _as_uuid(device_id),
                RegisteredDeviceCredential.status.in_(
                    [
                        RegisteredDeviceCredentialStatus.SUPERSEDED.value,
                        RegisteredDeviceCredentialStatus.REVOKED.value,
                    ]
                ),
            )
            .all()
        )
        for cred in stale_matches:
            if verify_password(secret, cred.secret_hash):
                conflict = active is not None
                return CredentialVerifyResult(
                    device=device,
                    credential=cred,
                    conflict_detected=conflict,
                    revoked=True,
                )

        # Désalignement device_id / secret inconnu
        if active is not None:
            return CredentialVerifyResult(device=device, revoked=True)

        return CredentialVerifyResult(device=device, revoked=True)

    def mark_device_conflict_if_needed(
        self, *, device: RegisteredDevice
    ) -> bool:
        """Passe le device en conflict si credential actif existe."""
        if device.status == RegisteredDeviceStatus.CONFLICT.value:
            return False
        active = self.get_active_for_device(device_id=str(device.id))
        if active is None:
            return False
        device.status = RegisteredDeviceStatus.CONFLICT.value
        self._db.add(device)
        return True

    def touch_last_contact(self, *, device: RegisteredDevice) -> None:
        device.last_contact_at = datetime.now(timezone.utc)
        self._db.add(device)
