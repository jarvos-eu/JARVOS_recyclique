"""Story 9.11 — backend comptage pièces/billets (référentiel, persistance, clôture)."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.core.auth import create_access_token
from recyclic_api.core.config import settings
from recyclic_api.core.exceptions import CashCloseVarianceExceededError, ConflictError
from recyclic_api.core.security import hash_password
from recyclic_api.models.cash_session import CashSession, CashSessionStatus
from recyclic_api.models.site import Site
from recyclic_api.models.site_module_config import SiteModuleConfig
from recyclic_api.models.user import User, UserRole, UserStatus
from recyclic_api.services.admin_settings_service import AdminSettingsService
from recyclic_api.services.cash_denomination_service import (
    MODULE_KEY_COMPTAGE_PIECES_BILLETS,
    CashDenominationService,
    is_comptage_module_required,
    seed_denominations_if_empty,
)
from recyclic_api.services.cash_session_service import CashSessionService
from recyclic_api.services.paheko_close_batch_builder import (
    SUB_KIND_CASH_VARIANCE_V1,
    build_planned_sub_writes,
)

_V1 = settings.API_V1_STR.rstrip("/")
_TEST_STEP_UP_PIN = "1234"


def _auth_headers(user_id) -> dict:
    return {"Authorization": f"Bearer {create_access_token(data={'sub': str(user_id)})}"}


def _close_headers(user_id) -> dict:
    return {**_auth_headers(user_id), "X-Step-Up-Pin": _TEST_STEP_UP_PIN}


def _grid_lines_for_total_cents(total_cents: int) -> list[dict]:
    """Construit une grille minimale atteignant total_cents (greedy décroissant)."""
    if total_cents <= 0:
        return [{"code": "EUR_2000", "quantity": 0}]
    lines: list[dict] = []
    remaining = total_cents
    for code, unit in (("EUR_2000", 2000), ("EUR_500", 500), ("EUR_100", 100)):
        qty = remaining // unit
        if qty:
            lines.append({"code": code, "quantity": qty})
            remaining -= qty * unit
    if remaining:
        raise ValueError(f"total_cents {total_cents} non décomposable avec le helper")
    return lines


def _patch_close_dependencies(monkeypatch) -> None:
    from pathlib import Path

    monkeypatch.setattr(
        "recyclic_api.services.paheko_outbox_service.enqueue_cash_session_close_outbox",
        lambda *_a, **_k: None,
    )
    monkeypatch.setattr(
        "recyclic_api.services.paheko_sync_final_action_policy.assert_a1_allowed_for_cash_session_close",
        lambda *_a, **_k: None,
    )

    def _fake_report(_db, _session, reports_dir=None):
        p = Path(reports_dir or ".") / f"{_session.id}.csv"
        p.write_text("id\n", encoding="utf-8")
        return p

    monkeypatch.setattr(
        "recyclic_api.api.api_v1.endpoints.cash_sessions.generate_cash_session_report",
        _fake_report,
    )


def _attach_revision(db_session: Session, session: CashSession) -> None:
    from recyclic_api.models.accounting_config import AccountingConfigRevision

    rev = (
        db_session.query(AccountingConfigRevision)
        .order_by(AccountingConfigRevision.revision_seq.desc())
        .first()
    )
    if rev is not None:
        session.accounting_config_revision_id = rev.id
        db_session.add(session)
        db_session.commit()


@pytest.fixture
def operator_user(db_session: Session) -> User:
    user = User(
        username=f"op-9-11-{uuid.uuid4().hex[:8]}",
        email=f"op911-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("testpassword123"),
        hashed_pin=hash_password(_TEST_STEP_UP_PIN),
        first_name="Op",
        last_name="911",
        role=UserRole.USER,
        status=UserStatus.APPROVED,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def site(db_session: Session, operator_user: User) -> Site:
    site = Site(
        name="Site 9.11",
        address="1 rue test",
        city="Test",
        postal_code="00000",
        country="FR",
        is_active=True,
    )
    db_session.add(site)
    db_session.commit()
    db_session.refresh(site)
    operator_user.site_id = site.id
    db_session.add(operator_user)
    db_session.commit()
    return site


@pytest.fixture
def open_session(db_session: Session, operator_user: User, site: Site) -> CashSession:
    session = CashSession(
        operator_id=operator_user.id,
        site_id=site.id,
        initial_amount=50.0,
        current_amount=50.0,
        status=CashSessionStatus.OPEN,
        total_sales=25.0,
        total_items=1,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


def _enable_comptage_module(db_session: Session, site_id: uuid.UUID) -> None:
    row = SiteModuleConfig(
        site_id=site_id,
        module_key=MODULE_KEY_COMPTAGE_PIECES_BILLETS,
        schema_version="1.0.0",
        payload={
            "enabled": True,
            "skip_allowed": False,
            "require_denomination_grid": True,
            "show_images": True,
        },
        version=1,
    )
    db_session.add(row)
    db_session.commit()


class TestReferential:
    def test_list_15_denominations(self, client: TestClient, db_session: Session, operator_user: User):
        seed_denominations_if_empty(db_session)
        resp = client.get(f"{_V1}/cash-denominations", headers=_auth_headers(operator_user.id))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 15
        codes = [d["code"] for d in data]
        assert codes[0] == "EUR_50000"
        assert codes[1] == "EUR_20000"
        rare = next(d for d in data if d["code"] == "EUR_50000")
        assert rare["display_default"] is False
        assert all(d["display_default"] is True for d in data if d["code"] != "EUR_50000")


class TestDenominationCountApi:
    def test_put_get_nominal(
        self,
        client: TestClient,
        db_session: Session,
        operator_user: User,
        open_session: CashSession,
    ):
        seed_denominations_if_empty(db_session)
        # total = 75 € = 50 fond + 25 ventes
        body = {"lines": _grid_lines_for_total_cents(7500)}
        put = client.put(
            f"{_V1}/cash-sessions/{open_session.id}/denomination-count",
            headers=_auth_headers(operator_user.id),
            json=body,
        )
        assert put.status_code == 200
        payload = put.json()
        assert payload["total_counted_cents"] == 7500
        assert payload["theoretical_cash_cents"] == 7500
        assert payload["variance_cents"] == 0
        assert payload["float_target_cents"] == 5000
        assert payload["withdraw_cents"] == 2500
        assert payload["has_count_recorded"] is True

        get = client.get(
            f"{_V1}/cash-sessions/{open_session.id}/denomination-count",
            headers=_auth_headers(operator_user.id),
        )
        assert get.status_code == 200
        assert get.json()["total_counted_cents"] == 7500

    def test_put_rejects_closed_session(
        self,
        client: TestClient,
        db_session: Session,
        operator_user: User,
        open_session: CashSession,
    ):
        seed_denominations_if_empty(db_session)
        open_session.status = CashSessionStatus.CLOSED
        db_session.add(open_session)
        db_session.commit()
        resp = client.put(
            f"{_V1}/cash-sessions/{open_session.id}/denomination-count",
            headers=_auth_headers(operator_user.id),
            json={"lines": [{"code": "EUR_2000", "quantity": 1}]},
        )
        assert resp.status_code == 400

    def test_get_denomination_count_on_closed_session(
        self,
        client: TestClient,
        db_session: Session,
        operator_user: User,
        open_session: CashSession,
    ):
        seed_denominations_if_empty(db_session)
        client.put(
            f"{_V1}/cash-sessions/{open_session.id}/denomination-count",
            headers=_auth_headers(operator_user.id),
            json={"lines": _grid_lines_for_total_cents(7500)},
        )
        open_session.status = CashSessionStatus.CLOSED
        db_session.add(open_session)
        db_session.commit()
        resp = client.get(
            f"{_V1}/cash-sessions/{open_session.id}/denomination-count",
            headers=_auth_headers(operator_user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["total_counted_cents"] == 7500
        assert resp.json()["has_count_recorded"] is True

    def test_get_denomination_count_403_other_operator(
        self,
        client: TestClient,
        db_session: Session,
        operator_user: User,
        open_session: CashSession,
    ):
        other = User(
            username=f"other-9-11-{uuid.uuid4().hex[:8]}",
            email=f"other911-{uuid.uuid4().hex[:8]}@example.com",
            hashed_password=hash_password("testpassword123"),
            first_name="Other",
            last_name="911",
            role=UserRole.USER,
            status=UserStatus.APPROVED,
            is_active=True,
        )
        db_session.add(other)
        db_session.commit()
        resp = client.get(
            f"{_V1}/cash-sessions/{open_session.id}/denomination-count",
            headers=_auth_headers(other.id),
        )
        assert resp.status_code == 403


class TestCloseIntegration:
    def test_comptage_required_without_grid(
        self,
        client: TestClient,
        db_session: Session,
        operator_user: User,
        site: Site,
        open_session: CashSession,
    ):
        seed_denominations_if_empty(db_session)
        _enable_comptage_module(db_session, site.id)
        resp = client.post(
            f"{_V1}/cash-sessions/{open_session.id}/close",
            headers=_close_headers(operator_user.id),
            json={"actual_amount": 75.0},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body.get("code") == "COMPTAGE_REQUIRED"
        refreshed = db_session.get(CashSession, open_session.id)
        assert refreshed.status == CashSessionStatus.OPEN

    def test_comptage_amount_mismatch(
        self,
        client: TestClient,
        db_session: Session,
        operator_user: User,
        site: Site,
        open_session: CashSession,
    ):
        seed_denominations_if_empty(db_session)
        _enable_comptage_module(db_session, site.id)
        client.put(
            f"{_V1}/cash-sessions/{open_session.id}/denomination-count",
            headers=_auth_headers(operator_user.id),
            json={"lines": _grid_lines_for_total_cents(7500)},
        )
        resp = client.post(
            f"{_V1}/cash-sessions/{open_session.id}/close",
            headers=_close_headers(operator_user.id),
            json={"actual_amount": 80.0},
        )
        assert resp.status_code == 400
        assert resp.json().get("code") == "COMPTAGE_AMOUNT_MISMATCH"

    def test_close_aligns_actual_amount_from_grid(
        self,
        client: TestClient,
        db_session: Session,
        operator_user: User,
        site: Site,
        open_session: CashSession,
        monkeypatch,
    ):
        seed_denominations_if_empty(db_session)
        _enable_comptage_module(db_session, site.id)
        _attach_revision(db_session, open_session)
        client.put(
            f"{_V1}/cash-sessions/{open_session.id}/denomination-count",
            headers=_auth_headers(operator_user.id),
            json={"lines": _grid_lines_for_total_cents(7500)},
        )
        _patch_close_dependencies(monkeypatch)

        resp = client.post(
            f"{_V1}/cash-sessions/{open_session.id}/close",
            headers=_close_headers(operator_user.id),
            json={"actual_amount": 75.0},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("anomaly_close_sheet") is False
        assert body.get("close_sheet_pdf_url") is None
        db_session.expire_all()
        refreshed = db_session.get(CashSession, open_session.id)
        assert refreshed is not None
        assert refreshed.status == CashSessionStatus.CLOSED
        assert refreshed.actual_amount == pytest.approx(75.0)
        snap = refreshed.accounting_close_snapshot
        assert snap is not None
        assert snap.get("schema_version") == 3
        assert snap.get("denomination_count_v1") is not None
        assert snap["denomination_count_v1"]["total_counted_cents"] == 7500

    def test_close_zero_theoretical_with_zero_grid(
        self,
        client: TestClient,
        db_session: Session,
        operator_user: User,
        site: Site,
        monkeypatch,
    ):
        seed_denominations_if_empty(db_session)
        _enable_comptage_module(db_session, site.id)
        empty_session = CashSession(
            operator_id=operator_user.id,
            site_id=site.id,
            initial_amount=0.0,
            current_amount=0.0,
            status=CashSessionStatus.OPEN,
            total_sales=0.0,
            total_items=0,
        )
        db_session.add(empty_session)
        db_session.commit()
        db_session.refresh(empty_session)
        _attach_revision(db_session, empty_session)
        client.put(
            f"{_V1}/cash-sessions/{empty_session.id}/denomination-count",
            headers=_auth_headers(operator_user.id),
            json={"lines": [{"code": "EUR_2000", "quantity": 0}]},
        )
        _patch_close_dependencies(monkeypatch)
        resp = client.post(
            f"{_V1}/cash-sessions/{empty_session.id}/close",
            headers=_close_headers(operator_user.id),
            json={"actual_amount": 0.0},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("deleted") is True
        assert "Session vide non enregistrée" in body.get("message", "")

    def test_close_anomaly_flags_on_variance(
        self,
        client: TestClient,
        db_session: Session,
        operator_user: User,
        site: Site,
        open_session: CashSession,
        monkeypatch,
    ):
        seed_denominations_if_empty(db_session)
        _enable_comptage_module(db_session, site.id)
        _attach_revision(db_session, open_session)
        client.put(
            f"{_V1}/cash-sessions/{open_session.id}/denomination-count",
            headers=_auth_headers(operator_user.id),
            json={"lines": _grid_lines_for_total_cents(7400)},
        )
        _patch_close_dependencies(monkeypatch)
        resp = client.post(
            f"{_V1}/cash-sessions/{open_session.id}/close",
            headers=_close_headers(operator_user.id),
            json={"actual_amount": 74.0, "variance_comment": "écart comptage pilote"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("anomaly_close_sheet") is True
        assert body.get("close_sheet_pdf_url") == f"/v1/cash-sessions/{open_session.id}/close-sheet.pdf"

    def test_module_off_legacy_close(
        self,
        client: TestClient,
        db_session: Session,
        operator_user: User,
        open_session: CashSession,
        monkeypatch,
    ):
        seed_denominations_if_empty(db_session)
        _attach_revision(db_session, open_session)
        _patch_close_dependencies(monkeypatch)
        resp = client.post(
            f"{_V1}/cash-sessions/{open_session.id}/close",
            headers=_close_headers(operator_user.id),
            json={"actual_amount": 75.0},
        )
        assert resp.status_code == 200
        db_session.expire_all()
        snap = db_session.get(CashSession, open_session.id).accounting_close_snapshot
        assert snap.get("schema_version") == 2
        assert "denomination_count_v1" not in snap or snap.get("denomination_count_v1") is None


class TestD33OnGridTotal:
    def test_d33_blocks_close_with_grid_variance(
        self,
        db_session: Session,
        operator_user: User,
        site: Site,
        open_session: CashSession,
    ):
        from recyclic_api.schemas.cash_denomination import DenominationCountUpsertV1, DenominationCountLineInputV1

        seed_denominations_if_empty(db_session)
        _enable_comptage_module(db_session, site.id)
        AdminSettingsService(db_session).upsert_cash_close_variance_max_eur(str(site.id), 2.0)
        denom = CashDenominationService(db_session)
        # Grille 78 € vs théorique 75 € → écart +3 € > seuil 2 €
        denom.upsert_denomination_count(
            open_session,
            operator_user,
            DenominationCountUpsertV1(
                lines=[DenominationCountLineInputV1(code="EUR_2000", quantity=39)]
            ),
        )
        service = CashSessionService(db_session)
        with pytest.raises(CashCloseVarianceExceededError):
            service.validate_session_close(open_session, 78.0, "écart important")


class TestPahekoNonRegression:
    def test_t3_unchanged_with_schema_version_3_snapshot(self, db_session: Session):
        import json
        from recyclic_api.models.accounting_config import AccountingConfigRevision
        from sqlalchemy import func

        max_seq = db_session.query(func.max(AccountingConfigRevision.revision_seq)).scalar()
        rev = AccountingConfigRevision(
            revision_seq=(max_seq or 0) + 1,
            snapshot_json=json.dumps(
                {
                    "schema_version": 1,
                    "global_accounts": {
                        "default_sales_account": "7070",
                        "default_donation_account": "7541",
                        "prior_year_refund_account": "672",
                        "cash_shortage_account": "658",
                        "cash_surplus_account": "758",
                    },
                    "payment_methods": [
                        {
                            "code": "cash",
                            "label": "Especes",
                            "active": True,
                            "kind": "cash",
                            "paheko_debit_account": "531",
                            "paheko_refund_credit_account": "531",
                        }
                    ],
                }
            ),
            note="pytest-9-11",
        )
        db_session.add(rev)
        db_session.commit()
        snap = {
            "schema_version": 3,
            "session_id": str(uuid.uuid4()),
            "site_id": str(uuid.uuid4()),
            "sync_correlation_id": "c1",
            "accounting_config_revision_id": str(rev.id),
            "totals": {
                "by_payment_method_signed": {"cash": 75.0},
                "refunds_current_fiscal_total": 0.0,
                "refunds_prior_closed_fiscal_total": 0.0,
                "donation_surplus_total": 0.0,
            },
            "closing": {
                "theoretical_cash_amount": 75.0,
                "actual_cash_amount": 73.0,
                "cash_variance": -2.0,
            },
            "denomination_count_v1": {
                "total_counted_cents": 7300,
                "theoretical_cash_cents": 7500,
                "variance_cents": -200,
                "breakdown_revision": "sha256:test",
                "recorded_at": "2026-06-06T12:00:00+00:00",
                "breakdown": [],
            },
        }
        enr = {
            "accounting_close_snapshot_frozen": snap,
            "cash_session_id": snap["session_id"],
            "closed_at": "2026-06-06T12:00:00+00:00",
            "site_id": snap["site_id"],
            "id_year": 2,
            "debit": "512",
            "credit": "707",
        }
        plan, err, _ = build_planned_sub_writes(snap, db=db_session, enriched_payload=enr)
        assert err is None
        assert len(plan) == 4
        assert plan[3]["kind"] == SUB_KIND_CASH_VARIANCE_V1


def test_is_comptage_module_required_defaults_off(db_session: Session, site: Site):
    assert is_comptage_module_required(db_session, site.id) is False
    _enable_comptage_module(db_session, site.id)
    assert is_comptage_module_required(db_session, site.id) is True


def test_resolve_close_raises_on_zero_grid_with_positive_theoretical(
    db_session: Session,
    operator_user: User,
    site: Site,
    open_session: CashSession,
):
    from recyclic_api.schemas.cash_denomination import DenominationCountUpsertV1, DenominationCountLineInputV1

    seed_denominations_if_empty(db_session)
    _enable_comptage_module(db_session, site.id)
    denom = CashDenominationService(db_session)
    denom.upsert_denomination_count(
        open_session,
        operator_user,
        DenominationCountUpsertV1(lines=[DenominationCountLineInputV1(code="EUR_2000", quantity=0)]),
    )
    with pytest.raises(ConflictError):
        denom.resolve_close_actual_amount(open_session, 0.0)
