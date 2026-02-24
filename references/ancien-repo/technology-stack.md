# Stack technique — RecyClique 1.4.4

**Source :** `repo/`  
**Objectif :** Référence pour migration v0.1.0.

---

## Frontend (part: frontend)

| Catégorie | Technologie | Version | Justification |
|-----------|-------------|---------|---------------|
| Framework | React | 18.2 | UI principale |
| Build | Vite | 5.x | Bundler / dev server |
| UI | Mantine | 8.3 | Composants (forms, dates, notifications) |
| State | Zustand | 5.x | State global côté client |
| Data / API | React Query | 3.39 | Cache et appels API |
| HTTP | Axios | 1.6 | Client HTTP |
| Forms | react-hook-form | 7.48 | Formulaires |
| Validation | Zod | 4.1 | Schémas et validation |
| Routing | react-router-dom | 6.8 | SPA |
| Charts | Recharts | 3.2 | Graphiques |
| DnD | @dnd-kit | 6.x / 10.x | Drag & drop (panier, tri) |
| Tests | Vitest, Playwright | 1.x / 1.55 | Unit + E2E |
| Langage | TypeScript | (module) | type="module" dans package.json |

**Pattern architecture :** Composants React + stores Zustand + couche API (React Query/axios) vers backend FastAPI. PWA offline-first (README).

---

## API (part: api)

| Catégorie | Technologie | Version | Justification |
|-----------|-------------|---------|---------------|
| Framework | FastAPI | 0.104 | API REST async |
| Serveur | Uvicorn | 0.24 | ASGI |
| ORM | SQLAlchemy | 2.0.23 | Modèles et accès BDD |
| Migrations | Alembic | 1.12 | Schéma BDD |
| BDD | PostgreSQL | (psycopg2-binary 2.9) | Données métier |
| Cache / session | Redis | 5.0.1 | Session / rate limit |
| Auth | python-jose (JWT), passlib (bcrypt) | 3.3 / 1.7 | JWT + hachage mots de passe |
| Rate limit | SlowAPI | 0.1.9 | Limitation débit |
| Validation | Pydantic | 2.5 | Settings et schémas |
| Email | sib-api-v3-sdk (Brevo) | 7.6 | Envoi et webhooks |
| Fichiers / export | WebDAV (webdavclient3), ReportLab, OpenPyXL, PyPDF2 | 3.14 / 4.0 / 3.1 / 3.0 | Exports Ecologic, PDF, Excel |
| Métriques | prometheus-client | 0.19 | Métriques |
| Tests | pytest, pytest-asyncio, httpx | 7.4 / 0.21 | Tests API |

**Pattern architecture :** API REST en couches (routes → services → modèles), middleware CORS/TrustedHost/SlowAPI, lifespan (scheduler, kDrive sync, init super-admin). Base commune avec `recyclic_api.core.config`, `recyclic_api.core.database`.

---

## Bot (part: bot)

| Catégorie | Technologie | Version | Justification |
|-----------|-------------|---------|---------------|
| Framework | python-telegram-bot | 20.7 | Bot Telegram |
| API HTTP | FastAPI + Uvicorn | 0.104 / 0.24 | Webhook ou services internes |
| Cache / état | Redis | 5.0.1 | Persistance session (redis_persistence) |
| Config | Pydantic Settings | 2.5 | Configuration |
| HTTP client | httpx | 0.25 | Appels vers API Recyclic |

**Pattern architecture :** Handlers Telegram (start, help, registration, depot, classify, webhook, notification_api), services (user, session, redis_persistence, notification). Prévision LangChain/Gemini pour classification EEE (commentée dans api/requirements.txt).
