"""
Contrat ModuleBase pour les modules RecyClique.
Tout module activé par le loader doit implémenter cette interface.
Référence : FR24, FR25 (epics.md) ; architecture EventBus/slots.
"""

from abc import ABC, abstractmethod
from typing import Any

from fastapi import FastAPI


class ModuleBase(ABC):
    """
    Interface minimale pour un module RecyClique.
    Méthodes : name, register (optionnel), startup, shutdown.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Identifiant du module (snake_case, ex. stub, caisse, reception)."""
        ...

    def register(self, app: FastAPI) -> None:
        """
        Enregistre le module dans l'app FastAPI (routes, dépendances, etc.).
        Par défaut : rien. À surcharger si le module expose des routes ou des deps.
        """
        pass

    async def startup(self) -> None:
        """
        Appelé au démarrage de l'application (après register).
        Connexions, chargement de config, etc.
        """
        pass

    async def shutdown(self) -> None:
        """
        Appelé à l'arrêt de l'application.
        Fermeture de connexions, nettoyage.
        """
        pass

    def get_config(self) -> dict[str, Any]:
        """
        Config optionnelle lue depuis le TOML (section [modules.<name>]).
        Retourne un dict vide par défaut.
        """
        return {}
