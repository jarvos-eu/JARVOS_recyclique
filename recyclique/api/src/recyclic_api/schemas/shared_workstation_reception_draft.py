"""Schémas brouillon réception poste partagé (Story 27.8)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SharedWorkstationReceptionDraftSummaryOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    poste_id: str
    ticket_id: str
    started_by_display: str
    started_at: str
    line_count: int = Field(ge=0)


class SharedWorkstationReceptionDraftGetOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: SharedWorkstationReceptionDraftSummaryOut


class SharedWorkstationReceptionDraftConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirm: bool = Field(
        ...,
        description="Confirmation explicite requise (true) pour reprise ou abandon.",
    )


class SharedWorkstationReceptionDraftResumeOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    poste_id: str
    ticket_id: str


class SharedWorkstationReceptionDraftAbandonOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    abandoned: bool = True
