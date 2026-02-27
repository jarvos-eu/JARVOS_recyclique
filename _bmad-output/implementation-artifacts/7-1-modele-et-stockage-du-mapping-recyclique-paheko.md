# Story 7.1: Modèle et stockage du mapping RecyClique ↔ Paheko

Status: done

<!-- Prérequis HITL : HITL-7.1, 7.2, 7.3 doivent être franchis avant implémentation (décisions mapping figées). -->

## Story

En tant qu'admin technique ou responsable compta,
je veux que le système gère un mapping configurable entre les référentiels RecyClique et leurs équivalents Paheko,
afin que le push caisse produise les bonnes écritures compta.

## Acceptance Criteria

1. **Étant donné** la spec de correspondance validée (HITL-7.3)  
   **Quand** le périmètre exact du mapping est figé (moyens de paiement, catégories, sites/emplacements)  
   **Alors** les entités ou tables de mapping existent en BDD RecyClique avec les champs de correspondance Paheko.

2. **Étant donné** les tables de mapping créées  
   **Quand** un client API envoie une requête de création ou mise à jour  
   **Alors** les données peuvent être créées/mises à jour via API ; la config Paheko reste la référence (NFR-I2, FR13b).

3. **Étant donné** des enregistrements de mapping existants  
   **Quand** le worker push (Epic 4) ou la clôture (Epic 5) ont besoin d'un identifiant Paheko  
   **Alors** le système peut résoudre RecyClique → Paheko pour moyens de paiement, catégories et sites/emplacements selon les tables de mapping.

## Tasks / Subtasks

- [x] Task 1 : Migrations BDD et modèles (AC: #1)
  - [x] Créer migration Alembic pour les tables de mapping (snake_case pluriel, index idx_*).
  - [x] Tables attendues (à aligner sur spec HITL-7.3) : au minimum `payment_method_mappings` (recyclic_id / code → paheko_id_method), `category_mappings` (category_id → paheko_category_id ou code), `location_mappings` (site_id ou register_id → paheko_id_location).
  - [x] Définir les modèles SQLAlchemy dans `api/models/` (ex. `mapping.py` ou sous-dossier `api/models/mapping/`).

- [x] Task 2 : Schémas Pydantic et API CRUD (AC: #2)
  - [x] Créer schemas Pydantic (create/update/read) pour chaque type de mapping dans `api/schemas/`.
  - [x] Exposer endpoints REST : `GET/POST/PATCH /api/mapping/payment_methods`, `GET/POST/PATCH /api/mapping/categories`, `GET/POST/PATCH /api/mapping/locations` (préfixe `/api` selon architecture).
  - [x] Protéger les routes par RBAC : rôles « admin technique » ou « responsable compta » (architecture) ; pas de suppression destructive sans politique définie (soft delete ou pas de DELETE en v1).

- [x] Task 3 : Intégration référence Paheko (AC: #2, #3)
  - [x] Documenter que la config Paheko (comptes, moyens de paiement, emplacements) est la référence ; les mappings RecyClique pointent vers des identifiants Paheko existants.
  - [x] Fournir un service ou repository en `api/services/` ou `api/repositories/` pour résoudre un id/code RecyClique → id Paheko (utilisé par le worker push et la logique de clôture).

- [x] Task 4 : Tests et conventions (AC: #1, #2, #3)
  - [x] Tests API (pytest) pour création/mise à jour/liste des mappings : dossier `tests/` à la racine de l'API, structure miroir des modules (ex. `tests/routers/test_mapping_payment_methods.py`).
  - [x] Respect des conventions (architecture) : snake_case BDD/API, erreurs `{ "detail": "..." }`, dates ISO 8601.

## Dev Notes

- **Périmètre mapping (epics.md + matrice)** : Moyens de paiement (`payment_transactions.payment_method` → `plugin_pos_tabs_payments.id_method`), catégories (`categories.id` / libellé → `plugin_pos_categories`), sites/emplacements (`cash_registers.site_id` / `register_id` → `plugin_pos_locations.id`). Détail exact des champs à figer avec la spec HITL-7.3 ; schémas de référence si disponibles : `references/dumps/schema-paheko-dev.md`, `references/dumps/schema-recyclic-dev.md`.
- **Source de vérité** : La config Paheko (comptes, moyens de paiement, exercices, emplacements) reste la référence ; RecyClique ne fait que stocker les correspondances pour envoyer les bons identifiants au plugin (NFR-I2). [Source: references/migration-paeco/audits/matrice-correspondance-caisse-poids.md §5]
- **Ressources à utiliser** : `references/migration-paeco/audits/matrice-correspondance-caisse-poids.md`, `references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md`, `references/artefacts/2026-02-25_05_grille-confrontation-recyclic-paheko.md`, `references/artefacts/2026-02-25_08_session-confrontation-recyclic-paheko.md`.

### Project Structure Notes

- **Backend** : Domaine « mapping » : `api/routers/mapping/` (préfixe routes `/api/mapping/...`, cohérent avec architecture), `api/models/mapping.py` (ou `api/models/`), `api/schemas/mapping.py`, `api/services/mapping_service.py`. Pas de frontend dans cette story (Story 7.2 = interface ou API d'administration).
- **Conventions** : Tables pluriel snake_case ; index `idx_{table}_{colonne}` ; API pluriel snake_case, préfixe `/api` ; montants en centimes si applicable ; pas de secret en clair.

### References

- [Epic 7 — Correspondance et mapping](_bmad-output/planning-artifacts/epics.md) : HITL obligatoires, Story 7.1/7.2.
- [Architecture — Data Architecture, Naming, API Patterns](_bmad-output/planning-artifacts/architecture.md) : Database Strategy, Implementation Patterns.
- [Matrice correspondance caisse/poids](references/migration-paeco/audits/matrice-correspondance-caisse-poids.md) : Tableau capacités, sections 2.x arbitrages, §5 compatibilité Paheko.
- [Catalogue qui stocke quoi](references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md) : §2.2 Sites/postes, §2.3 Sessions/ventes/paiements, §2.5 Catégories.
- [Checklist v0.1](references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md) : Conventions tests, Mantine, Vitest/RTL.

## Dev Agent Record

### Agent Model Used

(à remplir par l'agent d'implémentation)

### Debug Log References

### Completion Notes List

- Task 1 : Migration Alembic `api/db/alembic/versions/2026_02_27_7_1_mapping_tables.py` (down_revision 2026_02_27_5_4). Modeles SQLAlchemy dans `api/models/mapping.py` : PaymentMethodMapping (recyclic_code, paheko_id_method), CategoryMapping (category_id, paheko_category_id nullable, paheko_code), LocationMapping (site_id ou register_id, paheko_id_location) avec contrainte CK exactement un des deux. Export dans `api/models/__init__.py`.
- Task 2 : Schemas `api/schemas/mapping.py` (create/update/response par type). Routers `api/routers/mapping/` : payment_methods, categories, locations ; montes sous prefix `/api/mapping` (segments URL snake_case : `/api/mapping/payment_methods`, `/api/mapping/categories`, `/api/mapping/locations`). RBAC `require_permissions("admin")`. Pas de DELETE en v1. Validation : au moins un de paheko_category_id/paheko_code pour categories ; exactement un de site_id/register_id pour locations.
- Task 3 : `api/services/mapping_service.py` : get_paheko_id_method(db, recyclic_code), get_paheko_category(db, category_id), get_paheko_id_location(db, site_id=..., register_id=...). Doc reference Paheko dans docstring du module.
- Task 4 : 27 tests pytest dans `api/tests/routers/mapping/` (test_mapping_payment_methods.py, test_mapping_categories.py, test_mapping_locations.py). Conventions snake_case, erreurs `{ "detail": "..." }`, dates ISO 8601. Fixture `auth_headers` ajoutee dans `api/tests/conftest.py`. Tous les tests passent.

**Revisor (2026-02-27)** : Segment URL `payment-methods` corrige en `payment_methods` (architecture snake_case). Routes et tests alignes. AC 1-3 verifies ; pas de DELETE ; RBAC admin ; service de resolution OK pour worker/cloture.

### Senior Developer Review

**bmad-qa (2026-02-27)** : Revue adversarial effectuee. AC 1-3 verifies ; tasks cochees ; File List coherente. Conventions : snake_case (BDD, API, segments URL), RBAC `require_permissions("admin")`, pas de DELETE. Tests : correction des URLs dans `test_mapping_payment_methods.py` (payment-methods -> payment_methods) pour alignement avec les routes ; 27 tests passants. **Resultat : approved.**

### Change Log

| Date       | Auteur   | Modification |
|------------|----------|--------------|
| 2026-02-27 | bmad-qa  | Code review : approved. Correction URLs tests payment_methods. Story status -> done. |

### File List

- api/models/mapping.py (nouveau)
- api/models/__init__.py (modifie : export PaymentMethodMapping, CategoryMapping, LocationMapping)
- api/db/alembic/versions/2026_02_27_7_1_mapping_tables.py (nouveau)
- api/schemas/mapping.py (nouveau)
- api/routers/mapping/__init__.py (nouveau)
- api/routers/mapping/payment_methods.py (nouveau)
- api/routers/mapping/categories.py (nouveau)
- api/routers/mapping/locations.py (nouveau)
- api/services/mapping_service.py (nouveau)
- api/main.py (modifie : include_router mapping_router prefix /api)
- api/tests/conftest.py (modifie : fixture auth_headers)
- api/tests/routers/mapping/__init__.py (nouveau)
- api/tests/routers/mapping/test_mapping_payment_methods.py (nouveau)
- api/tests/routers/mapping/test_mapping_categories.py (nouveau)
- api/tests/routers/mapping/test_mapping_locations.py (nouveau)
