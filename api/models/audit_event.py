# Modèle AuditEvent — table audit_events (Story 3.3, architecture § Audit log).
# Journal des actions métier : déverrouillage caisse, ouvertures/fermetures session, etc.

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID

from api.models.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=True)
    resource_id = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_audit_events_timestamp", "timestamp"),
        Index("idx_audit_events_user_id", "user_id"),
        Index("idx_audit_events_action", "action"),
    )
