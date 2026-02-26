# Story 2.2: Postes de caisse — modèle BDD + API CRUD

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'**admin ou développeur**,
je veux une **table `cash_registers` et les endpoints CRUD + statut**,
afin de **pouvoir démarrer des sessions de caisse sur des postes identifiés par site**.

## Contexte et prérequis

- **Story 2.1 livrée** : table `sites` existante en BDD RecyClique, endpoints `GET/POST/PATCH/DELETE /v1/sites` opérationnels.
- **Epic 1 livré** (socle Docker, FastAPI, migrations Alembic dans `api/db/`).
- **Règle brownfield** : livrable = migration/copie depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md` (copy + consolidate + security). Référence audit caisse §1.3 Postes.

## Acceptance Criteria

1. **Étant donné** la table `sites` existante,  
   **Quand** la migration crée la table `cash_registers` avec les colonnes : `id`, `site_id` (FK vers `sites.id`), `name`, `location`, `is_active`, `enable_virtual`, `enable_deferred`, `created_at`, `updated_at`,  
   **Alors** la table existe en BDD PostgreSQL RecyClique avec contrainte FK sur `site_id`, types adaptés (UUID ou serial pour id, timestamps avec timezone), et index cohérents (ex. `idx_cash_registers_site_id`, `idx_cash_registers_is_active`).

2. **Étant donné** la table `cash_registers` créée,  
   **Quand** l'API expose les endpoints suivants,  
   **Alors** ils répondent correctement (codes HTTP, format JSON) :
   - `GET /v1/cash-registers` — liste des postes (filtre optionnel par `site_id`, `is_active`).
   - `GET /v1/cash-registers/{register_id}` — détail d'un poste (404 si absent).
   - `GET /v1/cash-registers/status` — statut global (occupé / libre) pour tous les postes (ou par site si spécifié).
   - `POST /v1/cash-registers` — création (body : site_id, name, location optionnel, is_active, enable_virtual, enable_deferred optionnels ; retour 201 + corps du poste créé).
   - `PATCH /v1/cash-registers/{register_id}` — mise à jour partielle (name, location, is_active, enable_virtual, enable_deferred).
   - `DELETE /v1/cash-registers/{register_id}` — suppression (204 ou 404).

3. **Étant donné** les conventions du projet,  
   **Alors** la structure respecte : BDD **snake_case** (noms de tables et colonnes), index `idx_{table}_{colonne}` si pertinent ; API **pluriel snake_case** pour les segments d'URL (`cash-registers`) ; réponses JSON **snake_case** ; erreurs au format `{ "detail": "..." }` ; dates en **ISO 8601**. Le champ `site_id` doit référencer un site existant (validation en création/mise à jour ; 400 ou 404 si site invalide).

4. **Livrable = migration/copie 1.4.4** : le modèle et les endpoints s'appuient sur les références 1.4.4 (audit caisse §1.3 Postes, data-models-api, catalogue « qui stocke quoi ») ; pas de conception from scratch.

## Definition of Done

- [x] Migration(s) appliquée(s) sans erreur (table `cash_registers` présente en PostgreSQL, FK `site_id` → `sites.id`).
- [x] Endpoints CRUD + `GET /v1/cash-registers/status` implémentés et testés (manuellement ou via tests API).
- [x] Conventions snake_case (BDD + API) et format d'erreur respectés ; validation `site_id` existant.
- [x] Références artefacts 08 (§2.2), 09 (§3.8) et audit caisse §1.3 Postes prises en compte ; checklist import 1.4.4 appliquée en cas de copie de code 1.4.4.

## Tasks / Subtasks

- [x] **Task 1** (AC: 1) — Migrations et modèle BDD
  - [x] Créer la migration pour la table `cash_registers` (id, site_id FK, name, location, is_active, enable_virtual, enable_deferred, created_at, updated_at).
  - [x] Définir le modèle SQLAlchemy (ou équivalent) pour `CashRegister` dans `api/models/` avec relation vers `Site`.
- [x] **Task 2** (AC: 2, 3) — API CRUD + status
  - [x] Créer le router `api/routers/cash_registers.py` (ou `api/routers/cash_registers/`) et les schemas Pydantic (request/response).
  - [x] Implémenter GET list (filtres site_id, is_active), GET by id, GET /status, POST 201, PATCH, DELETE 204 ; enregistrer le router sous le préfixe `/v1/cash-registers`.
  - [x] Valider `site_id` à la création et en PATCH (site existant) ; retour 400/404 si invalide.
  - [x] Respecter les conventions (snake_case, détail d'erreur, dates ISO 8601).
- [x] **Task 3** (AC: 4, DoD) — Conformité et références
  - [x] Vérifier l'alignement avec `references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md` §2.2 et `references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md` §3.8.
  - [x] S'appuyer sur `references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md` §1.3 Postes (liste postes, détail, statut global, CRUD).
  - [x] En cas de copie depuis 1.4.4 : appliquer `references/ancien-repo/checklist-import-1.4.4.md`.

## Fichiers concernés (indication)

- `api/db/alembic/versions/` — nouvelle migration pour `cash_registers`.
- `api/models/` — modèle CashRegister (ex. `api/models/cash_register.py`) avec relation vers Site.
- `api/routers/` — router cash_registers (ex. `api/routers/cash_registers.py`).
- `api/schemas/` — schemas Pydantic pour requêtes/réponses cash_registers.
- `api/tests/routers/` — tests API CRUD + status (ex. `api/tests/routers/test_cash_registers.py` ; structure miroir de `api/routers/`).
- Référence : `_bmad-output/planning-artifacts/architecture.md` (structure API, conventions).

## Dev Notes

- **Stack** : Python 3.12, FastAPI, PostgreSQL 16 (RecyClique). BDD RecyClique = PostgreSQL uniquement.
- **Préfixe API** : exposer les routes sous `/v1/cash-registers` (conforme artefact 09 §3.8). Segment URL avec tirets ; corps JSON en snake_case. **Ordre des routes** : déclarer `GET /status` **avant** `GET /{register_id}` pour que FastAPI ne capture pas « status » comme path parameter.
- **Source de vérité** : Postes de caisse = RecyClique uniquement ; pas de sync vers Paheko pour cette story (artefact 08 §2.2). Table des référentiels (epics.md) : la story 2.2 **livre** le référentiel Postes de caisse ; les stories 3.4, 5.1 en dépendent.
- **GET /v1/cash-registers/status** : en v1 peut retourner une liste de postes avec un indicateur « occupé » / « libre » (session ouverte ou non). La table `cash_sessions` sera introduite en Epic 5 ; pour cette story, le statut peut être « libre » pour tous les postes ou une implémentation minimale (champ dérivé vide) pour préparer l'intégration future.
- **Tests** : pytest + tests des endpoints (status codes, corps JSON, validation site_id). Structure : `api/tests/routers/test_cash_registers.py`. Réutiliser les fixtures de `api/tests/conftest.py` (db_engine, db_session, client). Créer au moins un site en fixture pour les tests de création/mise à jour avec `site_id`. Pas d'UI dans cette story.
- **Patterns établis (Story 2.1)** : structure `api/` (routers, schemas, models, db), migrations Alembic, conventions snake_case, erreurs `{ "detail": "..." }`, dates ISO 8601. Tests dans `api/tests/routers/` ; fixtures partagées dans `conftest.py`. PATCH : ne mettre à jour `updated_at` que si au moins un champ est fourni et modifié.

### Références

- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md §2.2] — Sites et postes (RecyClique, tables `sites`, `cash_registers`).
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md §3.8] — Endpoints Postes de caisse (GET list, GET by id, GET status, POST, PATCH, DELETE).
- [Source: references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md §1.3 Postes] — Liste postes, détail, statut global, CRUD ; champs `cash_registers` (id, name, location, site_id, is_active, workflow_options, enable_virtual, enable_deferred).
- [Source: references/ancien-repo/checklist-import-1.4.4.md] — Copy, Consolidate, Security pour tout import 1.4.4.
- [Source: references/ancien-repo/data-models-api.md] — Modèles de données 1.4.4 (à consulter pour la structure cash_registers).
- [Source: references/ancien-repo/fonctionnalites-actuelles.md §3.3] — Postes de caisse (liste, CRUD).
- [Source: _bmad-output/planning-artifacts/architecture.md] — Structure `api/`, conventions API, BDD snake_case.
- [Source: _bmad-output/implementation-artifacts/2-1-sites-modele-bdd-api-crud.md] — Patterns Story 2.1 (modèle Site, router sites, tests routers, conftest).

## Dev Agent Record

### Agent Model Used

bmad-dev (implementation story 2-2).

### Debug Log References

—
### Completion Notes List

- Migration `api/db/alembic/versions/2026_02_26_002_create_cash_registers_table.py` : table `cash_registers` avec id (UUID), site_id (FK vers sites.id CASCADE), name, location, is_active, enable_virtual, enable_deferred, created_at, updated_at ; index idx_cash_registers_site_id, idx_cash_registers_is_active.
- Modele `api/models/cash_register.py` (CashRegister) avec relation vers Site ; `api/models/site.py` mis a jour avec relation inverse cash_registers.
- Schemas `api/schemas/cash_register.py` : CashRegisterCreate, CashRegisterUpdate, CashRegisterResponse, CashRegisterStatusItem.
- Router `api/routers/cash_registers.py` : GET list (filtres site_id, is_active), GET /status (avant GET /{id}), GET /{id}, POST 201 (validation site existant 404), PATCH, DELETE 204 ; monte sous /v1 dans `api/main.py`.
- Conventions : snake_case BDD/API/JSON, erreurs `{ "detail": "..." }`, dates ISO 8601. PATCH n'actualise updated_at que si au moins un champ modifie.
- Tests `api/tests/routers/test_cash_registers.py` (17 tests) : list vide/filtres, status vide/avec postes/filtre site_id, get 404, create 201 + site not found 404, get after create, list returns created, patch / patch empty body / patch 404, delete 204 / delete 404, format erreur. Fixtures conftest reutilisees ; creation de site via API pour les tests avec site_id.

### File List

- api/db/alembic/versions/2026_02_26_002_create_cash_registers_table.py
- api/models/cash_register.py
- api/models/site.py
- api/models/__init__.py
- api/schemas/cash_register.py
- api/routers/cash_registers.py
- api/main.py
- api/tests/routers/test_cash_registers.py

## Senior Developer Review (AI)

**Date :** 2026-02-26  
**Résultat :** Approved  
**Git vs File List :** Fichiers story non commités (nouveaux) — cohérent avec livrable story 2-2.

- **AC 1–4 :** Implémentés (migration, CRUD, status, conventions, validation site_id, références 1.4.4).
- **Tasks [x] :** Toutes vérifiées (preuve dans les fichiers listés).
- **Tests :** 17 tests réels (list, filtres, status, 404, create 201, PATCH updated_at, DELETE 204/404, format erreur).
- **Améliorations optionnelles (LOW) :** ordre non spécifié sur GET list et GET /status ; `CashRegisterStatusItem.status` en `Literal["free","occupied"]` ; ajout optionnel de `site_id` dans l'item status pour éviter un aller-retour client.

## Change Log

| Date       | Actor   | Change |
|------------|---------|--------|
| 2026-02-26 | bmad-dev | Story 2-2 implementee : migration cash_registers, modele CashRegister, router CRUD + GET /status, schemas, tests (17). Statut review, sprint-status 2-2 -> review. |
| 2026-02-26 | bmad-qa | Code review adversarial : approved. Tous les AC et tasks verifies ; 0 HIGH/MEDIUM. Ameliorations optionnelles LOW documentees (ordre list/status, Literal status, site_id dans status item). Statut -> done, sprint-status 2-2 -> done. |
