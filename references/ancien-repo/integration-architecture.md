# Architecture d'intégration — RecyClique 1.4.4 (multi-part)

**Objectif :** Référence pour migration v0.1.0.

---

## Parties et flux

| De → Vers | Type | Détails |
|-----------|------|---------|
| **Frontend → API** | REST (HTTP/JSON) | Axios / React Query. Base URL configurable (ex. localhost:4433). Préfixe `/v1`. Auth : JWT Bearer (localStorage, 30 min). |
| **Bot → API** | REST (HTTP/JSON) | httpx. Endpoints : deposits (from-bot, classify), users (link-telegram), etc. Pas d'auth JWT côté bot (clé API ou équivalent à vérifier dans config bot). |
| **API → PostgreSQL** | SQL (SQLAlchemy) | Données métier. Migrations Alembic. |
| **API → Redis** | Cache / session | Sessions, rate limit (SlowAPI), éventuellement état bot. |
| **API → Brevo** | Email (HTTP) | Envoi email, webhooks (POST /v1/email/webhook, /v1/webhooks/brevo/...). |
| **API → kDrive / WebDAV** | Fichiers | Sync service (schedule_periodic_kdrive_sync), webdavclient3. |

---

## Points à migrer ou revoir

- Contrats REST (liste des endpoints et payloads) : voir `api-contracts-api.md`.
- Stratégie auth (JWT, durée, refresh) et lien bot ↔ API.
- Intégrations externes (Brevo, kDrive, exports Ecologic) : à conserver ou remplacer dans la v0.1.0.
