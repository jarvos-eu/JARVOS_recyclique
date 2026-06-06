"""Story 9.11 — référentiel dénominations, persistance grille, intégration clôture."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from recyclic_api.core.exceptions import ConflictError, NotFoundError, ValidationError
from recyclic_api.models.cash_denomination import CashDenomination, CashDenominationCount
from recyclic_api.models.cash_session import CashSession, CashSessionStatus
from recyclic_api.models.user import User
from recyclic_api.modules.module_config.registry import MODULE_KEY_COMPTAGE_PIECES_BILLETS
from recyclic_api.modules.module_config.service import (
    COMPTAGE_PIECES_BILLETS_DEFAULT_PAYLOAD,
    ModuleConfigService,
)
from recyclic_api.schemas.cash_denomination import (
    CashDenominationV1,
    DenominationCountBreakdownLineV1,
    DenominationCountResponseV1,
    DenominationCountSnapshotV1,
    DenominationCountUpsertV1,
)
from recyclic_api.services.admin_settings_service import get_close_variance_max_eur
from recyclic_api.services.cash_session_service import CLOSE_VARIANCE_TOLERANCE, CashSessionService

SCHEMA_VERSION_COMPTAGE_V1 = "1.0.0"
AMOUNT_MATCH_TOLERANCE_EUR = 0.005

DEFAULT_PAYLOAD_MODULE_OFF: Dict[str, Any] = dict(COMPTAGE_PIECES_BILLETS_DEFAULT_PAYLOAD)

# Seed de secours si migration non appliquée (tests SQLite).
_FALLBACK_DENOMINATIONS: List[Dict[str, Any]] = [
    {"code": "EUR_50000", "label_fr": "500 €", "kind": "note", "unit_value_cents": 50000, "display_order": 1, "display_default": False},
    {"code": "EUR_20000", "label_fr": "200 €", "kind": "note", "unit_value_cents": 20000, "display_order": 2, "display_default": True},
    {"code": "EUR_10000", "label_fr": "100 €", "kind": "note", "unit_value_cents": 10000, "display_order": 3, "display_default": True},
    {"code": "EUR_5000", "label_fr": "50 €", "kind": "note", "unit_value_cents": 5000, "display_order": 4, "display_default": True},
    {"code": "EUR_2000", "label_fr": "20 €", "kind": "note", "unit_value_cents": 2000, "display_order": 5, "display_default": True},
    {"code": "EUR_1000", "label_fr": "10 €", "kind": "note", "unit_value_cents": 1000, "display_order": 6, "display_default": True},
    {"code": "EUR_500", "label_fr": "5 €", "kind": "note", "unit_value_cents": 500, "display_order": 7, "display_default": True},
    {"code": "EUR_200", "label_fr": "2 €", "kind": "coin", "unit_value_cents": 200, "display_order": 8, "display_default": True},
    {"code": "EUR_100", "label_fr": "1 €", "kind": "coin", "unit_value_cents": 100, "display_order": 9, "display_default": True},
    {"code": "EUR_050", "label_fr": "50 c", "kind": "coin", "unit_value_cents": 50, "display_order": 10, "display_default": True},
    {"code": "EUR_020", "label_fr": "20 c", "kind": "coin", "unit_value_cents": 20, "display_order": 11, "display_default": True},
    {"code": "EUR_010", "label_fr": "10 c", "kind": "coin", "unit_value_cents": 10, "display_order": 12, "display_default": True},
    {"code": "EUR_005", "label_fr": "5 c", "kind": "coin", "unit_value_cents": 5, "display_order": 13, "display_default": True},
    {"code": "EUR_002", "label_fr": "2 c", "kind": "coin", "unit_value_cents": 2, "display_order": 14, "display_default": True},
    {"code": "EUR_001", "label_fr": "1 c", "kind": "coin", "unit_value_cents": 1, "display_order": 15, "display_default": True},
]


def resolve_comptage_module_payload(db: Session, site_id: uuid.UUID) -> Dict[str, Any]:
    """Lit module-config via ModuleConfigService (registre 9.13)."""
    return ModuleConfigService(db).resolve_payload_for_site(site_id, MODULE_KEY_COMPTAGE_PIECES_BILLETS)


def is_comptage_module_enabled(db: Session, site_id: uuid.UUID) -> bool:
    return bool(resolve_comptage_module_payload(db, site_id).get("enabled"))


def is_comptage_module_required(db: Session, site_id: uuid.UUID) -> bool:
    """Module actif pilote : enabled + skip_allowed false + grille requise."""
    payload = resolve_comptage_module_payload(db, site_id)
    return (
        bool(payload.get("enabled"))
        and not bool(payload.get("skip_allowed"))
        and bool(payload.get("require_denomination_grid"))
    )


def seed_denominations_if_empty(db: Session) -> None:
    """Idempotent — utile pour SQLite tests hors migration Alembic."""
    if db.query(CashDenomination).count() > 0:
        return
    for row in _FALLBACK_DENOMINATIONS:
        db.add(
            CashDenomination(
                code=row["code"],
                label_fr=row["label_fr"],
                kind=row["kind"],
                unit_value_cents=row["unit_value_cents"],
                display_order=row["display_order"],
                display_default=1 if row.get("display_default", True) else 0,
            )
        )
    db.commit()


def _denomination_to_schema(row: CashDenomination) -> CashDenominationV1:
    return CashDenominationV1(
        code=row.code,
        label_fr=row.label_fr,
        kind=row.kind,  # type: ignore[arg-type]
        unit_value_cents=row.unit_value_cents,
        display_order=row.display_order,
        display_default=bool(row.display_default),
    )


def _breakdown_revision(breakdown: List[DenominationCountBreakdownLineV1]) -> str:
    payload = [line.model_dump(mode="json") for line in breakdown]
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


class CashDenominationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self._session_service = CashSessionService(db)

    def list_denominations(self) -> List[CashDenominationV1]:
        seed_denominations_if_empty(self.db)
        rows = self.db.query(CashDenomination).order_by(CashDenomination.display_order.asc()).all()
        if len(rows) != 15:
            raise ValidationError("Référentiel dénominations incomplet — attendu 15 lignes.")
        return [_denomination_to_schema(r) for r in rows]

    def _assert_session_readable(self, session: CashSession, user: User) -> None:
        if user.site_id is not None and session.site_id != user.site_id:
            raise NotFoundError("Session de caisse non trouvée")

    def _assert_session_writable(self, session: CashSession, user: User) -> None:
        self._assert_session_readable(session, user)
        if session.status == CashSessionStatus.CLOSED:
            raise ConflictError("La session est déjà fermée — comptage non modifiable.")

    def _theoretical_cash_cents(self, session: CashSession) -> int:
        preview = self._session_service.get_closing_preview(session, 0.0)
        return int(round(preview["theoretical_amount"] * 100))

    def _float_target_cents(self, session: CashSession) -> int:
        return int(round(float(session.initial_amount or 0) * 100))

    def _load_quantities_map(self, session_id: uuid.UUID) -> Dict[str, int]:
        rows = (
            self.db.query(CashDenominationCount)
            .filter(CashDenominationCount.cash_session_id == session_id)
            .all()
        )
        return {r.denomination_code: int(r.quantity) for r in rows}

    def _has_count_recorded(self, session_id: uuid.UUID) -> bool:
        return (
            self.db.query(CashDenominationCount)
            .filter(CashDenominationCount.cash_session_id == session_id)
            .count()
            > 0
        )

    def _build_breakdown(
        self,
        denominations: List[CashDenominationV1],
        quantities: Dict[str, int],
    ) -> Tuple[List[DenominationCountBreakdownLineV1], int]:
        breakdown: List[DenominationCountBreakdownLineV1] = []
        total = 0
        for denom in denominations:
            qty = int(quantities.get(denom.code, 0))
            line_total = qty * denom.unit_value_cents
            total += line_total
            breakdown.append(
                DenominationCountBreakdownLineV1(
                    code=denom.code,
                    quantity=qty,
                    unit_value_cents=denom.unit_value_cents,
                    line_total_cents=line_total,
                )
            )
        return breakdown, total

    def _latest_recorded_at(self, session_id: uuid.UUID) -> Optional[datetime]:
        row = (
            self.db.query(CashDenominationCount.recorded_at)
            .filter(CashDenominationCount.cash_session_id == session_id)
            .order_by(CashDenominationCount.recorded_at.desc())
            .first()
        )
        return row[0] if row else None

    def build_response_for_session(self, session: CashSession) -> DenominationCountResponseV1:
        denominations = self.list_denominations()
        quantities = self._load_quantities_map(session.id)
        breakdown, total_counted = self._build_breakdown(denominations, quantities)
        theoretical = self._theoretical_cash_cents(session)
        float_target = self._float_target_cents(session)
        withdraw = max(0, total_counted - float_target)
        return DenominationCountResponseV1(
            denominations=denominations,
            breakdown=breakdown,
            total_counted_cents=total_counted,
            theoretical_cash_cents=theoretical,
            variance_cents=total_counted - theoretical,
            float_target_cents=float_target,
            withdraw_cents=withdraw,
            recorded_at=self._latest_recorded_at(session.id),
            has_count_recorded=self._has_count_recorded(session.id),
        )

    def get_denomination_count(self, session: CashSession, user: User) -> DenominationCountResponseV1:
        self._assert_session_readable(session, user)
        return self.build_response_for_session(session)

    def upsert_denomination_count(
        self,
        session: CashSession,
        user: User,
        body: DenominationCountUpsertV1,
    ) -> DenominationCountResponseV1:
        self._assert_session_writable(session, user)
        denominations = self.list_denominations()
        valid_codes = {d.code for d in denominations}
        quantities = {d.code: 0 for d in denominations}
        for line in body.lines:
            if line.code not in valid_codes:
                raise ValidationError(f"Code dénomination inconnu : {line.code!r}")
            quantities[line.code] = int(line.quantity)

        now = datetime.now(timezone.utc)
        for denom in denominations:
            qty = quantities[denom.code]
            existing = (
                self.db.query(CashDenominationCount)
                .filter(
                    CashDenominationCount.cash_session_id == session.id,
                    CashDenominationCount.denomination_code == denom.code,
                )
                .one_or_none()
            )
            if existing is None:
                self.db.add(
                    CashDenominationCount(
                        cash_session_id=session.id,
                        site_id=session.site_id,
                        denomination_code=denom.code,
                        quantity=qty,
                        unit_value_cents=denom.unit_value_cents,
                        recorded_at=now,
                        recorded_by_user_id=user.id,
                    )
                )
            else:
                existing.quantity = qty
                existing.unit_value_cents = denom.unit_value_cents
                existing.recorded_at = now
                existing.recorded_by_user_id = user.id
                self.db.add(existing)

        self.db.commit()
        self.db.refresh(session)
        return self.build_response_for_session(session)

    def resolve_close_actual_amount(
        self,
        session: CashSession,
        client_actual_amount: float,
    ) -> Tuple[float, Optional[DenominationCountResponseV1]]:
        """
        Si module requis : valide la grille et retourne le montant serveur (€).
        Lève ValidationError avec message structuré si échec.
        """
        if not is_comptage_module_required(self.db, session.site_id):
            return client_actual_amount, None

        grid = self.build_response_for_session(session)
        if not grid.has_count_recorded:
            raise ConflictError(
                {
                    "code": "COMPTAGE_REQUIRED",
                    "message": (
                        "Comptage par dénomination requis : enregistrez la grille "
                        "(PUT denomination-count) avant la clôture."
                    ),
                }
            )

        if grid.total_counted_cents == 0 and grid.theoretical_cash_cents > 0:
            raise ConflictError(
                {
                    "code": "COMPTAGE_REQUIRED",
                    "message": (
                        "Comptage par dénomination requis : total grille à 0 alors que "
                        "le montant théorique espèces est positif."
                    ),
                }
            )

        server_amount = grid.total_counted_cents / 100.0
        if abs(client_actual_amount - server_amount) > AMOUNT_MATCH_TOLERANCE_EUR:
            raise ConflictError(
                {
                    "code": "COMPTAGE_AMOUNT_MISMATCH",
                    "message": (
                        f"Le montant client ({client_actual_amount:.2f} €) ne correspond pas "
                        f"au total grille ({server_amount:.2f} €)."
                    ),
                }
            )
        return server_amount, grid

    def build_snapshot_block(self, session: CashSession) -> Optional[Dict[str, Any]]:
        if not is_comptage_module_enabled(self.db, session.site_id):
            return None
        if not self._has_count_recorded(session.id):
            return None
        grid = self.build_response_for_session(session)
        recorded_at = grid.recorded_at or datetime.now(timezone.utc)
        snap = DenominationCountSnapshotV1(
            total_counted_cents=grid.total_counted_cents,
            theoretical_cash_cents=grid.theoretical_cash_cents,
            variance_cents=grid.variance_cents,
            breakdown_revision=_breakdown_revision(grid.breakdown),
            recorded_at=recorded_at.isoformat(),
            breakdown=grid.breakdown,
        )
        return snap.model_dump(mode="json")

    def evaluate_anomaly_close_sheet(
        self,
        session: CashSession,
        *,
        variance_cents: int,
        grid: Optional[DenominationCountResponseV1] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Signaux PDF anomalie (génération PDF = story 9.12)."""
        if not is_comptage_module_enabled(self.db, session.site_id):
            return False, None

        grid = grid or self.build_response_for_session(session)
        variance_eur = abs(variance_cents) / 100.0
        block_max = get_close_variance_max_eur(self.db, session.site_id)
        rare_qty = next(
            (line.quantity for line in grid.breakdown if line.code == "EUR_50000"),
            0,
        )
        is_anomaly = (
            variance_cents != 0
            or variance_eur > CLOSE_VARIANCE_TOLERANCE + 1e-9
            or variance_eur > block_max + 1e-9
            or rare_qty > 0
        )
        if not is_anomaly:
            return False, None
        return True, f"/v1/cash-sessions/{session.id}/close-sheet.pdf"
