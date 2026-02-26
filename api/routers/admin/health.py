"""Health check — GET /health (status, database, redis). Réponse snake_case."""

from fastapi import APIRouter

from api.config import get_settings

router = APIRouter(tags=["health"])


def _check_database() -> str:
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


def _check_redis() -> str:
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


@router.get("/health")
def health() -> dict:
    """Health check : status, database, redis (snake_case)."""
    db = _check_database()
    redis_status = _check_redis()
    status = "ok" if (db == "ok" and redis_status == "ok") else "degraded"
    return {
        "status": status,
        "database": db,
        "redis": redis_status,
    }
