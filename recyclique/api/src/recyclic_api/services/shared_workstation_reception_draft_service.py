"""Brouillon réception poste partagé — autorité serveur (Story 27.8)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from recyclic_api.core.audit import (
    log_shared_workstation_reception_draft_abandoned,
    log_shared_workstation_reception_draft_access_refused,
    log_shared_workstation_reception_draft_resumed,
)
from recyclic_api.core.auth import user_has_permission
from recyclic_api.models import PosteReception, TicketDepot, TicketDepotStatus
from recyclic_api.models.user import User, UserRole
from recyclic_api.modules.module_config.registry import MODULE_KEY_RECEPTION
from recyclic_api.repositories.reception import PosteReceptionRepository, TicketDepotRepository
from recyclic_api.schemas.shared_workstation_reception_draft import (
    SharedWorkstationReceptionDraftSummaryOut,
)
from recyclic_api.services.reception_service import (
    RECEPTION_ACCESS_PERMISSION_KEY,
    ReceptionService,
    SharedWorkstationReceptionScope,
)
from recyclic_api.services.shared_workstation_effective_modules_service import (
    SharedWorkstationEffectiveModulesService,
)

SHARED_WORKSTATION_RECEPTION_DRAFT_FORBIDDEN = "SHARED_WORKSTATION_RECEPTION_DRAFT_FORBIDDEN"
SHARED_WORKSTATION_RECEPTION_DRAFT_ALREADY_ACTIVE = (
    "SHARED_WORKSTATION_RECEPTION_DRAFT_ALREADY_ACTIVE"
)
SHARED_WORKSTATION_RECEPTION_DRAFT_NOT_FOUND = "SHARED_WORKSTATION_RECEPTION_DRAFT_NOT_FOUND"


@dataclass(frozen=True)
class SharedWorkstationReceptionDraft:
    poste: PosteReception
    ticket: TicketDepot


def _operator_display(user: User) -> str:
    label = (user.username or "").strip()
    if not label:
        return "Opérateur"
    return label.split(".")[0].split("@")[0][:32]


class SharedWorkstationReceptionDraftService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._poste_repo = PosteReceptionRepository(db)
        self._ticket_repo = TicketDepotRepository(db)
        self._reception = ReceptionService(db)
        self._effective = SharedWorkstationEffectiveModulesService(db)

    def _assert_reception_access(
        self,
        *,
        device_id: str,
        operator_user_id: str,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> User:
        self._effective.assert_module_in_effective_set(
            device_id=device_id,
            operator_user_id=operator_user_id,
            module_key=MODULE_KEY_RECEPTION,
            request_id=request_id,
            actor_user_id=actor_user_id,
        )
        try:
            operator_uuid = uuid.UUID(str(operator_user_id))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": SHARED_WORKSTATION_RECEPTION_DRAFT_FORBIDDEN,
                    "message": "Opérateur invalide",
                },
            ) from exc
        operator = self._db.get(User, operator_uuid)
        if operator is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": SHARED_WORKSTATION_RECEPTION_DRAFT_FORBIDDEN,
                    "message": "Opérateur introuvable",
                },
            )
        if operator.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN) and not user_has_permission(
            operator, RECEPTION_ACCESS_PERMISSION_KEY, self._db
        ):
            log_shared_workstation_reception_draft_access_refused(
                db=self._db,
                device_id=device_id,
                operator_user_id=operator_user_id,
                actor_user_id=actor_user_id,
                request_id=request_id,
                outcome="reception_access_denied",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": SHARED_WORKSTATION_RECEPTION_DRAFT_FORBIDDEN,
                    "message": "Accès réception refusé pour cet opérateur",
                },
            )
        return operator

    def _find_active_draft(self, *, device_id: str) -> Optional[SharedWorkstationReceptionDraft]:
        try:
            device_uuid = uuid.UUID(str(device_id))
        except ValueError:
            return None
        poste = self._poste_repo.find_open_by_registered_device_id(device_uuid)
        if poste is None:
            return None
        ticket = (
            self._db.query(TicketDepot)
            .options(selectinload(TicketDepot.lignes))
            .filter(
                TicketDepot.poste_id == poste.id,
                TicketDepot.status == TicketDepotStatus.OPENED.value,
            )
            .order_by(TicketDepot.created_at.desc())
            .first()
        )
        if ticket is None:
            return None
        return SharedWorkstationReceptionDraft(poste=poste, ticket=ticket)

    def build_authorized_summary(
        self,
        draft: SharedWorkstationReceptionDraft,
        *,
        viewer: User,
    ) -> SharedWorkstationReceptionDraftSummaryOut:
        opener = self._db.get(User, draft.poste.opened_by_user_id)
        started_by_display = _operator_display(opener) if opener else "Opérateur"
        line_count = len(draft.ticket.lignes or [])
        started_at = draft.poste.opened_at
        return SharedWorkstationReceptionDraftSummaryOut(
            poste_id=str(draft.poste.id),
            ticket_id=str(draft.ticket.id),
            started_by_display=started_by_display,
            started_at=started_at.isoformat() if started_at else "",
            line_count=line_count,
        )

    def get_draft_for_device(
        self,
        *,
        device_id: str,
        operator_user_id: str,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Optional[SharedWorkstationReceptionDraftSummaryOut]:
        operator = self._assert_reception_access(
            device_id=device_id,
            operator_user_id=operator_user_id,
            actor_user_id=actor_user_id,
            request_id=request_id,
        )
        draft = self._find_active_draft(device_id=device_id)
        if draft is None:
            return None
        return self.build_authorized_summary(draft, viewer=operator)

    def resume_draft(
        self,
        *,
        device_id: str,
        operator_user_id: str,
        confirm: bool,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> tuple[str, str]:
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "confirm=true requis pour reprendre le brouillon",
                },
            )
        operator = self._assert_reception_access(
            device_id=device_id,
            operator_user_id=operator_user_id,
            actor_user_id=actor_user_id,
            request_id=request_id,
        )
        draft = self._find_active_draft(device_id=device_id)
        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": SHARED_WORKSTATION_RECEPTION_DRAFT_NOT_FOUND,
                    "message": "Aucun brouillon réception actif sur ce poste",
                },
            )
        previous_operator_id = str(draft.poste.opened_by_user_id)
        log_shared_workstation_reception_draft_resumed(
            db=self._db,
            device_id=device_id,
            poste_id=str(draft.poste.id),
            ticket_id=str(draft.ticket.id),
            operator_user_id=operator_user_id,
            previous_operator_user_id=previous_operator_id,
            actor_user_id=actor_user_id,
            request_id=request_id,
        )
        self._db.commit()
        return str(draft.poste.id), str(draft.ticket.id)

    def abandon_draft(
        self,
        *,
        device_id: str,
        operator_user_id: str,
        confirm: bool,
        actor_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "confirm=true requis pour abandonner le brouillon",
                },
            )
        self._assert_reception_access(
            device_id=device_id,
            operator_user_id=operator_user_id,
            actor_user_id=actor_user_id,
            request_id=request_id,
        )
        draft = self._find_active_draft(device_id=device_id)
        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": SHARED_WORKSTATION_RECEPTION_DRAFT_NOT_FOUND,
                    "message": "Aucun brouillon réception actif sur ce poste",
                },
            )
        scope = SharedWorkstationReceptionScope(device_id=device_id)
        operator = self._db.get(User, uuid.UUID(str(operator_user_id)))
        if operator is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": SHARED_WORKSTATION_RECEPTION_DRAFT_FORBIDDEN,
                    "message": "Opérateur introuvable",
                },
            )
        self._reception.close_ticket(
            ticket_id=draft.ticket.id,
            actor_user=operator,
            shared_workstation_scope=scope,
        )
        self._reception.close_poste(
            poste_id=draft.poste.id,
            actor_user=operator,
            shared_workstation_scope=scope,
        )
        log_shared_workstation_reception_draft_abandoned(
            db=self._db,
            device_id=device_id,
            poste_id=str(draft.poste.id),
            ticket_id=str(draft.ticket.id),
            operator_user_id=operator_user_id,
            actor_user_id=actor_user_id,
            request_id=request_id,
        )
        self._db.commit()

    def assert_no_active_draft_for_device(self, *, device_id: str) -> None:
        if self._find_active_draft(device_id=device_id) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": SHARED_WORKSTATION_RECEPTION_DRAFT_ALREADY_ACTIVE,
                    "message": "Un brouillon réception est déjà actif sur ce poste",
                },
            )


