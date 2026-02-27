# Modèle LoginHistory — table login_history (RecyClique, Story 3.1).
# Traçabilité des connexions : user_id, ip, user_agent, success.

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID

from api.models.base import Base


class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    username = Column(String(128), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    success = Column(Boolean, nullable=False, default=False)
    logged_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_login_history_user_id", "user_id"),
        Index("idx_login_history_logged_at", "logged_at"),
    )
