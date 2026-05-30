"""Credentials device poste partagé (Epic 27.4) — secret hashé, jamais en clair."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from recyclic_api.core.database import Base


class RegisteredDeviceCredentialStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    SUPERSEDED = "superseded"


class RegisteredDeviceCredential(Base):
    __tablename__ = "registered_device_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("registered_devices.id"),
        nullable=False,
        index=True,
    )
    secret_hash = Column(String(255), nullable=False)
    secret_prefix = Column(String(8), nullable=True)
    status = Column(String(32), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revocation_reason = Column(String(64), nullable=True)

    device = relationship("RegisteredDevice", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<RegisteredDeviceCredential(id={self.id}, device_id={self.device_id}, "
            f"status={self.status})>"
        )
