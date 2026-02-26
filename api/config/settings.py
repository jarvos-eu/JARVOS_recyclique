# RecyClique API — Configuration (Pydantic Settings).
# Pas de secrets en dur : variables d'environnement ou .env à la racine du repo.

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str | None = None
    redis_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
