"""Schémas contexte poste partagé (Epic 27.2) — invariant serveur tuple."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from recyclic_api.schemas.context_envelope import ContextRuntimeState


class SharedWorkstationContextOut(BaseModel):
    """
    Tuple autoritaire poste partagé : site_id + device_id + operator_user_id + module_key + override.

    ``operator_user_id`` null ⇒ refus par défaut sur routes métier poste partagé.
    """

    model_config = ConfigDict(extra="forbid")

    site_id: str | None = None
    device_id: str | None = None
    operator_user_id: str | None = None
    module_key: str | None = None
    override_active: bool | None = None
    runtime_state: ContextRuntimeState = ContextRuntimeState.forbidden
    restriction_message: str | None = Field(
        default=None,
        description="Message serveur if forbidden / degraded.",
    )
    effective_module_keys: list[str] | None = Field(
        default=None,
        description=(
            "Story 27.7 — modules effectifs (intersection serveur) ; présent si session opérateur active."
        ),
    )
    reception_draft_summary: dict | None = Field(
        default=None,
        description="Story 27.8 — résumé brouillon réception si module effectif et brouillon actif.",
    )
