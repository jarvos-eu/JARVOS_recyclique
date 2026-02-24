# Structure du projet et classification — RecyClique 1.4.4

**Source analysée :** `references/ancien-repo/repo`  
**Objectif :** Analyse référentielle pour migration vers JARVOS Recyclique v0.1.0 (nouveau backend).  
**Date :** 2026-02-24

---

## 1. Project structure (vue d’ensemble)

- **Type de dépôt :** monorepo (multi-part)
- **Parties détectées :** 3 — frontend (web), api (backend), bot (backend)
- **Racine analysée :** `repo/`

### Arborescence principale

```
repo/
├── api/                    # Backend FastAPI (Python)
│   ├── src/                # Code source API
│   ├── tests/
│   ├── requirements.txt, requirements-dev.txt, requirements-migrations.txt
│   └── ...
├── frontend/               # Interface web React (TypeScript, Vite)
│   ├── src/
│   ├── package.json        # v1.4.4
│   └── ...
├── bot/                    # Bot Telegram (Python)
│   ├── requirements.txt
│   └── ...
├── docs/                   # Documentation (architecture, PRD, stories)
├── scripts/                # Déploiement, backup, migrations, utilitaires
├── tests/                  # Tests E2E / intégration
├── docker-compose*         # Orchestration des services
├── README.md
└── package.json            # Racine (dépendances de test uniquement)
```

---

## 2. Project parts metadata

| Part ID   | Type (CSV) | Stack principal | Racine      | Rôle |
|-----------|------------|------------------|-------------|------|
| **frontend** | web     | React 18, Vite, Mantine, Zustand, React Query | `repo/frontend/` | PWA caisse + admin, offline-first |
| **api**      | backend | FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis | `repo/api/`     | REST API, auth, exports, métier |
| **bot**      | backend | Python (Telegram) | `repo/bot/`     | Enregistrement vocal, classification IA (prévu LangChain/Gemini) |

- **Détection :** `key_file_patterns` (package.json, requirements.txt, structure api/ frontend/ bot/) alignés avec les types **web** et **backend** du fichier documentation-requirements.csv.
- **Intégration :** Frontend appelle l’API (axios, React Query) ; bot indépendant (polling). Pas de workspace monorepo (pnpm/lerna) au niveau racine.

---

## 3. Validation classification

Cette classification est destinée à une **analyse référentielle uniquement** : elle sert à identifier ce qui doit être migré vers la v0.1.0 et ce qui peut être laissé de côté. Elle ne vise pas le développement continu de la branche 1.4.4.

Si la classification te convient, on enchaîne avec l’inventaire de la documentation existante et le contexte utilisateur (étape 2).
