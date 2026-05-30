"""Service métier — registre RegisteredDevice (Epic 27.1)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from recyclic_api.core.exceptions import NotFoundError, ValidationError
from recyclic_api.models.registered_device import (
    DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
    RegisteredDevice,
    RegisteredDeviceStatus,
    RegisteredDeviceType,
)
from recyclic_api.models.site import Site
from recyclic_api.schemas.registered_device import (
    RegisteredDeviceCreate,
    RegisteredDeviceUpdate,
)


def _as_uuid(value: Union[str, UUID, None]) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def _effective_timeout(seconds: Optional[int]) -> Optional[int]:
    if seconds is None:
        return DEFAULT_INACTIVITY_TIMEOUT_SECONDS
    return seconds


class RegisteredDeviceService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        site_id: Optional[str] = None,
        status: Optional[str] = None,
        include_revoked: bool = False,
    ) -> List[RegisteredDevice]:
        query = self._db.query(RegisteredDevice)
        if site_id:
            query = query.filter(RegisteredDevice.site_id == _as_uuid(site_id))
        if status:
            query = query.filter(RegisteredDevice.status == status)
        if not include_revoked:
            query = query.filter(
                RegisteredDevice.status != RegisteredDeviceStatus.REVOKED.value
            )
        return query.offset(skip).limit(limit).all()

    def get(self, *, device_id: str) -> Optional[RegisteredDevice]:
        return (
            self._db.query(RegisteredDevice)
            .filter(RegisteredDevice.id == _as_uuid(device_id))
            .first()
        )

    def get_required(self, *, device_id: str) -> RegisteredDevice:
        device = self.get(device_id=device_id)
        if not device:
            raise NotFoundError("Poste partagé introuvable")
        return device

    def _require_site(self, site_id: str) -> Site:
        site = self._db.query(Site).filter(Site.id == _as_uuid(site_id)).first()
        if not site:
            raise NotFoundError("Site introuvable")
        return site

    def create(self, *, data: RegisteredDeviceCreate) -> RegisteredDevice:
        self._require_site(data.site_id)
        if data.device_type != RegisteredDeviceType.SHARED_WORKSTATION.value:
            raise ValidationError(
                f"device_type doit être {RegisteredDeviceType.SHARED_WORKSTATION.value!r}"
            )
        status = (
            data.status or RegisteredDeviceStatus.PENDING_ENROLLMENT.value
        )
        device = RegisteredDevice(
            device_type=RegisteredDeviceType.SHARED_WORKSTATION.value,
            name=data.name,
            location=data.location,
            site_id=_as_uuid(data.site_id),
            status=status,
            allowed_module_keys=list(data.allowed_module_keys),
            inactivity_timeout_seconds=_effective_timeout(
                data.inactivity_timeout_seconds
            ),
        )
        self._db.add(device)
        self._db.commit()
        self._db.refresh(device)
        return device

    def update(
        self, *, device: RegisteredDevice, data: RegisteredDeviceUpdate
    ) -> RegisteredDevice:
        old_site_id = device.site_id
        if data.site_id is not None:
            self._require_site(data.site_id)
            device.site_id = _as_uuid(data.site_id)
        if data.name is not None:
            device.name = data.name
        if data.location is not None:
            device.location = data.location
        if data.status is not None:
            device.status = data.status
            if data.status == RegisteredDeviceStatus.REVOKED.value:
                now = datetime.now(timezone.utc)
                if device.revoked_at is None:
                    device.revoked_at = now
            else:
                device.revoked_at = None
        if data.allowed_module_keys is not None:
            device.allowed_module_keys = list(data.allowed_module_keys)
        if data.inactivity_timeout_seconds is not None:
            device.inactivity_timeout_seconds = data.inactivity_timeout_seconds
        if data.last_contact_at is not None:
            device.last_contact_at = data.last_contact_at

        self._db.add(device)
        self._db.commit()
        self._db.refresh(device)
        from recyclic_api.services.shared_workstation_context_service import (
            SharedWorkstationContextService,
        )

        sw_service = SharedWorkstationContextService(self._db)
        if data.status == RegisteredDeviceStatus.REVOKED.value:
            sw_service.invalidate_sessions_for_device(
                device_id=str(device.id),
                reason="device_revoked",
            )
        elif data.site_id is not None and old_site_id != device.site_id:
            sw_service.invalidate_sessions_for_device(
                device_id=str(device.id),
                reason="device_site_change",
            )
        return device

    def revoke(self, *, device: RegisteredDevice) -> RegisteredDevice:
        """Révocation idempotente : status=revoked + revoked_at."""
        now = datetime.now(timezone.utc)
        if device.status != RegisteredDeviceStatus.REVOKED.value:
            device.status = RegisteredDeviceStatus.REVOKED.value
            device.revoked_at = now
        elif device.revoked_at is None:
            device.revoked_at = now
        self._db.add(device)
        self._db.commit()
        self._db.refresh(device)
        from recyclic_api.services.shared_workstation_context_service import (
            SharedWorkstationContextService,
        )

        SharedWorkstationContextService(self._db).invalidate_sessions_for_device(
            device_id=str(device.id),
            reason="device_revoked",
        )
        return device
