# Story 1.3: Docker Compose minimal et déploiement d'une instance

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'**admin technique**,
je veux **déployer l'instance complète (RecyClique en un container, Paheko, PostgreSQL, Redis) via Docker Compose**,
afin de **faire tourner RecyClique et ses dépendances en une seule commande**.

## Acceptance Criteria

1. **Audit Docker local (prérequis obligatoire)**  
   **Étant donné** Docker Desktop (ou équivalent) avec des containers existants possibles (ex. ancien RecyClique)  
   **Quand** l'admin exécute l'audit (ex. `docker ps -a`, `docker network ls`, `docker volume ls`) et documente l'existant  
   **Alors** une stratégie d'isolation est choisie (nom de projet Compose, préfixes) et documentée (README ou doc déploiement)  
   **Et** la création du `docker-compose.yml` et le premier `docker-compose up` respectent cette stratégie (pas de chevauchement de ports, noms, networks) ; **aucune suppression ni modification des containers, networks ou volumes existants** (audit en lecture seule).

2. **Déploiement via Docker Compose**  
   **Étant donné** un fichier `docker-compose.yml` et un Dockerfile pour RecyClique (build frontend puis image avec FastAPI servant dist + API)  
   **Quand** je lance `docker-compose up` avec les services RecyClique, Paheko (SQLite), PostgreSQL (RecyClique), Redis  
   **Alors** le container RecyClique démarre et sert le front et l'API ; le health check répond  
   **Et** les secrets et la config passent par variables d'environnement ou fichier `.env` (NFR-S2) ; les versions Python et Node sont figées dans le Dockerfile et documentées dans le README (checklist v0.1).

## Tasks / Subtasks

- [x] Task 1 : Audit Docker et stratégie d'isolation (AC: #1)
  - [x] Documenter la procédure d'audit (commandes `docker ps -a`, `docker network ls`, `docker volume ls`) dans README ou doc déploiement
  - [x] Définir et documenter la stratégie d'isolation : nom de projet Compose (ex. `recyclic` ou `jarvos_recyclique`), préfixes des services, ports dédiés pour éviter conflits avec l'existant
  - [x] Rappeler explicitement : audit en lecture seule — ne rien supprimer ni modifier dans les ressources Docker existantes
- [x] Task 2 : Dockerfile RecyClique (AC: #2)
  - [x] Créer un Dockerfile multi-stage : stage 1 build frontend (Node, `npm ci`, `npm run build` → `frontend/dist`) ; stage 2 image runtime Python avec FastAPI servant `frontend/dist` + API
  - [x] Figer les versions : Python 3.12 (ou version LTS documentée), Node 20 LTS pour le build (checklist v0.1)
  - [x] Exposer le port de l'application (ex. 8000) ; configurer l'utilisateur non-root si possible (bonnes pratiques)
- [x] Task 3 : docker-compose.yml et services (AC: #2)
  - [x] Déclarer les services : `recyclic` (build depuis Dockerfile, dépendances vers postgres et redis), `paheko` (image existante ou référence, SQLite), `postgres` (PostgreSQL pour RecyClique), `redis` (EventBus + file push)
  - [x] Définir `depends_on` pour le service RecyClique : postgres et redis (démarrage dans le bon ordre)
  - [x] Appliquer le nom de projet / préfixes selon la stratégie d'isolation (Task 1)
  - [x] Configurer les networks et volumes nécessaires (données PostgreSQL, Redis, Paheko SQLite si besoin) sans toucher aux ressources existantes
  - [x] Variables d'environnement : passer `DATABASE_URL`, `REDIS_URL`, et toute config RecyClique via `env_file` ou `environment` ; aucun secret en dur (NFR-S2)
- [x] Task 4 : Démarrage et health check (AC: #2)
  - [x] S'assurer que `docker-compose up` lance RecyClique après build frontend ; le container sert le SPA (statics + catch-all) et l'API ; `GET /health` répond avec status ok / database / redis
  - [x] Documenter la commande de démarrage et l'URL d'accès (ex. http://localhost:8000) dans le README
- [x] Task 5 : Documentation versions et config (AC: #2)
  - [x] Indiquer dans le README (ou doc déploiement) les versions Python et Node utilisées (alignées Dockerfile)
  - [x] Fournir un `.env.example` listant les variables requises (DATABASE_URL, REDIS_URL, etc.) sans valeurs sensibles

- [x] **Review Follow-ups (AI)**
  - [x] [AI-Review][MEDIUM] Documenter ou supprimer `requirements.txt` à la racine : présent dans le dépôt (avec pytest/httpx et pydantic-settings>=2.6.0) mais absent de la File List ; aligner avec `api/requirements.txt` (versions pydantic-settings 2.0 vs 2.6) ou documenter l'usage (dev local vs Docker) et mettre à jour la File List.
  - [x] [AI-Review][LOW] doc/deployment.md §2 : préciser comment exposer PostgreSQL sur l'hôte (ex. ajouter `ports: - "5433:5432"` au service postgres) si besoin.
  - [x] [AI-Review][LOW] Documenter que GET /health renvoie `database: "unconfigured"` tant que la couche DB n'est pas en place (même avec DATABASE_URL défini), pour éviter confusion.
  - [x] [AI-Review][LOW] Optionnel : ajouter un healthcheck au service Redis dans docker-compose pour renforcer depends_on.

## Dev Notes

- **Contexte déploiement** (epics.md) : Paheko a déjà été déployé en Docker avec dump de prod (instance dev/local existante). Cette story s'appuie sur cette hypothèse : l'intégration RecyClique ↔ Paheko cible une instance Paheko déjà en place. En 1.3, on livre un Compose minimal qui peut faire coexister RecyClique, Paheko (SQLite), PostgreSQL (RecyClique), Redis — sans modifier l'existant Docker.
- **Image Paheko** : utiliser l'image Docker officielle Paheko (ou la référence documentée dans le projet) pour le service `paheko` ; pas de build custom pour Paheko dans cette story.
- **Un seul container RecyClique** (architecture) : build frontend → `frontend/dist` inclus dans l'image ; FastAPI sert statics + API. Pas de séparation front/back en déploiement.
- **Secrets** : NFR-S2 — config via variables d'environnement ou fichier `.env` ; pas de secrets en dur dans le code ni dans les images. Documenter dans `.env.example` les clés attendues.
- **Versions** (checklist v0.1, architecture) : figer Python (ex. 3.12) et Node (ex. 20 LTS) dans le Dockerfile et les documenter dans le README.
- **Health check** : l'endpoint `GET /health` existe déjà (Story 1.2) ; en Compose, RecyClique doit pouvoir joindre PostgreSQL et Redis une fois les URLs configurées ; le health doit refléter l'état (ok / unconfigured / error).

### Project Structure Notes

- Fichiers à créer ou modifier : `Dockerfile` à la racine du repo (aligné architecture), `docker-compose.yml` à la racine, `.env.example` à la racine, `README.md` ou `doc/deployment.md` pour audit + démarrage.
- Alignement avec `_bmad-output/planning-artifacts/architecture.md` : Infrastructure & Deployment (Docker Compose, un container RecyClique, Paheko, Redis, PostgreSQL), config via env.

### Previous Story Intelligence (1.1, 1.2)

- **1.1** : Frontend dans `frontend/`, build → `frontend/dist/`, structure par domaine. Ne pas modifier la structure frontend.
- **1.2** : API dans `api/`, `main.py` avec routers sous `/api/*`, `GET /health` à la racine, StaticFiles sur `frontend/dist/assets` (monté `/assets`), route catch-all pour SPA. Config Pydantic Settings (`api/config/settings.py`). Le Dockerfile doit produire une image qui contient `frontend/dist` (build lors de l'image) et exécute l'API (Uvicorn/Gunicorn). En dev, si `frontend/dist` est absent, l'API affiche un message ; en image Docker, le build frontend est fait dans le stage de build.

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.3, prérequis audit et critères d'acceptation]
- [Source: _bmad-output/planning-artifacts/epics.md — Additional Requirements, Infrastructure et déploiement, Checklist v0.1 (versions Python/Node)]
- [Source: _bmad-output/planning-artifacts/architecture.md — Infrastructure & Deployment, Technical Constraints (un container RecyClique, Docker Compose)]
- [Source: _bmad-output/planning-artifacts/architecture.md — Project Structure & Boundaries, Complete Project Directory Structure (docker-compose.yml, Dockerfile à la racine)]
- [Source: _bmad-output/planning-artifacts/architecture.md — NFR-S2, config via env / secrets manager]

## Change Log

- **2026-02-26** : Implémentation story 1.3 — Docker Compose minimal. Ajout Dockerfile multi-stage (Node 20 + Python 3.12), docker-compose.yml (recyclic, paheko, postgres, redis), doc/deployment.md (audit + stratégie d'isolation), README.md racine, .env.example, api/requirements.txt. Health check GET /health et démarrage documentés.
- **2026-02-26** : Code review (adversarial). AC1 et AC2 validés ; tâches [x] vérifiées. 1 MEDIUM (requirements.txt racine non documenté / divergence versions), 3 LOW (doc 5433, health database unconfigured, healthcheck Redis optionnel). Status → in-progress ; follow-ups ajoutés. Review : changes-requested.
- **2026-02-26** : Corrections post-review. requirements.txt racine documenté (usage dev local + tests), pydantic-settings aligné 2.0.0 ; doc/deployment.md : exposition PostgreSQL 5433:5432, GET /health database unconfigured documenté ; healthcheck Redis ajouté dans docker-compose. File List mise à jour. Status → review.
- **2026-02-26** : Code review (2e passe). Vérification des 4 Review Follow-ups : tous conformes (requirements.txt racine, doc 5433, health unconfigured, healthcheck Redis). Review : approved. Status → done.

## Senior Developer Review (AI)

- **Git vs Story :** Fichier `requirements.txt` à la racine présent (pytest/httpx, pydantic-settings>=2.6.0) non listé dans la File List ; divergence avec `api/requirements.txt` (pydantic-settings>=2.0.0). Reste des fichiers story cohérents.
- **AC :** AC1 (audit, stratégie d'isolation, lecture seule) et AC2 (Compose, health check, env, versions) validés sur les fichiers.
- **Tasks :** Toutes les tâches [x] vérifiées (doc/deployment.md, Dockerfile, docker-compose.yml, README, .env.example).
- **Findings :** 1 MEDIUM (requirements.txt racine), 3 LOW (doc exposition PostgreSQL 5433, health database unconfigured à documenter, healthcheck Redis optionnel). Décision : changes-requested ; action items en Review Follow-ups.

**2e passe (post-corrections) :** Les 4 Review Follow-ups ont été vérifiés sur les fichiers : (1) requirements.txt racine documenté, pydantic-settings 2.0.0, File List à jour ; (2) doc/deployment.md §2 expose 5433:5432 ; (3) health database unconfigured documenté §3 et implémenté dans api/routers/admin/health.py ; (4) healthcheck Redis présent dans docker-compose.yml. Aucun nouveau finding. Décision : approved. Status → done.

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

- Build Docker RecyClique : `docker compose build recyclic` réussi (multi-stage Node 20 + Python 3.12).
- `docker compose up -d` peut échouer si le port 8080 (Paheko) est déjà utilisé sur l'hôte ; doc déploiement indique d'adapter le mapping ou de libérer le port après audit.

### Completion Notes List

- **Task 1** : Procédure d'audit et stratégie d'isolation documentées dans `doc/deployment.md` (commandes docker ps -a / network ls / volume ls, projet `jarvos_recyclique`, ports 8000 / 8080 / 5432 / 6379, audit lecture seule).
- **Task 2** : Dockerfile multi-stage créé à la racine : stage 1 Node 20-alpine (npm install ou npm ci si package-lock.json présent, npm run build → frontend/dist), stage 2 Python 3.12-slim (curl pour healthcheck, utilisateur non-root `app`, port 8000, CMD uvicorn api.main:app).
- **Task 3** : docker-compose.yml avec name `jarvos_recyclique`, services recyclic (build Dockerfile, depends_on postgres+redis avec condition healthy/started), paheko (image paheko/paheko, port 8080, volume SQLite), postgres (16-alpine, healthcheck), redis (7-alpine), networks et volumes dédiés, DATABASE_URL/REDIS_URL via environment et env_file .env.
- **Task 4** : Healthcheck Docker sur GET /health (curl), démarrage et URL documentés dans README (docker compose up --build, http://localhost:8000, http://localhost:8000/health).
- **Task 5** : Versions Python 3.12 et Node 20 LTS dans README et doc/deployment.md ; .env.example créé (DATABASE_URL, REDIS_URL, POSTGRES_PASSWORD, CORS_ORIGINS, DEBUG) sans valeurs sensibles.
- Fichiers ajoutés : api/requirements.txt (fastapi, uvicorn, pydantic-settings, redis), .gitignore (.env), README.md racine.
- **Post-review** : requirements.txt racine documenté et aligné (pydantic-settings>=2.0.0) ; doc/deployment.md : exposition PostgreSQL 5433:5432, health database unconfigured ; healthcheck Redis dans docker-compose.

### File List

- Dockerfile (racine)
- docker-compose.yml (racine)
- .env.example (racine)
- README.md (racine)
- requirements.txt (racine — dev local et tests ; Docker utilise api/requirements.txt)
- doc/deployment.md
- api/requirements.txt
- .gitignore (modifié : ajout .env)
