"""Postes partagés enrôlés (Epic 27) — distinct de cash_registers et poste_reception."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from recyclic_api.core.database import Base


class RegisteredDeviceType(str, enum.Enum):
    SHARED_WORKSTATION = "shared_workstation"


class RegisteredDeviceStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING_ENROLLMENT = "pending_enrollment"
    IDENTITY_LOST = "identity_lost"
    CONFLICT = "conflict"
    REVOKED = "revoked"


# Timeout inactivité par défaut (15 min) — ajustable story 27.9
DEFAULT_INACTIVITY_TIMEOUT_SECONDS = 900


class RegisteredDevice(Base):
    """
    Registre serveur des postes partagés enrôlés.

    L'identifiant stable API est ``device_id`` (colonne ``id``) — jamais confondu avec
    ``cash_registers.id`` ni ``poste_reception.id``.
    """

    __tablename__ = "registered_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_type = Column(String(64), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False, index=True)
    status = Column(String(32), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    allowed_module_keys = Column(JSON, nullable=False, server_default=text("'[]'"))
    inactivity_timeout_seconds = Column(Integer, nullable=True)
    last_contact_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    site = relationship("Site", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<RegisteredDevice(device_id={self.id}, name={self.name!r}, "
            f"status={self.status})>"
        )
