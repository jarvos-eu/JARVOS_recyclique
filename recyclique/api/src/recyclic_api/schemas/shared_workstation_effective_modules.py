"""Schémas intersection modules poste partagé (Story 27.7)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SharedWorkstationEffectiveModulesOut(BaseModel):
    """Modules effectifs calculés serveur — projection autoritaire."""

    model_config = ConfigDict(extra="forbid")

    module_keys: list[str] = Field(default_factory=list)
    computed_at: datetime
    site_id: str
    device_id: str
    operator_user_id: str


class SharedWorkstationProbeModuleOut(BaseModel):
    """Réponse probe — preuve garde sans données métier sensibles."""

    model_config = ConfigDict(extra="forbid")

    module_key: str
    effective: bool = True
