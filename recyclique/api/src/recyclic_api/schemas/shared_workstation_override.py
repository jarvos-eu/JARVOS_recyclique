"""Schémas override SuperAdmin poste partagé — Epic 27.10."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from recyclic_api.schemas.pin import PinSetRequest


class SharedWorkstationOverrideDeactivateReason(str, Enum):
    USER_EXIT = "user_exit"
    ADMIN_ACTION = "admin_action"


class SharedWorkstationOverrideActivateRequest(BaseModel):
    """Body POST /v1/shared-workstation/override/activate."""

    confirmation_pin: str

    @field_validator("confirmation_pin")
    @classmethod
    def validate_confirmation_pin(cls, v: str) -> str:
        return PinSetRequest.validate_pin(v)


class SharedWorkstationOverrideActivateResponse(BaseModel):
    override_active: bool
    override_started_at: datetime
    override_expires_at: datetime


class SharedWorkstationOverrideDeactivateRequest(BaseModel):
    """Body POST /v1/shared-workstation/override/deactivate."""

    reason: SharedWorkstationOverrideDeactivateReason = Field(
        default=SharedWorkstationOverrideDeactivateReason.USER_EXIT,
    )


class SharedWorkstationOverrideDeactivateResponse(BaseModel):
    override_active: bool
