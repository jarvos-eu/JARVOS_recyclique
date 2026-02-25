# Patterns d'architecture — RecyClique 1.4.4

**Contexte :** Analyse référentielle pour migration. Ces patterns décrivent l'existant à prendre en compte (ou à remplacer) dans la v0.1.0.

---

## Vue d'ensemble

- **Frontend :** SPA React (Vite), state Zustand + React Query, appel REST vers une seule API. PWA offline-first.
- **API :** Backend monolithique FastAPI (routes, services, modèles SQLAlchemy), PostgreSQL + Redis, JWT 30 min, pas de microservices.
- **Bot :** Processus séparé (Telegram), Redis pour état/session, communication avec l'API via HTTP (httpx).
- **Intégration :** Frontend → API (REST) ; Bot → API (REST). Pas de file d'événements partagée.

---

## Frontend

- **Architecture :** Composants + hooks, stores Zustand par domaine, React Query pour les données serveur.
- **Entrée :** Vite dev/build, pas de SSR.
- **Auth :** Token JWT en localStorage, expiration 30 min, reconnexion manuelle (README).
- **Rôles :** cashier, admin, super-admin (caisse vs administration).

---

## API

- **Architecture :** Style “API-centric” : `api_router` (api_v1), sous-routes par domaine ; services métier ; modèles SQLAlchemy + Alembic.
- **Points d'entrée :** `recyclic_api.main` (FastAPI app), lifespan (scheduler, kDrive, init DB/super-admin).
- **Sécurité :** JWT (python-jose), bcrypt, SlowAPI (rate limit), CORS, TrustedHost.
- **Données :** PostgreSQL (moteur + SessionLocal), migrations via Alembic.

---

## Bot

- **Architecture :** Handlers par intention (start, help, inscription, dépôt, classification), services (user, session, redis, notification). Peut tourner en polling ou webhook (webhook_server).
- **État :** Redis (persistance session/dépôt).
- **Intégration :** Appels HTTP vers l'API Recyclic pour enregistrement et métier.

---

## Déploiement (existant)

- Docker Compose (README, docs/architecture/9).
- Services : API (port 4433), Frontend (4444), Bot (polling). Sauvegarde PostgreSQL, rollback et feature flags documentés.

---

## Utile pour la migration v0.1.0

- **À reprendre ou s'en inspirer :** Règles métier (caisse, catégories EEE, exports Ecologic), rôles et permissions, flux inscription, structure des épics/stories et de la doc (PRD, architecture).
- **À revoir / remplacer :** Nouveau backend (stack et découpage à définir), stratégie auth/session (durée, refresh), choix PWA/offline, périmètre du bot et intégration IA.
