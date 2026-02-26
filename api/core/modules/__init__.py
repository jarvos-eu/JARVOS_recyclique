# api/core/modules — Loader de modules RecyClique (TOML, ModuleBase).
# Voir architecture : FR24, FR25. EventBus et slots côté front dans workers/ et frontend slots.

from .base import ModuleBase
from .loader import load_modules_from_toml, get_loaded_modules

__all__ = [
    "ModuleBase",
    "load_modules_from_toml",
    "get_loaded_modules",
]
