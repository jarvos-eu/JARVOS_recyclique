# Modèle RegistrationRequest — table registration_request (RecyClique, Story 3.1).
# Inscription en attente d'approbation admin.

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID

from api.models.base import Base


class RegistrationRequest(Base):
    __tablename__ = "registration_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(128), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    requested_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        Index("idx_registration_request_status", "status"),
        Index("idx_registration_request_requested_at", "requested_at"),
    )
