"""Schémas ContextEnvelope minimal (Story 2.2) — alignés sur contracts/openapi/recyclique-api.yaml."""

from datetime import datetime
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class ContextRuntimeState(str, Enum):
    """États runtime UI — noms figés contrat OpenAPI (spec 1.3 §4.2)."""

    ok = "ok"
    degraded = "degraded"
    forbidden = "forbidden"


class ExploitationContextIdsOut(BaseModel):
    """Identifiants de contexte visibles ; champs optionnels (brownfield)."""

    model_config = ConfigDict(extra="forbid")

    site_id: str | None = None
    cash_register_id: str | None = None
    cash_session_id: str | None = None
    reception_post_id: str | None = None
    # Epic 27.2 — poste partagé (null par défaut pour utilisateur web classique)
    device_id: str | None = Field(
        default=None,
        description="UUID canonique RegisteredDevice — distinct cash_register_id / reception_post_id.",
    )
    operator_user_id: str | None = Field(
        default=None,
        description="Opérateur PIN actif sur le poste (session serveur).",
    )
    module_key: str | None = Field(
        default=None,
        description="Module courant session opérateur ; intersection effective en story 27.7.",
    )
    override_active: bool | None = Field(
        default=None,
        description="Override SuperAdmin actif côté serveur (activation complète story 27.10).",
    )


class ContextEnvelopeResponse(BaseModel):
    """
    Enveloppe autoritaire serveur.
    `permission_keys` : sous-ensemble effectif minimal (Story 2.2) ; union rôles + groupes exhaustive en Story 2.3.
    """

    model_config = ConfigDict(extra="forbid")

    runtime_state: ContextRuntimeState
    context: ExploitationContextIdsOut | None = None
    permission_keys: List[str] = Field(default_factory=list)
    computed_at: datetime
    restriction_message: str | None = Field(
        default=None,
        description="Précision serveur pour degraded / forbidden (pas de logique métier côté client).",
    )
    presentation_labels: Dict[str, str] | None = Field(
        default=None,
        description="Map label_key CREOS → libellé affichable (Story 5.5) ; présentation uniquement.",
    )
    effective_module_keys: List[str] | None = Field(
        default=None,
        description=(
            "Story 27.7 — intersection serveur site × allowlist poste × permissions opérateur. "
            "Présent uniquement quand device_id + operator_user_id actifs ; sinon absent ou []."
        ),
    )
