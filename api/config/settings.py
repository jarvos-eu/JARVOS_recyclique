# RecyClique API — Configuration (Pydantic Settings).
# Pas de secrets en dur : variables d'environnement ou .env à la racine du repo.
# NFR-S2 : config JWT (secret, durées) via env.
# Story 4.1 : canal push Paheko (endpoint, secret, résilience) — NFR-S1, NFR-S2, FR19.

from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str | None = None
    redis_url: str | None = None

    # JWT (NFR-S2 — secrets en env)
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Canal push Paheko (Story 4.1 — NFR-S1, NFR-S2)
    # URL du plugin Paheko (ex. https://paheko.example/plugin/recyclic/push)
    paheko_plugin_url: str | None = None
    # Secret partagé pour signer/authentifier les requêtes ; ne pas mettre de valeur par défaut en prod.
    paheko_plugin_secret: SecretStr | None = None
    # Résilience (FR19) : nombre max de tentatives d'envoi d'un message vers Paheko.
    paheko_push_max_retries: int = 5
    # Délai initial (secondes) avant la première retentative.
    paheko_push_backoff_seconds: float = 1.0
    # Facteur d'exponentiel entre chaque retentative (délai = backoff_seconds * factor^tentative).
    paheko_push_backoff_factor: float = 2.0

    # Story 4.2 : nom du stream Redis pour la file push caisse (événements pos.ticket.created, etc.).
    redis_stream_push_caisse: str = "recyclic:push:caisse"


@lru_cache
def get_settings() -> Settings:
    return Settings()
