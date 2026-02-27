# Checks sante reutilisables — GET /health et GET /v1/admin/health (Story 8.4).

from api.config import get_settings
from api.workers.push_consumer import get_push_worker_state


def check_database() -> str:
    """Retourne 'ok', 'unconfigured' ou 'error'."""
    settings = get_settings()
    if not settings.database_url:
        return "unconfigured"
    try:
        from sqlalchemy import text
        from api.db.session import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"


def check_redis() -> str:
    """Retourne 'ok', 'unconfigured' ou 'error'."""
    settings = get_settings()
    if not settings.redis_url:
        return "unconfigured"
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        return "ok"
    except Exception:
        return "error"


def check_push_worker() -> str:
    """Retourne 'ok', 'unconfigured' ou 'error' (scheduler = push worker)."""
    state = get_push_worker_state()
    if not state["configured"]:
        return "unconfigured"
    if not state.get("running", False):
        return "error"
    if state.get("last_error") is not None:
        return "error"
    return "ok"
