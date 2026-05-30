"""Codes d'enrôlement one-time poste partagé (Epic 27.4)."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from recyclic_api.core.database import Base


class DeviceEnrollmentPurpose(str, enum.Enum):
    INITIAL_ENROLLMENT = "initial_enrollment"
    RECONNECT = "reconnect"
    REPLACE = "replace"


class DeviceEnrollmentCode(Base):
    __tablename__ = "device_enrollment_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("registered_devices.id"),
        nullable=False,
        index=True,
    )
    code = Column(String(12), nullable=False, unique=True, index=True)
    purpose = Column(String(32), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    device = relationship("RegisteredDevice", lazy="joined")
    created_by = relationship("User", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<DeviceEnrollmentCode(id={self.id}, device_id={self.device_id}, "
            f"purpose={self.purpose})>"
        )
