# Story 3.1: Users, JWT et gestion de compte (terrain)



Status: done



<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->



## Story



En tant qu'**opérateur terrain**,

je veux **me connecter à RecyClique avec un identifiant et un mot de passe et recevoir un token JWT**,

afin **d'accéder aux fonctionnalités selon mon rôle**.



## Acceptance Criteria



1. **Étant donné** les tables `users`, `user_sessions`, `login_history`, `registration_request` créées par migration  

   **Quand** je soumets mes identifiants à `POST /v1/auth/login`  

   **Alors** l'API retourne un JWT (access token + refresh token) ; les requêtes avec le token sont reconnues (FR16).



2. **Étant donné** un utilisateur authentifié  

   **Quand** j'utilise les endpoints de compte  

   **Alors** fonctionnent : logout, refresh, forgot-password, reset-password, PIN login (`POST /v1/auth/pin`) ; `GET/PUT /v1/users/me` (profil, password, PIN) ; secrets et config JWT en variables d'environnement (NFR-S2).



3. **Étant donné** le périmètre v1  

   **Quand** le livrable est livré  

   **Alors** il correspond à la migration/copie 1.4.4 (artefact 08 §2.1, artefact 09 §3.2/3.3, artefact 10 §4.1 à 4.6).



## Tasks / Subtasks



- [x] Task 1 : Migrations BDD users et auth (AC: 1, 3)

  - [x] Créer migration Alembic : tables `users`, `user_sessions`, `login_history`, `registration_request` (snake_case, index idx_* selon conventions).

  - [x] Aligner schéma sur 1.4.4 et `references/ancien-repo/checklist-import-1.4.4.md` (copy + consolidate + security).

- [x] Task 2 : Auth API — login, JWT, refresh, logout (AC: 1, 2)

  - [x] Implémenter `POST /v1/auth/login` (body: username, password) → JWT access + refresh.

  - [x] Implémenter `POST /v1/auth/refresh`, `POST /v1/auth/logout`.

  - [x] Middleware/dépendance FastAPI pour valider le JWT sur les routes protégées.

  - [x] Config JWT (secret, durée access/refresh) via Pydantic Settings / `.env` (NFR-S2).

- [x] Task 3 : Endpoints compte et mot de passe (AC: 2)

  - [x] `GET /v1/users/me`, `PUT /v1/users/me` (profil).

  - [x] `PUT /v1/users/me/password` (changement mot de passe).

  - [x] `PUT /v1/users/me/pin` (gestion PIN pour caisse).

  - [x] `POST /v1/auth/forgot-password`, `POST /v1/auth/reset-password` (email Brevo si applicable).

- [x] Task 4 : Connexion par PIN (AC: 2)

  - [x] `POST /v1/auth/pin` (body: pin) → tokens + user ; même JWT que login classique (artefact 10 §4.6).

- [x] Task 5 : Signup et workflow approbation (AC: 3)

  - [x] `POST /v1/auth/signup` ; enregistrement en `registration_request` ; workflow approbation admin (utilisateurs en attente).

- [x] Task 6 : Tests et santé

  - [x] Tests API (pytest) pour login, refresh, logout, /users/me ; pas de secrets en dur.

  - [x] Tests frontend : composants auth en `*.test.tsx` (Vitest + RTL + jsdom) selon convention projet (frontend/README.md).

  - [x] Vérifier que le health check existant n'est pas cassé ; ne pas modifier les routes health ni le montage des statics.



### Review Follow-ups (AI)



- [x] [AI-Review][HIGH] PUT /v1/users/me : vérifier unicité de l'email avant mise à jour (ou capturer IntegrityError et retourner 400). Sinon prise d'un email déjà utilisé → erreur 500. [api/routers/v1/users.py]

- [x] [AI-Review][MEDIUM] Documenter api/tests/conftest.py dans la File List de la story (fixtures db_session, client ajoutées pour les tests auth). [story File List]

- [x] [AI-Review][MEDIUM] POST /v1/auth/pin : charge tous les utilisateurs actifs avec PIN puis boucle pour vérifier le PIN — perf O(n) et fuite de timing. Envisager mitigation (ex. rate limit, index) pour la suite. [api/routers/v1/auth.py]

- [ ] [AI-Review][LOW] jwt_secret_key par défaut "change-me-in-production" — s'assurer que le déploiement impose bien la variable d'environnement. [api/config/settings.py]

- [ ] [AI-Review][LOW] reset_password : après reset, les refresh tokens existants restent valides ; optionnel v1 : invalider les sessions au reset. [api/routers/v1/auth.py]

- [ ] [AI-Review][LOW] LoginForm : pas d'appel API dans le composant (délégation au parent) — acceptable ; pas de test E2E vers /v1/auth/login dans ce livrable. [frontend/src/auth/LoginForm.tsx]



## Dev Notes



- **Auth & Security (architecture)** : JWT v0.1 pour le terrain ; secrets en env / secrets manager ; pas de secret en clair dans les requêtes (NFR-S1, NFR-S2). [Source: _bmad-output/planning-artifacts/architecture.md § Authentication & Security]

- **Préfixe API** : tous les endpoints auth/users sont sous le préfixe `/v1/` (ex. router monté avec `prefix="/v1/auth"`, `prefix="/v1"` pour users). [Source: epics.md Additional Requirements, artefact 09]

- **Réutilisation socle** : s'appuyer sur la structure livrée en Epic 1 (main, config, routers, health, statics) ; ne pas recréer ni modifier les routes health ni le montage des statics.

- **API** : REST, JSON ; endpoints pluriel snake_case ; erreur = `{ "detail": "..." }`. [Source: epics.md Additional Requirements]

- **BDD** : PostgreSQL RecyClique ; snake_case (tables pluriel), index `idx_{table}_{colonne}`. [Source: architecture.md, epics.md]

- **Règle brownfield** : Livrable = migration/copie depuis 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md` (copy + consolidate + security). Références : artefact 08 §2.1 (qui stocke quoi — users terrain en RecyClique), artefact 09 §3.2/3.3 (périmètre auth et users), artefact 10 §4 (traçabilité écran → appels API login, signup, profil, PIN).

- **Utilisateurs terrain** : source de vérité = RecyClique (tables `users`, `user_sessions`, `login_history`, `registration_request`). Comptes admin/compta = Paheko (hors scope cette story). [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md §2.1]

- **Frontend** : écrans Login, Signup, Profil, Forgot/Reset password, PIN (option) ; routes `/login`, `/signup`, etc. ; appels API selon artefact 10 §4.1 à 4.6. JWT ~30 min ; refresh via `POST /v1/auth/refresh`. [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md §4]



### Project Structure Notes



- **Backend** : `api/` avec `routers/` par domaine (`auth`, etc.), `schemas/`, `services/`, `models/`, `config/`. Routers auth dans `api/routers/auth/` (architecture § Structure Patterns).

- **Frontend** : `frontend/src/` avec sous-dossiers par domaine (`auth/`, `shared/`). Composants auth dans `frontend/src/auth/`. [Source: architecture.md]

- **Tests** : API = `tests/` à la racine de l'API, structure miroir (ex. `tests/routers/test_auth.py`). Frontend = tests co-locés `*.test.tsx` (Vitest + RTL + jsdom). [Source: architecture.md, règles projet]



### References



- [Source: _bmad-output/planning-artifacts/epics.md] Epic 3, Story 3.1, FR16, NFR-S2

- [Source: _bmad-output/planning-artifacts/architecture.md] Authentication & Security, API & Communication, structure backend/frontend

- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md] §2.1 Utilisateurs et rôles

- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md] §3.2 Authentification, §3.3 Utilisateurs

- [Source: references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md] §4.1 Login, §4.2 Signup, §4.4 Profil, §4.6 Connexion par PIN

- [Source: references/ancien-repo/checklist-import-1.4.4.md] Copy + consolidate + security

- [Source: references/ancien-repo/data-models-api.md] Modèles users/sessions si documenté



## Dev Agent Record



### Agent Model Used



{{agent_model_name_version}}



### Debug Log References



### Completion Notes List



- Migration Alembic 005 : tables users, user_sessions, login_history, registration_request (snake_case, index idx_*). Modèles SQLAlchemy User, UserSession, LoginHistory, RegistrationRequest.

- Auth v1 : POST /v1/auth/login, /refresh, /logout, /signup, /forgot-password, /reset-password, /pin. JWT via python-jose, passlib bcrypt. Dépendance get_current_user (api/core/deps.py) pour routes protégées. Config JWT dans settings (jwt_secret_key, jwt_algorithm, jwt_access_token_expire_minutes, jwt_refresh_token_expire_days).

- Users v1 : GET/PUT /v1/users/me, PUT /v1/users/me/password, PUT /v1/users/me/pin. Montage routers sous /v1/auth et /v1 (users).

- Tests API : 18 tests dans test_auth.py (login, refresh, logout, signup, pin, /users/me, password, pin, put_me email unique). Pas de secrets en dur.

- Tests frontend : LoginForm.tsx + LoginForm.test.tsx (Vitest + RTL + jsdom). Health check et routes existants non modifiés.

- Review follow-ups (2026-02-27) : PUT /v1/users/me vérifie unicité email avant update → 400 si email déjà pris ; POST /v1/auth/pin risque O(n)/timing documenté + TODO rate limit/index ; File List conftest déjà présente.



### Senior Developer Review (AI)



**Date :** 2026-02-27  

**Résultat :** changes-requested (1 HIGH, 2 MEDIUM, 3 LOW).



**Git vs story :** 1 fichier modifié non listé dans la File List : `api/tests/conftest.py` (fixtures db_session, client pour tests auth).



**CRITIQUE / HIGH :**

- PUT /v1/users/me : mise à jour de l'email sans vérification d'unicité. Si l'email est déjà pris par un autre utilisateur, la contrainte unique en BDD lève une exception non gérée → erreur 500. Il faut soit vérifier avant update, soit capturer IntegrityError et retourner 400 avec message explicite.



**MEDIUM :**

- File List incomplète : conftest.py modifié pour les tests auth mais non documenté.

- POST /v1/auth/pin : chargement de tous les utilisateurs actifs avec PIN puis boucle de vérification → coût O(n) et possible fuite par timing ; à traiter en suite (rate limit, index ou acceptation du risque v1).



**LOW :**

- Default jwt_secret_key dans settings ; s'assurer que la prod impose la variable d'environnement.

- reset_password n'invalide pas les refresh tokens existants (amélioration possible).

- LoginForm sans appel API direct (OK) ; pas de test E2E vers l'API dans ce livrable.



**AC / Tasks :** AC 1, 2, 3 couverts par l'implémentation. Tâches marquées [x] correspondent au code. Les points ci-dessus sont des correctifs ou améliorations à traiter en follow-up.



**Date (second passage) :** 2026-02-27  

**Résultat :** approved. Vérification des corrections : (1) PUT /v1/users/me vérifie unicité email via AuthService.get_user_by_email avant update → 400 si email déjà pris (api/routers/v1/users.py L35-44), test test_put_me_email_already_taken_400 présent ; (2) api/tests/conftest.py présent dans la File List ; (3) POST /v1/auth/pin documenté (risque O(n)/timing) + TODO rate limit/index (api/routers/v1/auth.py L126-131). Livrable complet, AC et tâches validés.



### File List



- api/db/alembic/versions/2026_02_27_005_create_users_auth_tables.py

- api/models/user.py

- api/models/user_session.py

- api/models/login_history.py

- api/models/registration_request.py

- api/models/__init__.py

- api/config/settings.py

- api/services/__init__.py

- api/services/auth.py

- api/schemas/auth.py

- api/schemas/user.py

- api/core/deps.py

- api/routers/v1/__init__.py

- api/routers/v1/auth.py

- api/routers/v1/users.py

- api/main.py

- api/requirements.txt

- api/tests/routers/test_auth.py

- api/tests/conftest.py

- frontend/src/auth/LoginForm.tsx

- frontend/src/auth/LoginForm.test.tsx

- frontend/src/auth/index.ts (export LoginForm)

- frontend/src/test/setup.ts

- frontend/package.json (scripts test, test:run)

- frontend/src/App.test.tsx (placeholder pour suite)

- _bmad-output/implementation-artifacts/sprint-status.yaml



## Change Log



- 2026-02-27 : Implémentation story 3.1 — migrations users/auth, API auth v1 (login, refresh, logout, signup, forgot/reset, pin), API users v1 (/me, password, pin), tests API pytest et frontend Vitest/RTL.

- 2026-02-27 : Code review adversarial — changes-requested ; 1 HIGH (unicité email PUT /users/me), 2 MEDIUM (File List conftest, perf PIN), 3 LOW ; Review Follow-ups ajoutés ; statut → in-progress.

- 2026-02-27 : Corrections review : PUT /v1/users/me unicité email (400), POST /v1/auth/pin doc risque + TODO ; Review Follow-ups HIGH et MEDIUM cochés.

- 2026-02-27 : Code review adversarial (second passage) — approved ; corrections HIGH et MEDIUM vérifiées ; statut → done.

