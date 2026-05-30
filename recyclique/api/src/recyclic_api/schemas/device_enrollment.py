"""Schémas Pydantic — enrôlement poste partagé (Epic 27.4)."""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from recyclic_api.models.device_enrollment_code import DeviceEnrollmentPurpose

EnrollmentPurposeLiteral = Literal[
    DeviceEnrollmentPurpose.INITIAL_ENROLLMENT.value,
    DeviceEnrollmentPurpose.RECONNECT.value,
    DeviceEnrollmentPurpose.REPLACE.value,
]

ConflictActionLiteral = Literal["refuse", "replace_definitively", "create_distinct"]


class DeviceEnrollmentCodeIssueRequest(BaseModel):
    purpose: EnrollmentPurposeLiteral


class DeviceEnrollmentCodeIssueResponse(BaseModel):
    code: str
    expires_at: datetime
    purpose: str


class SharedWorkstationEnrollCompleteRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=12)

    @field_validator("code")
    @classmethod
    def _normalize_code(cls, v: str) -> str:
        return v.strip().upper()


class SharedWorkstationEnrollCompleteResponse(BaseModel):
    device_id: str
    device_secret: str
    device_name: str
    site_id: str


class SharedWorkstationDeviceStatusResponse(BaseModel):
    device_id: str
    device_name: str
    site_id: str
    status: str
    allowed_module_keys: List[str] = Field(default_factory=list)
    inactivity_timeout_seconds: Optional[int] = None


class RegisteredDeviceConflictResolveRequest(BaseModel):
    action: ConflictActionLiteral
    name: Optional[str] = Field(None, min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def _name_required_for_distinct(cls, v: Optional[str], info) -> Optional[str]:
        return v


class RegisteredDeviceConflictResolveResponse(BaseModel):
    device_id: str
    status: str
    distinct_device_id: Optional[str] = None
    enrollment_code: Optional[str] = None
    enrollment_code_expires_at: Optional[datetime] = None
    enrollment_code_purpose: Optional[str] = None
