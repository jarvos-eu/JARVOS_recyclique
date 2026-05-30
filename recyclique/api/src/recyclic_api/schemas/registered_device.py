"""Schémas Pydantic — RegisteredDevice (Epic 27.1)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from recyclic_api.models.registered_device import (
    DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
    RegisteredDeviceStatus,
    RegisteredDeviceType,
)
from recyclic_api.modules.module_config.registry import is_active_module_key

_MVP_DEVICE_TYPE = RegisteredDeviceType.SHARED_WORKSTATION.value
_ALLOWED_STATUSES = {s.value for s in RegisteredDeviceStatus}


def _validate_allowed_module_keys(keys: List[str]) -> List[str]:
    if not keys:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for raw in keys:
        key = str(raw).strip()
        if not key:
            raise ValueError("module_key vide interdit dans allowed_module_keys")
        if key in seen:
            raise ValueError(f"module_key en double: {key}")
        seen.add(key)
        if not is_active_module_key(key):
            raise ValueError(f"module_key inconnu du registre serveur: {key}")
        normalized.append(key)
    return normalized


def _validate_device_type(value: str) -> str:
    if value != _MVP_DEVICE_TYPE:
        raise ValueError(
            f"device_type doit être {_MVP_DEVICE_TYPE!r} (MVP Epic 27.1)"
        )
    return value


def _validate_status(value: str) -> str:
    if value not in _ALLOWED_STATUSES:
        raise ValueError(f"status invalide: {value}")
    return value


class RegisteredDeviceResponse(BaseModel):
    """Réponse API — identifiant canonique ``device_id`` (≠ cash_register_id)."""

    model_config = ConfigDict(from_attributes=True)

    device_id: str = Field(..., description="Identifiant stable du poste partagé (UUID)")
    device_type: str
    name: str
    location: Optional[str] = None
    site_id: str
    status: str
    revoked_at: Optional[datetime] = None
    allowed_module_keys: List[str] = Field(default_factory=list)
    inactivity_timeout_seconds: Optional[int] = None
    last_contact_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def _map_orm_id_to_device_id(cls, data: Any) -> Any:
        if hasattr(data, "id"):
            return {
                "device_id": str(data.id),
                "device_type": data.device_type,
                "name": data.name,
                "location": data.location,
                "site_id": str(data.site_id),
                "status": data.status,
                "revoked_at": data.revoked_at,
                "allowed_module_keys": data.allowed_module_keys or [],
                "inactivity_timeout_seconds": data.inactivity_timeout_seconds,
                "last_contact_at": data.last_contact_at,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
        if isinstance(data, dict) and "id" in data and "device_id" not in data:
            out = dict(data)
            out["device_id"] = str(out.pop("id"))
            return out
        return data

    @field_validator("site_id", "device_id", mode="before")
    @classmethod
    def _uuid_to_str(cls, v: Any) -> Any:
        if hasattr(v, "__str__"):
            return str(v)
        return v


class RegisteredDeviceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    site_id: str
    location: Optional[str] = Field(None, max_length=255)
    device_type: str = Field(
        default=_MVP_DEVICE_TYPE,
        description="MVP : seul shared_workstation est accepté",
    )
    status: Optional[str] = Field(
        default=RegisteredDeviceStatus.PENDING_ENROLLMENT.value,
        description="Défaut pending_enrollment à la création admin",
    )
    allowed_module_keys: List[str] = Field(default_factory=list)
    inactivity_timeout_seconds: Optional[int] = Field(
        None,
        ge=60,
        le=7200,
        description=f"NULL = défaut serveur ({DEFAULT_INACTIVITY_TIMEOUT_SECONDS}s)",
    )

    @field_validator("device_type")
    @classmethod
    def _device_type_mvp(cls, v: str) -> str:
        return _validate_device_type(v)

    @field_validator("status")
    @classmethod
    def _status_create(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v == RegisteredDeviceStatus.REVOKED.value:
            raise ValueError("Utiliser POST /revoke pour révoquer un poste")
        return _validate_status(v)

    @field_validator("allowed_module_keys")
    @classmethod
    def _allowlist(cls, v: List[str]) -> List[str]:
        return _validate_allowed_module_keys(v)

    @field_validator("site_id", mode="before")
    @classmethod
    def _site_id_str(cls, v: Any) -> str:
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError("site_id requis")
        return str(v).strip() if isinstance(v, str) else str(v)


class RegisteredDeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    site_id: Optional[str] = None
    status: Optional[str] = None
    allowed_module_keys: Optional[List[str]] = None
    inactivity_timeout_seconds: Optional[int] = Field(None, ge=60, le=7200)
    last_contact_at: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def _status_patch(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v == RegisteredDeviceStatus.REVOKED.value:
            raise ValueError("Utiliser POST /revoke pour révoquer un poste")
        return _validate_status(v)

    @field_validator("allowed_module_keys")
    @classmethod
    def _allowlist_patch(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        return _validate_allowed_module_keys(v)

    @field_validator("site_id", mode="before")
    @classmethod
    def _site_id_optional(cls, v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            raise ValueError("site_id ne peut pas être vide")
        return str(v).strip() if isinstance(v, str) else str(v)


class RegisteredDeviceRevokeRequest(BaseModel):
    """Corps optionnel pour révocation explicite (raison future)."""

    reason: Optional[str] = Field(None, max_length=500)
