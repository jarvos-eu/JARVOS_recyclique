# Tests agrégats déclaratifs (Story 9.1) — modèle, service, API read-only.
# Story 9.2 : tests export (module decla).

import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.models import (
    Category,
    CashRegister,
    CashSession,
    DeclarativeAggregate,
    Sale,
    SaleItem,
    Site,
    User,
)
from api.services.declarative_service import (
    FLOW_CAISSE,
    FLOW_RECEPTION,
    _quarter_bounds,
    compute_and_persist_aggregates,
)
from api.tests.conftest import FAKE_SITE_ID, FAKE_USER_ID, TestingSessionLocal


@pytest.fixture
def db_session() -> Session:
    """Session DB pour tests déclaratifs (même engine que conftest)."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_quarter_bounds() -> None:
    """_quarter_bounds retourne des plages correctes pour T1–T4."""
    start, end = _quarter_bounds(2026, 1)
    assert start == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert end == datetime(2026, 4, 1, tzinfo=timezone.utc)

    start, end = _quarter_bounds(2026, 4)
    assert start == datetime(2026, 10, 1, tzinfo=timezone.utc)
    assert end == datetime(2027, 1, 1, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="quarter"):
        _quarter_bounds(2026, 0)
    with pytest.raises(ValueError, match="quarter"):
        _quarter_bounds(2026, 5)


def test_compute_and_persist_aggregates_empty(db_session: Session) -> None:
    """Sans données source, compute_and_persist_aggregates insère 0 lignes."""
    n = compute_and_persist_aggregates(db_session, 2026, 1)
    assert n == 0
    rows = db_session.query(DeclarativeAggregate).filter_by(year=2026, quarter=1).all()
    assert len(rows) == 0


def test_compute_and_persist_aggregates_one_aggregate(
    db_session: Session,
) -> None:
    """Après ajout manuel d'un agrégat, recalcul remplace par les données source (ici vides)."""
    cat_id = uuid.uuid4()
    c = Category(
        id=cat_id,
        name="Test Cat",
        display_order=0,
        display_order_entry=0,
    )
    db_session.add(c)
    db_session.commit()

    rec = DeclarativeAggregate(
        year=2026,
        quarter=1,
        category_id=cat_id,
        flow_type=FLOW_CAISSE,
        weight_kg=10.0,
        quantity=2,
    )
    db_session.add(rec)
    db_session.commit()
    assert db_session.query(DeclarativeAggregate).count() == 1

    n = compute_and_persist_aggregates(db_session, 2026, 1)
    # Pas de ventes ni lignes dépôt dans la période -> 0 lignes après recalcul
    assert n == 0
    assert db_session.query(DeclarativeAggregate).filter_by(year=2026, quarter=1).count() == 0


def test_declarative_aggregate_model(db_session: Session) -> None:
    """Le modèle DeclarativeAggregate persiste correctement."""
    cat_id = uuid.uuid4()
    c = Category(
        id=cat_id,
        name="Cat",
        display_order=0,
        display_order_entry=0,
    )
    db_session.add(c)
    db_session.commit()

    agg = DeclarativeAggregate(
        year=2026,
        quarter=2,
        category_id=cat_id,
        flow_type=FLOW_RECEPTION,
        weight_kg=5.5,
        quantity=3,
    )
    db_session.add(agg)
    db_session.commit()
    db_session.refresh(agg)
    assert agg.id is not None
    assert agg.year == 2026
    assert agg.quarter == 2
    assert agg.flow_type == FLOW_RECEPTION
    assert agg.weight_kg == 5.5
    assert agg.quantity == 3


def test_get_declarative_aggregates_200(
    client: TestClient,
    auth_headers: dict,
    db_session: Session,
) -> None:
    """GET /v1/declarative/aggregates avec admin retourne 200 et une liste."""
    resp = client.get("/v1/declarative/aggregates", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

    # Avec filtre year/quarter
    resp2 = client.get(
        "/v1/declarative/aggregates?year=2026&quarter=1",
        headers=auth_headers,
    )
    assert resp2.status_code == 200
    assert isinstance(resp2.json(), list)


def test_post_compute_aggregates_200(client: TestClient, auth_headers: dict) -> None:
    """POST /v1/declarative/aggregates/compute avec admin retourne 200 et rows_persisted."""
    resp = client.post(
        "/v1/declarative/aggregates/compute",
        json={"year": 2026, "quarter": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "rows_persisted" in data
    assert isinstance(data["rows_persisted"], int)


def test_post_compute_aggregates_400_invalid_quarter(
    client: TestClient, auth_headers: dict
) -> None:
    """POST /v1/declarative/aggregates/compute avec quarter invalide retourne 400."""
    resp = client.post(
        "/v1/declarative/aggregates/compute",
        json={"year": 2026, "quarter": 0},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    resp2 = client.post(
        "/v1/declarative/aggregates/compute",
        json={"year": 2026, "quarter": 5},
        headers=auth_headers,
    )
    assert resp2.status_code == 400


def test_get_declarative_aggregates_422_invalid_flow_type(
    client: TestClient, auth_headers: dict
) -> None:
    """GET /v1/declarative/aggregates avec flow_type invalide retourne 422."""
    resp = client.get(
        "/v1/declarative/aggregates?flow_type=invalid",
        headers=auth_headers,
    )
    assert resp.status_code == 422
    detail = resp.json().get("detail", "")
    assert "caisse" in detail and "reception" in detail


def test_post_compute_aggregates_400_invalid_year(
    client: TestClient, auth_headers: dict
) -> None:
    """POST /v1/declarative/aggregates/compute avec year hors plage retourne 400."""
    resp = client.post(
        "/v1/declarative/aggregates/compute",
        json={"year": 1800, "quarter": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    resp2 = client.post(
        "/v1/declarative/aggregates/compute",
        json={"year": 2200, "quarter": 1},
        headers=auth_headers,
    )
    assert resp2.status_code == 400


def test_compute_and_persist_aggregates_from_sale_items_integration(
    client: TestClient,
    auth_headers: dict,
    db_session: Session,
) -> None:
    """Créer Sale + SaleItem dans une période, appeler compute_and_persist_aggregates, vérifier une ligne dans declarative_aggregates."""
    # S'assurer que Site et User existent (alignés sur conftest _db_with_user si client a été utilisé)
    site = db_session.get(Site, FAKE_SITE_ID)
    user = db_session.get(User, FAKE_USER_ID)
    if site is None:
        site = Site(id=FAKE_SITE_ID, name="Test Site", is_active=True)
        db_session.add(site)
        db_session.flush()
    if user is None:
        user = User(
            id=FAKE_USER_ID,
            username="test_reception",
            email="test@reception.local",
            password_hash="hash",
            role="operator",
            status="active",
            site_id=site.id,
        )
        db_session.add(user)
        db_session.flush()

    reg = CashRegister(site_id=site.id, name="R1", is_active=True)
    db_session.add(reg)
    db_session.flush()
    opened_at = datetime(2026, 1, 15, tzinfo=timezone.utc)
    cs = CashSession(
        register_id=reg.id,
        site_id=site.id,
        operator_id=user.id,
        opened_at=opened_at,
        status="open",
    )
    db_session.add(cs)
    db_session.flush()

    cat = Category(
        id=uuid.uuid4(),
        name="Cat Decla",
        display_order=0,
        display_order_entry=0,
    )
    db_session.add(cat)
    db_session.flush()

    sale_date = datetime(2026, 2, 15, tzinfo=timezone.utc)
    sale = Sale(
        cash_session_id=cs.id,
        operator_id=user.id,
        total_amount=0,
        sale_date=sale_date,
        created_at=sale_date,
    )
    db_session.add(sale)
    db_session.flush()
    item = SaleItem(
        sale_id=sale.id,
        category_id=cat.id,
        quantity=3,
        unit_price=0,
        total_price=0,
        weight=2.5,
    )
    db_session.add(item)
    db_session.commit()

    n = compute_and_persist_aggregates(db_session, 2026, 1)
    assert n == 1
    rows = (
        db_session.query(DeclarativeAggregate)
        .filter_by(year=2026, quarter=1, flow_type=FLOW_CAISSE, category_id=cat.id)
        .all()
    )
    assert len(rows) == 1
    assert rows[0].weight_kg == 2.5
    assert rows[0].quantity == 3


def test_get_declarative_aggregates_without_admin_403(
    client: TestClient, auth_headers: dict
) -> None:
    """GET /v1/declarative/aggregates sans permission admin retourne 403."""
    from api.core import deps

    with patch.object(deps, "get_user_permission_codes_from_user", return_value=set()):
        resp = client.get("/v1/declarative/aggregates", headers=auth_headers)
    assert resp.status_code == 403


def test_post_compute_aggregates_without_admin_403(
    client: TestClient, auth_headers: dict
) -> None:
    """POST /v1/declarative/aggregates/compute sans permission admin retourne 403."""
    from api.core import deps

    with patch.object(deps, "get_user_permission_codes_from_user", return_value=set()):
        resp = client.post(
            "/v1/declarative/aggregates/compute",
            json={"year": 2026, "quarter": 1},
            headers=auth_headers,
        )
    assert resp.status_code == 403


def test_export_declarative_aggregates_200_csv(
    client: TestClient, auth_headers: dict
) -> None:
    """GET /v1/declarative/export avec format=csv et admin retourne 200 et un CSV."""
    resp = client.get(
        "/v1/declarative/export?year=2026&quarter=1&format=csv",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    assert "declarative_aggregates.csv" in resp.headers.get("content-disposition", "")
    body = resp.text
    assert "year" in body and "quarter" in body and "flow_type" in body


def test_export_declarative_aggregates_200_json(
    client: TestClient, auth_headers: dict
) -> None:
    """GET /v1/declarative/export avec format=json et admin retourne 200 et un JSON."""
    resp = client.get(
        "/v1/declarative/export?year=2026&quarter=1&format=json",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")
    data = resp.json()
    assert isinstance(data, list)


def test_export_declarative_aggregates_422_invalid_format(
    client: TestClient, auth_headers: dict
) -> None:
    """GET /v1/declarative/export avec format invalide retourne 422."""
    resp = client.get(
        "/v1/declarative/export?year=2026&quarter=1&format=xml",
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_export_declarative_aggregates_without_admin_403(
    client: TestClient, auth_headers: dict
) -> None:
    """GET /v1/declarative/export sans permission admin retourne 403."""
    from api.core import deps

    with patch.object(deps, "get_user_permission_codes_from_user", return_value=set()):
        resp = client.get(
            "/v1/declarative/export?year=2026&quarter=1&format=csv",
            headers=auth_headers,
        )
    assert resp.status_code == 403
