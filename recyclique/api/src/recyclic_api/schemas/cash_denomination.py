"""Story 9.11 — schémas OpenAPI / Pydantic comptage pièces-billets."""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class CashDenominationV1(BaseModel):
    code: str
    label_fr: str
    kind: Literal["coin", "note"]
    unit_value_cents: int = Field(..., ge=1)
    display_order: int
    display_default: bool


class DenominationCountLineInputV1(BaseModel):
    code: str
    quantity: int = Field(..., ge=0)


class DenominationCountUpsertV1(BaseModel):
    lines: List[DenominationCountLineInputV1] = Field(
        ...,
        description="Quantités par code dénomination ; codes absents traités comme 0.",
    )


class DenominationCountBreakdownLineV1(BaseModel):
    code: str
    quantity: int
    unit_value_cents: int
    line_total_cents: int


class DenominationCountResponseV1(BaseModel):
    denominations: List[CashDenominationV1] = Field(
        ...,
        description="Référentiel embarqué (15 lignes EUR).",
    )
    breakdown: List[DenominationCountBreakdownLineV1]
    total_counted_cents: int
    theoretical_cash_cents: int
    variance_cents: int
    float_target_cents: int = Field(
        ...,
        description="Fond cible à laisser dans le tiroir (centimes).",
    )
    withdraw_cents: int = Field(
        ...,
        description="Montant à retirer du tiroir après clôture (centimes).",
    )
    recorded_at: Optional[datetime] = None
    has_count_recorded: bool = Field(
        ...,
        description="True si au moins un PUT denomination-count a été enregistré pour la session.",
    )


class DenominationCountSnapshotV1(BaseModel):
    """Bloc snapshot figé à la clôture (extension schema_version 3)."""

    total_counted_cents: int
    theoretical_cash_cents: int
    variance_cents: int
    breakdown_revision: str
    recorded_at: str
    breakdown: List[DenominationCountBreakdownLineV1]
