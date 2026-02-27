# Story 6.1: Ouverture de poste de réception et création de tickets de dépôt

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'opérateur réception (poste démarré par un admin),
je veux ouvrir un poste de réception et créer des tickets de dépôt,
afin d'enregistrer les entrées matière de façon traçable.

## Acceptance Criteria

1. **Étant donné** un utilisateur autorisé avec un poste réception actif (Epic 3 — démarrage poste par admin),
   **Quand** j'ouvre un poste de réception (action « Ouvrir poste »),
   **Alors** le poste est enregistré en BDD RecyClique (table `poste_reception` : id, opened_by_user_id, opened_at, status = 'opened', closed_at nullable) et l'état « poste courant » est disponible pour la session (FR8).

2. **Étant donné** un poste de réception ouvert,
   **Quand** je crée un nouveau ticket de dépôt (action « Créer ticket »),
   **Alors** le ticket est enregistré en BDD RecyClique (table `ticket_depot` : id, poste_id FK, benevole_user_id [souvent opérateur connecté], created_at, status = 'opened', closed_at nullable) et apparaît dans la liste (FR8).

3. **Étant donné** des tickets existants pour le poste courant (ou filtres),
   **Quand** je consulte la liste des tickets,
   **Alors** `GET /v1/reception/tickets` retourne les tickets avec pagination/filtres attendus ; le détail d'un ticket est accessible via `GET /v1/reception/tickets/{ticket_id}`.

4. Aucune synchronisation manuelle vers Paheko n'est requise pour cette story (FR10). La réception reste source de vérité matière dans RecyClique.

5. Livrable = migration/copie depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md` et audit `references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md` (artefact 10 §6.1/6.2).

## Tasks / Subtasks

- [x] Task 1 — Migrations BDD (AC: 1, 2, 5)
  - [x] Créer table `poste_reception` (id, opened_by_user_id FK users, opened_at, closed_at nullable, status, created_at, updated_at) ; index idx_poste_reception_opened_by_user_id, idx_poste_reception_status.
  - [x] Créer table `ticket_depot` (id, poste_id FK poste_reception, benevole_user_id FK users, created_at, closed_at nullable, status, updated_at) ; index idx_ticket_depot_poste_id, idx_ticket_depot_benevole_user_id.
  - [x] Conventions : snake_case, noms de tables tel qu'en 1.4.4 (poste_reception, ticket_depot).
- [x] Task 2 — API réception postes (AC: 1)
  - [x] `POST /v1/reception/postes/open` — body optionnel : `{ opened_at? }` (saisie différée). Réponse : poste créé (opened_by_user_id = utilisateur connecté). Enregistrer ouverture et fermeture poste dans `audit_events` (architecture § Monitoring / audit log).
  - [x] `GET /v1/reception/postes/current` — retourne le poste ouvert pour l'utilisateur connecté (404 si aucun) ; permet d'afficher l'état du poste au chargement de l'accueil (traçabilité §6.1).
  - [x] Router sous `/v1/reception/` ; permission `reception.access`.
- [x] Task 3 — API réception tickets (AC: 2, 3)
  - [x] `POST /v1/reception/tickets` — body optionnel : `{ poste_id? }` (ou déduit du poste courant). benevole_user_id = utilisateur connecté par défaut.
  - [x] `GET /v1/reception/tickets` — query : pagination (`page`, `page_size`), filtre `poste_id`, `status`. Réponse : `{ items, total, page, page_size }` (snake_case, architecture § Format Patterns).
  - [x] `GET /v1/reception/tickets/{ticket_id}` — détail d'un ticket (sans lignes obligatoires pour 6.1 ; les lignes sont en story 6.2).
- [x] Task 4 — Frontend accueil réception (AC: 1, 2, 3)
  - [x] Route `/reception` ; permission `reception.access`.
  - [x] Au chargement : `GET /v1/reception/postes/current` pour afficher l'état du poste (ouvert / fermé). Boutons « Ouvrir poste » (modal ou étape avec opened_at optionnel), « Créer ticket », « Fermer poste » (optionnel pour 6.1 : `POST /v1/reception/postes/{poste_id}/close`).
  - [x] Liste des tickets du poste courant : chargement via GET /v1/reception/tickets (poste_id du poste courant) ; clic vers détail ticket (vue minimale pour 6.1, lignes en 6.2).
  - [x] Alignement Mantine, structure `frontend/src/reception/` (architecture § Project Structure).

- [x] **Review Follow-ups (AI)**
  - [x] [AI-Review][MEDIUM] Frontend réception : utiliser Mantine (Button, TextInput, Modal, etc.) au lieu de div/button/input natifs avec styles inline — architecture et checklist v0.1. [ReceptionAccueilPage.tsx, ReceptionTicketDetailPage.tsx]
  - [x] [AI-Review][MEDIUM] Tests API réception : ajouter scénarios métier avec client authentifié (conftest client fixture) — open poste, get current, create ticket, list tickets avec pagination/filtres. [test_reception_postes.py, test_reception_tickets.py]
  - [x] [AI-Review][MEDIUM] Tests frontend : ajouter tests pour ReceptionTicketDetailPage (chargement, affichage détail, erreur). [ReceptionTicketDetailPage.test.tsx]
  - [x] [AI-Review][LOW] AppNav : masquer le lien Réception si l'utilisateur n'a pas la permission reception.access (optionnel ; l'API renvoie déjà 403). [AppNav.tsx]
  - [x] [AI-Review][LOW] Tests API : couvrir POST /v1/reception/tickets/{id}/close (401 sans auth + scénario avec auth). [test_reception_tickets.py]

## Dev Notes

- **Références obligatoires** : `references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md` (tableau §2 : API ↔ tables), `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` §6.1 et §6.2 (accueil, ouverture poste, liste tickets).
- **Pas de site_id** sur `poste_reception` ni `ticket_depot` ; le site est déductible via `poste_reception.opened_by_user_id` → `users.site_id` (audit §3).
- **Saisie différée** : `POST /v1/reception/postes/open` avec `opened_at` dans le passé autorisé (B44-P2, B44-P4) ; à supporter en body optionnel.
- **Fermeture poste** : `POST /v1/reception/postes/{poste_id}/close` — dans le périmètre 6.1 pour que l'opérateur puisse clôturer le poste ; endpoint à exposer. Fermeture ticket : `POST /v1/reception/tickets/{ticket_id}/close` peut être implémenté en API en 6.1 (audit) ; l'UI détail ticket + lignes est en 6.2.
- **Conventions API** : REST, JSON ; dates ISO 8601 ; erreur `{ "detail": "..." }` ; endpoints pluriel snake_case. Poids en kg (réception).
- **Tests** : co-locés `*.test.tsx` (frontend) ; Vitest + React Testing Library + jsdom. API : pytest, structure miroir `tests/routers/reception/` (ex. `test_reception_postes.py`, `test_reception_tickets.py` — architecture § Structure Patterns).

### Project Structure Notes

- **API** : router réception dans `api/routers/reception/` (architecture § Project Structure) ; schemas Pydantic pour PosteReception, TicketDepot ; modèles SQLAlchemy cohérents avec les autres domaines (sites, cash_registers). Pas de `api/domains/reception/` — convention = routers par domaine.
- **Frontend** : `frontend/src/reception/` (aligné architecture) ; routes sous `/reception` ; permission `reception.access` vérifiée côté route et API.

### References

- [Source: references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md] — tableau étape → API → tables BDD
- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md §6.1, §6.2] — accueil réception, ouverture poste, liste tickets, actions → appels API
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 6, Story 6.1, FR8, FR10
- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md] — qui stocke quoi (réception RecyClique)
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md] — périmètre API v1 réception
- [Source: references/ancien-repo/checklist-import-1.4.4.md] — copy + consolidate + security
- [Source: _bmad-output/planning-artifacts/architecture.md] — API REST, auth, conventions, logging, audit

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Task 1 : Modèle PosteReception mis à jour (closed_at, created_at, updated_at, status=opened, index opened_by_user_id). Modèle TicketDepot créé. Migration SQL `api/migrations/2026_02_27_6_1_reception_postes_tickets.sql` pour PostgreSQL (CREATE/ALTER).
- Task 2 : POST /v1/reception/postes/open (body optionnel), GET /v1/reception/postes/current (404 si aucun), POST /v1/reception/postes/{poste_id}/close. Audit events reception_post_opened, reception_post_closed.
- Task 3 : POST /v1/reception/tickets, GET /v1/reception/tickets (pagination, filtre poste_id, status), GET /v1/reception/tickets/{ticket_id}, POST /v1/reception/tickets/{ticket_id}/close.
- Task 4 : Route /reception (ReceptionAccueilPage), /reception/tickets/:ticketId (ReceptionTicketDetailPage). Client API frontend src/api/reception.ts. Boutons Ouvrir poste (modal opened_at), Créer ticket, Fermer poste ; liste tickets avec lien vers détail.
- Tests : ReceptionAccueilPage.test.tsx (Vitest, 2 tests). API tests api/tests/routers/reception/test_reception_postes.py, test_reception_tickets.py (401 sans auth).
- Review follow-ups (2026-02-27) : (1) Frontend réception refait avec Mantine (Button, Modal, Stack, Title, Text, List, Anchor ; main.tsx + postcss). (2) Tests API avec client authentifié : open/get/close poste, create/list/get/close ticket, pagination et filtres. (3) ReceptionTicketDetailPage.test.tsx : chargement, détail, erreur, ID manquant. (4) AppNav : lien Réception conditionné à reception.access (permissions dans LoginResponse + AuthContext + CaisseContext). (5) Tests API POST tickets/{id}/close : 401 sans auth, 200 avec auth.

### File List

- api/models/poste_reception.py (modified)
- api/models/ticket_depot.py (new)
- api/models/__init__.py (modified)
- api/migrations/2026_02_27_6_1_reception_postes_tickets.sql (new)
- api/schemas/poste_reception.py (modified)
- api/schemas/ticket_depot.py (new)
- api/schemas/auth.py (modified — permissions dans LoginResponse)
- api/routers/v1/reception.py (modified — order_by/limit poste courant ; close ticket)
- api/routers/v1/auth.py (modified — permissions dans login/pin response)
- frontend/package.json (modified — @mantine/core, @mantine/hooks, postcss)
- frontend/postcss.config.cjs (new)
- frontend/src/main.tsx (modified — MantineProvider, @mantine/core/styles.css)
- frontend/src/api/reception.ts (new)
- frontend/src/api/auth.ts (modified — permissions dans PinLoginResponse)
- frontend/src/auth/AuthContext.tsx (modified — permissions, setFromPinLogin(..., permissions))
- frontend/src/caisse/CaisseContext.tsx (modified — setFromPinLogin avec permissions)
- frontend/src/caisse/AppNav.tsx (modified — permissionCode reception.access, useAuth permissions)
- frontend/src/reception/ReceptionAccueilPage.tsx (new)
- frontend/src/reception/ReceptionAccueilPage.test.tsx (new)
- frontend/src/reception/ReceptionTicketDetailPage.tsx (new)
- frontend/src/reception/ReceptionTicketDetailPage.test.tsx (new)
- frontend/src/App.tsx (modified)
- api/tests/conftest.py (new)
- api/tests/__init__.py (new)
- api/tests/routers/__init__.py (new)
- api/tests/routers/reception/__init__.py (new)
- api/tests/routers/reception/test_reception_postes.py (new)
- api/tests/routers/reception/test_reception_tickets.py (new)
- api/requirements.txt (modified — pytest ajouté)

## Senior Developer Review (AI)

**Date :** 2026-02-27  
**Résultat :** changes-requested  
**Git vs File List :** Fichiers 6.1 présents en working tree (plusieurs en untracked). File List cohérente avec les fichiers livrés.

**Synthèse :** Les AC 1 à 5 sont couverts par l'implémentation (postes, tickets, API, frontend, migrations). Aucune tâche marquée [x] n'est fausse. Points bloquants pour approbation : (1) frontend réception n'utilise pas Mantine (alignement architecture/checklist v0.1), (2) tests API limités à 401 sans auth, pas de scénarios métier avec client authentifié, (3) pas de tests frontend pour la page détail ticket. Points mineurs : lien Réception visible sans vérification permission côté nav, tests manquants pour close ticket API.

**Décision :** Status → in-progress. Tâches « Review Follow-ups (AI) » ajoutées pour Mantine, tests API métier, tests frontend détail, et optionnels (AppNav, close ticket).

**Date (second passage) :** 2026-02-27  
**Résultat :** approved  
**Synthèse :** Les 5 follow-ups sont traités. Vérification : Mantine (ReceptionAccueilPage, ReceptionTicketDetailPage, main.tsx), tests API avec client fixture (conftest), tests frontend ReceptionTicketDetailPage (chargement, erreur, ID manquant), AppNav permission reception.access, tests POST tickets/{id}/close (401 + 200). 13 tests API réception et 5 tests frontend réception exécutés et passants. Status → done.

## Change Log

- 2026-02-27 : Story 6.1 implémentée — migrations poste_reception/ticket_depot, API réception (postes + tickets), frontend accueil réception (/reception, postes, tickets), tests frontend et API.
- 2026-02-27 : Code review adversarial (BMAD) — 4 MEDIUM, 2 LOW. Status → in-progress. Suivi : Mantine frontend réception, tests API métier, tests frontend détail ticket, optionnel AppNav permission et close ticket tests.
- 2026-02-27 : Suivi code review — Mantine (ReceptionAccueilPage, ReceptionTicketDetailPage, main.tsx, postcss). Tests API avec client authentifié (conftest StaticPool, override get_current_user + patch deps permissions). Tests frontend ReceptionTicketDetailPage. AppNav conditionné à reception.access (permissions dans auth login/pin + AuthContext). Tests POST tickets/{id}/close. GET postes/current avec order_by/limit. Status → review.
- 2026-02-27 : Code review adversarial (second passage) — 5 follow-ups vérifiés et traités. Tests exécutés : 13 API réception, 5 frontend réception. Résultat : approved. Status → done.
