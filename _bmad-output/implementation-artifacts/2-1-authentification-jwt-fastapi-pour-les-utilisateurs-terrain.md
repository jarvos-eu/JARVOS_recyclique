# Story 2.1: Authentification JWT (FastAPI) pour les utilisateurs terrain

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'opérateur terrain,
je veux me connecter à RecyClique avec un identifiant et un mot de passe et recevoir un token JWT,
afin d'accéder aux fonctionnalités selon mon rôle.

## Acceptance Criteria

1. **Étant donné** un utilisateur terrain avec identifiant et mot de passe valides  
   **Quand** je soumets mes identifiants à l'API (ex. POST /api/auth/login)  
   **Alors** l'API retourne un JWT (et éventuellement un refresh token) ; les requêtes avec le token dans le header sont reconnues (FR16)  
   **Et** les utilisateurs admin peuvent continuer à s'authentifier via Paheko (auth séparée) ; les secrets et la config JWT sont en env (NFR-S2).

## Tasks / Subtasks

- [x] **Backend — endpoint login et émission JWT** (AC: 1)
  - [x] Créer ou compléter le router `api/routers/auth/` avec POST `/api/auth/login` (body: identifiant, mot de passe).
  - [x] Valider les identifiants contre la source des utilisateurs terrain (PostgreSQL RecyClique : modèle utilisateur avec rôles). **Mots de passe** : toujours stockés hashés (bcrypt ou passlib) ; jamais en clair (NFR-S2).
  - [x] Émettre un JWT (access token) avec claims pertinents (sub, exp, rôle si besoin) ; optionnel : refresh token. Librairie : PyJWT ou python-jose (aligner avec les dépendances existantes).
  - [x] Config JWT (secret, algorithme, durée de vie) via Pydantic Settings / variables d'environnement (NFR-S2).
- [x] **Backend — dépendance d'authentification et protection des routes** (AC: 1)
  - [x] Mettre en place une dépendance FastAPI (ex. `api/core/deps.py`) qui lit le Bearer token du header Authorization, vérifie et décode le JWT, et expose l'utilisateur courant.
  - [x] Documenter ou appliquer le pattern sur au moins une route protégée (ex. GET /api/auth/me) pour prouver que « les requêtes avec le token sont reconnues ».
- [x] **Frontend — écran/login et stockage du token** (AC: 1)
  - [x] Page ou composant de login dans `frontend/src/auth/` (formulaire identifiant + mot de passe, appel POST /api/auth/login). **UI** : composants Mantine (alignement checklist v0.1 / 1.4.4).
  - [x] Stocker le token (ex. mémoire + localStorage ou sessionStorage selon politique) et l'envoyer dans le header Authorization pour les appels API suivants.
  - [x] Gérer les états isLoading/isPending et les erreurs (identifiants invalides, 401).
- [x] **Clarifier la frontière admin / terrain** (AC: 1)
  - [x] S'assurer que la doc ou le code indique que l'auth admin reste via Paheko (pas de conflit avec ce login JWT) ; pas d'implémentation Paheko dans cette story, uniquement « les utilisateurs admin peuvent continuer à s'authentifier via Paheko ».

- [x] **Review Follow-ups (AI)**
  - [x] [AI-Review][MEDIUM] Refuser ou avertir si JWT_SECRET_KEY vaut la valeur par défaut en production (api/config/settings.py) — risque sécurité si déploiement sans variable d'env.
  - [x] [AI-Review][MEDIUM] Documenter en dev : VITE_API_URL ou proxy Vite pour appels API vers backend (frontend README ou story) — éviter 404 login quand front 5173 / API 8000.
  - [x] [AI-Review][MEDIUM] Test unitaire GET /api/auth/me sans token → 401 sans dépendre de DATABASE_URL (api/tests/test_auth.py) — actuellement test skippé si pas de BDD.
  - [ ] [AI-Review][LOW] Optionnel : health check async ou éviter asyncio.run dans endpoint sync (api/routers/admin/health.py).
  - [ ] [AI-Review][LOW] Optionnel : max_length sur LoginRequest identifiant / mot_de_passe (api/schemas/auth.py) pour limiter DoS.

## Dev Notes

- **Auth & Security (architecture)** : JWT v0.1 pour le terrain ; secrets en env / secrets manager ; pas de secret en clair dans les requêtes (NFR-S2). Référence : `_bmad-output/planning-artifacts/architecture.md` — Authentication & Security, Naming Patterns (API), Format Patterns.
- **Emplacement code** : `api/routers/auth/` (login, éventuellement refresh, me) ; `api/core/deps.py` pour la dépendance get_current_user ; `api/config/settings.py` pour JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES (ou équivalent). Frontend : `frontend/src/auth/` (composant Login, contexte ou store auth si déjà prévu).
- **BDD RecyClique** : les utilisateurs terrain doivent être stockés côté RecyClique (PostgreSQL). Si un modèle `users` ou équivalent n'existe pas encore, le créer (id, username/login, **password hash** via bcrypt ou passlib, role, etc.) avec migrations ou scripts d'init cohérents avec la structure existante (snake_case, voir architecture).
- **Audit log** : tracer la connexion réussie (et optionnellement la déconnexion) dans la table dédiée (ex. `audit_events`) conformément à l'architecture (journal des actions métier).
- **Tests** : côté API, tests unitaires ou d'intégration pour POST /api/auth/login (succès, identifiants invalides, réponse contenant access_token). Côté frontend, tests co-locés `*.test.tsx` (Vitest + RTL) pour le formulaire de login et le comportement en cas d'erreur (convention v0.1).

### Project Structure Notes

- **API** : `api/routers/auth/` — endpoints pluriel snake_case (ex. `/api/auth/login`, `/api/auth/me`). Réponses succès = objet (ex. `{ "access_token": "...", "token_type": "bearer" }`) ; erreur = `{ "detail": "..." }` (FastAPI standard). Pas de secrets en dur.
- **Frontend** : `frontend/src/auth/` pour les écrans et composants d'authentification. Conventions : composants PascalCase, hooks camelCase, état immuable, isLoading/isPending pour le chargement (architecture § Process Patterns). **UI** : Mantine pour les composants du formulaire de login (checklist v0.1).

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 2, Story 2.1]
- [Source: _bmad-output/planning-artifacts/architecture.md — Authentication & Security, API & Communication Patterns, Implementation Patterns, Audit log]
- [Source: references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md — tests co-locés, Vitest+RTL, Mantine]
- [Source: _bmad-output/planning-artifacts/epics.md — Décisions architecturales de référence v0.1, NFR-S2]
- FR16 : authentification utilisateurs terrain via JWT (FastAPI) ; utilisateurs admin via Paheko (auth séparée).

## Dev Agent Record

### Agent Model Used

(à remplir par l'agent dev)

### Debug Log References

### Completion Notes List

- Backend : router auth avec POST /login (identifiant, mot_de_passe), validation contre PostgreSQL (modèle User, passlib bcrypt), émission JWT (PyJWT), config JWT dans settings (jwt_secret_key, jwt_algorithm, jwt_expire_minutes). Dépendance get_current_user dans api/core/deps.py, route protégée GET /api/auth/me. Table users et audit_events, init_db au lifespan, seed optionnel (SEED_TERRAIN_PASSWORD). Audit log sur connexion réussie (auth.login).
- Frontend : Mantine 7 (core + hooks + PostCSS), écran Login dans frontend/src/auth/, AuthContext (token localStorage, login, logout, isPending, erreurs), client API avec Authorization Bearer. App affiche Login si non authentifié, contenu si authentifié. Tests co-locés Login.test.tsx et App.test.tsx (Vitest + RTL), matchMedia mock en setup.
- Frontière admin/terrain : commentaires dans api/routers/auth/router.py et api/core/deps.py indiquant que l'auth admin reste via Paheko (séparée).
- Tests API : api/tests/test_auth.py (login succès, identifiants invalides, réponse access_token, me sans token → 401) ; nécessitent DATABASE_URL (skippés sinon). test_me_requires_auth_no_db : GET /me sans token → 401 sans BDD (mock get_async_session).
- **Review follow-ups MEDIUM (2026-02-26)** : (1) Refus de démarrage en production si JWT_SECRET_KEY vaut « change-me-in-production » (lifespan dans api/main.py). (2) Doc dev frontend : frontend/README.md (VITE_API_URL ou proxy Vite pour front 5173 → API 8000). (3) Test unitaire GET /api/auth/me sans token → 401 sans DATABASE_URL (test_me_requires_auth_no_db avec override get_async_session).

### File List

- api/requirements.txt (ajout sqlalchemy, asyncpg, passlib, pyjwt, pytest, pytest-asyncio, httpx)
- api/config/settings.py (jwt_secret_key, jwt_algorithm, jwt_expire_minutes, seed_terrain_password)
- api/main.py (modifié : refus démarrage prod si JWT_SECRET_KEY défaut dans lifespan)
- api/db/__init__.py (nouveau)
- api/db/session.py (nouveau)
- api/db/seed.py (nouveau)
- api/models/__init__.py (nouveau)
- api/models/base.py (nouveau)
- api/models/user.py (nouveau)
- api/models/audit_events.py (nouveau)
- api/schemas/__init__.py (nouveau)
- api/schemas/auth.py (nouveau)
- api/services/__init__.py (nouveau)
- api/services/auth_service.py (nouveau)
- api/core/deps.py (nouveau)
- api/routers/auth/router.py (modifié : login, me)
- api/routers/admin/health.py (modifié : ping BDD si configurée)
- api/tests/test_auth.py (nouveau ; test_me_requires_auth_no_db sans BDD)
- pytest.ini (nouveau)
- frontend/README.md (nouveau : doc dev VITE_API_URL / proxy)
- frontend/package.json (Mantine, postcss, user-event)
- frontend/postcss.config.cjs (nouveau)
- frontend/src/main.tsx (MantineProvider, style Mantine)
- frontend/src/App.tsx (AuthProvider, Login ou contenu)
- frontend/src/api/client.ts (nouveau)
- frontend/src/auth/types.ts (nouveau)
- frontend/src/auth/AuthContext.tsx (nouveau)
- frontend/src/auth/Login.tsx (nouveau)
- frontend/src/auth/Login.test.tsx (nouveau)
- frontend/src/App.test.tsx (modifié : mock useAuth, MantineProvider)
- frontend/src/test/setup.ts (matchMedia mock)

## Change Log

- 2026-02-26 : Implémentation story 2.1 — auth JWT (backend login/me, modèle User + audit_events, deps get_current_user), frontend Mantine + Login + AuthContext + stockage token, tests API et frontend, doc frontière admin/terrain.
- 2026-02-26 : Code review adversarial (BMAD QA). Résultat : changes-requested. AC et tâches implémentés. Sujets à traiter : JWT secret par défaut en prod, doc dev VITE_API_URL/proxy, test /me sans BDD. Follow-ups ajoutés en tâches ; statut → in-progress.
- 2026-02-26 : Corrections suite review (MEDIUM) : refus démarrage en prod si JWT_SECRET_KEY défaut (main.py lifespan), frontend/README.md pour VITE_API_URL/proxy, test test_me_requires_auth_no_db (401 sans BDD). Statut → review.
- 2026-02-26 : Code review adversarial (second passage). Vérification des 3 MEDIUM : OK. Résultat : approved. Statut → done.

## Senior Developer Review (AI)

- **Date** : 2026-02-26
- **Résultat** : Changes requested
- **Git vs File List** : Fichiers story non commités (repo avec nombreux fichiers non suivis) ; File List cohérent avec les fichiers présents dans l'arbre.
- **AC** : AC1 implémenté (POST /api/auth/login, JWT, requêtes avec token reconnues, GET /me, frontière admin/terrain documentée).
- **Points MEDIUM** : (1) Secret JWT par défaut non refusé en production. (2) Dev frontend : VITE_API_URL ou proxy non documenté. (3) test_me_requires_auth skippé sans BDD — pas de test 401 sans dépendance BDD.
- **Points LOW** : health sync + asyncio.run ; test redondant ; pas de max_length sur LoginRequest.
- **Statut** : review — follow-ups MEDIUM traités (refus JWT secret défaut en prod, doc VITE_API_URL, test /me 401 sans BDD). jusqu'à résolution des follow-ups MEDIUM (ou décision d'accepter en l'état).


---
- **Date** : 2026-02-26 (second passage)
- **Résultat** : Approved
- **Vérification des 3 MEDIUM** : (1) api/main.py lifespan lève ValueError en prod si jwt_secret_key == "change-me-in-production". (2) frontend/README.md documente VITE_API_URL et proxy pour dev (5173 → 8000). (3) test_me_requires_auth_no_db exécuté avec succès sans DATABASE_URL (override get_async_session, JWT_SECRET_KEY pour lifespan). Aucune régression. Statut → done.
