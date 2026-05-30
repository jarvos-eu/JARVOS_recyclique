"""Schémas session opérateur poste partagé — Epic 27.9 (timeout, handoff)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OperatorSessionEndReason(str, Enum):
    MANUAL_LOCK = "manual_lock"
    HANDOFF = "handoff"
    TIMEOUT = "timeout"


class SharedWorkstationOperatorSessionEndRequest(BaseModel):
    """Body POST /v1/shared-workstation/operator-session/end."""

    reason: OperatorSessionEndReason = Field(
        default=OperatorSessionEndReason.MANUAL_LOCK,
        description="Raison audit de fin de session",
    )


class SharedWorkstationOperatorSessionEndResponse(BaseModel):
    ended: bool
    session_id: Optional[UUID] = None


class SharedWorkstationOperatorSessionStatusResponse(BaseModel):
    active: bool
    operator_user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    last_activity_at: Optional[datetime] = None
    inactivity_timeout_seconds: Optional[int] = None
    seconds_until_lock: Optional[int] = None
    override_active: bool = False
    override_started_at: Optional[datetime] = None
    override_seconds_remaining: Optional[int] = None
    can_activate_super_admin_override: bool = False
