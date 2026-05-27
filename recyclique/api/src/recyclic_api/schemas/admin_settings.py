from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict, AliasChoices
from typing import Optional


def to_camel(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


class AlertThresholds(BaseModel):
    """Dashboard alert thresholds persisted server-side."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, revalidate_instances='never')

    cash_discrepancy: float = Field(
        ...,
        ge=0,
        description="Cash discrepancy avant alerte",
        validation_alias=AliasChoices("cash_discrepancy", "cashDiscrepancy"),
        serialization_alias="cashDiscrepancy",
    )
    low_inventory: int = Field(
        ...,
        ge=0,
        description="Nombre d'articles minimum avant alerte d'inventaire",
        validation_alias=AliasChoices("low_inventory", "lowInventory"),
        serialization_alias="lowInventory",
    )


class AlertThresholdsResponse(BaseModel):
    """Response payload for threshold retrieval."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, revalidate_instances='never')

    thresholds: AlertThresholds
    site_id: Optional[str] = Field(None, description="Site concerne par cette configuration", serialization_alias="siteId")


DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR = 2.0


class CashCloseVarianceMax(BaseModel):
    """Seuil D33 — blocage clôture si |écart espèces| dépasse max_eur (Story 9.10)."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, revalidate_instances="never")

    max_eur: float = Field(
        default=DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR,
        gt=0,
        le=500,
        description="Seuil maximal d'écart espèces autorisé à la clôture (€)",
        validation_alias=AliasChoices("max_eur", "maxEur"),
        serialization_alias="maxEur",
    )


class CashCloseVarianceMaxResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, revalidate_instances="never")

    setting: CashCloseVarianceMax
    site_id: Optional[str] = Field(None, serialization_alias="siteId")


class CashCloseVarianceMaxUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, revalidate_instances="never")

    setting: CashCloseVarianceMax
    site_id: Optional[str] = Field(None, validation_alias=AliasChoices("site_id", "siteId"), serialization_alias="siteId")


class AlertThresholdsUpdate(BaseModel):
    """Request payload for updating alert thresholds."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, revalidate_instances='never')

    thresholds: AlertThresholds
    site_id: Optional[str] = Field(None, description="Site cible pour la configuration", validation_alias=AliasChoices("site_id", "siteId"), serialization_alias="siteId")
