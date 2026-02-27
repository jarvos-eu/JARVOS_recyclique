# Story 3.4: Démarrer un poste (caisse ou réception) avec un compte administrateur

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->
<!-- HITL (optionnel) : après livraison, valider le flux multi-sites (choix lieu/caisse) avant 3.5 — voir epics.md HITL-3.4. -->

## Story

En tant qu'**administrateur**,
je veux **démarrer un poste de caisse ou de réception en sélectionnant le site et la caisse**,
afin **qu'un opérateur puisse ensuite utiliser ce poste**.

## Acceptance Criteria

1. **Étant donné** un utilisateur avec rôle admin authentifié et des sites + postes existants (Epic 2)  
   **Quand** je demande l'ouverture d'un poste caisse ou réception pour un site/caisse donné  
   **Alors** le poste est enregistré et l'état est disponible (FR14) ; l'action est tracée (audit_events).

2. **Étant donné** un contexte multi-sites / multi-caisses  
   **Quand** l'admin démarre un poste caisse  
   **Alors** le site et la caisse sont correctement associés au poste (site_id, register_id) ; l'état « poste démarré » est consultable (ex. GET /v1/cash-registers/status ou équivalent).

3. **Étant donné** un admin qui démarre un poste réception  
   **Quand** l'admin appelle l'ouverture d'un poste de réception  
   **Alors** le poste réception est créé (table poste_reception ou équivalent) et tracé en audit_events ; un opérateur avec reception.access peut ensuite l'utiliser (Epic 6).

4. **Étant donné** le périmètre v1  
   **Quand** le livrable est livré  
   **Alors** il correspond à la migration/copie 1.4.4 (artefact 08 §2.2, artefact 09 §3.8, artefact 10 §5.1 et §6.1/6.2).

## Tasks / Subtasks

- [ ] Task 1 : Backend — état « poste caisse démarré » et API (AC: 1, 2, 4)
  - [ ] Définir et persister l'état « poste caisse démarré » : soit colonnes sur `cash_registers` (ex. `started_at`, `started_by_user_id`), soit table dédiée (ex. `register_starts`) selon convention 1.4.4 ; migration Alembic si nouveau schéma.
  - [ ] Endpoint **POST /v1/cash-registers/{register_id}/start** (ou **POST /v1/admin/cash-registers/start** avec body `{ site_id, register_id }`) : permission admin ; vérifier site_id et register_id cohérents (register appartient au site) ; enregistrer l'état ; retourner 200 + état.
  - [ ] Optionnel : **POST /v1/cash-registers/{register_id}/stop** pour « arrêter » le poste (remettre started_at à null) ; permission admin.
  - [ ] S'assurer que **GET /v1/cash-registers** et **GET /v1/cash-registers/status** exposent l'état démarré (started_at / started_by) pour que le dashboard caisse (artefact 10 §5.1) et les opérateurs puissent voir quels postes sont prêts.
- [ ] Task 2 : Backend — audit démarrage poste caisse (AC: 1)
  - [ ] À chaque démarrage (et éventuellement arrêt) de poste caisse : enregistrer un événement dans `audit_events` (action ex. `register_started`, `register_stopped` ; resource_type `cash_register`, resource_id register_id ; details site_id, user_id). Réutiliser le modèle AuditEvent et la logique d'écriture de la story 3.3.
- [ ] Task 3 : Backend — démarrage poste réception (AC: 1, 3, 4)
  - [ ] Exposer ou réutiliser **POST /v1/reception/postes/open** (artefact 10 §6.2) avec permission **admin** (en plus ou à la place de reception.access pour l'ouverture par un admin). Body `{ opened_at? }` selon spec. Créer l'enregistrement poste réception (table `poste_reception` ou équivalent selon 1.4.4).
  - [ ] Enregistrer un événement d'audit (action ex. `reception_post_opened`, resource_type `reception_post`, resource_id poste_id) pour l'ouverture par un admin.
  - [ ] Si la table `poste_reception` ou les endpoints réception ne sont pas encore livrés (Epic 6), livrer un contrat d'API et un stub backend (route + audit) pour que le frontend admin puisse appeler « Démarrer poste réception » ; l'implémentation complète restera en Epic 6.
- [ ] Task 4 : Frontend — écran admin « Démarrer un poste » (AC: 1, 2, 3)
  - [ ] Écran (ou modal) accessible aux seuls admins : choix « Caisse » ou « Réception ». Pour **Caisse** : liste des sites (GET /v1/sites), puis liste des postes du site (GET /v1/cash-registers?site_id=… ou filtre côté front), bouton « Démarrer ce poste » → POST start register ; affichage du succès et de l'état. Pour **Réception** : bouton « Ouvrir un poste réception » → POST /v1/reception/postes/open (si implémenté) ou appel stub ; affichage du succès.
  - [ ] Route suggérée : `/admin/start-post` ou depuis le dashboard admin avec entrée « Démarrer un poste (caisse/réception) ». Aligner sur artefact 10 §5.1 (données affichées, appels API au chargement).
  - [ ] Gestion des erreurs (403, 404, 400) et message de succès ; pas de secret ni token exposé.
- [ ] Task 5 : Tests et non-régression (AC: 1–4)
  - [ ] Tests API (pytest) : POST start register avec admin → 200 et état enregistré ; sans admin → 403 ; site_id/register_id incohérents → 400 ; vérifier audit_events. POST reception/postes/open avec admin → 201 ou 200 selon implémentation ; audit créé.
  - [ ] Tests frontend (Vitest + RTL + jsdom) : composant ou page « Démarrer un poste » (affichage sites/postes, soumission caisse, message succès/erreur) ; co-locés `*.test.tsx`.
  - [ ] Vérifier que les flows 3.1, 3.2, 3.3 et les endpoints Epic 2 (sites, cash-registers) ne régressent pas.

## Dev Notes

- **FR14** : Un administrateur peut démarrer un poste (caisse ou réception) avec un compte administrateur. [Source: epics.md FR Coverage Map]
- **Prérequis** : Story 3.1 (auth) + Epic 2 stories 2.1 et 2.2 (sites, cash_registers). Réutiliser `get_current_user` et `require_permissions` (admin) dans `api/core/deps.py` ; ne pas dupliquer la logique JWT.
- **Règle brownfield** : Livrable = migration/copie 1.4.4. Références : artefact 08 §2.2 (sites, postes de caisse en RecyClique), §2.4 (postes de réception) ; artefact 09 §3.8 (cash-registers, status) ; artefact 10 §5.1 (Dashboard caisses — choix type, liste postes, statut), §6.1/6.2 (accueil réception, ouverture poste). [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md, 2026-02-26_09_perimetre-api-recyclique-v1.md, 2026-02-26_10_tracabilite-ecran-donnees-appels-api.md]
- **Audit** : Réutiliser le modèle `AuditEvent` et la table `audit_events` livrés en story 3.3 (`api/models/audit_events.py`) ; même pattern (action, resource_type, resource_id, details, user_id). Si possible, même transaction que l'action (démarrage/arrêt) pour éviter état incohérent (voir 3.3). [Source: _bmad-output/implementation-artifacts/3-3-gestion-des-pin-operateur-caisse-et-deverrouillage-de-session.md]
- **Multi-sites / multi-caisses** : Lors du démarrage caisse, vérifier que le `register_id` appartient bien au `site_id` (contrainte FK ou requête) pour éviter des associations incorrectes.
- **Réception** : Si les modèles/endpoints réception (poste_reception, POST /v1/reception/postes/open) ne sont pas encore en place (Epic 6), livrer un stub (route admin + audit) pour que le flux admin « Démarrer poste réception » soit cohérent ; l'implémentation métier complète reste dans Epic 6.

### Project Structure Notes

- **Backend** : Routers sous `api/routers/` (préfixe `/v1` au montage) — aligner l'emplacement avec le mapping architecture : caisse/POS → `api/routers/pos/`, admin → `api/routers/admin/`. Soit étendre un router `cash_registers` (ou `admin`), soit créer une route dédiée sous `admin` pour « start register ». Réception : `api/routers/v1/reception.py` ou équivalent pour POST postes/open. Modèles : `cash_registers` (Epic 2) ; ajout colonnes ou table register_starts selon choix ; `poste_reception` si déjà prévu (sinon stub). Audit : `api/models/audit_events.py` (existant, story 3.3).
- **Frontend** : Nouvelle page ou section sous `frontend/src/admin/` (ex. `StartPostPage.tsx` ou `StartPost.tsx`) ; routes `/admin/start-post` ou intégration dans le dashboard admin. Appels API : GET /v1/sites, GET /v1/cash-registers, POST start, POST reception/postes/open. Aligner sur Mantine (convention projet).
- **Tests** : API = `api/tests/routers/test_cash_registers.py` ou `test_admin_start_post.py` ; frontend = tests co-locés `*.test.tsx`.

### References

- [Source: _bmad-output/planning-artifacts/epics.md] Epic 3, Story 3.4, FR14, HITL-3.4
- [Source: _bmad-output/planning-artifacts/architecture.md] Authentification (compte admin pour postes), Audit log (audit_events, `api/models/audit_events.py`), mapping structure (admin, pos)
- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md] §2.2 Sites et postes, §2.4 Réception (poste_reception)
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md] §3.8 cash-registers, GET/POST status ; réception postes/open
- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md] §5.1 Dashboard caisses, §6.1 Accueil réception, §6.2 Ouverture poste réception
- [Source: references/ancien-repo/checklist-import-1.4.4.md] Copy + consolidate + security
- [Source: _bmad-output/implementation-artifacts/3-3-gestion-des-pin-operateur-caisse-et-deverrouillage-de-session.md] AuditEvent, audit_events, enregistrement session_unlocked
- [Source: _bmad-output/implementation-artifacts/3-2-groupes-permissions-et-rbac.md] require_permissions, admin, routes /v1/sites, /v1/cash-registers

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- **Task 1–2** : Colonnes `started_at` et `started_by_user_id` sur `cash_registers` (migration 007). POST /v1/admin/cash-registers/start (body `site_id`, `register_id`) et POST /v1/cash-registers/{register_id}/stop ; GET /v1/cash-registers et GET /v1/cash-registers/status exposent started_at/started_by_user_id ; statut « started » vs « free ». Audit `register_started` / `register_stopped` dans la même transaction (modèle `api/models/audit_event.py`).
- **Task 3** : Table `poste_reception` (migration 008), modèle `PosteReception` ; POST /v1/reception/postes/open (admin ou reception.access), body `opened_at?` ; audit `reception_post_opened`. Router v1/reception monté sous /v1.
- **Task 4** : Page `StartPostPage.tsx` (frontend/src/admin/) : choix Caisse/Réception, chargement sites puis postes, soumission caisse (POST start) et réception (POST postes/open), messages succès/erreur. Client API dans frontend/src/api/admin.ts. Route à brancher sur /admin/start-post lorsque le routeur app est en place.
- **Task 5** : Tests API dans test_admin_start_post.py (start/stop, 403/400, audit, status, reception open). Tests frontend StartPostPage.test.tsx (affichage, soumission, messages). Non-régression : tests cash_registers et auth inchangés.

### File List

- api/db/alembic/versions/2026_02_27_007_cash_registers_started_at_started_by.py
- api/db/alembic/versions/2026_02_27_008_create_poste_reception_table.py
- api/models/cash_register.py
- api/models/poste_reception.py
- api/models/__init__.py
- api/schemas/cash_register.py
- api/schemas/poste_reception.py
- api/routers/cash_registers.py
- api/routers/v1/admin/cash_registers_start.py
- api/routers/v1/admin/__init__.py
- api/routers/v1/reception.py
- api/routers/v1/__init__.py
- api/main.py
- api/tests/conftest.py
- api/tests/routers/test_admin_start_post.py
- frontend/src/api/admin.ts
- frontend/src/api/index.ts
- frontend/src/admin/StartPostPage.tsx
- frontend/src/admin/StartPostPage.test.tsx

## Senior Developer Review (AI)

**Date:** 2026-02-27  
**Résultat:** Approved (après correction mineure)

### Vérifications effectuées

- **AC 1–4** : Validés. Poste caisse (start/stop) et réception (postes/open) enregistrés et tracés en audit_events ; GET /v1/cash-registers et /status exposent started_at/started_by ; site_id/register_id vérifiés ; table poste_reception et POST /v1/reception/postes/open avec admin ou reception.access.
- **Tasks** : Implémentation conforme (migrations 007/008, routers admin + reception, StartPostPage + client API, tests pytest et Vitest).
- **Sécurité** : Permission admin sur start/stop et réception ; pas de token exposé côté front.

### Correction appliquée pendant la review

- **Détails d'audit** : Remplacement de la construction en f-string des champs `details` par `json.dumps(...)` dans `api/routers/v1/admin/cash_registers_start.py` et `api/routers/cash_registers.py` (stop), pour garantir un JSON valide et éviter tout risque d'échappement.

### Points de vigilance (non bloquants)

- **Route frontend** : La page `StartPostPage` n'est pas encore montée dans l'app (App.tsx vide) ; les Completion Notes indiquent « Route à brancher sur /admin/start-post lorsque le routeur app est en place » — cohérent avec l'état actuel du frontend.

## Change Log

| Date       | Author | Change |
|------------|--------|--------|
| 2026-02-27 | AI QA  | Code review adversarial : AC et tasks validés ; correction audit details (json.dumps) ; statut → done. |
