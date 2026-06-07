"""Tests Story 9.13 — module-config comptage-pieces-billets."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from recyclic_api.core.config import settings
from recyclic_api.core.security import create_access_token, hash_password
from recyclic_api.models.site import Site
from recyclic_api.models.site_module_config import SiteModuleConfig
from recyclic_api.models.user import User, UserRole, UserStatus
from recyclic_api.modules.module_config.registry import (
    MODULE_KEY_COMPTAGE_PIECES_BILLETS,
    SCHEMA_VERSION_COMPTAGE_PIECES_BILLETS_V1,
)
from recyclic_api.modules.module_config.service import COMPTAGE_PIECES_BILLETS_DEFAULT_PAYLOAD
from recyclic_api.services.cash_denomination_service import (
    is_comptage_module_required,
    resolve_comptage_module_payload,
)
from tests.caisse_sale_eligibility import grant_user_caisse_sale_eligibility

_V1 = settings.API_V1_STR.rstrip("/")
_MODULE_KEY = MODULE_KEY_COMPTAGE_PIECES_BILLETS
_DEFAULT_PAYLOAD = dict(COMPTAGE_PIECES_BILLETS_DEFAULT_PAYLOAD)
_PILOT_PAYLOAD = {
    "enabled": True,
    "skip_allowed": False,
    "require_denomination_grid": True,
    "show_images": True,
}


def _url(site_id: uuid.UUID, module_key: str = _MODULE_KEY) -> str:
    return f"{_V1}/sites/{site_id}/module-config/{module_key}"


def _admin_for_site(db_session: Session, site: Site) -> tuple[User, str]:
    uid = uuid.uuid4()
    admin = User(
        id=uid,
        username=f"adm_cpt_{uid.hex[:8]}@test.com",
        hashed_password=hash_password("pw"),
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        legacy_external_contact_id=f"leg_{uid.hex[:12]}",
        site_id=site.id,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    token = create_access_token(data={"sub": str(admin.id)})
    return admin, token


def test_get_default_comptage_200(client: TestClient, db_session: Session):
    site = Site(id=uuid.uuid4(), name="Site comptage default", is_active=True)
    db_session.add(site)
    db_session.commit()
    _, token = _admin_for_site(db_session, site)

    r = client.get(_url(site.id), headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["schema_version"] == SCHEMA_VERSION_COMPTAGE_PIECES_BILLETS_V1
    assert body["payload"] == _DEFAULT_PAYLOAD
    assert body.get("version") == 0


def test_patch_pilot_payload_then_get_reflects_200(client: TestClient, db_session: Session):
    site = Site(id=uuid.uuid4(), name="Site comptage pilot", is_active=True)
    db_session.add(site)
    db_session.commit()
    _, token = _admin_for_site(db_session, site)

    patch_body = {
        "schema_version": SCHEMA_VERSION_COMPTAGE_PIECES_BILLETS_V1,
        "payload": _PILOT_PAYLOAD,
    }
    r_patch = client.patch(
        _url(site.id),
        json=patch_body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_patch.status_code == 200, r_patch.text
    assert r_patch.json()["payload"] == _PILOT_PAYLOAD

    r_get = client.get(_url(site.id), headers={"Authorization": f"Bearer {token}"})
    assert r_get.status_code == 200
    assert r_get.json()["payload"] == _PILOT_PAYLOAD


def test_get_unknown_module_key_still_404(client: TestClient, db_session: Session):
    site = Site(id=uuid.uuid4(), name="Site unknown mod", is_active=True)
    db_session.add(site)
    db_session.commit()
    _, token = _admin_for_site(db_session, site)

    r = client.get(
        _url(site.id, "cashflow"),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


def test_get_comptage_operational_read_user_with_caisse_access_200(
    client: TestClient, db_session: Session
):
    site = Site(id=uuid.uuid4(), name="Site caisse op", is_active=True)
    db_session.add(site)
    db_session.commit()

    uid = uuid.uuid4()
    operator = User(
        id=uid,
        username=f"op_cpt_{uid.hex[:8]}@test.com",
        hashed_password=hash_password("pw"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        legacy_external_contact_id=f"leg_{uid.hex[:12]}",
        site_id=site.id,
    )
    db_session.add(operator)
    db_session.commit()
    grant_user_caisse_sale_eligibility(db_session, operator, site.id)
    token = create_access_token(data={"sub": str(operator.id)})

    r = client.get(_url(site.id), headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    assert r.json()["payload"] == _DEFAULT_PAYLOAD


def test_get_comptage_operational_read_user_without_caisse_access_403(
    client: TestClient, db_session: Session
):
    site = Site(id=uuid.uuid4(), name="Site caisse denied", is_active=True)
    db_session.add(site)
    db_session.commit()

    uid = uuid.uuid4()
    operator = User(
        id=uid,
        username=f"op_denied_{uid.hex[:8]}@test.com",
        hashed_password=hash_password("pw"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        legacy_external_contact_id=f"leg_{uid.hex[:12]}",
        site_id=site.id,
    )
    db_session.add(operator)
    db_session.commit()
    token = create_access_token(data={"sub": str(operator.id)})

    r = client.get(_url(site.id), headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_get_wrong_site_idor_403(client: TestClient, db_session: Session):
    site_a = Site(id=uuid.uuid4(), name="Site A cpt", is_active=True)
    site_b = Site(id=uuid.uuid4(), name="Site B cpt", is_active=True)
    db_session.add_all([site_a, site_b])
    db_session.commit()
    _, token = _admin_for_site(db_session, site_a)

    r = client.get(_url(site_b.id), headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_patch_invalid_payload_missing_field_422(client: TestClient, db_session: Session):
    site = Site(id=uuid.uuid4(), name="Site invalid payload", is_active=True)
    db_session.add(site)
    db_session.commit()
    _, token = _admin_for_site(db_session, site)

    body = {
        "schema_version": SCHEMA_VERSION_COMPTAGE_PIECES_BILLETS_V1,
        "payload": {"enabled": True},
    }
    r = client.patch(
        _url(site.id),
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422


def test_patch_invalid_payload_unknown_property_422(client: TestClient, db_session: Session):
    site = Site(id=uuid.uuid4(), name="Site extra prop", is_active=True)
    db_session.add(site)
    db_session.commit()
    _, token = _admin_for_site(db_session, site)

    body = {
        "schema_version": SCHEMA_VERSION_COMPTAGE_PIECES_BILLETS_V1,
        "payload": {**_DEFAULT_PAYLOAD, "extra_field": True},
    }
    r = client.patch(
        _url(site.id),
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422


def test_resolver_defaults_off_and_pilot_on(db_session: Session):
    site = Site(id=uuid.uuid4(), name="Resolver site", is_active=True)
    db_session.add(site)
    db_session.commit()

    assert resolve_comptage_module_payload(db_session, site.id) == _DEFAULT_PAYLOAD
    assert is_comptage_module_required(db_session, site.id) is False

    db_session.add(
        SiteModuleConfig(
            site_id=site.id,
            module_key=_MODULE_KEY,
            schema_version=SCHEMA_VERSION_COMPTAGE_PIECES_BILLETS_V1,
            payload=_PILOT_PAYLOAD,
            version=1,
        )
    )
    db_session.commit()

    assert resolve_comptage_module_payload(db_session, site.id) == _PILOT_PAYLOAD
    assert is_comptage_module_required(db_session, site.id) is True


def test_resolver_falls_back_to_defaults_on_corrupt_payload(db_session: Session):
    site = Site(id=uuid.uuid4(), name="Corrupt payload site", is_active=True)
    db_session.add(site)
    db_session.add(
        SiteModuleConfig(
            site_id=site.id,
            module_key=_MODULE_KEY,
            schema_version=SCHEMA_VERSION_COMPTAGE_PIECES_BILLETS_V1,
            payload="not-a-dict",  # type: ignore[arg-type]
            version=1,
        )
    )
    db_session.commit()

    assert resolve_comptage_module_payload(db_session, site.id) == _DEFAULT_PAYLOAD
    assert is_comptage_module_required(db_session, site.id) is False
