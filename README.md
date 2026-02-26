# JARVOS RecyClique

Application RecyClique (caisse, réception, administration) — frontend React (Vite, TypeScript) et API FastAPI. Intégration Paheko (compta, membres).

- **Frontend :** [frontend/README.md](frontend/README.md)
- **Déploiement (Docker Compose) :** [doc/deployment.md](doc/deployment.md)

## Déploiement Docker Compose

**Prérequis :** Docker Desktop (ou moteur Docker + Compose). Avant le premier démarrage, effectuer l’**audit Docker local** (lecture seule) et respecter la **stratégie d’isolation** décrites dans [doc/deployment.md](doc/deployment.md).

### Démarrer l’instance

À la racine du dépôt :

```bash
# Optionnel : copier .env.example vers .env pour surcharger les variables
# cp .env.example .env

docker compose up --build
```

- **RecyClique (SPA + API) :** http://localhost:8000  
- **Health check :** http://localhost:8000/health (status, database, redis)  
- **Paheko :** http://localhost:8080  

Le container RecyClique sert le frontend (build inclus dans l’image) et l’API ; il dépend de PostgreSQL et Redis (démarrage dans l’ordre via `depends_on`).

### Versions (checklist v0.1)

| Composant   | Version        |
|------------|----------------|
| Python     | 3.12           |
| Node (build)| 20 LTS         |
| PostgreSQL | 16             |
| Redis      | 7              |
| Paheko     | image `paheko/paheko` |

Ces versions sont figées dans le Dockerfile et le `docker-compose.yml`, et détaillées dans [doc/deployment.md](doc/deployment.md).

### Configuration et secrets

Aucun secret en dur dans le code ni dans les images. Les variables (DATABASE_URL, REDIS_URL, etc.) passent par le fichier `.env` ou les variables d’environnement. Voir [.env.example](.env.example) pour la liste des clés attendues (sans valeurs sensibles).
