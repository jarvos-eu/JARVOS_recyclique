# Story 8.2 — Administration sites, postes, sessions et rapports caisse

- **Epic:** epic-8 (Administration, compta v1 et vie associative)
- **Story_key:** 8-2-administration-sites-postes-sessions-et-rapports-caisse
- **Livrable:** migration/copie 1.4.4 — artefact 10 §7.4 à §7.7

---

## User story

En tant qu'admin,
je veux les écrans complets d'administration des sites, des postes de caisse, du gestionnaire de sessions et des rapports caisse,
afin de piloter les opérations de caisse et d'accéder aux rapports.

---

## Critères d'acceptation

- **Étant donné** les APIs sites / cash-registers / cash-sessions existantes (Epics 2 et 5),
- **Quand** j'accède aux écrans admin correspondants,
- **Alors** :
  - **Sites** : écran admin sites (liste, formulaire création/édition) opérationnel — CRUD via API.
  - **Postes de caisse** : écran admin postes (liste, formulaire) opérationnel — CRUD sites/postes.
  - **Gestionnaire de sessions** : écran avec filtres (période, site, poste, opérateur, statut) et pagination.
  - **Rapports caisse** : rapports par session (téléchargement par session) et export bulk (filtres période, etc.) opérationnels.
- **Et** livrable = migration/copie 1.4.4 (artefact 10 §7.4, §7.5, §7.6, §7.7).

### Détail par écran (référence artefact 10)

- **Permissions** : tous les écrans de cette story requièrent le rôle **admin** (ou permission dédiée rapports/sessions pour le détail session).

| Écran | Routes | Données / Appels API |
|-------|--------|----------------------|
| Sites | `/admin/sites`, `/admin/sites-and-registers` | GET /v1/sites ; POST/PATCH/DELETE /v1/sites/{id} |
| Postes caisse | `/admin/cash-registers` | GET /v1/cash-registers, GET /v1/sites ; POST/PATCH/DELETE /v1/cash-registers/{id} |
| Gestionnaire sessions | `/admin/session-manager` | GET /v1/cash-sessions (filtres, pagination) ; correctifs Super Admin si exposés |
| Rapports caisse | `/admin/reports`, `/admin/reports/cash-sessions` | GET /v1/admin/reports/cash-sessions ; GET .../by-session/{session_id} ou .../{filename} ; POST .../export-bulk |

---

## Tasks

1. **Frontend — Admin sites**
   - Implémenter les routes `/admin/sites` et `/admin/sites-and-registers` (selon 1.4.4).
   - Liste des sites (GET /v1/sites), formulaire création/édition, actions CRUD (POST, PATCH, DELETE).

2. **Frontend — Admin postes**
   - Implémenter la route `/admin/cash-registers`.
   - Liste des postes (GET /v1/cash-registers, GET /v1/sites pour lien site), formulaire CRUD poste (name, site_id, location, is_active, enable_virtual, enable_deferred).

3. **Frontend — Admin sessions**
   - Implémenter la route `/admin/session-manager`.
   - Liste des sessions avec filtres (période, site, poste, opérateur, statut) et pagination (GET /v1/cash-sessions avec query params).
   - Lien vers détail session (/admin/cash-sessions/:id — écran 5.5).
   - Si prévu en v1 : actions correctifs Super Admin (fix-blocked-deferred, merge-duplicate-deferred).

4. **Frontend — Admin rapports caisse**
   - Implémenter les routes `/admin/reports`, `/admin/reports/cash-sessions`.
   - Liste des rapports ; téléchargement par session (GET by-session/{id} ou par filename).
   - Export bulk : POST /v1/admin/reports/cash-sessions/export-bulk avec filtres (période, etc.).

5. **APIs (Epics 2 et 5)**
   - S'appuyer sur les endpoints existants Epics 2 (sites, cash-registers) et 5 (cash-sessions, rapports).
   - Vérifier et compléter si besoin : GET /v1/cash-sessions avec filtres et pagination ; GET /v1/admin/reports/cash-sessions (liste), GET .../by-session/{session_id}, GET .../{filename}, POST .../export-bulk.

---

## Références

- **Epic 8, Story 8.2 :** `_bmad-output/planning-artifacts/epics.md`
- **Traçabilité écran → API :** `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` (§7.4 à §7.7)
- **Checklist import 1.4.4 :** `references/ancien-repo/checklist-import-1.4.4.md`
- **Architecture et conventions :** `_bmad-output/planning-artifacts/architecture.md` (Gap Analysis, Implementation Readiness) ; `references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md`
- **Sprint status :** `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Conventions d'implémentation

- **UI / styling :** Mantine (alignement 1.4.4) ; pas de Tailwind ni autre lib UI.
- **Layout admin :** écrans intégrés au layout admin (navigation / sidebar admin) selon `frontend/src/admin/` et spec UX.
- **Tests frontend :** Vitest + React Testing Library + jsdom ; tests co-locés `*.test.tsx` à côté des composants (voir `frontend/README.md`).
- **Structure :** écrans admin dans le module admin (ex. `frontend/src/admin/` ou structure définie dans l'architecture).

---

## Code review (2026-02-27)

- **Résultat :** `changes-requested`
- **Fichier :** `_bmad-output/implementation-artifacts/8-2-administration-sites-postes-sessions-et-rapports-caisse.review.json`
- **Résumé :** Routes et backends conformes ; permission admin et Mantine OK. **À corriger :** filtre opérateur manquant dans le gestionnaire de sessions (AC explicite). Optionnel : GET rapport par filename ; correctifs Super Admin non implémentés.

### Correction appliquée (2026-02-27)

- **Filtre opérateur :** Ajout dans `AdminSessionManagerPage` d'un Select « Opérateur » chargé via `getUsers(accessToken)` (GET /v1/users), avec passage de `operator_id` à `getCashSessionsList`. L'API GET /v1/cash-sessions gère déjà `operator_id`. Filtre inclus dans le bouton Réinitialiser.
- **Client API :** `getUsers` et type `User` ajoutés dans `frontend/src/api/admin.ts`.
- **Story prête pour re-review.**
