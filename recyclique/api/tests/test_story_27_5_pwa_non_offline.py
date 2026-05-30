"""Story 27.5 — garde-fous API network-only (PWA installable, pas de cache métier offline)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.models.site import Site
from recyclic_api.modules.module_config.registry import MODULE_KEY_KPI_LIVE_BANNER
from tests.api_v1_paths import v1

_REGISTERED_DEVICES = "/registered-devices"
_SHARED_WS = "/shared-workstation"


def _make_site(db: Session) -> Site:
    site = Site(id=uuid4(), name="Site 27.5", is_active=True)
    db.add(site)
    db.commit()
    return site


@pytest.mark.story_27_5
class TestStory275PwaApiNoStoreHeaders:
    """Les endpoints Epic 27 sensibles restent no-store (complément politique PWA)."""

    def test_story_27_5_registered_devices_list_no_store(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json={
                "name": "Poste PWA",
                "site_id": str(site.id),
                "allowed_module_keys": [MODULE_KEY_KPI_LIVE_BANNER],
            },
        )
        list_resp = super_admin_client.get(
            v1(f"{_REGISTERED_DEVICES}?site_id={site.id}")
        )
        assert list_resp.status_code == 200
        assert list_resp.headers.get("cache-control") == "no-store"

    def test_story_27_5_shared_workstation_enroll_complete_no_store(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        create_resp = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json={
                "name": "Poste SW",
                "site_id": str(site.id),
                "allowed_module_keys": [MODULE_KEY_KPI_LIVE_BANNER],
            },
        )
        device_id = create_resp.json()["device_id"]
        code_resp = super_admin_client.post(
            v1(f"{_REGISTERED_DEVICES}/{device_id}/enrollment-codes"),
            json={"purpose": "initial_enrollment"},
        )
        assert code_resp.headers.get("cache-control") == "no-store"
        code = code_resp.json()["code"]
        enroll_resp = super_admin_client.post(
            v1(f"{_SHARED_WS}/enroll/complete"),
            json={"code": code},
        )
        assert enroll_resp.status_code == 200
        assert enroll_resp.headers.get("cache-control") == "no-store"
