# Story 6.2: Saisie des lignes de réception (poids, catégorie, destination)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'opérateur réception,
je veux saisir sur chaque ticket des lignes avec poids (kg), catégorie et destination,
afin que les flux matière soient disponibles pour les déclarations et le suivi.

## Acceptance Criteria

1. **Étant donné** un ticket de dépôt ouvert (créé en Story 6.1),
   **Quand** j'ajoute une ligne avec `poids_kg`, `category_id` (optionnel) et `destination`,
   **Alors** la ligne est persistée en BDD RecyClique (table `ligne_depot` : id, ticket_id FK, poids_kg, category_id nullable FK categories, destination, notes nullable, is_exit, created_at, updated_at) et visible dans le détail du ticket (FR9, FR10).

2. **Étant donné** un ticket avec des lignes existantes,
   **Quand** je modifie une ligne (champs modifiables) ou je modifie uniquement le poids d'une ligne,
   **Alors** `PUT /v1/reception/lignes/{ligne_id}` met à jour la ligne et `PATCH /v1/reception/tickets/{ticket_id}/lignes/{ligne_id}/weight` met à jour uniquement `poids_kg` ; les données restent cohérentes en BDD.

3. **Étant donné** un ticket avec des lignes,
   **Quand** je supprime une ligne,
   **Alors** `DELETE /v1/reception/lignes/{ligne_id}` supprime la ligne en BDD ; le ticket reste valide.

4. **Étant donné** un opérateur sur l'écran détail ticket,
   **Quand** la page se charge,
   **Alors** les lignes du ticket sont chargées via `GET /v1/reception/tickets/{ticket_id}` (avec lignes) ou `GET /v1/reception/lignes` (filtre ticket_id) ; les catégories visibles en réception sont chargées via `GET /v1/categories/entry-tickets` ou `GET /v1/reception/categories` (ordre `display_order_entry`).

5. Les données réception restent la source de vérité matière/poids dans RecyClique ; aucune sync manuelle obligatoire vers Paheko (FR10). Bonnes pratiques accessibilité (NFR-A1) sur les champs de saisie (contraste, navigation clavier).

6. Livrable = migration/copie depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md` et audit `references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md` (artefact 08 §2.4, artefact 10 §6.4).

## Tasks / Subtasks

- [x] Task 1 — Modèle BDD et migration (AC: 1, 6)
  - [x] Créer table `ligne_depot` : id, ticket_id FK ticket_depot, poids_kg (numeric, obligatoire), category_id FK categories (nullable), destination (enum USER-DEFINED — valeurs à extraire du schéma 1.4.4 ou ancien-repo), notes (text nullable), is_exit (boolean, défaut false), created_at, updated_at. Index idx_ligne_depot_ticket_id, idx_ligne_depot_category_id.
  - [x] Conventions : snake_case, nom de table tel qu'en 1.4.4.
- [x] Task 2 — API réception lignes (AC: 1, 2, 3, 4)
  - [x] `POST /v1/reception/lignes` — body : `{ ticket_id, category_id?, poids_kg, destination, notes?, is_exit? }`. Réponse : ligne créée. Vérifier que le ticket existe et appartient au poste courant ou à l'utilisateur (règle métier 6.1).
  - [x] `GET /v1/reception/lignes` — query : pagination, filtre `ticket_id` (obligatoire ou fortement recommandé pour l'écran détail). Réponse : `{ items, total, page, page_size }`.
  - [x] `GET /v1/reception/tickets/{ticket_id}` — étendre la réponse pour inclure les lignes du ticket (ou documenter que les lignes sont chargées via GET /v1/reception/lignes?ticket_id=).
  - [x] `PUT /v1/reception/lignes/{ligne_id}` — body : champs modifiables (poids_kg, category_id, destination, notes, is_exit).
  - [x] `PATCH /v1/reception/tickets/{ticket_id}/lignes/{ligne_id}/weight` — body : `{ weight }` (poids_kg). Traçabilité/audit selon architecture si nécessaire.
  - [x] `DELETE /v1/reception/lignes/{ligne_id}`.
  - [x] Router sous `/v1/reception/` ; permission `reception.access`.
- [x] Task 3 — Frontend détail ticket + lignes (AC: 1, 2, 3, 4, 5)
  - [x] Écran détail ticket (ex. `/reception/tickets/:ticketId` déjà créé en 6.1) : au chargement, appeler GET ticket + GET lignes (ou GET ticket avec lignes incluses) et GET /v1/categories/entry-tickets (ou /v1/reception/categories) pour les listes de valeurs.
  - [x] Formulaire ou ligne inline : ajout de ligne (poids_kg, sélecteur catégorie, sélecteur destination, notes optionnel, is_exit optionnel). Soumission → POST /v1/reception/lignes.
  - [x] Liste des lignes : affichage avec actions Modifier (PUT), Modifier poids (PATCH weight), Supprimer (DELETE). Alignement Mantine (Select, NumberInput, TextInput, Button, Table ou List).
  - [x] Accessibilité : labels, contraste, navigation clavier (NFR-A1).
- [x] Task 4 — Tests (AC: 1–6)
  - [x] Tests API : 401 sans auth pour chaque endpoint (POST, GET, PUT, PATCH weight, DELETE lignes) ; scénarios avec client authentifié (conftest) ; validation body (poids_kg obligatoire, destination obligatoire, ticket_id valide).
  - [x] Tests frontend : composant ou page de saisie des lignes (ajout, liste, modification, suppression) ; tests co-locés `*.test.tsx`, Vitest + RTL + jsdom.

### Review Follow-ups (AI)

- [x] [AI-Review][MEDIUM] Formulaire « Ajouter une ligne » et modal « Modifier » partagent le même état (categoryId, destination, notes, isExit). Quand la modal d'édition est ouverte, le formulaire d'ajout affiche les valeurs de la ligne en cours d'édition — confusion UX. [ReceptionTicketDetailPage.tsx]
- [x] [AI-Review][MEDIUM] Tests frontend : pas de tests pour l'ajout de ligne, la modification, la suppression ni le modal poids. Seuls chargement, détail et erreur sont couverts (Task 4 exige « ajout, liste, modification, suppression »). [ReceptionTicketDetailPage.test.tsx]
- [x] [AI-Review][LOW] API : destination accepte toute chaîne (1–64 caractères) sans validation contre les valeurs métier (recyclage, revente, etc.) — risque de typo ou valeurs incohérentes. [api/schemas/ligne_depot.py, api/routers/v1/reception.py]
- [x] [AI-Review][LOW] Accessibilité NFR-A1 : labels et data-testid présents ; pas de vérification aria-* ou contraste explicite. [ReceptionTicketDetailPage.tsx]

## Dev Notes

- **Références obligatoires** : `references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md` (tableau §2 : Ligne de dépôt ajout/modif/poids/suppression, API ↔ table `ligne_depot` ; §3 hébergement données). `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` §6.4 (Détail ticket + lignes de dépôt).
- **GET ticket** : `GET /v1/reception/tickets/{ticket_id}` existe en 6.1 ; 6.2 étend la réponse pour inclure les lignes du ticket, ou le front charge les lignes via `GET /v1/reception/lignes?ticket_id=...`.
- **Destination** : enum côté BDD (USER-DEFINED) ; structure dans `references/dumps/schema-recyclic-dev.md` (table `ligne_depot`). Valeurs à lister depuis le schéma 1.4.4 ou ancien-repo. Si non documenté, définir un enum cohérent (ex. valeurs métier courantes pour flux matière) et le documenter dans la story ou l'API.
- **Catégories réception** : `GET /v1/categories/entry-tickets` ou `GET /v1/reception/categories` — catégories avec `is_visible_reception` (ou équivalent), ordre `display_order_entry` (Epic 2 Story 2.3).
- **Pas de site_id** sur ticket_depot ni ligne_depot ; site déductible via poste → opened_by_user_id → users.site_id (audit §3).
- **Story 6.1** : postes (poste_reception, poste courant), tickets (ticket_depot, GET/POST tickets, GET ticket/{id}), fermeture ticket/poste. Réutiliser `api/routers/v1/reception.py`, `frontend/src/reception/`, `frontend/src/api/reception.ts`, modèles PosteReception et TicketDepot. La page `ReceptionTicketDetailPage` existe déjà — y ajouter la gestion des lignes (état, appels API, formulaire).
- **Conventions** : API REST, JSON ; snake_case ; erreur `{ "detail": "..." }` ; dates ISO 8601. Poids en kg (réception). Frontend : composants PascalCase, hooks camelCase ; état immuable ; isLoading/isPending.
- **Tests** : co-locés `*.test.tsx` (frontend) ; Vitest + React Testing Library + jsdom. API : pytest, structure miroir `api/tests/routers/reception/` (ex. `test_reception_lignes.py`).

### Project Structure Notes

- **API** : étendre le router existant `api/routers/v1/reception.py` (6.1) avec les endpoints lignes. Nouveaux modèles/schemas : `api/models/ligne_depot.py` (ou dans un module reception si convention différente), `api/schemas/ligne_depot.py`. Pas de nouveau domaine — même router réception que 6.1.
- **Frontend** : étendre `frontend/src/reception/ReceptionTicketDetailPage.tsx` et `frontend/src/api/reception.ts` (fonctions pour lignes). Pas de nouveau dossier.

### References

- [Source: references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md] — tableau étape → API → tables BDD ; §3 données poids/catégories/destination
- [Source: references/dumps/schema-recyclic-dev.md] — table `ligne_depot` (structure, destination USER-DEFINED)
- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md §6.4] — Détail ticket + lignes : chargement, POST/PUT/DELETE/PATCH weight
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 6, Story 6.2, FR9, FR10
- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md] — réception RecyClique source de vérité
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md] — périmètre API v1 réception
- [Source: _bmad-output/implementation-artifacts/6-1-ouverture-de-poste-de-reception-et-creation-de-tickets-de-depot.md] — Story 6.1 (postes, tickets, routes, API client, Mantine)
- [Source: _bmad-output/planning-artifacts/architecture.md] — conventions API, auth, structure, tests

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Task 1 : Modèle LigneDepot (api/models/ligne_depot.py), relation TicketDepot.lignes, migration SQL 2026_02_27_6_2_reception_ligne_depot.sql. Destination en VARCHAR(64) (valeurs métier : recyclage, revente, destruction, don, autre).
- Task 2 : POST/GET/PUT/PATCH weight/DELETE lignes dans api/routers/v1/reception.py ; GET /tickets/{id} étendu avec joinedload(lignes) et réponse TicketDepotResponse.lignes ; ticket_id obligatoire pour GET /lignes ; permission reception.access ; vérification ticket/poste utilisateur (_get_ticket_for_user, _get_ligne_for_user).
- Task 3 : ReceptionTicketDetailPage étendu : chargement ticket + categories (getTicket, getCategoriesEntryTickets), formulaire ajout ligne (NumberInput, Select catégorie/destination, TextInput notes, Checkbox is_exit), tableau des lignes avec actions Modifier / Poids / Supprimer (modals Mantine). Labels et data-testid pour accessibilité.
- Task 4 : test_reception_lignes.py (401 pour chaque endpoint, create/list/get ticket with lignes/put/patch weight/delete, validation body) ; ReceptionTicketDetailPage.test.tsx mis à jour (mock getCategoriesEntryTickets, ResizeObserver), assertion reception-lignes-empty.
- **Review follow-ups (2026-02-27)** : (1) État formulaire « Ajouter une ligne » séparé de la modal « Modifier » (editPoidsKg, editCategoryId, editDestination, editNotes, editIsExit). (2) Tests frontend : ajout ligne, modification, suppression, modal poids (userEvent, within, mocks). (3) API : destination en Literal (recyclage, revente, destruction, don, autre) ; test test_create_ligne_validation_destination_valeurs_metier. (4) Accessibilité : role="form", aria-label, aria-required ; contraste Mantine NFR-A1.

### File List

- api/models/ligne_depot.py (new)
- api/models/ticket_depot.py (modified — relationship lignes)
- api/models/__init__.py (modified — LigneDepot)
- api/migrations/2026_02_27_6_2_reception_ligne_depot.sql (new)
- api/schemas/ligne_depot.py (new — Literal destination)
- api/schemas/ticket_depot.py (modified — lignes in TicketDepotResponse, import LigneDepotResponse)
- api/routers/v1/reception.py (modified — lignes endpoints, get_ticket with lignes, helpers _get_ticket_for_user, _get_ligne_for_user)
- api/tests/routers/reception/test_reception_lignes.py (modified — test_create_ligne_validation_destination_valeurs_metier)
- frontend/src/api/reception.ts (modified — LigneDepotItem, TicketDepotItem.lignes, getLignes, createLigne, updateLigne, updateLigneWeight, deleteLigne, getCategoriesEntryTickets)
- frontend/package.json (modified — devDependency @testing-library/user-event)
- frontend/src/reception/ReceptionTicketDetailPage.tsx (modified — état séparé add/edit, aria form/required)
- frontend/src/reception/ReceptionTicketDetailPage.test.tsx (modified — tests ajout, modification, suppression, modal poids)

## Senior Developer Review (AI)

**Date :** 2026-02-27

**Git vs story :** Fichiers de la File List présents en working tree (untracked/modified). Pas de commit dédié 6.2 ; pas de fausse déclaration de fichiers.

**Résumé :** 2 MEDIUM, 2 LOW. Aucun CRITICAL. AC 1–4 validés implémentés ; AC 5–6 conformes ou hors périmètre code. Toutes les tâches [x] correspondent à du code présent.

- **MEDIUM** — Formulaire « Ajouter une ligne » et modal « Modifier » partagent le même état (categoryId, destination, notes, isExit). Quand la modal d'édition est ouverte, le formulaire d'ajout affiche les valeurs de la ligne en cours d'édition (confusion UX). [ReceptionTicketDetailPage.tsx]
- **MEDIUM** — Tests frontend : pas de tests pour l'ajout de ligne, la modification, la suppression ni le modal poids. Seuls chargement, détail et erreur sont couverts ; Task 4 exige « ajout, liste, modification, suppression ». [ReceptionTicketDetailPage.test.tsx]
- **LOW** — API : destination accepte toute chaîne 1–64 caractères sans validation contre les valeurs métier (recyclage, revente, etc.). [api/schemas/ligne_depot.py, reception.py]
- **LOW** — Accessibilité NFR-A1 : labels et data-testid présents ; pas de vérification aria-* ou contraste explicite.

**Statut après revue :** review (follow-ups traités).

**Revue second passage (2026-02-27) :** Les 4 follow-ups vérifiés dans le code : état add/edit séparé (editPoidsKg, editCategoryId, etc.), tests frontend ajout/modification/suppression/modal poids, API destination en Literal + test 422, accessibilité role="form" / aria-label / aria-required. Aucun CRITICAL ni HIGH. reviewResult: approved → Status: done.

## Change Log

- 2026-02-27 : Story 6.2 implémentée — table ligne_depot, API réception lignes (POST/GET/PUT/PATCH weight/DELETE), GET ticket avec lignes, frontend détail ticket (formulaire ajout, tableau, modals modifier/poids), tests API et frontend.
- 2026-02-27 : **Corrections review** — État formulaire ajout séparé de la modal modifier (editCategoryId, editDestination, editNotes, editIsExit) ; tests frontend ajout/modification/suppression/modal poids ; API destination en Literal (recyclage, revente, destruction, don, autre) ; aria role/aria-label/aria-required sur formulaires. Story → review, sprint-status 6-2 → review.
- 2026-02-27 : **Code review second passage** — Vérification des 4 follow-ups : tous traités. reviewResult approved. Story → done, sprint-status 6-2 → done.
