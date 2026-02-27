# Story 8.3 — Import/export catégories et admin avancé

**Epic:** epic-8 — Administration, compta v1 et vie associative  
**Story key:** 8-3-import-export-categories-et-admin-avance  
**Statut:** done (code review approved 2026-02-27)  
**Livrable:** migration/copie 1.4.4 — artefact 10 §8.1  
**Références:** `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.3), `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` (§8.1)

---

## User story

En tant qu'admin,
je veux importer et exporter des catégories (CSV) et accéder à l'interface d'administration avancée des catégories,
afin de gérer facilement le référentiel EEE/décla.

---

## Contexte

- La table `categories` et les endpoints CRUD de base existent (Story 2.3, Epic 2).
- L'import/export CSV des catégories avait été reporté à l'Epic 8 (note Story 2.3 dans epics.md).
- Cette story livre l'écran admin catégories complet + import/export CSV (template, analyse, exécution), hard delete, restauration et fil d'Ariane (breadcrumb).

---

## Critères d'acceptation

**Étant donné** la table `categories` existante (Epic 2) et les endpoints de base  
**Quand** j'accède à l'écran admin catégories  
**Alors** les éléments suivants sont opérationnels :

1. **Écran admin catégories**  
   - Route `/admin/categories`.  
   - Arborescence des catégories (hiérarchie) ; liste plate avec ordre, visibilité caisse/réception ; nom, official_name.  
   - Boutons CRUD, visibilité, ordre d'affichage (sale, entry).  
   - Breadcrumb (fil d'Ariane) pour la navigation dans la hiérarchie.

2. **Import/export CSV**  
   - **Template** : téléchargement d'un fichier CSV modèle (`GET /v1/categories/import/template` ou équivalent).  
   - **Analyse** : envoi d'un fichier CSV pour analyse sans écriture (`POST /v1/categories/import/analyze`).  
   - **Exécution** : exécution de l'import après validation (`POST /v1/categories/import/execute`).  
   - **Export** : export des catégories en CSV (`GET /v1/categories/actions/export` ou équivalent).

3. **Hard delete**  
   - Suppression définitive d'une catégorie (endpoint dédié, ex. `DELETE /v1/categories/{category_id}/hard`) ; comportement cohérent avec l'artefact 10 §8.1 (vérification usage si applicable).

4. **Restauration**  
   - Restauration d'une catégorie soft-deleted (`POST /v1/categories/{category_id}/restore`).

5. **Alignement 1.4.4**  
   - Livrable = migration/copie depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md`.  
   - Référence détail écran et appels API : artefact 10 §8.1.

---

## Tasks

- [x] **Frontend — écran `/admin/categories`**  
  - Page admin catégories : arborescence, liste, CRUD, visibilité, ordre (sale = `PUT .../display-order`, entry = `PUT .../display-order-entry`).  
  - Breadcrumb pour la navigation hiérarchique.  
  - Boutons / liens vers import CSV, export CSV, et actions hard delete / restore depuis l'UI.

- [x] **Endpoints import/export CSV**  
  - `GET /v1/categories/import/template` — retourne un fichier CSV modèle.  
  - `GET /v1/categories/actions/export` (ou équivalent) — export des catégories en CSV.  
  - Aligner noms et contrats avec l'artefact 10 §8.1 et la liste endpoints 1.4.4 si différente.

- [x] **Import — analyse**  
  - `POST /v1/categories/import/analyze` — accepte un fichier CSV, retourne un rapport d'analyse (lignes valides/erreurs, preview) sans écrire en BDD.

- [x] **Import — exécution**  
  - `POST /v1/categories/import/execute` — exécute l'import après validation (payload peut reprendre le résultat de l'analyse ou le fichier + options).

- [x] **Hard delete**  
  - Endpoint `DELETE /v1/categories/{category_id}/hard` (ou convention projet) ; vérifier usage si requis (ex. `GET /v1/categories/{category_id}/has-usage`) ; traçabilité / audit si prévu.

- [x] **Restauration**  
  - S'assurer que `POST /v1/categories/{category_id}/restore` est opérationnel et exposé depuis l'écran admin (catégories soft-deleted visibles et restaurables).

---

## Livrable et références

- **Livrable :** 1.4.4 — artefact 10 §8.1 (Page catégories admin : route, permissions, données, appels API, actions).  
- **Références à charger pour l'implémentation :**  
  - `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` (§8.1)  
  - `references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md`  
  - `references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md`  
  - `references/ancien-repo/checklist-import-1.4.4.md`  
  - `references/ancien-repo/data-models-api.md`, `references/ancien-repo/v1.4.4-liste-endpoints-api.md` (catégories)

---

*Story créée par bmad-sm — 2026-02-27.*
