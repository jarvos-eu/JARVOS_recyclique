"""Registre d'accès module_key → permissions + résolution site (Story 27.7)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Callable, Final

from sqlalchemy.orm import Session

from recyclic_api.models.site import Site
from recyclic_api.modules.module_config.registry import (
    ACTIVE_MODULE_KEYS,
    MODULE_KEY_KPI_LIVE_BANNER,
    MODULE_KEY_RECEPTION,
    is_active_module_key,
)
from recyclic_api.services.reception_service import RECEPTION_ACCESS_PERMISSION_KEY
from recyclic_api.modules.module_config.service import ModuleConfigService

PERMISSION_VIEW_LIVE_BAND: Final[str] = "recyclique.exploitation.view-live-band"


@dataclass(frozen=True)
class ModuleAccessEntry:
    module_key: str
    required_permission_keys: tuple[str, ...]
    site_enabled_resolver: Callable[[Session, Site | None], bool]


def _resolve_kpi_live_banner_site_enabled(db: Session, site: Site | None) -> bool:
    return ModuleConfigService(db).resolve_bandeau_live_slice_enabled(site)


def _resolve_reception_site_enabled(_db: Session, site: Site | None) -> bool:
    """MVP pilote Story 27.8 — actif si site existe ; config document dédiée différée."""
    return site is not None and bool(site.is_active)


_MODULE_ACCESS_REGISTRY: dict[str, ModuleAccessEntry] = {
    MODULE_KEY_KPI_LIVE_BANNER: ModuleAccessEntry(
        module_key=MODULE_KEY_KPI_LIVE_BANNER,
        required_permission_keys=(PERMISSION_VIEW_LIVE_BAND,),
        site_enabled_resolver=_resolve_kpi_live_banner_site_enabled,
    ),
    MODULE_KEY_RECEPTION: ModuleAccessEntry(
        module_key=MODULE_KEY_RECEPTION,
        required_permission_keys=(RECEPTION_ACCESS_PERMISSION_KEY,),
        site_enabled_resolver=_resolve_reception_site_enabled,
    ),
}


def get_module_access_entry(module_key: str) -> ModuleAccessEntry | None:
    if not is_active_module_key(module_key):
        return None
    return _MODULE_ACCESS_REGISTRY.get(module_key)


def is_site_module_enabled(
    db: Session,
    *,
    site_id: uuid.UUID,
    module_key: str,
) -> bool:
    """Délègue au resolver du access_registry ; False si module_key inconnu."""
    entry = get_module_access_entry(module_key)
    if entry is None:
        return False
    site = db.get(Site, site_id)
    return entry.site_enabled_resolver(db, site)


def iter_intersectable_module_keys() -> tuple[str, ...]:
    """Clés registre actives avec entrée access — ordre stable."""
    return tuple(
        key
        for key in sorted(ACTIVE_MODULE_KEYS)
        if key in _MODULE_ACCESS_REGISTRY
    )
