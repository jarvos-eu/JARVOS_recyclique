# Tests API admin Groupes et Permissions (Story 3.2).
# 403 sans permission, accès OK avec admin, CRUD groupes/permissions, liaisons.

import pytest
from fastapi.testclient import TestClient


class TestAdminRBACAccess:
    """Accès refusé 403 sans permission, accès OK avec permission admin."""

    def test_admin_groups_list_without_auth_returns_401(self, client: TestClient) -> None:
        """Sans token : 401."""
        r = client.get("/v1/admin/groups")
        assert r.status_code == 401

    def test_admin_groups_list_without_admin_permission_returns_403(
        self,
        client: TestClient,
        user_without_admin: tuple,
    ) -> None:
        """Avec token mais sans permission admin : 403."""
        _, token = user_without_admin
        r = client.get("/v1/admin/groups", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403

    def test_admin_groups_list_with_admin_permission_returns_200(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """Avec permission admin : 200 et liste (éventuellement vide)."""
        r = client.get("/v1/admin/groups", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_admin_permissions_list_with_admin_permission_returns_200(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """GET /v1/admin/permissions avec admin : 200."""
        r = client.get("/v1/admin/permissions", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestMePermissions:
    """GET /v1/users/me/permissions."""

    def test_me_permissions_returns_list(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """Utilisateur admin reçoit au moins la permission admin."""
        r = client.get("/v1/users/me/permissions", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert "admin" in data


class TestAdminGroupsCRUD:
    """CRUD groupes avec permission admin."""

    def test_create_and_list_group(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST groupe puis GET liste."""
        r = client.post(
            "/v1/admin/groups",
            headers=auth_headers,
            json={"name": "test_group", "description": "Groupe test"},
        )
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == "test_group"
        group_id = body["id"]

        r2 = client.get("/v1/admin/groups", headers=auth_headers)
        assert r2.status_code == 200
        ids = [g["id"] for g in r2.json()]
        assert group_id in ids

    def test_get_group_detail(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST groupe puis GET /v1/admin/groups/{id} avec permission_ids et user_ids."""
        r = client.post(
            "/v1/admin/groups",
            headers=auth_headers,
            json={"name": "detail_group", "description": ""},
        )
        assert r.status_code == 201
        group_id = r.json()["id"]

        r2 = client.get(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r2.status_code == 200
        data = r2.json()
        assert data["name"] == "detail_group"
        assert "permission_ids" in data
        assert "user_ids" in data

    def test_update_and_delete_group(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """PUT puis DELETE groupe."""
        r = client.post(
            "/v1/admin/groups",
            headers=auth_headers,
            json={"name": "to_update", "description": "Avant"},
        )
        assert r.status_code == 201
        group_id = r.json()["id"]

        r2 = client.put(
            f"/v1/admin/groups/{group_id}",
            headers=auth_headers,
            json={"description": "Après"},
        )
        assert r2.status_code == 200
        assert r2.json()["description"] == "Après"

        r3 = client.delete(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r3.status_code == 204

        r4 = client.get(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r4.status_code == 404


class TestAdminPermissionsCRUD:
    """CRUD permissions avec permission admin."""

    def test_create_and_list_permission(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST permission puis GET liste."""
        r = client.post(
            "/v1/admin/permissions",
            headers=auth_headers,
            json={"code": "test.perm", "label": "Permission test"},
        )
        assert r.status_code == 201
        assert r.json()["code"] == "test.perm"

        r2 = client.get("/v1/admin/permissions", headers=auth_headers)
        assert r2.status_code == 200
        codes = [p["code"] for p in r2.json()]
        assert "test.perm" in codes


class TestAdminGroupLiaisons:
    """POST/DELETE groups/{id}/permissions et groups/{id}/users — vérifier 200/204 et effet sur GET détail."""

    def test_add_and_remove_group_permission_by_id(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST .../groups/{id}/permissions avec permission_id puis DELETE ; GET détail reflète les changements."""
        r_perm = client.get("/v1/admin/permissions", headers=auth_headers)
        assert r_perm.status_code == 200
        perms = r_perm.json()
        assert len(perms) >= 1
        perm_id = perms[0]["id"]

        r_grp = client.post(
            "/v1/admin/groups",
            headers=auth_headers,
            json={"name": "liaison_perm_grp", "description": ""},
        )
        assert r_grp.status_code == 201
        group_id = r_grp.json()["id"]

        r_detail_before = client.get(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r_detail_before.status_code == 200
        assert perm_id not in r_detail_before.json()["permission_ids"]

        r_add = client.post(
            f"/v1/admin/groups/{group_id}/permissions",
            headers=auth_headers,
            json={"permission_id": perm_id},
        )
        assert r_add.status_code == 204

        r_detail_after = client.get(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r_detail_after.status_code == 200
        assert perm_id in r_detail_after.json()["permission_ids"]

        r_del = client.delete(
            f"/v1/admin/groups/{group_id}/permissions/{perm_id}",
            headers=auth_headers,
        )
        assert r_del.status_code == 204

        r_detail_final = client.get(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r_detail_final.status_code == 200
        assert perm_id not in r_detail_final.json()["permission_ids"]

    def test_add_group_permissions_by_ids(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """POST .../groups/{id}/permissions avec permission_ids (liste) ; GET détail contient les ids."""
        r_perm = client.get("/v1/admin/permissions", headers=auth_headers)
        assert r_perm.status_code == 200
        perms = r_perm.json()
        assert len(perms) >= 1
        perm_ids = [p["id"] for p in perms[:2]]  # 1 ou 2 selon seed

        r_grp = client.post(
            "/v1/admin/groups",
            headers=auth_headers,
            json={"name": "liaison_perms_grp", "description": ""},
        )
        assert r_grp.status_code == 201
        group_id = r_grp.json()["id"]

        r_add = client.post(
            f"/v1/admin/groups/{group_id}/permissions",
            headers=auth_headers,
            json={"permission_ids": perm_ids},
        )
        assert r_add.status_code == 204

        r_detail = client.get(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r_detail.status_code == 200
        detail_ids = r_detail.json()["permission_ids"]
        for pid in perm_ids:
            assert pid in detail_ids

    def test_add_and_remove_group_user_by_id(
        self,
        client: TestClient,
        auth_headers: dict,
        admin_user_and_token: tuple,
    ) -> None:
        """POST .../groups/{id}/users avec user_id puis DELETE ; GET détail reflète les changements."""
        user, _ = admin_user_and_token
        user_id = str(user.id)

        r_grp = client.post(
            "/v1/admin/groups",
            headers=auth_headers,
            json={"name": "liaison_user_grp", "description": ""},
        )
        assert r_grp.status_code == 201
        group_id = r_grp.json()["id"]

        r_detail_before = client.get(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r_detail_before.status_code == 200
        assert user_id not in r_detail_before.json()["user_ids"]

        r_add = client.post(
            f"/v1/admin/groups/{group_id}/users",
            headers=auth_headers,
            json={"user_id": user_id},
        )
        assert r_add.status_code == 204

        r_detail_after = client.get(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r_detail_after.status_code == 200
        assert user_id in r_detail_after.json()["user_ids"]

        r_del = client.delete(
            f"/v1/admin/groups/{group_id}/users/{user_id}",
            headers=auth_headers,
        )
        assert r_del.status_code == 204

        r_detail_final = client.get(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r_detail_final.status_code == 200
        assert user_id not in r_detail_final.json()["user_ids"]

    def test_add_group_users_by_ids(
        self,
        client: TestClient,
        auth_headers: dict,
        admin_user_and_token: tuple,
    ) -> None:
        """POST .../groups/{id}/users avec user_ids (liste) ; GET détail contient les ids."""
        user, _ = admin_user_and_token
        user_id = str(user.id)

        r_grp = client.post(
            "/v1/admin/groups",
            headers=auth_headers,
            json={"name": "liaison_users_grp", "description": ""},
        )
        assert r_grp.status_code == 201
        group_id = r_grp.json()["id"]

        r_add = client.post(
            f"/v1/admin/groups/{group_id}/users",
            headers=auth_headers,
            json={"user_ids": [user_id]},
        )
        assert r_add.status_code == 204

        r_detail = client.get(f"/v1/admin/groups/{group_id}", headers=auth_headers)
        assert r_detail.status_code == 200
        assert user_id in r_detail.json()["user_ids"]


class TestHealthUnchanged:
    """Health check inchangé (pas de régression)."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """GET /health sans auth : 200."""
        r = client.get("/health")
        assert r.status_code == 200
