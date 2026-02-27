# Service audit — écriture dans audit_events (Story 3.3, 7.2).

from uuid import UUID

from sqlalchemy.orm import Session

from api.models import AuditEvent


def write_audit_event(
    db: Session,
    *,
    user_id: UUID | None = None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: str | None = None,
) -> AuditEvent:
    """Enregistre un événement dans audit_events. Flush uniquement (caller commit)."""
    event = AuditEvent(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
    )
    db.add(event)
    db.flush()
    return event
