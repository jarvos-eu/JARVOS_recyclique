# Story 3.2: Groupes, permissions et RBAC

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'**admin**,
je veux **pouvoir assigner des rôles et des permissions aux utilisateurs via des groupes**,
afin **de contrôler l'accès aux différentes fonctionnalités de l'application**.

## Acceptance Criteria

1. **Étant donné** les tables `groups`, `permissions`, `user_groups`, `group_permissions` créées par migration  
   **Quand** un utilisateur possède les permissions requises et envoie son JWT  
   **Alors** le middleware (ou dépendance) API valide le token **et** les permissions avant d'accéder à la ressource.

2. **Étant donné** un admin authentifié  
   **Quand** j'accède aux endpoints d'admin groupes et permissions  
   **Alors** les endpoints fonctionnent : `GET/POST/PUT/DELETE /v1/admin/groups`, `GET/POST/PUT/DELETE /v1/admin/permissions` ; liaisons groupe–permissions et groupe–utilisateurs (`POST/DELETE /v1/admin/groups/{group_id}/permissions`, `POST/DELETE /v1/admin/groups/{group_id}/users`).

3. **Étant donné** la matrice RBAC du PRD  
   **Quand** le système est en place  
   **Alors** les rôles suivants sont couverts via groupes/permissions : opérateur caisse, opérateur réception, responsable compta/admin, admin technique, bénévole ; permissions métier (ex. `caisse.access`, `caisse.virtual.access`, `caisse.deferred.access`, `reception.access`, admin) sont implémentées et vérifiées côté API.

4. **Étant donné** le périmètre v1  
   **Quand** le livrable est livré  
   **Alors** il correspond à la migration/copie 1.4.4 (artefact 08 §2.1, artefact 09, artefact 10 §7.11).

## Tasks / Subtasks

- [x] Task 1 : Migrations BDD groupes et permissions (AC: 1, 4)
  - [x] Créer migration Alembic : tables `groups`, `permissions`, `user_groups`, `group_permissions` (snake_case, index idx_* selon conventions).
  - [x] Aligner schéma sur 1.4.4 et `references/ancien-repo/checklist-import-1.4.4.md` (copy + consolidate + security).
- [x] Task 2 : Middleware / dépendance « permission requise » (AC: 1, 3)
  - [x] Étendre `api/core/deps.py` : dépendance `require_permissions(*perms)` qui, après validation JWT (get_current_user), vérifie que l'utilisateur a **au moins une** des permissions listées (OR) via ses groupes ; 403 si aucune permission requise.
  - [x] Exposer `GET /v1/users/me/permissions` pour le front (liste des permissions de l'utilisateur connecté).
  - [x] Appliquer la dépendance sur les routes **/v1/admin/\*** (ex. `admin` ou `admin.groups`, `admin.permissions` selon convention) et sur les routes caisse/réception selon la matrice RBAC (PRD § Rôles et permissions).
- [x] Task 3 : API admin groupes (AC: 2)
  - [x] `GET /v1/admin/groups` — liste groupes.
  - [x] `GET /v1/admin/groups/{group_id}` — détail (permissions, utilisateurs).
  - [x] `POST /v1/admin/groups`, `PUT /v1/admin/groups/{group_id}`, `DELETE /v1/admin/groups/{group_id}`.
  - [x] `POST /v1/admin/groups/{group_id}/permissions` (body : permission_id ou liste), `DELETE /v1/admin/groups/{group_id}/permissions/{permission_id}`.
  - [x] `POST /v1/admin/groups/{group_id}/users` (body : user_id ou liste), `DELETE /v1/admin/groups/{group_id}/users/{user_id}`.
- [x] Task 4 : API admin permissions (AC: 2)
  - [x] `GET /v1/admin/permissions` — liste des permissions (codes et libellés).
  - [x] `POST /v1/admin/permissions`, `PUT /v1/admin/permissions/{permission_id}`, `DELETE /v1/admin/permissions/{permission_id}` (avec prudence : ne pas casser les liaisons existantes).
- [x] Task 5 : Graine de permissions et groupes (AC: 3)
  - [x] Créer les permissions de base (caisse.access, caisse.virtual.access, caisse.deferred.access, reception.access, admin, etc.) et les groupes correspondant aux rôles PRD (opérateur caisse, opérateur réception, responsable compta/admin, admin technique, bénévole) avec liaisons groupe–permissions ; par migration Alembic (données initiales) ou script de seed exécutable après migration, selon convention projet.
- [x] Task 6 : Tests et santé (AC: 1–4)
  - [x] Tests API (pytest) : accès refusé 403 sans permission ; accès OK avec permission ; CRUD groupes/permissions ; liaison groupe–utilisateurs et groupe–permissions.
  - [x] Vérifier que les routes auth/users existantes (story 3.1) ne régressent pas ; health check inchangé.

- [x] **Review Follow-ups (AI)**
  - [x] [AI-Review][HIGH] Appliquer require_permissions sur les routes caisse/réception selon matrice RBAC : /v1/sites, /v1/cash-registers, /v1/categories, /v1/presets (ex. caisse.access ou reception.access selon endpoint). Actuellement seule /v1/admin/* est protégée. [AC3, Task 2]
  - [x] [AI-Review][HIGH] Ajouter tests pytest pour les liaisons : POST/DELETE /v1/admin/groups/{id}/permissions et POST/DELETE /v1/admin/groups/{id}/users (vérifier 200/204 et effet sur GET détail). [Task 6]
  - [x] [AI-Review][MEDIUM] Déclarer response_model=list[str] sur GET /v1/users/me/permissions (api/routers/v1/users.py). [cohérence API]
  - [x] [AI-Review][MEDIUM] Documenter dans la story ou le code la décision CASCADE sur suppression permission (liaisons group_permissions supprimées) vs « ne pas casser les liaisons » (story Task 4). [doc]
  - [x] [AI-Review][LOW] Aligner File List / commits : nombreux fichiers 3.2 en untracked ; un commit dédié 3.2 ou mise à jour File List si périmètre différent. [transparence]

## Dev Notes

- **Autorisation (architecture)** : RBAC selon matrice PRD (opérateur caisse, opérateur réception, responsable compta/admin, admin technique, bénévole) ; mode caisse verrouillé (menu caisse seul) est traité en story 3.5 ; ici on livre le **modèle** groupes/permissions et la **vérification** permission sur chaque route protégée. [Source: _bmad-output/planning-artifacts/architecture.md § Authentication & Security]
- **Réutilisation story 3.1** : `get_current_user` dans `api/core/deps.py` ; JWT déjà validé. Ajouter une dépendance `require_permissions(*permission_codes)` qui charge les groupes de l'utilisateur, déduit les permissions, et lève 403 si aucune permission requise n'est présente. Ne pas dupliquer la logique JWT.
- **Routes admin v1** : Groupes et permissions exposés sous **/v1/admin/** (router monté dans `api/routers/v1/` avec prefix `/v1`, routes sous `admin/`). Ne pas utiliser le router existant `/api/admin` (legacy) — voir `api/main.py`.
- **Source de vérité** : Groupes et permissions en RecyClique uniquement (tables `groups`, `permissions`, `user_groups`, `group_permissions`) ; pas de sync vers Paheko. [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md §2.1]
- **Règle brownfield** : Livrable = migration/copie 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md`. Références : artefact 08 §2.1, artefact 09 §3.2/3.3, artefact 10 §7.11 (Groupes, Permissions).
- **Endpoints existants 1.4.4** : `GET/POST/PUT/DELETE /v1/admin/groups`, `.../permissions` ; liaisons groupe–permissions et groupe–utilisateurs. [Source: references/ancien-repo/fonctionnalites-actuelles.md, references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md §7.11]
- **Suppression permission (CASCADE)** : La migration 001 définit `ON DELETE CASCADE` sur la FK `group_permissions.permission_id`. Supprimer une permission supprime donc automatiquement les entrées de la table d'association ; les groupes ne sont pas modifiés. Documenté dans le docstring de `DELETE /v1/admin/permissions/{id}` (api/routers/v1/admin/permissions.py).
- **Matrice RBAC PRD** : Opérateur caisse (caisse oui, réception non, compta non, admin technique non, vie asso non) ; Opérateur réception (réception oui, reste non) ; Responsable compta/admin (déverrouillage/accès selon config, compta oui v1 via Paheko) ; Admin technique (admin technique oui) ; Bénévole (vie asso oui). [Source: _bmad-output/planning-artifacts/prd.md § Rôles et permissions (matrice RBAC)]
- **Permissions caisse** : `caisse.access`, `caisse.virtual.access`, `caisse.deferred.access` (audit caisse 1.4.4). Réception : `reception.access`. Admin : permission(s) admin ou super-admin selon convention. [Source: references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md, artefact 10]

### Project Structure Notes

- **Backend** : Nouveaux modèles dans `api/models/` (group.py, permission.py, tables association) ; routers **admin** dans `api/routers/v1/` (ex. `admin.py` ou `admin/groups.py`, `admin/permissions.py`) montés sous préfixe `/v1` avec routes `admin/` → URLs `/v1/admin/groups`, `/v1/admin/permissions`. Dépendance permission dans `api/core/deps.py`.
- **Frontend** : Écrans admin Groupes et Permissions (liste, détail, formulaires CRUD) selon artefact 10 §7.11 — routes `/admin/groups`, `/admin/permissions`. Peut être livré en API seule dans cette story avec placeholders frontend ou écrans minimaux selon décision ; détail des écrans complets en Epic 8 (story 8.1).
- **Tests** : API = `api/tests/routers/test_admin_groups.py`, `test_admin_permissions.py` (ou un seul fichier test admin RBAC), réutiliser `conftest.py` (client, db_session) comme en story 3.1. Frontend = tests co-locés `*.test.tsx` si composants ajoutés.

### References

- [Source: _bmad-output/planning-artifacts/epics.md] Epic 3, Story 3.2, FR4, FR5, FR14, FR15, FR16
- [Source: _bmad-output/planning-artifacts/architecture.md] Authentication & Security, RBAC, api/core/deps.py
- [Source: _bmad-output/planning-artifacts/prd.md] § Rôles et permissions (matrice RBAC)
- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md] §2.1 Utilisateurs et rôles, Groupes et permissions
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md] §3.2 Authentification, §3.3 Utilisateurs
- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md] §7.11 Groupes et Permissions
- [Source: references/ancien-repo/checklist-import-1.4.4.md] Copy + consolidate + security
- [Source: references/ancien-repo/data-models-api.md] Permission, Group, user_groups, group_permissions
- [Source: references/ancien-repo/fonctionnalites-actuelles.md] Groupes et permissions, GET /v1/users/me/permissions
- [Source: _bmad-output/implementation-artifacts/3-1-users-jwt-et-gestion-de-compte-terrain.md] get_current_user, structure auth, deps.py

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Task 1 : Alembic initialisé (alembic.ini à la racine, api/alembic/env.py, script.py.mako). Migration 001 crée tables groups, permissions, user_groups, group_permissions (PostgreSQL UUID, index idx_*). Modèles Group, Permission, tables association dans api/models/group.py et permission.py ; User.groups ajouté.
- Task 2 : require_permissions(*permission_codes) dans deps.py (OR des permissions via groupes) ; GET /v1/users/me/permissions dans users router ; routes /v1/admin/* protégées par require_permissions(\"admin\").
- Task 3 : Router admin groupes (api/routers/v1/admin/groups.py) : CRUD + POST/DELETE group_id/permissions et group_id/users. Monté sous /v1/admin.
- Task 4 : Router admin permissions (api/routers/v1/admin/permissions.py) : CRUD complet.
- Task 5 : Migration 002 seed : permissions (caisse.access, caisse.virtual.access, caisse.deferred.access, reception.access, admin, vie_asso.access) et groupes (operateur_caisse, operateur_reception, responsable_compta_admin, admin_technique, benevole) avec liaisons.
- Task 6 : Tests pytest dans api/tests/routers/test_admin_rbac.py (10 tests) : 401/403 sans auth/admin, 200 avec admin, CRUD groupes/permissions, GET /me/permissions, health inchangé. conftest avec client, db_session, auth_headers (SQLite fichier pour partage connexions). Corrections review : tests liaisons POST/DELETE groups/{id}/permissions et groups/{id}/users (body permission_id/permission_ids, user_id/user_ids) ; protection routes caisse/réception → tests Epic 2 (sites, cash_registers, categories, presets) mis à jour avec auth_headers. **Review follow-ups** : routes /v1/sites, /v1/cash-registers, /v1/categories, /v1/presets déjà protégées par require_permissions (admin ou caisse.access/reception.access). Tests liaisons groupe-permissions et groupe-users dans TestAdminGroupLiaisons. GET /me/permissions a response_model=list[str]. CASCADE sur suppression permission documenté dans delete_permission (api/routers/v1/admin/permissions.py).

### File List

- alembic.ini
- api/alembic/env.py
- api/alembic/script.py.mako
- api/alembic/versions/2026_02_27_001_groups_permissions_rbac.py
- api/alembic/versions/2026_02_27_002_seed_permissions_groups.py
- api/core/deps.py
- api/main.py
- api/models/__init__.py
- api/models/group.py
- api/models/permission.py
- api/models/user.py
- api/routers/v1/__init__.py
- api/routers/v1/admin/__init__.py
- api/routers/v1/admin/groups.py
- api/routers/v1/admin/permissions.py
- api/routers/v1/users.py
- api/routers/sites.py
- api/routers/cash_registers.py
- api/routers/categories.py
- api/routers/presets.py
- api/schemas/group.py
- api/schemas/permission.py
- api/services/permissions.py
- api/tests/__init__.py
- api/tests/conftest.py
- api/tests/routers/__init__.py
- api/tests/routers/test_admin_rbac.py
- api/tests/routers/test_sites.py
- api/tests/routers/test_cash_registers.py
- api/tests/routers/test_categories.py
- api/tests/routers/test_presets.py
- .gitignore

## Senior Developer Review (AI)

**Date:** 2026-02-27  
**Résultat:** Changes requested

### Git vs Story
- Fichiers de la story : File List ci-dessous aligné avec les fichiers créés/modifiés pour la story 3.2 (y compris corrections review). Commit dédié 3.2 recommandé pour traçabilité.

### Problèmes identifiés

| Sévérité | Description |
|----------|-------------|
| **HIGH** | Routes caisse/réception non protégées par `require_permissions` : /v1/sites, /v1/cash-registers, /v1/categories, /v1/presets sont accessibles sans permission. AC3 et Task 2 demandent d'appliquer la dépendance « sur les routes caisse/réception selon la matrice RBAC ». |
| **HIGH** | Tests des liaisons groupe–permissions et groupe–users manquants : pas de test pour POST/DELETE `.../groups/{id}/permissions` ni POST/DELETE `.../groups/{id}/users`. |
| **MEDIUM** | GET /v1/users/me/permissions sans `response_model=list[str]`. |
| **MEDIUM** | Suppression d'une permission supprime les liaisons (CASCADE) ; la story mentionnait « avec prudence : ne pas casser les liaisons » — à documenter ou adapter. |
| **LOW** | Alignement File List / historique git (commit dédié ou précision du périmètre). |

### Points validés
- Migrations 001 et 002 présentes et conformes (tables, index, seed permissions/groupes).
- `require_permissions` et `get_user_permission_codes_from_user` corrects ; routes /v1/admin/* protégées par `require_permissions("admin")`.
- CRUD groupes et permissions implémenté ; endpoints liaisons présents et fonctionnels.
- GET /v1/users/me/permissions implémenté ; health inchangé.
- Tests 401/403/200, CRUD groupes et permissions, GET /me/permissions, health présents.

---

**Date (second passage):** 2026-02-27  
**Résultat:** Approved

### Vérification des corrections
- **HIGH (protection routes)** : Confirmé. `sites.py` (require_permissions admin), `cash_registers.py` (caisse.access | admin pour GET, admin pour write), `categories.py` (caisse.access | reception.access | admin pour GET, admin pour write), `presets.py` (caisse.access | admin pour GET, admin pour write).
- **HIGH (tests liaisons)** : Confirmé. `TestAdminGroupLiaisons` : test_add_and_remove_group_permission_by_id, test_add_group_permissions_by_ids, test_add_and_remove_group_user_by_id, test_add_group_users_by_ids — POST/DELETE groups/{id}/permissions et groups/{id}/users avec 200/204 et effet sur GET détail.
- **MEDIUM (response_model)** : Confirmé. GET /v1/users/me/permissions a `response_model=list[str]` (users.py L25).
- **MEDIUM (CASCADE)** : Confirmé. Docstring delete_permission dans permissions.py : « suppression (liaisons group_permissions en CASCADE) ».
- **LOW** : Reste ouvert (alignement File List / commits) — non bloquant.

## Change Log

| Date       | Événement              | Détail |
|------------|------------------------|--------|
| 2026-02-27 | Code review (AI)       | Changes requested : protection routes caisse/réception, tests liaisons, petits points MEDIUM/LOW. Status → in-progress. |
| 2026-02-27 | Corrections review     | Require_permissions sur /v1/sites (admin), /v1/cash-registers (GET caisse.access\|admin, write admin), /v1/categories (GET caisse.access\|reception.access\|admin, write admin), /v1/presets (GET caisse.access\|admin, write admin). Tests liaisons groupe-permissions et groupe-users. response_model=list[str] sur GET /me/permissions. CASCADE documenté (story + permissions router). File List aligné. Review Follow-ups cochés. |
| 2026-02-27 | Code review (AI) 2e passage | Approved. Corrections HIGH/MEDIUM vérifiées en place. Status → done. Sprint 3-2 → done. |
