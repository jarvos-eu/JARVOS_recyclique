# Story 2.1: Sites — modèle BDD + API CRUD

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'**admin ou développeur**,
je veux une **table `sites` en BDD RecyClique et les endpoints CRUD correspondants**,
afin que **les postes de caisse et les sessions puissent être rattachés à un site**.

## Contexte et prérequis

- **Epic 1 livré** (socle Docker, FastAPI, frontend, health check).
- **Migrations** : Alembic (ou équivalent) doivent être initialisées dans `api/db/`. Si ce n'est pas encore le cas, cette story inclut la mise en place du système de migrations puis la première migration pour `sites`.
- **Règle brownfield** : livrable = migration/copie depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md` (copy + consolidate + security).

## Acceptance Criteria

1. **Étant donné** un environnement RecyClique opérationnel (Epic 1),  
   **Quand** la migration crée la table `sites` avec les colonnes : `id`, `name`, `is_active`, `created_at`, `updated_at`,  
   **Alors** la table existe en BDD PostgreSQL RecyClique avec les types adaptés (UUID ou serial pour id, timestamps avec timezone), contraintes et index cohérents (ex. `idx_sites_is_active` si requêtes par is_active).

2. **Étant donné** la table `sites` créée,  
   **Quand** l'API expose les endpoints suivants,  
   **Alors** ils répondent correctement (codes HTTP, format JSON) :
   - `GET /v1/sites` — liste des sites (filtre optionnel par `is_active`).
   - `GET /v1/sites/{site_id}` — détail d'un site (404 si absent).
   - `POST /v1/sites` — création (body : name, is_active optionnel ; retour 201 + corps du site créé).
   - `PATCH /v1/sites/{site_id}` — mise à jour partielle (name, is_active).
   - `DELETE /v1/sites/{site_id}` — suppression (204 ou 404).

3. **Étant donné** les conventions du projet,  
   **Alors** la structure respecte : BDD **snake_case** (noms de tables et colonnes), index `idx_{table}_{colonne}` si pertinent ; API **pluriel snake_case** pour les segments d'URL ; réponses JSON **snake_case** ; erreurs au format `{ "detail": "..." }` ; dates en **ISO 8601**.

4. **Livrable = migration/copie 1.4.4** : le modèle et les endpoints s'appuient sur les références 1.4.4 (data-models-api, catalogue « qui stocke quoi ») ; pas de conception from scratch.

## Definition of Done

- [x] Migration(s) appliquée(s) sans erreur (table `sites` présente en PostgreSQL).
- [x] Endpoints CRUD listés ci-dessus implémentés et testés (manuellement ou via tests API).
- [x] Conventions snake_case (BDD + API) et format d'erreur respectés.
- [x] Références artefacts 08 (§2.2) et 09 (§3.4) prises en compte ; checklist import 1.4.4 appliquée en cas de copie de code 1.4.4.

## Tasks / Subtasks

- [x] **Task 1** (AC: 1) — Migrations et modèle BDD
  - [x] Initialiser Alembic (ou équivalent) dans `api/db/` si absent.
  - [x] Créer la migration pour la table `sites` (id, name, is_active, created_at, updated_at).
  - [x] Définir le modèle SQLAlchemy (ou équivalent) pour `sites` dans `api/models/` (ou structure en vigueur).
- [x] **Task 2** (AC: 2, 3) — API CRUD
  - [x] Créer le router `api/routers/sites.py` (ou `api/routers/sites/`) et les schemas Pydantic (request/response).
  - [x] Implémenter GET list, GET by id, POST, PATCH, DELETE ; enregistrer le router sous le préfixe `/v1/sites`.
  - [x] Respecter les conventions (snake_case, détail d'erreur, dates ISO 8601).
- [x] **Task 3** (AC: 4, DoD) — Conformité et références
  - [x] Vérifier l'alignement avec `references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md` §2.2 et `references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md` §3.4.
  - [x] En cas de copie depuis 1.4.4 : appliquer `references/ancien-repo/checklist-import-1.4.4.md`.

- **Review Follow-ups (AI)** — à traiter avant passage en done
  - [x] [AI-Review][MEDIUM] Exécuter les migrations en CI/test ou tester contre PostgreSQL ; documenter la limite SQLite si conservée. [api/tests/test_sites.py]
  - [x] [AI-Review][MEDIUM] Déplacer `api/tests/test_sites.py` vers `api/tests/routers/test_sites.py` et aligner structure miroir architecture. [api/tests/]
  - [x] [AI-Review][LOW] Déplacer fixtures communes (db_engine, db_session, client) dans `conftest.py` pour réutilisation. [api/tests/conftest.py, api/tests/test_sites.py]
  - [x] [AI-Review][LOW] PATCH : ne mettre à jour `updated_at` que si au moins un champ (name ou is_active) est fourni et modifié. [api/routers/sites.py]

## Fichiers concernés (indication)

- `api/db/` — migrations (Alembic ou équivalent).
- `api/models/` — modèle Site (ex. `api/models/site.py` ou dans un module `sites`).
- `api/routers/` — router sites (ex. `api/routers/sites.py`).
- `api/schemas/` — schemas Pydantic pour requêtes/réponses sites.
- `api/tests/` — tests API CRUD (ex. `api/tests/routers/test_sites.py` ; structure miroir de `api/routers/` selon architecture).
- Optionnel : `api/services/sites.py` si logique métier extraite du router.
- Référence : `_bmad-output/planning-artifacts/architecture.md` (structure API, conventions).

## Dev Notes

- **Stack** : Python 3.12, FastAPI, PostgreSQL 16 (RecyClique). BDD RecyClique = PostgreSQL uniquement (architecture).
- **Préfixe API** : exposer les routes sous `/v1/sites` (conforme artefact 09 §3.4) ; le montage global (ex. préfixe `/api`) est défini dans `api/main.py`.
- **Source de vérité** : Sites = RecyClique uniquement ; pas de sync vers Paheko pour cette story (artefact 08 §2.2).
- **Tests** : Côté API, pytest + tests des endpoints (status codes, corps JSON). Structure des tests : `api/tests/routers/test_sites.py` (structure miroir). Si `TEST_DATABASE_URL` (postgresql://...) est défini, les migrations Alembic sont exécutées sur cette BDD avant les tests ; sinon SQLite temporaire + create_all (voir conftest.py). Pas d'UI dans cette story.
- **Table des référentiels** (epics.md) : la story 2.1 **livre** le référentiel Sites ; les stories 2.2, 3.4, 5.1 en dépendent.
- **Patterns établis** : pour la structure `api/` (routers, schemas, models, db) et les conventions de nommage, s'appuyer sur `_bmad-output/planning-artifacts/architecture.md` et, si disponible, `_bmad-output/implementation-artifacts/epic-1-retro-2026-02-26.md`.

### Références

- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md §2.2] — Sites et postes (RecyClique, table `sites`).
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md §3.4] — Endpoints Sites (GET/POST/PATCH/DELETE).
- [Source: references/ancien-repo/checklist-import-1.4.4.md] — Copy, Consolidate, Security pour tout import 1.4.4.
- [Source: references/ancien-repo/data-models-api.md] — Modèles de données 1.4.4 (à consulter pour la structure sites).
- [Source: _bmad-output/planning-artifacts/architecture.md] — Structure `api/`, conventions API, BDD snake_case.

## Dev Agent Record

### Agent Model Used

bmad-dev (implementation story 2-1).

### Debug Log References

—

### Completion Notes List

- Alembic initialisé dans `api/db/alembic`, première migration `2026_02_26_001_create_sites_table.py` (table sites, UUID, timestamps TZ, index idx_sites_is_active).
- Modèle `api/models/site.py` (Site), base `api/models/base.py`, schemas `api/schemas/site.py` (SiteCreate, SiteUpdate, SiteResponse).
- Router `api/routers/sites.py` : GET list (filtre is_active), GET by id, POST 201, PATCH, DELETE 204 ; monté sous `/v1/sites` dans `api/main.py`.
- Conventions : snake_case BDD/API/JSON, erreurs `{ "detail": "..." }`, dates ISO 8601.
- Tests : `api/tests/routers/test_sites.py` (12 tests CRUD + format erreur + PATCH sans modification). Fixtures partagées dans `api/tests/conftest.py`. Si `TEST_DATABASE_URL` est défini (PostgreSQL), migrations Alembic exécutées avant les tests ; sinon SQLite + create_all. Conformité catalogue §2.2 et périmètre API §3.4 ; pas de copie 1.4.4 (conception alignée références).
- Fichiers main.py, config/settings.py, db/session.py, routers (auth, pos stubs), admin/health.py complétés ou créés pour faire passer la suite existante (health, modules loader, catch-all).

### File List

- api/requirements.txt (ajout redis)
- api/config/settings.py
- api/db/session.py
- api/db/__init__.py
- api/db/alembic/env.py
- api/db/alembic/versions/2026_02_26_001_create_sites_table.py
- api/models/base.py
- api/models/site.py
- api/models/__init__.py
- api/schemas/site.py
- api/routers/sites.py
- api/routers/auth/router.py
- api/routers/pos/router.py
- api/routers/admin/health.py
- api/main.py
- api/alembic.ini
- api/tests/conftest.py
- api/tests/routers/__init__.py
- api/tests/routers/test_sites.py


## Senior Developer Review (AI)

**Reviewer:** bmad-qa (adversarial code review)  
**Date:** 2026-02-26  
**Outcome:** Approved (2e passage — follow-ups implémentés)

### Git vs Story

- Fichiers du File List présents (nouveaux ou modifiés). Pas de fichier listé sans changement.
- Fichiers _bmad-output/ et __pycache__ exclus de la revue code.

### AC Validation

- **AC1** (table sites, colonnes, types, index) : IMPLEMENTED — migration 2026_02_26_001 et modèle Site conformes.
- **AC2** (endpoints CRUD, codes HTTP, JSON) : IMPLEMENTED — GET list/filter, GET by id 404, POST 201, PATCH, DELETE 204/404.
- **AC3** (conventions snake_case, détail erreur, ISO 8601) : IMPLEMENTED.
- **AC4** (références 1.4.4 / catalogue §2.2, périmètre §3.4) : IMPLEMENTED (alignement sans copie 1.4.4).

### Task Audit

- Toutes les tâches marquées [x] sont réalisées (migrations, modèle, router, schemas, tests, conformité).

### Findings

- **MEDIUM** — **Tests sur SQLite, production PostgreSQL** : Les tests (`api/tests/test_sites.py`) utilisent SQLite (fichier temporaire) et `Base.metadata.create_all(engine)`. La migration Alembic n'est jamais exécutée dans la suite de tests. Comportement UUID et timestamps TZ peut diverger entre SQLite et PostgreSQL. À traiter : exécuter les migrations en test ou cibler PostgreSQL (ex. container de test).
- **MEDIUM** — **Structure des tests** : `architecture.md` impose une structure miroir « tests à la racine de l'API, ex. `tests/routers/test_pos_sessions.py` ». L'implémentation utilise `api/tests/test_sites.py` au lieu de `api/tests/routers/test_sites.py`. Déplacer le fichier et mettre à jour les imports.
- **LOW** — **conftest.py minimal** : Les fixtures (db_engine, db_session, client) sont dans `test_sites.py`. Pour réutilisation (futurs tests de routers), déplacer vers `conftest.py`.
- **LOW** — **Pas d'auth sur /v1/sites** : Conforme au périmètre de la story (auth = Epic 3). À prévoir plus tard.
- **LOW** — **PATCH sans modification** : Un `PATCH` avec body `{}` met quand même à jour `updated_at`. Sémantiquement, ne mettre à jour `updated_at` que si au moins un champ est modifié (optionnel).

### Review Follow-ups (AI)

- [x] [AI-Review][MEDIUM] Exécuter les migrations en CI/test ou tester contre PostgreSQL ; documenter la limite SQLite si conservée. [api/tests/test_sites.py]
- [x] [AI-Review][MEDIUM] Déplacer `api/tests/test_sites.py` vers `api/tests/routers/test_sites.py` et aligner structure miroir architecture. [api/tests/]
- [x] [AI-Review][LOW] Déplacer fixtures communes (db_engine, db_session, client) dans `conftest.py` pour réutilisation. [api/tests/conftest.py, api/tests/test_sites.py]
- [x] [AI-Review][LOW] PATCH : ne mettre à jour `updated_at` que si au moins un champ (name ou is_active) est fourni et modifié. [api/routers/sites.py]

## Change Log

| Date       | Actor   | Change |
|-----------|---------|--------|
| 2026-02-26 | bmad-qa | Code review adversarial : changes requested — 2 MEDIUM (tests SQLite vs PG, structure tests/routers), 2 LOW (conftest, PATCH updated_at). Story status → in-progress, follow-ups ajoutés. |
| 2026-02-26 | bmad-dev | Correctifs review : migrations Alembic en test si TEST_DATABASE_URL ; tests déplacés vers api/tests/routers/test_sites.py ; fixtures dans conftest.py ; PATCH n'actualise updated_at que si champ modifié. Story → review. |
| 2026-02-26 | bmad-qa | Code review 2e passage : vérification des 4 follow-ups OK. Approved. Story status → done, sprint-status 2-1 → done. |
