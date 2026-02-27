# Module déclarations éco-organismes (Story 9.2 post-MVP).
# Expose les routes d'export (GET /v1/declarative/export) lorsque le module est activé dans modules.toml.
# L'inclusion du router est faite dans main.py (ordre des routes avant catch-all).

from api.core.modules.base import ModuleBase


class DeclaModule(ModuleBase):
    """Module post-MVP : export des agrégats déclaratifs (formats CSV/JSON, multi-éco-organismes)."""

    def __init__(self) -> None:
        self._config: dict = {}

    @property
    def name(self) -> str:
        return "decla"

    def set_config(self, config: dict) -> None:
        """Injection de la config TOML (section [decla])."""
        self._config = dict(config) if config else {}

    def get_config(self) -> dict:
        return dict(self._config)

    def register(self, app) -> None:
        """N'enregistre pas les routes ici : main.py les inclut conditionnellement pour maîtriser l'ordre (avant catch-all)."""
        pass

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass
