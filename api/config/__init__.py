# RecyClique API — Configuration (Pydantic Settings).
# Pas de secrets en dur : variables d'environnement ou .env à la racine du repo.

from .settings import get_settings, Settings

__all__ = ["get_settings", "Settings"]
