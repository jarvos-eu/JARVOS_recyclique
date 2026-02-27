"""Health check — GET /health (status, database, redis, push_worker). Réponse snake_case."""

from fastapi import APIRouter

from api.services.health_checks import check_database, check_redis, check_push_worker

router = APIRouter(tags=["health"])


def _check_database() -> str:
    return check_database()


def _check_redis() -> str:
    return check_redis()


def _check_push_worker() -> str:
    return check_push_worker()


@router.get("/health")
def health() -> dict:
    """Health check : status, database, redis, push_worker (snake_case)."""
    db = _check_database()
    redis_status = _check_redis()
    push_worker_status = _check_push_worker()
    status = "ok" if (db == "ok" and redis_status == "ok") else "degraded"
    return {
        "status": status,
        "database": db,
        "redis": redis_status,
        "push_worker": push_worker_status,
    }
