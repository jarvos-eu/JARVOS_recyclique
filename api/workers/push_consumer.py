"""
Consumer Redis Streams — file push caisse → plugin Paheko (Story 4.2, AC1, AC2).

Consomme le stream configuré (redis_stream_push_caisse), envoie les événements
(pos.ticket.created ou équivalent) au plugin Paheko en HTTPS avec secret partagé.
ACK uniquement après succès HTTP 2xx ; en échec : retry avec backoff, pas d'ACK
(message reste en file). Logs structurés JSON, correlation_id = message id.
"""

import json
import logging
import threading
import time
from typing import Any

import httpx
import redis

from api.config import get_settings

logger = logging.getLogger(__name__)

CONSUMER_GROUP = "recyclic-push"
CONSUMER_NAME = "worker-1"
BLOCK_NEW_MS = 5000
BLOCK_PENDING_MS = 1000

# État partagé pour le health check (thread-safe).
_push_worker_state: dict[str, Any] = {
    "configured": False,
    "running": False,
    "last_error": None,
    "last_success_at": None,
}
_push_worker_lock = threading.Lock()
_shutdown_event: threading.Event | None = None


def set_shutdown_event(event: threading.Event) -> None:
    """Définit l'event d'arrêt (appelé au startup du lifespan)."""
    global _shutdown_event
    _shutdown_event = event


def get_push_worker_state() -> dict[str, Any]:
    """Retourne une copie de l'état du worker (pour GET /health)."""
    with _push_worker_lock:
        return {
            "configured": _push_worker_state["configured"],
            "running": _push_worker_state["running"],
            "last_error": _push_worker_state["last_error"],
            "last_success_at": _push_worker_state["last_success_at"],
        }


def _set_state(**kwargs: Any) -> None:
    with _push_worker_lock:
        for k, v in kwargs.items():
            if k in _push_worker_state:
                _push_worker_state[k] = v


def _log_structured(
    level: int,
    message: str,
    correlation_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Log structuré JSON ; pas de données sensibles."""
    log_obj: dict[str, Any] = {
        "message": message,
        "logger": logger.name,
    }
    if correlation_id:
        log_obj["correlation_id"] = correlation_id
    if extra:
        for k, v in extra.items():
            if k not in ("secret", "password", "token"):
                log_obj[k] = v
    logger.log(level, json.dumps(log_obj))


def _send_to_paheko(url: str, secret: str, payload: dict[str, Any]) -> tuple[bool, str | None]:
    """
    Envoie le payload au plugin Paheko en POST HTTPS.
    Retourne (success, error_message).
    Les 4xx ne sont pas retentés (client error) ; 5xx et erreurs réseau oui (FR20).
    """
    headers = {
        "Content-Type": "application/json",
        "X-Paheko-Secret": secret,
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload, headers=headers)
        if 200 <= resp.status_code < 300:
            return True, None
        # 4xx = client error, pas de retry (story : échec temporaire 5xx / réseau)
        if 400 <= resp.status_code < 500:
            return False, f"HTTP {resp.status_code}"
        return False, f"HTTP {resp.status_code}"
    except httpx.HTTPError as e:
        return False, str(type(e).__name__)
    except Exception as e:
        return False, str(e)


def _process_message(
    redis_client: redis.Redis,
    stream_key: str,
    message_id: bytes | str,
    data: dict[bytes | str, bytes | str],
    url: str,
    secret: str,
    max_retries: int,
    backoff_seconds: float,
    backoff_factor: float,
) -> bool:
    """
    Traite un message : envoi à Paheko avec retries ; ACK si succès.
    Retourne True si ACK effectué, False sinon (message reste en PEL).
    """
    mid = message_id.decode() if isinstance(message_id, bytes) else message_id
    correlation_id = mid

    # Décoder le payload (Redis renvoie bytes ou str).
    def _decode(v: bytes | str) -> str:
        return v.decode("utf-8") if isinstance(v, bytes) else v

    payload_dict: dict[str, Any] = {}
    for k, v in data.items():
        key = _decode(k)
        if key in ("payload", "data"):
            try:
                payload_dict = json.loads(_decode(v))
            except json.JSONDecodeError:
                payload_dict = {"raw": _decode(v)}
            break
    if not payload_dict and data:
        payload_dict = {_decode(k): _decode(v) for k, v in data.items()}

    last_err: str | None = None
    for attempt in range(1, max_retries + 1):
        ok, err = _send_to_paheko(url, secret, payload_dict)
        if ok:
            _log_structured(
                logging.INFO,
                "Paheko push success",
                correlation_id=correlation_id,
                extra={"attempt": attempt},
            )
            try:
                redis_client.xack(stream_key, CONSUMER_GROUP, mid)
            except Exception as e:
                _log_structured(
                    logging.ERROR,
                    "XACK failed after Paheko success",
                    correlation_id=correlation_id,
                    extra={"error": str(e)},
                )
                return False
            _set_state(last_error=None, last_success_at=time.time())
            return True
        last_err = err
        _log_structured(
            logging.ERROR,
            "Paheko push failed",
            correlation_id=correlation_id,
            extra={"attempt": attempt, "max_retries": max_retries, "error": err},
        )
        # 4xx = client error, pas de retry (FR20 : échec temporaire 5xx / réseau)
        if err and err.startswith("HTTP 4"):
            break
        if attempt < max_retries:
            delay = backoff_seconds * (backoff_factor ** (attempt - 1))
            time.sleep(delay)

    _set_state(last_error=last_err)
    return False


def _ensure_consumer_group(r: redis.Redis, stream_key: str) -> None:
    """Crée le consumer group si nécessaire (MKSTREAM pour créer le stream)."""
    try:
        r.xgroup_create(stream_key, CONSUMER_GROUP, id="0", mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" in str(e):
            return
        raise


def run_push_consumer() -> None:
    """
    Boucle principale du consumer : XREADGROUP (nouveaux puis pending),
    envoi Paheko, ACK si succès. S'exécute dans le thread appelant (à lancer
    en tâche de fond depuis le lifespan FastAPI).
    """
    settings = get_settings()
    if not settings.redis_url:
        _log_structured(logging.INFO, "Push worker unconfigured: redis_url missing")
        return
    if not settings.paheko_plugin_url or not settings.paheko_plugin_secret:
        _log_structured(logging.INFO, "Push worker unconfigured: paheko_plugin_url or secret missing")
        return

    _set_state(configured=True, running=True)
    stream_key = settings.redis_stream_push_caisse
    url = settings.paheko_plugin_url
    secret = settings.paheko_plugin_secret.get_secret_value()
    max_retries = settings.paheko_push_max_retries
    backoff_seconds = settings.paheko_push_backoff_seconds
    backoff_factor = settings.paheko_push_backoff_factor

    try:
        r = redis.from_url(settings.redis_url, decode_responses=False)
    except Exception as e:
        _log_structured(logging.ERROR, "Push worker Redis connection failed", extra={"error": str(e)})
        _set_state(running=False, last_error=str(e))
        return

    try:
        _ensure_consumer_group(r, stream_key)
    except Exception as e:
        _log_structured(logging.ERROR, "Push worker XGROUP CREATE failed", extra={"error": str(e)})
        _set_state(running=False, last_error=str(e))
        return

    _log_structured(logging.INFO, "Push worker started", extra={"stream": stream_key})

    while True:
        if _shutdown_event and _shutdown_event.is_set():
            break
        try:
            # Nouveaux messages
            streams = r.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                {stream_key: ">"},
                block=BLOCK_NEW_MS,
                count=10,
            )
            if streams:
                for stream_name, messages in streams:
                    for msg_id, data in messages:
                        _process_message(
                            r,
                            stream_key,
                            msg_id,
                            data,
                            url,
                            secret,
                            max_retries,
                            backoff_seconds,
                            backoff_factor,
                        )
                continue
            # Pending messages (retry)
            streams = r.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                {stream_key: "0"},
                block=BLOCK_PENDING_MS,
                count=10,
            )
            if streams:
                for stream_name, messages in streams:
                    for msg_id, data in messages:
                        _process_message(
                            r,
                            stream_key,
                            msg_id,
                            data,
                            url,
                            secret,
                            max_retries,
                            backoff_seconds,
                            backoff_factor,
                        )
        except redis.ConnectionError as e:
            _log_structured(logging.ERROR, "Push worker Redis connection error", extra={"error": str(e)})
            _set_state(last_error=str(e))
            time.sleep(5)
        except Exception as e:
            _log_structured(logging.ERROR, "Push worker error", extra={"error": str(e)})
            _set_state(last_error=str(e))
            time.sleep(5)

    _set_state(running=False)
    _log_structured(logging.INFO, "Push worker stopped")
