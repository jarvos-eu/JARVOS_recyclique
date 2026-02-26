# Story 2.3: Catégories — modèle BDD + API CRUD, hiérarchie et visibilité

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'admin ou développeur,
je veux une table `categories` avec hiérarchie parent/enfant et indicateurs de visibilité (caisse/réception),
afin que les lignes de vente et de réception puissent référencer des catégories métier.

## Acceptance Criteria

1. **Étant donné** un environnement RecyClique opérationnel (Epic 1)
   **Quand** la migration crée la table `categories` (id, name, parent_id nullable, official_name, is_visible_sale, is_visible_reception, display_order, display_order_entry, deleted_at)
   **Alors** les endpoints de base fonctionnent : `GET /v1/categories`, `GET /v1/categories/hierarchy`, `GET /v1/categories/{id}`, `POST /v1/categories`, `PUT /v1/categories/{id}`, `DELETE /v1/categories/{id}` (soft delete), `POST /v1/categories/{id}/restore`, `GET /v1/categories/sale-tickets`, `GET /v1/categories/entry-tickets`, `PUT /v1/categories/{id}/visibility`, `PUT /v1/categories/{id}/display-order`
   **Et** la hiérarchie (parent_id auto-référentielle) est requêtable ; livrable = migration/copie 1.4.4 (artefact 08 §2.5, artefact 09 §3.9).

2. **Étant donné** des catégories existantes avec parent_id et indicateurs de visibilité
   **Quand** on appelle `GET /v1/categories/sale-tickets` (resp. `entry-tickets`)
   **Alors** seules les catégories avec `is_visible_sale=true` (resp. `is_visible_reception=true`) et non supprimées sont retournées, avec ordre cohérent (display_order / display_order_entry).

3. **Étant donné** une catégorie existante
   **Quand** on appelle `PUT /v1/categories/{id}/visibility` avec `is_visible_sale` et/ou `is_visible_reception`
   **Alors** les indicateurs sont mis à jour ; `PUT /v1/categories/{id}/display-order` met à jour l'ordre d'affichage.

4. **Étant donné** une catégorie avec des enfants ou des usages (lignes vente/réception)
   **Quand** on demande un soft delete
   **Alors** la catégorie est marquée deleted_at ; la restauration via `POST /v1/categories/{id}/restore` remet deleted_at à null. Les contraintes métier (usage éventuel) sont respectées selon la règle 1.4.4.

## Tasks / Subtasks

- [x] Task 1 : Migration et modèle BDD (AC: 1)
  - [x] Créer migration Alembic pour table `categories` : id, name, parent_id (FK self nullable), official_name, is_visible_sale, is_visible_reception, display_order, display_order_entry, deleted_at, created_at, updated_at
  - [x] Index : idx_categories_parent_id, idx_categories_deleted_at, idx_categories_is_visible_sale, idx_categories_is_visible_reception
  - [x] Modèle SQLAlchemy Category avec relation self parent/children
- [x] Task 2 : Schémas Pydantic et router CRUD de base (AC: 1)
  - [x] Schemas : CategoryCreate, CategoryUpdate, CategoryResponse, CategoryHierarchyNode
  - [x] GET /v1/categories (liste, filtres optionnels), GET /v1/categories/hierarchy, GET /v1/categories/{id}
  - [x] POST /v1/categories, PUT /v1/categories/{id}, DELETE /v1/categories/{id} (soft), POST /v1/categories/{id}/restore
- [x] Task 3 : Endpoints visibilité et ordre (AC: 2, 3)
  - [x] GET /v1/categories/sale-tickets, GET /v1/categories/entry-tickets (filtrés par visibilité, tri)
  - [x] PUT /v1/categories/{id}/visibility, PUT /v1/categories/{id}/display-order
- [x] Task 4 : Règles métier et tests (AC: 4)
  - [x] Soft delete et restore cohérents avec 1.4.4 ; tests unitaires API (pytest) pour les endpoints critiques

## Dev Notes

- **Règle brownfield** : livrable = migration/copie depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md`. Références obligatoires : artefact 08 §2.5 (catalogue qui stocke quoi — catégories), artefact 09 §3.9 (périmètre API catégories), `references/ancien-repo/data-models-api.md` (modèle Category, hiérarchie). Pour le soft delete et restore (AC4), appliquer la règle 1.4.4 = copy + consolidate + security (checklist-import) ; contraintes métier sur usages (lignes vente/réception) selon data-models-api.md et artefact 09.
- **Hors périmètre cette story** : import/export CSV des catégories → reporté Epic 8 (Story 8.3). Ne pas implémenter `GET /v1/categories/import/template`, `POST /v1/categories/import/analyze`, `POST /v1/categories/import/execute`, `GET /v1/categories/actions/export` ni endpoints `breadcrumb`, `children`, `parent`, `has-usage`, `hard` sauf si présents en 1.4.4 et nécessaires pour le CRUD minimal décrit ci-dessus ; privilégier le périmètre explicite des AC.
- **Conventions** : BDD snake_case (tables pluriel, index idx_{table}_{colonne}). API : endpoints pluriel snake_case, erreur `{ "detail": "..." }`, dates ISO 8601. Router dans `api/routers/` par domaine (ex. `api/routers/categories.py` ou sous-dossier `api/routers/referentiels/` selon structure existante).
- **Source de vérité** : RecyClique pour le référentiel catégories ; Paheko reçoit créations/matchs à la volée au push caisse (hors scope cette story).

### Project Structure Notes

- Aligner avec la structure existante Epic 2 : si les stories 2.1 (sites) et 2.2 (cash_registers) ont défini un router `api/routers/referentiels/` ou `api/routers/sites.py` / `cash_registers.py`, réutiliser le même pattern (ex. `api/routers/categories.py` ou `api/routers/referentiels/categories.py`).
- Modèles : `api/models/` (ex. `api/models/category.py`). Migrations : `api/db/` ou `api/alembic/`.
- Tests API (pytest) : structure miroir sous `api/tests/` (ex. `api/tests/routers/test_categories.py`). Couvrir au minimum les endpoints critiques (CRUD, hierarchy, sale-tickets, entry-tickets, visibility, display-order, soft delete/restore).

### References

- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md §2.5]
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md §3.9]
- [Source: references/ancien-repo/data-models-api.md]
- [Source: _bmad-output/planning-artifacts/architecture.md — Naming Patterns, Structure Patterns, Format Patterns]
- [Source: _bmad-output/planning-artifacts/epics.md — Epic 2, Story 2.3]

## Dev Agent Record

### Agent Model Used

bmad-dev (Story 2.3).

### Debug Log References

—

### Completion Notes List

- Migration Alembic 003 : table `categories` (id UUID, name, parent_id FK self nullable, official_name, is_visible_sale, is_visible_reception, display_order, display_order_entry, deleted_at, created_at, updated_at), index idx_categories_parent_id, idx_categories_deleted_at, idx_categories_is_visible_sale, idx_categories_is_visible_reception.
- Modèle SQLAlchemy `api/models/category.py` : Category avec relation self parent/children.
- Schemas Pydantic `api/schemas/category.py` : CategoryCreate, CategoryUpdate, CategoryResponse, CategoryHierarchyNode, CategoryVisibilityUpdate, CategoryDisplayOrderUpdate.
- Router `api/routers/categories.py` : GET list (filtres include_deleted, parent_id, is_visible_sale, is_visible_reception), GET /hierarchy, GET /sale-tickets, GET /entry-tickets, GET /{id}, POST, PUT /{id}, DELETE /{id} (soft), POST /{id}/restore, PUT /{id}/visibility, PUT /{id}/display-order. Routes spécifiques avant /{id} pour éviter capture.
- Tests `api/tests/routers/test_categories.py` : 24 tests (CRUD, hierarchy, sale-tickets, entry-tickets, visibility, display-order, soft delete, restore, put parent_id=self et cycle rejetés, format erreur). Suite complète passante.
- Code review (QA) : correction PUT rejet parent_id=soi (400) et détection cycle hiérarchie (400) ; helper _get_descendant_ids dans router.
- Conventions : snake_case BDD/API, erreurs `{ "detail": "..." }`, dates ISO 8601. Alignement artefact 08 §2.5 et 09 §3.9.

### File List

- api/db/alembic/versions/2026_02_26_003_create_categories_table.py
- api/models/category.py
- api/models/__init__.py
- api/schemas/category.py
- api/routers/categories.py
- api/main.py
- api/tests/routers/test_categories.py

## Change Log

| Date       | Actor   | Change |
|-----------|---------|--------|
| 2026-02-26 | bmad-dev | Implémentation Story 2.3 : migration categories, modèle, schemas, router CRUD + hierarchy, sale-tickets, entry-tickets, visibility, display-order, soft delete/restore. 22 tests API. Story → review, sprint-status 2-3 → review. |
| 2026-02-26 | bmad-qa | Code review adversarial : validation AC 1–4 et tâches. Corrections appliquées : rejet parent_id=soi et cycle hiérarchie (PUT), 2 tests ajoutés. Story → done, sprint-status 2-3 → done. |

## Senior Developer Review (AI)

- **Git vs Story** : Fichiers de la story présents (File List cohérent) ; non commités au moment de la review (recommandation : commit après validation).
- **AC** : AC1–AC4 implémentés (migration, endpoints, filtres visibilité, soft delete/restore).
- **Tâches** : Toutes marquées [x] et vérifiées.
- **Corrections en review** : (1) PUT /v1/categories/{id} autorisait parent_id=category_id (référence circulaire) → rejet 400 « Parent cannot be self ». (2) Aucune détection de cycle (parent_id = descendant) → ajout _get_descendant_ids et rejet 400 « Parent would create a cycle ». Tests test_put_category_parent_self_rejected et test_put_category_parent_cycle_rejected ajoutés.
- **Recommandations optionnelles** : optimisation N+1 sur GET /hierarchy (eager load ou chargement plat) ; s'assurer que les fichiers sont commités.
- **Verdict** : Approved.
