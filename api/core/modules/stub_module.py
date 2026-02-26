"""
Module stub RecyClique pour démonstration du loader (ModuleBase).
Utilisé par la config TOML (modules.example.toml). Pas de logique métier.
"""

from api.core.modules.base import ModuleBase


class StubModule(ModuleBase):
    """Module exemple : enregistré au démarrage pour valider le loader."""

    def __init__(self) -> None:
        self._config: dict = {}

    @property
    def name(self) -> str:
        return "stub"

    def set_config(self, config: dict) -> None:
        """Injection de la config TOML (section [stub])."""
        self._config = dict(config) if config else {}

    def get_config(self) -> dict:
        return dict(self._config)

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass
