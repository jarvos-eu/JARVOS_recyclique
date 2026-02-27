"""
Publish events to Redis stream for push caisse → Paheko (Story 5.1, 5.3).
Worker push_consumer consumes this stream and sends to plugin Paheko.

Contrat pos.session.closed (Story 5.3) :
- Le plugin Paheko reçoit le payload (session_id, closed_at, closing_amount, actual_amount,
  variance_comment, total_sales, total_items) et doit : (1) clôturer la session côté Paheko,
  (2) contrôler les totaux RecyClique vs Paheko, (3) exécuter syncAccounting (écritures comptables).
- En cas d'erreur Paheko : retry par le worker selon config Epic 4 ; ne pas laisser la session
  RecyClique en état incohérent (session déjà marquée closed en BDD).
- NFR-I2 : les écritures compta respectent la config Paheko (comptes, exercice, moyens de paiement).
"""

import json
import logging
from typing import Any
from uuid import UUID

import redis

from api.config import get_settings

logger = logging.getLogger(__name__)


def _get_redis() -> redis.Redis | None:
    settings = get_settings()
    if not settings.redis_url:
        return None
    try:
        return redis.from_url(settings.redis_url, decode_responses=True)
    except Exception as e:
        logger.warning("Push publish: Redis unavailable: %s", e)
        return None


def publish_session_event(event_type: str, payload: dict[str, Any]) -> bool:
    """
    Publish a session event (pos.session.opened | pos.session.closed) to the push stream.
    Returns True if published, False if Redis unavailable or error.
    """
    settings = get_settings()
    stream_key = settings.redis_stream_push_caisse
    r = _get_redis()
    if r is None:
        return False
    try:
        message = {
            "event": event_type,
            "payload": json.dumps(payload),
        }
        r.xadd(stream_key, message, maxlen=10000)
        return True
    except Exception as e:
        logger.warning("Push publish failed: %s", e)
        return False


def publish_session_opened(
    session_id: UUID,
    operator_id: UUID,
    register_id: UUID,
    site_id: UUID,
    initial_amount: int,
    opened_at: str,
    session_type: str = "real",
) -> bool:
    """Publish pos.session.opened for Paheko plugin to create session."""
    return publish_session_event(
        "pos.session.opened",
        {
            "session_id": str(session_id),
            "operator_id": str(operator_id),
            "register_id": str(register_id),
            "site_id": str(site_id),
            "initial_amount": initial_amount,
            "opened_at": opened_at,
            "session_type": session_type,
        },
    )


def publish_session_closed(
    session_id: UUID,
    closed_at: str,
    closing_amount: int | None = None,
    actual_amount: int | None = None,
    variance_comment: str | None = None,
    total_sales: int | None = None,
    total_items: int | None = None,
) -> bool:
    """Publish pos.session.closed for Paheko plugin: clôture session + contrôle totaux + syncAccounting (Story 5.3)."""
    payload: dict[str, Any] = {
        "session_id": str(session_id),
        "closed_at": closed_at,
    }
    if closing_amount is not None:
        payload["closing_amount"] = closing_amount
    if actual_amount is not None:
        payload["actual_amount"] = actual_amount
    if variance_comment is not None:
        payload["variance_comment"] = variance_comment
    if total_sales is not None:
        payload["total_sales"] = total_sales
    if total_items is not None:
        payload["total_items"] = total_items
    return publish_session_event("pos.session.closed", payload)


def publish_ticket_created(payload: dict[str, Any]) -> bool:
    """
    Publish pos.ticket.created for Paheko plugin (Story 5.2).
    payload must contain: event, sale_id, cash_session_id, operator_id, items, payments, etc.
    Montants en centimes, poids en kg (conversion g cote plugin si besoin).
    """
    payload.setdefault("event", "pos.ticket.created")
    return publish_session_event("pos.ticket.created", payload)
