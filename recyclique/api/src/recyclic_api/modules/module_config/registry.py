"""Liste blanche serveur des module_key actifs (05-MOD-registre)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

MODULE_KEY_KPI_LIVE_BANNER: Final[str] = "kpi-live-banner"
SCHEMA_VERSION_KPI_LIVE_BANNER_V1: Final[str] = "1.0.0"
MODULE_KEY_RECEPTION: Final[str] = "reception"
MODULE_KEY_COMPTAGE_PIECES_BILLETS: Final[str] = "comptage-pieces-billets"
SCHEMA_VERSION_COMPTAGE_PIECES_BILLETS_V1: Final[str] = "1.0.0"

ACTIVE_MODULE_KEYS: Final[frozenset[str]] = frozenset(
    {MODULE_KEY_KPI_LIVE_BANNER, MODULE_KEY_RECEPTION, MODULE_KEY_COMPTAGE_PIECES_BILLETS}
)


@dataclass(frozen=True)
class ModuleRegistryEntry:
    module_key: str
    schema_version: str
    schema_relative_path: str


_REGISTRY: dict[str, ModuleRegistryEntry] = {
    MODULE_KEY_KPI_LIVE_BANNER: ModuleRegistryEntry(
        module_key=MODULE_KEY_KPI_LIVE_BANNER,
        schema_version=SCHEMA_VERSION_KPI_LIVE_BANNER_V1,
        schema_relative_path="references/config-modules-site-id/schemas/kpi-live-banner.v1.json",
    ),
    MODULE_KEY_COMPTAGE_PIECES_BILLETS: ModuleRegistryEntry(
        module_key=MODULE_KEY_COMPTAGE_PIECES_BILLETS,
        schema_version=SCHEMA_VERSION_COMPTAGE_PIECES_BILLETS_V1,
        schema_relative_path="references/config-modules-site-id/schemas/comptage-pieces-billets.v1.json",
    ),
}


def is_active_module_key(module_key: str) -> bool:
    return module_key in ACTIVE_MODULE_KEYS


def get_registry_entry(module_key: str) -> ModuleRegistryEntry | None:
    return _REGISTRY.get(module_key)
