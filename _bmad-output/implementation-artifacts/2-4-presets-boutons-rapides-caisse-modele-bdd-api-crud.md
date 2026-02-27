# Story 2.4: Presets (boutons rapides caisse) — modèle BDD + API CRUD

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'admin ou développeur,
je veux une table `preset_buttons` et les endpoints CRUD + liste des actifs,
afin que l'écran caisse puisse charger les boutons rapides au démarrage.

## Acceptance Criteria

1. **Étant donné** la table `categories` existante (Story 2.3 livrée)
   **Quand** la migration crée la table `preset_buttons` (id, name, category_id FK nullable, preset_price, button_type, sort_order, is_active, created_at, updated_at)
   **Alors** les endpoints fonctionnent : `GET /v1/presets`, `GET /v1/presets/active`, `GET /v1/presets/{id}`, `POST /v1/presets`, `PATCH /v1/presets/{id}`, `DELETE /v1/presets/{id}`
   **Et** la structure respecte les conventions snake_case (artefact 08 §2.6, artefact 09 §3.12) ; livrable = migration/copie 1.4.4.

2. **Étant donné** des presets existants avec is_active et sort_order
   **Quand** on appelle `GET /v1/presets/active`
   **Alors** seuls les presets avec `is_active=true` sont retournés, triés par `sort_order` (ordre croissant).

3. **Étant donné** un preset avec `category_id` renseigné
   **Quand** on crée ou met à jour le preset
   **Alors** `category_id` est une clé étrangère vers `categories.id` (nullable : preset sans catégorie autorisé). La suppression ou l'invalidation d'une catégorie doit être gérée selon la règle 1.4.4 (contraintes métier, pas de cascade destructive non documentée).

4. **Étant donné** les types de bouton en 1.4.4 (Don, Recyclage, Déchèterie, etc.)
   **Quand** le modèle est implémenté
   **Alors** `button_type` est représenté de façon cohérente avec 1.4.4 (enum ou varchar selon schéma source) ; les valeurs sont au minimum Don, Recyclage, Déchèterie (audit 1.4.4 §1.3) et documentées ou dérivées de `references/ancien-repo/data-models-api.md` (PresetButton, ButtonType) et `references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md`.

## Tasks / Subtasks

- [x] Task 1 : Migration et modèle BDD (AC: 1)
  - [x] Créer migration Alembic pour table `preset_buttons` : id (UUID), name, category_id (FK → categories.id nullable), preset_price (integer centimes), button_type, sort_order (integer), is_active (boolean), created_at, updated_at
  - [x] Index : idx_preset_buttons_category_id, idx_preset_buttons_is_active, idx_preset_buttons_sort_order
  - [x] Modèle SQLAlchemy PresetButton avec relation optionnelle vers Category
- [x] Task 2 : Schémas Pydantic et router CRUD (AC: 1, 2, 3)
  - [x] Schemas : PresetCreate, PresetUpdate, PresetResponse
  - [x] GET /v1/presets (liste, filtre optionnel par category_id), GET /v1/presets/active (is_active=true, tri sort_order), GET /v1/presets/{id}
  - [x] POST /v1/presets, PATCH /v1/presets/{id}, DELETE /v1/presets/{id}
  - [x] Routes spécifiques avant /{id} pour éviter capture (ordre : /active puis /{id})
- [x] Task 3 : Règles métier et tests (AC: 3, 4)
  - [x] Validation category_id existant ou null à la création/mise à jour ; tests unitaires API (pytest) pour CRUD et GET /active

## Dev Notes

- **Prérequis** : Story 2.3 (catégories) livrée. La table `categories` existe ; le router et les modèles catégories sont dans `api/routers/categories.py`, `api/models/category.py`.
- **Règle brownfield** : livrable = migration/copie depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md`. Références obligatoires : artefact 08 §2.6 (catalogue qui stocke quoi — presets), artefact 09 §3.12 (périmètre API presets), `references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md` (§ Presets / tableau endpoints), `references/ancien-repo/data-models-api.md` (PresetButton, ButtonType), `references/ancien-repo/v1.4.4-liste-endpoints-api.md` (section Presets).
- **Conventions** : BDD snake_case (tables pluriel, index idx_{table}_{colonne}). API : endpoints pluriel, base path `/v1/presets` ; erreur `{ "detail": "..." }` ; dates ISO 8601 ; montants en centimes (preset_price). Router dans `api/routers/presets.py` (même pattern que 2.3 : `api/routers/categories.py`), enregistrement dans `api/main.py`. `DELETE /v1/presets/{id}` = suppression définitive (pas de soft delete sur les presets).
- **Hors périmètre cette story** : logique métier « Presets Recyclage / Déchèterie » (B49-P6), usage des presets dans POST /v1/sales (lignes avec preset_id) → Epic 5. Cette story livre uniquement le référentiel BDD + API CRUD + GET /active pour que l'écran caisse puisse charger les boutons au démarrage.

### Project Structure Notes

- Router : `api/routers/presets.py` (alignement 2.3 : `api/routers/categories.py`). Modèles : `api/models/preset.py` (ou `preset_button.py`). Migrations : `api/db/` ou `api/alembic/` (version 004 après 003_categories). Enregistrement du router dans `api/main.py`.
- Tests API (pytest) : `api/tests/routers/test_presets.py`. Couvrir au minimum : CRUD, GET /active (filtre is_active, tri sort_order), validation category_id (existant / null), ordre des routes (/active avant /{id}).

### Previous Story Intelligence (Story 2.3 — Catégories)

- Migration : numéro de version Alembic à enchaîner (ex. 004 après 003_categories). Même convention UUID pour id.
- Router : placer les routes fixes (`/active`, `/hierarchy`, etc.) **avant** la route `/{id}` pour éviter que "active" ou "hierarchy" ne soient capturés comme id. Story 2.3 a documenté ce point et la review a corrigé l'ordre.
- Erreurs : rejet 400 avec `{ "detail": "..." }` pour validation métier (ex. category_id invalide). Pas de cascade DELETE non documentée sur categories → presets ; décider (ex. interdire suppression catégorie si presets liés, ou mettre category_id à null) selon 1.4.4.
- Tests : pytest, client TestClient FastAPI ; fixtures pour BDD (session, categories). Pattern : créer catégorie puis preset avec category_id pour les tests liés.

### References

- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md §2.6]
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md §3.12]
- [Source: references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md — Presets, tableau endpoints]
- [Source: references/ancien-repo/data-models-api.md — PresetButton, ButtonType]
- [Source: references/ancien-repo/v1.4.4-liste-endpoints-api.md — Presets]
- [Source: _bmad-output/planning-artifacts/architecture.md — Naming, Structure, Format]
- [Source: _bmad-output/planning-artifacts/epics.md — Epic 2, Story 2.4]
- [Source: _bmad-output/implementation-artifacts/2-3-categories-modele-bdd-api-crud-hierarchie-et-visibilite.md — patterns router/tests]

## Dev Agent Record

### Agent Model Used

bmad-dev (Story 2.4). l'agent dev.)

### Debug Log References

—

### Completion Notes List

- Migration Alembic 004 : table `preset_buttons` (id UUID, name, category_id FK categories.id nullable SET NULL on delete, preset_price integer centimes, button_type varchar 64, sort_order integer, is_active boolean, created_at, updated_at). Index idx_preset_buttons_category_id, idx_preset_buttons_is_active, idx_preset_buttons_sort_order.
- Modèle SQLAlchemy `api/models/preset.py` : PresetButton avec relation optionnelle vers Category (backref preset_buttons).
- Schémas Pydantic `api/schemas/preset.py` : PresetCreate, PresetUpdate, PresetResponse (snake_case, preset_price centimes).
- Router `api/routers/presets.py` : GET /v1/presets (filtre category_id optionnel), GET /v1/presets/active (is_active=true, tri sort_order) avant GET /{id}, GET/POST/PATCH/DELETE /v1/presets/{id}. Validation category_id : 400 si fourni et catégorie inexistante. PATCH permet de remettre category_id à null (body.model_dump(exclude_unset=True)).
- Tests `api/tests/routers/test_presets.py` : 18 tests (CRUD, GET /active, filtre category_id, validation category_id existant/null/unset null, ordre routes /active avant /{id}, format erreur detail). Suite complète passante.

### File List

- api/db/alembic/versions/2026_02_26_004_create_preset_buttons_table.py
- api/models/preset.py
- api/models/__init__.py
- api/schemas/preset.py
- api/routers/presets.py
- api/main.py
- api/tests/routers/test_presets.py

## Senior Developer Review (AI)

- **Date** : 2026-02-27
- **Résultat** : Approuvée (avec correctif appliqué)
- **Vérifications** : AC1–AC4 et toutes les tâches validés. File List conforme aux fichiers modifiés. 18 tests API passants.
- **Correctif en review** : PATCH /v1/presets/{id} ne permettait pas de remettre `category_id` à null. Utilisation de `body.model_dump(exclude_unset=True)` dans le router pour ne mettre à jour que les champs fournis et accepter `category_id: null`. Test `test_patch_preset_category_id_unset_null` ajouté.
- **Note** : Pas de validation des valeurs de `button_type` (whitelist Don/Recyclage/Déchèterie) — accepté au regard du périmètre (varchar 1.4.4).

## Change Log

| Date       | Actor    | Change |
|------------|----------|--------|
| 2026-02-26 | bmad-dev | Implémentation Story 2.4 : migration preset_buttons, modèle PresetButton, schemas, router CRUD + GET /active, validation category_id. 17 tests API. Story → review, sprint-status 2-4 → review. |
| 2026-02-27 | bmad-qa  | Code review adversarial : correctif PATCH (category_id remis à null via exclude_unset), test unset null ajouté. 18 tests passants. Story → done, sprint-status 2-4 → done. |
