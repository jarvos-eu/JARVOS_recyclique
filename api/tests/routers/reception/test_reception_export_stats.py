# Tests API export CSV et stats live réception — Story 6.3.
# 401 sans auth, validation des query params. Tests avec auth+DB (conftest : fixtures ticket/lignes).

import uuid

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

_BASE = "/v1/reception"


def test_download_token_requires_auth():
    ticket_id = str(uuid.uuid4())
    r = client.post(f"{_BASE}/tickets/{ticket_id}/download-token")
    assert r.status_code == 401


def test_export_ticket_csv_requires_auth():
    ticket_id = str(uuid.uuid4())
    r = client.get(f"{_BASE}/tickets/{ticket_id}/export-csv")
    assert r.status_code == 401


def test_export_lignes_csv_requires_auth():
    r = client.get(
        f"{_BASE}/lignes/export-csv",
        params={"date_from": "2026-02-01", "date_to": "2026-02-28"},
    )
    assert r.status_code == 401


def test_stats_live_requires_auth():
    r = client.get(f"{_BASE}/stats/live")
    assert r.status_code == 401


def test_export_lignes_csv_requires_date_from():
    r = client.get(
        f"{_BASE}/lignes/export-csv",
        params={"date_to": "2026-02-28"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert r.status_code in (401, 422)


def test_export_lignes_csv_requires_date_to():
    r = client.get(
        f"{_BASE}/lignes/export-csv",
        params={"date_from": "2026-02-01"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert r.status_code in (401, 422)


# ---- Tests avec auth et données (fixture reception_user_with_ticket_and_lignes) ----


def test_export_ticket_csv_with_auth_contains_lines(reception_user_with_ticket_and_lignes):
    """Avec auth et ticket existant, l'export CSV du ticket contient les lignes (en-têtes + données)."""
    data = reception_user_with_ticket_and_lignes
    token = data["token"]
    ticket_id = data["ticket_id"]
    r = client.get(
        f"{_BASE}/tickets/{ticket_id}/export-csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("Content-Type", "")
    body = r.text
    assert "ticket_id" in body or "ligne_id" in body
    assert "recyclage" in body
    assert "revente" in body
    assert "10.5" in body or "10,5" in body
    assert "2.25" in body or "2,25" in body
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    assert len(lines) >= 2  # header + at least 2 data rows


def test_export_lignes_csv_with_auth_and_period(reception_user_with_ticket_and_lignes):
    """Avec auth et période date_from/date_to, export lignes CSV retourne 200 et contenu CSV."""
    data = reception_user_with_ticket_and_lignes
    token = data["token"]
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    r = client.get(
        f"{_BASE}/lignes/export-csv",
        params={"date_from": today, "date_to": today},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("Content-Type", "")
    body = r.text
    assert "ticket_id" in body or "ligne_id" in body
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    assert len(lines) >= 1  # at least header


def test_stats_live_returns_coherent_json(reception_user_with_ticket_and_lignes):
    """Avec auth, GET stats/live retourne un JSON avec tickets_today, total_weight_kg, lines_count."""
    data = reception_user_with_ticket_and_lignes
    token = data["token"]
    r = client.get(
        f"{_BASE}/stats/live",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    j = r.json()
    assert "tickets_today" in j
    assert "total_weight_kg" in j
    assert "lines_count" in j
    assert isinstance(j["tickets_today"], int)
    assert isinstance(j["total_weight_kg"], (int, float))
    assert isinstance(j["lines_count"], int)
    assert j["tickets_today"] >= 1
    assert j["lines_count"] >= 2
    assert j["total_weight_kg"] >= 10.5 + 2.25 - 0.01  # allow rounding
