"""Tests du module api.config.settings (Story 4.1 — canal push Paheko, résilience)."""

import pytest

from api.config.settings import Settings, get_settings


def test_settings_has_paheko_and_resilience_fields():
    """Les settings exposent les champs canal push et résilience."""
    get_settings.cache_clear()
    s = get_settings()
    assert hasattr(s, "paheko_plugin_url")
    assert hasattr(s, "paheko_plugin_secret")
    assert hasattr(s, "paheko_push_max_retries")
    assert hasattr(s, "paheko_push_backoff_seconds")
    assert hasattr(s, "paheko_push_backoff_factor")
    assert hasattr(s, "redis_stream_push_caisse")


def test_settings_resilience_defaults():
    """Valeurs par défaut de résilience (FR19)."""
    get_settings.cache_clear()
    s = get_settings()
    assert s.paheko_push_max_retries == 5
    assert s.paheko_push_backoff_seconds == 1.0
    assert s.paheko_push_backoff_factor == 2.0
    assert s.redis_stream_push_caisse == "recyclic:push:caisse"


def test_settings_load_paheko_from_env(monkeypatch):
    """Chargement URL et résilience depuis variables d'environnement (mock)."""
    get_settings.cache_clear()
    monkeypatch.setenv("PAHEKO_PLUGIN_URL", "https://paheko.example/plugin/push")
    monkeypatch.setenv("PAHEKO_PLUGIN_SECRET", "secret-value")
    monkeypatch.setenv("PAHEKO_PUSH_MAX_RETRIES", "3")
    monkeypatch.setenv("PAHEKO_PUSH_BACKOFF_SECONDS", "2.5")
    s = get_settings()
    assert s.paheko_plugin_url == "https://paheko.example/plugin/push"
    assert s.paheko_plugin_secret is not None
    assert s.paheko_plugin_secret.get_secret_value() == "secret-value"
    assert s.paheko_push_max_retries == 3
    assert s.paheko_push_backoff_seconds == 2.5


def test_settings_secret_not_in_repr(monkeypatch):
    """Le secret ne doit pas apparaître en clair dans repr (NFR-S1, NFR-S2)."""
    get_settings.cache_clear()
    monkeypatch.setenv("PAHEKO_PLUGIN_SECRET", "sensitive-data")
    s = get_settings()
    r = repr(s)
    assert "sensitive-data" not in r
