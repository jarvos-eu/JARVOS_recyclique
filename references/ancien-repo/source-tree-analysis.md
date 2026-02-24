# Arbre source et dossiers critiques — RecyClique 1.4.4

**Racine :** `repo/`

---

## Arborescence annotée

```
repo/
├── api/                          # Backend FastAPI (part: api)
│   ├── src/recyclic_api/
│   │   ├── main.py               # Point d'entrée ASGI, lifespan, CORS, rate limit
│   │   ├── api/api_v1/
│   │   │   ├── api.py            # Agrégation des routers (prefix /v1)
│   │   │   └── endpoints/        # Routes par domaine (auth, users, sales, reception, admin...)
│   │   ├── core/                 # config, database, auth
│   │   ├── models/               # SQLAlchemy (User, Sale, Category, CashSession...)
│   │   ├── schemas/              # Pydantic (requêtes/réponses)
│   │   ├── services/             # Logique métier (cash_session, category, export, email...)
│   │   ├── utils/                # rate_limit, session_metrics, classification_cache...
│   │   └── initial_data.py       # Init super-admin
│   ├── alembic.ini, alembic/     # Migrations BDD
│   ├── tests/
│   └── requirements*.txt
│
├── frontend/                     # Frontend React (part: frontend)
│   ├── src/
│   │   ├── main.tsx, App.tsx     # Entrée SPA
│   │   ├── components/           # ui, layout, tickets, presets, categories, business
│   │   ├── pages/ ou routes/     # Pages / routes
│   │   ├── api/ ou services/     # Client API (axios, React Query)
│   │   └── stores/               # Zustand (si présent)
│   ├── package.json              # v1.4.4
│   └── vite.config.*
│
├── bot/                          # Bot Telegram (part: bot)
│   ├── src/
│   │   ├── main.py               # Entrée bot
│   │   ├── webhook_server.py     # Serveur webhook (optionnel)
│   │   ├── handlers/             # start, help, registration, depot, classify, webhook, notification_api
│   │   ├── services/             # user, session, redis_persistence, notification
│   │   └── config.py
│   └── requirements.txt
│
├── docs/                         # Documentation (architecture, PRD, stories, runbooks)
│   ├── index.md                  # Entrée doc (volumineux)
│   ├── architecture/            # Brownfield architecture
│   ├── prd/, v1.3.0-active/     # PRD, épics
│   ├── stories/                  # User stories BMAD
│   ├── validation/, frontend-spec/, bugs/, qa/, runbooks/
│   └── pending-tech-debt/, migration-report...
│
├── scripts/                      # Déploiement, backup, migrations, utilitaires
├── tests/                        # Tests E2E / intégration (hors api/ et frontend/)
├── docker-compose*.yml           # Orchestration
├── README.md
└── package.json                  # Dev (test deps seulement)
```

---

## Points d’intégration

- **Frontend → API :** Appels HTTP vers base URL API (ex. localhost:4433), préfixe `/v1`. Auth : JWT dans en-tête ou localStorage.
- **Bot → API :** httpx vers même API (deposits, users, etc.). Pas de file d’événements partagée.
- **BDD :** PostgreSQL partagée par l’API ; Redis pour sessions / rate limit / bot state.
