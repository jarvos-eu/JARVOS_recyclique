"""
Loader de modules RecyClique : lecture config TOML et enregistrement des modules ModuleBase.
Référence : FR24, FR25 ; architecture api/config/modules.toml, api/core/modules/.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from api.config import get_settings
from api.core.modules.base import ModuleBase

logger = logging.getLogger(__name__)

# Registre des modules chargés (nom -> instance) pour diagnostic et lifespan
_loaded_modules: dict[str, ModuleBase] = {}


def get_loaded_modules() -> dict[str, ModuleBase]:
    """Retourne le registre des modules actuellement chargés (lecture seule)."""
    return dict(_loaded_modules)


def _parse_toml(path: Path) -> dict[str, Any]:
    """Lit un fichier TOML et retourne le contenu en dict (Python 3.11+ tomllib)."""
    import tomllib
    with open(path, "rb") as f:
        return tomllib.load(f)


def _get_modules_config_path() -> Path | None:
    """Chemin du fichier TOML des modules (env ou défaut). Limité au repo (sécurité)."""
    settings = get_settings()
    root = Path(__file__).resolve().parent.parent.parent.parent
    raw = getattr(settings, "modules_config_path", None)
    if raw:
        p = Path(raw)
        if p.is_absolute():
            p = p.resolve()
        else:
            p = (root / raw).resolve()
        # Restriction : doit être sous la racine du repo et se terminer par .toml
        if not str(p).startswith(str(root)) or p.suffix.lower() != ".toml":
            return None
        return p if p.is_file() else None
    p = root / "api" / "config" / "modules.toml"
    return p if p.is_file() else None


def _resolve_module_instance(module_id: str, config: dict[str, Any]) -> ModuleBase | None:
    """
    Résout un module par son identifiant (registre connu pour cette story).
    Évolutif vers entry points ou discovery par chemin.
    """
    from api.core.modules import stub_module  # noqa: F401

    registry: dict[str, type[ModuleBase]] = {
        "stub": stub_module.StubModule,
    }
    cls = registry.get(module_id)
    if not cls:
        logger.warning("Module inconnu ignoré: %s", module_id)
        return None
    instance = cls()
    if hasattr(instance, "set_config"):
        instance.set_config(config)
    return instance


def load_modules_from_toml(app: FastAPI) -> None:
    """
    Lit la config TOML des modules, instancie chaque module activé,
    appelle register(app) puis enregistre pour startup/shutdown dans le lifespan.
    """
    config_path = _get_modules_config_path()
    if not config_path:
        logger.info("Aucun fichier de config modules (modules.toml) trouvé — pas de modules chargés.")
        return

    try:
        data = _parse_toml(config_path)
    except Exception as e:
        logger.exception("Erreur lecture config modules %s: %s", config_path, e)
        return

    modules_section = data.get("modules", data)
    if isinstance(modules_section, dict):
        enabled = modules_section.get("enabled", [])
    else:
        enabled = []
    if not isinstance(enabled, list):
        enabled = []

    if not enabled:
        logger.info("Config modules sans entrée 'enabled' — pas de modules chargés.")
        return

    for module_id in enabled:
        if not isinstance(module_id, str):
            continue
        module_id = module_id.strip().lower()
        if not module_id:
            continue
        module_config = data.get(module_id, {})
        if not isinstance(module_config, dict):
            module_config = {}

        instance = _resolve_module_instance(module_id, module_config)
        if instance is None:
            continue
        try:
            instance.register(app)
            _loaded_modules[instance.name] = instance
            logger.info("Module enregistré: %s", instance.name)
        except Exception as e:
            logger.exception("Erreur enregistrement module %s: %s", module_id, e)


async def startup_modules() -> None:
    """Appelé au startup de l'app : exécute startup() sur chaque module chargé."""
    for name, mod in list(_loaded_modules.items()):
        try:
            await mod.startup()
            logger.info("Module démarré: %s", name)
        except Exception as e:
            logger.exception("Erreur startup module %s: %s", name, e)


async def shutdown_modules() -> None:
    """Appelé au shutdown de l'app : exécute shutdown() sur chaque module chargé."""
    for name, mod in list(_loaded_modules.items()):
        try:
            await mod.shutdown()
            logger.info("Module arrêté: %s", name)
        except Exception as e:
            logger.exception("Erreur shutdown module %s: %s", name, e)
