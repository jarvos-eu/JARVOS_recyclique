# API RecyClique

Application FastAPI : routes métier sous `/api`, health à la racine, statics + SPA.

**Statics / SPA :** Les statics du SPA Vite sont servis via StaticFiles : le répertoire `frontend/dist/assets` est monté sur `/assets` (et non tout `frontend/dist`). L’`index.html` est servi par la route catch-all pour le routage côté client.

**Traçabilité Git :** Les dossiers et fichiers `api/` et `requirements.txt` sont à committer par le développeur pour la traçabilité git.

## Démarrage

```bash
# Depuis la racine du repo
pip install -r requirements.txt
uvicorn api.main:app --reload
```

- API : http://127.0.0.1:8000  
- Health : http://127.0.0.1:8000/health  
- Docs : http://127.0.0.1:8000/docs  

Si le build frontend n'existe pas (`frontend/dist/`), exécuter d'abord `npm run build` dans `frontend/`.

## Patterns API (futures routes métier)

- **Réponses** : **snake_case** pour tous les champs JSON.
- **Dates** : **ISO 8601** (ex. `2026-02-26T08:00:00Z`).
- **Montants** : en **centimes** (entiers) pour éviter les erreurs d'arrondi.
- **Config** : pas de secrets en dur ; `api/config/settings.py` (Pydantic Settings, `.env`).

## Structure

- `config/` — settings Pydantic
- `routers/` — auth, pos, reception, admin (health dans admin, exposé en GET /health)
- `schemas/`, `services/`, `models/`, `db/`, `core/` — à enrichir selon les stories
