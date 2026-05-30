"""Session opérateur PIN sur poste partagé (Epic 27.2) — distinct de user_sessions et cash_sessions."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from recyclic_api.core.database import Base


class DeviceOperatorSessionStatus(str, enum.Enum):
    ACTIVE = "active"
    ENDED = "ended"
    SUPERSEDED = "superseded"
    INVALIDATED = "invalidated"


class DeviceOperatorSession(Base):
    """
    Session opérateur active sur un poste partagé enrôlé.

    Au plus une session ``active`` par ``device_id`` (contrainte applicative).
    La vérification PIN publique (story 27.6) appellera ``DeviceOperatorSessionService.start_session``.
    """

    __tablename__ = "device_operator_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("registered_devices.id"),
        nullable=False,
        index=True,
    )
    operator_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    site_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sites.id"),
        nullable=False,
        index=True,
    )
    active_module_key = Column(String(64), nullable=True)
    override_active = Column(Boolean, nullable=False, server_default=text("false"))
    status = Column(String(32), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    device = relationship("RegisteredDevice", lazy="joined")
    operator = relationship("User", lazy="joined")
    site = relationship("Site", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<DeviceOperatorSession(id={self.id}, device_id={self.device_id}, "
            f"operator_user_id={self.operator_user_id}, status={self.status})>"
        )
