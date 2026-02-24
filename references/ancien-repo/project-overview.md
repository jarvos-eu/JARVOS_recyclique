# Aperçu projet — RecyClique 1.4.4 (analyse brownfield)

**Date d’analyse :** 2026-02-24  
**Objectif :** Analyse **référentielle** pour migration vers JARVOS Recyclique v0.1.0 (nouveau backend). Ne vise pas le développement continu de la branche 1.4.4.

---

## Résumé

- **Projet :** RecyClique (Recyclic) — outil de gestion pour ressourceries (POC en production test). Version analysée : 1.4.4.
- **Mission (README) :** Réduire le temps administratif des ressourceries, assurer la conformité réglementaire Ecologic. Bot Telegram (dépôts vocaux, classification IA), interface caisse, exports automatisés.
- **Type de dépôt :** Monorepo en 3 parties — **frontend** (web), **api** (backend), **bot** (backend).
- **Stack :** React 18 + Vite + Mantine + Zustand + React Query | FastAPI + SQLAlchemy + Alembic + PostgreSQL + Redis | python-telegram-bot + Redis. Docker Compose.
- **Architecture :** SPA → API REST ; Bot → API REST. PWA offline-first. JWT 30 min, rôles cashier / admin / super-admin.

---

## Tableau de référence rapide

| Élément | Détail |
|--------|--------|
| **Frontend** | `repo/frontend/` — React, TypeScript, Vite, Mantine, Zustand, React Query |
| **API** | `repo/api/` — FastAPI, /v1/*, PostgreSQL, Redis, Alembic |
| **Bot** | `repo/bot/` — Telegram, Redis, httpx vers API |
| **Documentation** | `repo/docs/` — architecture, PRD, stories BMAD, runbooks, tech-debt |
| **Déploiement** | Docker Compose, Nginx, scripts dans `scripts/`, CI dans `.github/workflows/` |

---

## Liens vers la documentation générée

Voir **index.md** dans ce dossier (`references/ancien-repo/index.md`) pour la liste complète des documents et le point d’entrée pour la migration.
