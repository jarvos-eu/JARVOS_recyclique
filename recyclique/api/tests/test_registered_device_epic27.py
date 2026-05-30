"""Epic 27.1 — RegisteredDevice : modèle, CRUD SuperAdmin, allowlist, non-confusion."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from recyclic_api.core.database import Base
from recyclic_api.models.cash_register import CashRegister
from recyclic_api.models.poste_reception import PosteReception, PosteReceptionStatus
from recyclic_api.models.registered_device import (
    DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
    RegisteredDevice,
    RegisteredDeviceStatus,
    RegisteredDeviceType,
)
from recyclic_api.models.site import Site
from recyclic_api.models.user import User
from recyclic_api.modules.module_config.registry import MODULE_KEY_KPI_LIVE_BANNER
from tests.api_v1_paths import v1

_REGISTERED_DEVICES = "/registered-devices"


def _make_site(db: Session) -> Site:
    site = Site(id=uuid4(), name="Site Epic27", is_active=True)
    db.add(site)
    db.commit()
    return site


def _device_payload(site_id: str, **overrides) -> dict:
    base = {
        "name": "Poste Hall",
        "site_id": site_id,
        "allowed_module_keys": [MODULE_KEY_KPI_LIVE_BANNER],
    }
    base.update(overrides)
    return base


class TestRegisteredDeviceModel:
    def test_registered_device_table_in_metadata(self):
        assert "registered_devices" in Base.metadata.tables

    def test_registered_device_fk_site_id(self, db_session: Session):
        site = _make_site(db_session)
        device = RegisteredDevice(
            id=uuid4(),
            device_type=RegisteredDeviceType.SHARED_WORKSTATION.value,
            name="P1",
            site_id=site.id,
            status=RegisteredDeviceStatus.PENDING_ENROLLMENT.value,
            allowed_module_keys=[],
            inactivity_timeout_seconds=DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
        )
        db_session.add(device)
        db_session.commit()
        insp = inspect(db_session.get_bind())
        fks = insp.get_foreign_keys("registered_devices")
        assert any(
            "site_id" in (fk.get("constrained_columns") or [])
            for fk in fks
        )


class TestRegisteredDeviceCrudSuperAdmin:
    def test_crud_lifecycle_super_admin(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        create_resp = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(site.id)),
        )
        assert create_resp.status_code == 201
        body = create_resp.json()
        assert "device_id" in body
        assert "id" not in body or body.get("id") is None
        assert body["device_type"] == RegisteredDeviceType.SHARED_WORKSTATION.value
        assert body["status"] == RegisteredDeviceStatus.PENDING_ENROLLMENT.value
        assert body["allowed_module_keys"] == [MODULE_KEY_KPI_LIVE_BANNER]
        assert body["inactivity_timeout_seconds"] == DEFAULT_INACTIVITY_TIMEOUT_SECONDS
        assert create_resp.headers.get("cache-control") == "no-store"

        device_id = body["device_id"]

        get_resp = super_admin_client.get(v1(f"{_REGISTERED_DEVICES}/{device_id}"))
        assert get_resp.status_code == 200
        assert get_resp.json()["device_id"] == device_id

        list_resp = super_admin_client.get(
            v1(f"{_REGISTERED_DEVICES}?site_id={site.id}")
        )
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1

        patch_resp = super_admin_client.patch(
            v1(f"{_REGISTERED_DEVICES}/{device_id}"),
            json={"name": "Poste Hall B", "status": RegisteredDeviceStatus.ACTIVE.value},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["name"] == "Poste Hall B"
        assert patch_resp.json()["status"] == RegisteredDeviceStatus.ACTIVE.value

        revoke_resp = super_admin_client.post(
            v1(f"{_REGISTERED_DEVICES}/{device_id}/revoke"),
            json={},
        )
        assert revoke_resp.status_code == 200
        revoked = revoke_resp.json()
        assert revoked["status"] == RegisteredDeviceStatus.REVOKED.value
        assert revoked["revoked_at"] is not None

        get_revoked = super_admin_client.get(v1(f"{_REGISTERED_DEVICES}/{device_id}"))
        assert get_revoked.status_code == 200
        assert get_revoked.json()["status"] == RegisteredDeviceStatus.REVOKED.value

    def test_list_excludes_revoked_by_default(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        r = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(site.id)),
        )
        device_id = r.json()["device_id"]
        super_admin_client.post(v1(f"{_REGISTERED_DEVICES}/{device_id}/revoke"))

        without = super_admin_client.get(v1(_REGISTERED_DEVICES))
        assert without.status_code == 200
        assert len(without.json()) == 0

        with_revoked = super_admin_client.get(
            v1(f"{_REGISTERED_DEVICES}?include_revoked=true")
        )
        assert len(with_revoked.json()) == 1

    def test_non_super_admin_forbidden(
        self, admin_client: TestClient, user_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        payload = _device_payload(str(site.id))
        assert admin_client.post(v1(_REGISTERED_DEVICES), json=payload).status_code == 403
        assert user_client.post(v1(_REGISTERED_DEVICES), json=payload).status_code == 403
        assert admin_client.get(v1(_REGISTERED_DEVICES)).status_code == 403

    def test_create_unknown_site_404(self, super_admin_client: TestClient):
        resp = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(uuid4())),
        )
        assert resp.status_code == 404
        assert "Site" in resp.json()["detail"]


class TestRegisteredDeviceValidation:
    def test_allowlist_unknown_module_key_422(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        resp = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(site.id), allowed_module_keys=["not-a-module"]),
        )
        assert resp.status_code == 422

    def test_allowlist_duplicate_module_key_422(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        resp = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(
                str(site.id),
                allowed_module_keys=[
                    MODULE_KEY_KPI_LIVE_BANNER,
                    MODULE_KEY_KPI_LIVE_BANNER,
                ],
            ),
        )
        assert resp.status_code == 422

    def test_device_type_not_shared_workstation_422(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        resp = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(site.id), device_type="printer"),
        )
        assert resp.status_code == 422

    def test_patch_status_from_revoked_clears_revoked_at(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(site.id)),
        ).json()["device_id"]
        super_admin_client.post(v1(f"{_REGISTERED_DEVICES}/{device_id}/revoke"))
        patch_resp = super_admin_client.patch(
            v1(f"{_REGISTERED_DEVICES}/{device_id}"),
            json={"status": RegisteredDeviceStatus.ACTIVE.value},
        )
        assert patch_resp.status_code == 200
        body = patch_resp.json()
        assert body["status"] == RegisteredDeviceStatus.ACTIVE.value
        assert body["revoked_at"] is None

    def test_revoke_idempotent(
        self, super_admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(site.id)),
        ).json()["device_id"]
        super_admin_client.post(v1(f"{_REGISTERED_DEVICES}/{device_id}/revoke"))
        second = super_admin_client.post(
            v1(f"{_REGISTERED_DEVICES}/{device_id}/revoke")
        )
        assert second.status_code == 200
        assert second.json()["status"] == RegisteredDeviceStatus.REVOKED.value


class TestRegisteredDeviceIdentifierSeparation:
    """device_id (RegisteredDevice) ≠ cash_registers.id ≠ poste_reception.id."""

    def test_device_id_not_accepted_as_cash_register_id(
        self, super_admin_client: TestClient, admin_client: TestClient, db_session: Session
    ):
        site = _make_site(db_session)
        device_id = super_admin_client.post(
            v1(_REGISTERED_DEVICES),
            json=_device_payload(str(site.id)),
        ).json()["device_id"]

        # Route caisse : device_id ne doit pas résoudre un CashRegister
        resp = admin_client.get(v1(f"/cash-registers/{device_id}"))
        assert resp.status_code == 404
        assert "introuvable" in resp.json()["detail"].lower()

        # Preuve table séparée : aucune ligne cash_registers avec cet id
        assert (
            db_session.query(CashRegister)
            .filter(CashRegister.id == UUID(device_id))
            .first()
        ) is None

    def test_device_id_distinct_from_poste_reception_id(
        self,
        super_admin_client: TestClient,
        db_session: Session,
    ):
        site = _make_site(db_session)
        # Utiliser un poste réception existant ou en créer un via la session admin
        poste_id = uuid4()
        opener = db_session.query(User).filter(User.role.isnot(None)).first()
        if opener is None:
            pytest.skip("aucun utilisateur en base pour PosteReception")
        poste = PosteReception(
            id=poste_id,
            opened_by_user_id=opener.id,
            status=PosteReceptionStatus.OPENED.value,
        )
        db_session.add(poste)
        db_session.commit()

        device_id = super_admin_client.post(
            v1(f"{_REGISTERED_DEVICES}/"),
            json=_device_payload(str(site.id)),
        ).json()["device_id"]

        assert device_id != str(poste_id)
        assert (
            db_session.query(RegisteredDevice)
            .filter(RegisteredDevice.id == poste_id)
            .first()
        ) is None
        assert (
            db_session.query(PosteReception)
            .filter(PosteReception.id == UUID(device_id))
            .first()
        ) is None
