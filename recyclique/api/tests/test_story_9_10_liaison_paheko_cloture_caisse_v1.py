"""Story 9.10 — T3 écart 658/758 (batch Paheko) et seuil D33 par site."""

from __future__ import annotations

import json
import uuid
from types import SimpleNamespace

import pytest
from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import HTTPException

from recyclic_api.core.exceptions import CashCloseVarianceExceededError, ValidationError
from recyclic_api.utils.domain_exception_http import raise_domain_exception_as_http
from recyclic_api.services.paheko_close_batch_builder import (
    SUB_KIND_CASH_VARIANCE_V1,
    build_planned_sub_writes,
    sub_write_idempotency_key,
)
from recyclic_api.models.accounting_config import AccountingConfigRevision
from recyclic_api.models.cash_session import CashSessionStatus
from recyclic_api.services.admin_settings_service import AdminSettingsService
from recyclic_api.services.cash_session_service import CashSessionService, CLOSE_VARIANCE_TOLERANCE


def _revision_snapshot(
    *,
    shortage: str = "658",
    surplus: str = "758",
    cash_debit: str = "531",
) -> dict:
    return {
        "schema_version": 1,
        "global_accounts": {
            "default_sales_account": "7070",
            "default_donation_account": "7541",
            "prior_year_refund_account": "672",
            "cash_shortage_account": shortage,
            "cash_surplus_account": surplus,
        },
        "payment_methods": [
            {
                "code": "cash",
                "label": "Especes",
                "active": True,
                "kind": "cash",
                "paheko_debit_account": cash_debit,
                "paheko_refund_credit_account": cash_debit,
            },
        ],
    }


def _insert_revision(db_session: Session, snap: dict | None = None) -> AccountingConfigRevision:
    max_seq = db_session.query(func.max(AccountingConfigRevision.revision_seq)).scalar()
    next_seq = (max_seq or 0) + 1
    rev = AccountingConfigRevision(
        revision_seq=next_seq,
        snapshot_json=json.dumps(snap or _revision_snapshot()),
        note="pytest-9-10",
    )
    db_session.add(rev)
    db_session.commit()
    db_session.refresh(rev)
    return rev


def _snap(
    *,
    cash_variance: float,
    rev_id: str,
    by_pm: dict | None = None,
) -> dict:
    return {
        "schema_version": 1,
        "session_id": str(uuid.uuid4()),
        "site_id": str(uuid.uuid4()),
        "sync_correlation_id": "c1",
        "accounting_config_revision_id": rev_id,
        "totals": {
            "by_payment_method_signed": by_pm or {"cash": 10.0},
            "refunds_current_fiscal_total": 0.0,
            "refunds_prior_closed_fiscal_total": 0.0,
            "donation_surplus_total": 0.0,
        },
        "closing": {
            "theoretical_cash_amount": 10.0,
            "actual_cash_amount": 10.0 + cash_variance,
            "cash_variance": cash_variance,
        },
    }


def _enr(snap: dict) -> dict:
    return {
        "accounting_close_snapshot_frozen": snap,
        "cash_session_id": str(uuid.uuid4()),
        "closed_at": "2026-01-15T10:00:00+00:00",
        "site_id": snap.get("site_id"),
        "id_year": 2,
        "debit": "512",
        "credit": "707",
    }


def test_t3_shortage_minus_150(db_session: Session) -> None:
    rev = _insert_revision(db_session)
    snap = _snap(cash_variance=-1.50, rev_id=str(rev.id))
    plan, err, _ = build_planned_sub_writes(snap, db=db_session, enriched_payload=_enr(snap))
    assert err is None
    assert len(plan) == 4
    t3 = plan[3]
    assert t3["kind"] == SUB_KIND_CASH_VARIANCE_V1
    assert t3["amount"] == 1.50
    body = t3.get("http_body")
    assert body is not None
    lines = body.get("lines") or []
    debits = [ln for ln in lines if ln.get("debit")]
    credits = [ln for ln in lines if ln.get("credit")]
    assert any(ln.get("account") == "658" and ln.get("debit") == 1.50 for ln in debits)
    assert any(ln.get("account") == "531" and ln.get("credit") == 1.50 for ln in credits)


def test_t3_surplus_plus_080(db_session: Session) -> None:
    rev = _insert_revision(db_session)
    snap = _snap(cash_variance=0.80, rev_id=str(rev.id))
    plan, err, _ = build_planned_sub_writes(snap, db=db_session, enriched_payload=_enr(snap))
    assert err is None
    t3 = plan[3]
    assert t3["amount"] == 0.80
    lines = (t3.get("http_body") or {}).get("lines") or []
    assert any(ln.get("account") == "531" and ln.get("debit") == 0.80 for ln in lines)
    assert any(ln.get("account") == "758" and ln.get("credit") == 0.80 for ln in lines)


def test_t3_skip_zero(db_session: Session) -> None:
    rev = _insert_revision(db_session)
    snap = _snap(cash_variance=0.0, rev_id=str(rev.id))
    plan, err, _ = build_planned_sub_writes(snap, db=db_session, enriched_payload=_enr(snap))
    assert err is None
    t3 = plan[3]
    assert t3["observability"]["body_format"] == "skipped_zero"
    assert t3.get("http_body") is None


def test_t3_missing_accounts_error(db_session: Session) -> None:
    rev = _insert_revision(db_session, snap=_revision_snapshot(shortage="", surplus="758"))
    snap = _snap(cash_variance=-2.0, rev_id=str(rev.id))
    _, err, msg = build_planned_sub_writes(snap, db=db_session, enriched_payload=_enr(snap))
    assert err == "variance_accounts_missing"
    assert msg


def test_d33_block_above_threshold(db_session: Session) -> None:
    site_id = uuid.uuid4()
    AdminSettingsService(db_session).upsert_cash_close_variance_max_eur(str(site_id), 2.0)
    service = CashSessionService(db_session)
    session = SimpleNamespace(
        id=uuid.uuid4(),
        site_id=site_id,
        status=CashSessionStatus.OPEN,
        initial_amount=100.0,
        total_sales=0.0,
    )
    service.get_total_donations_for_session = lambda _sid: 0.0  # type: ignore[method-assign]
    with pytest.raises(CashCloseVarianceExceededError, match="seuil autorisé"):
        service.validate_session_close(session, 103.0, "commentaire ok")


def test_d33_allow_below_threshold(db_session: Session) -> None:
    site_id = uuid.uuid4()
    AdminSettingsService(db_session).upsert_cash_close_variance_max_eur(str(site_id), 2.0)
    service = CashSessionService(db_session)
    session = SimpleNamespace(
        id=uuid.uuid4(),
        site_id=site_id,
        status=CashSessionStatus.OPEN,
        initial_amount=100.0,
        total_sales=0.0,
    )
    service.get_total_donations_for_session = lambda _sid: 0.0  # type: ignore[method-assign]
    preview = service.validate_session_close(session, 101.50, "écart modéré")
    assert preview["variance"] == pytest.approx(1.50)
    assert 1.50 > CLOSE_VARIANCE_TOLERANCE


def test_d33_at_threshold_allowed(db_session: Session) -> None:
    site_id = uuid.uuid4()
    AdminSettingsService(db_session).upsert_cash_close_variance_max_eur(str(site_id), 2.0)
    service = CashSessionService(db_session)
    session = SimpleNamespace(
        id=uuid.uuid4(),
        site_id=site_id,
        status=CashSessionStatus.OPEN,
        initial_amount=100.0,
        total_sales=0.0,
    )
    service.get_total_donations_for_session = lambda _sid: 0.0  # type: ignore[method-assign]
    preview = service.validate_session_close(session, 102.0, "écart au seuil")
    assert preview["variance"] == pytest.approx(2.0)


def test_d33_negative_variance_above_threshold(db_session: Session) -> None:
    site_id = uuid.uuid4()
    AdminSettingsService(db_session).upsert_cash_close_variance_max_eur(str(site_id), 2.0)
    service = CashSessionService(db_session)
    session = SimpleNamespace(
        id=uuid.uuid4(),
        site_id=site_id,
        status=CashSessionStatus.OPEN,
        initial_amount=100.0,
        total_sales=0.0,
    )
    service.get_total_donations_for_session = lambda _sid: 0.0  # type: ignore[method-assign]
    with pytest.raises(CashCloseVarianceExceededError):
        service.validate_session_close(session, 97.0, "manque")


def test_d33_http_422_mapping() -> None:
    with pytest.raises(HTTPException) as exc_info:
        raise_domain_exception_as_http(
            CashCloseVarianceExceededError("Écart > seuil"),
            not_found_status=404,
            conflict_status=400,
            validation_status=400,
        )
    assert exc_info.value.status_code == 422


def test_t3_snapshot_missing_revision(db_session: Session) -> None:
    snap = _snap(cash_variance=-1.0, rev_id=str(uuid.uuid4()))
    snap.pop("accounting_config_revision_id")
    _, err, _ = build_planned_sub_writes(snap, db=db_session, enriched_payload=_enr(snap))
    assert err == "snapshot_missing_revision"


def test_t3_revision_not_found(db_session: Session) -> None:
    snap = _snap(cash_variance=-1.0, rev_id=str(uuid.uuid4()))
    _, err, _ = build_planned_sub_writes(snap, db=db_session, enriched_payload=_enr(snap))
    assert err == "revision_not_found"


def test_t3_variance_at_skip_boundary_not_zero(db_session: Session) -> None:
    rev = _insert_revision(db_session)
    snap = _snap(cash_variance=0.005, rev_id=str(rev.id))
    plan, err, _ = build_planned_sub_writes(snap, db=db_session, enriched_payload=_enr(snap))
    assert err is None
    t3 = plan[3]
    assert t3["kind"] == SUB_KIND_CASH_VARIANCE_V1
    assert t3.get("observability", {}).get("body_format") != "skipped_zero"
    assert t3.get("http_body") is not None


def test_batch_idempotency_sub_key_index_3() -> None:
    batch_key = "batch:test-session"
    sub = sub_write_idempotency_key(batch_key, 3, SUB_KIND_CASH_VARIANCE_V1)
    assert sub == f"{batch_key}:sub:3:{SUB_KIND_CASH_VARIANCE_V1}"
