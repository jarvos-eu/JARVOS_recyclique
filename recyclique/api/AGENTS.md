# AGENTS — recyclique/api

## Purpose

Backend **canon** Recyclique v2 : paquet Python **`recyclic-api`** (FastAPI, SQLAlchemy 2.0 **sync**, Pydantic v2, Alembic). Exposé en HTTP pour **peintre-nano** ; image Docker Python 3.11 = référence runtime.

**Parents :** lire [`../../AGENTS.md`](../../AGENTS.md) puis ce fichier avant toute édition.

## Ownership

- **Strophe** — règles métier sensibles (admin, exports bulk, stats cross-site).
- **Agents** — endpoints, services, migrations, tests pytest ; respect convention ORM sync (Epic 26).

## Local contracts

- **ORM synchrone + FastAPI (Epic 26) :** si le corps n’utilise que `sqlalchemy.orm.Session` et des appels **synchrones**, utiliser **`def`**, pas `async def` ornemental. Réserver `async def` aux chemins avec **`await` réel** (upload, I/O async) et le **signaler** (commentaire ou note d’archi).
  - Norme : [`_bmad-output/planning-artifacts/architecture/2026-04-22-convention-routes-services-sync-orm-api-v1-epic-26.md`](../../_bmad-output/planning-artifacts/architecture/2026-04-22-convention-routes-services-sync-orm-api-v1-epic-26.md)
  - Pilotes code : `endpoints/categories.py`, `category_service.py`, `category_management.py`
- **Schémas OpenAPI reviewable :** source partagée `contracts/openapi/recyclique-api.yaml` — ne pas diverger silencieusement du contrat versionné.
- **Surfaces admin sensibles** (step-up PIN, idempotency, audit) : tableau dans [`README.md`](README.md) § Story 16.4.
- **Config :** `core/config.py` — CORS (`BACKEND_CORS_ORIGINS` / `FRONTEND_URL`), `ENVIRONMENT`.
- **Qualité Python :** Ruff, Black, isort — config unique `pyproject.toml` (pas de `pytest.ini`).

## Work guidance

- Setup local : [`README.md`](README.md) (`pip install -r requirements.txt -r requirements-dev.txt`, `pip install -e ".[dev]"`).
- Migrations : `migrations/`, `alembic.ini` — ne pas contourner Alembic pour le schéma cible prod.
- Nouvelle route : schéma Pydantic v2, service sync par défaut, test pytest miroir sous `tests/`.
- Changement d’API publique : mettre à jour **contracts/openapi** + régénération TS + tests — voir [`../../contracts/AGENTS.md`](../../contracts/AGENTS.md).
- Règles détaillées agents : [`../../_bmad-output/project-context.md`](../../_bmad-output/project-context.md) § Python.

## Verification

Référence complète : [`tests/README.md`](tests/README.md).

**Smoke local minimal (hors conteneur) :**

```bash
cd recyclique/api
python -m pytest tests/test_infrastructure.py
```

**Lot compose / CI élargi :** script et liste pytest réelle documentés dans `tests/README.md` (service `api-tests` commenté — ne pas supposer `docker-compose run api-tests`).

Avant PR API : pytest sur le périmètre touché + lint Ruff selon habitudes du repo. Pas de push sans OK Strophe ([`references/procedure-git-cursor.md`](../../references/procedure-git-cursor.md)).
