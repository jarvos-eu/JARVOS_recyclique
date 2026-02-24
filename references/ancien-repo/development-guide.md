# Guide de développement — RecyClique 1.4.4 (référence migration)

---

## Prérequis

- **API :** Python 3.x, PostgreSQL, Redis. Dépendances : `api/requirements.txt`, `api/requirements-dev.txt`.
- **Frontend :** Node.js, npm/pnpm. Dépendances : `frontend/package.json`.
- **Bot :** Python, Redis. Dépendances : `bot/requirements.txt`.
- **Global :** Docker et Docker Compose (recommandé pour dev local).

---

## Démarrage rapide (README)

```bash
docker-compose up
```

Création du premier super-admin :

```bash
docker-compose exec api sh /app/create_admin.sh votre_nom_utilisateur votre_mot_de_passe_securise
```

- API : http://localhost:4433  
- Frontend : http://localhost:4444  
- Bot : mode polling

---

## Commandes utiles (hors Docker)

- **API :** `uvicorn` avec module `recyclic_api.main:app` (depuis `api/`, avec PYTHONPATH ou install en mode editable). Migrations : `alembic upgrade head`.
- **Frontend :** `npm run dev` / `vite` (depuis `frontend/`). Build : `npm run build`. Tests : `npm run test`, `npm run test:run`.
- **Tests API :** pytest depuis `api/` (voir `api/tests/`).

---

## Configuration

- **API :** Fichier `.env` dans `api/` (copier depuis `env.example`). Variables notables : Brevo (BREVO_API_KEY, BREVO_WEBHOOK_SECRET), BDD, Redis, JWT.
- **Sessions :** JWT 30 min, pas de refresh automatique (reconnexion manuelle).

---

## Conventions (README / docs)

- Méthodologie BMad : documentation-first, épics/stories, tests pyramidaux, TypeScript/Python.
- Rôles : cashier, admin, super-admin (caisse vs administration).

Ce guide sert de **référence** pour la migration v0.1.0 ; les procédures exactes (env, scripts) sont dans le repo source.
