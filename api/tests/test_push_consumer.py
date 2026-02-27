"""Tests du worker push Redis Streams → Paheko (Story 4.2)."""

import pytest

from api.config import get_settings
from api.workers.push_consumer import (
    get_push_worker_state,
    run_push_consumer,
    _send_to_paheko,
)


def test_get_push_worker_state_returns_expected_keys():
    """L'état du worker expose configured, running, last_error, last_success_at."""
    state = get_push_worker_state()
    assert "configured" in state
    assert "running" in state
    assert "last_error" in state
    assert "last_success_at" in state


def test_run_push_consumer_exits_when_unconfigured(monkeypatch):
    """Sans redis_url, le consumer sort immédiatement sans erreur."""
    get_settings.cache_clear()
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("PAHEKO_PLUGIN_URL", raising=False)
    monkeypatch.delenv("PAHEKO_PLUGIN_SECRET", raising=False)
    run_push_consumer()
    state = get_push_worker_state()
    assert state["configured"] is False


def test_send_to_paheko_returns_false_on_connection_error():
    """Échec (URL invalide ou connexion refusée) retourne (False, message)."""
    ok, err = _send_to_paheko(
        "http://",
        "secret",
        {"event_type": "pos.ticket.created"},
    )
    assert ok is False
    assert err is not None
