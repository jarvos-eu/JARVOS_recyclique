"""Schémas PIN poste partagé — Epic 27.6 (lock screen opérateur)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from recyclic_api.schemas.pin import PinSetRequest


class SharedWorkstationOperatorPinVerifyRequest(BaseModel):
    """Body POST /v1/shared-workstation/operator-pin/verify."""

    operator_user_id: UUID
    pin: str

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, v: str) -> str:
        return PinSetRequest.validate_pin(v)


class SharedWorkstationOperatorPinVerifyResponse(BaseModel):
    session_id: UUID
    device_id: UUID
    operator_user_id: UUID
    site_id: UUID
    started_at: datetime


class SharedWorkstationOperatorSessionStatusResponse(BaseModel):
    active: bool
    operator_user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None


class ClearOperatorPinLockoutRequest(BaseModel):
    operator_user_id: UUID
