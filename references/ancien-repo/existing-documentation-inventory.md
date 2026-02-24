# Inventaire de la documentation existante — RecyClique 1.4.4

**Racine :** `repo/`  
**Date :** 2026-02-24

---

## Documentation existante (inventaire)

| Fichier / dossier | Type | Partie | Description |
|-------------------|------|--------|-------------|
| `README.md` | readme | global | Mission, démarrage Docker, stack (React + FastAPI + PostgreSQL), rôles/permissions, Brevo |
| `docs/` | dossier | global | Documentation principale (architecture, PRD, stories, validation, bugs) |
| `docs/index.md` | index | global | Point d’entrée documentation (volumineux) |
| `docs/architecture/` | architecture | global | Architecture brownfield (index + chapitres 1–14, infra, déploiement, rollback) |
| `docs/architecture/index.md` | architecture | global | Sommaire architecture (analyse existant, stack, modèles, API, tests, sécurité) |
| `docs/architecture/9-infrastructure-et-dploiement.md` | deployment | global | Infra, sauvegarde PostgreSQL, rollback |
| `docs/architecture.old/` | architecture | global | Ancienne version (unified-project-structure, etc.) |
| `docs/prd/` | prd | global | PRD et épics (index dans docs/prd/) |
| `docs/v1.3.0-active/` | prd + architecture | global | PRD v1.3.0, architecture active, épics détaillés |
| `docs/v1.3.0-active/prd/` | prd | global | Épics 1–6, goals, contraintes, tests |
| `docs/v1.3.0-active/architecture/` | architecture | global | Architecture détaillée, schéma BDD, API, déploiement |
| `docs/stories/` | stories | global | User stories BMAD (~100 stories v4) |
| `docs/validation/` | validation | global | Specs validation (ex. validation-b45-p0-frontend-spec.md) |
| `docs/frontend-spec/` | spec | frontend | Spécifications frontend |
| `docs/bugs/` | bugs | global | Documentation bugs |
| `docs/qa/`, `docs/runbooks/` | qa / runbooks | global | Gates, runbooks (dev-workflow, rollback-test-guide) |
| `docs/pending-tech-debt/` | tech-debt | global | Stories tech debt (rollback, déploiement, Alembic, etc.) |
| `docs/migration-report.md`, `docs/final-migration-report.md` | migration | global | Rapports de migration |
| `docs/export_doc_ecosystem/`, `docs/eco-organismes/` | ecosystem | global | Exports, éco-organismes |
| `docs/meeting-transcription/` | script | global | Transcription réunions (README, etc.) |
| `frontend/README.md` | readme | frontend | Doc frontend |
| `api/tests/README.md`, `tests/README.md` | readme | api / global | Tests |
| `scripts/README*.md`, `scripts/*/README.md` | readme | global | Scripts (sécurité, load, meeting-transcription) |
| `.github/workflows/` | ci | global | CI (ex. alembic-check.yml) |

---

## Contexte utilisateur (pour cette analyse)

- **Objectif :** Analyse **référentielle uniquement** — pas de développement sur la branche 1.4.4.
- **Cible :** Migration vers **JARVOS Recyclique v0.1.0** avec **nouveau backend**.
- **Usage :** Identifier ce qu’il faut **migrer** (fonctionnel, métier, patterns, décisions) et ce qu’on **ne reprend pas**.
- **Priorité :** Alimenter le Brief, le PRD et l’architecture du refactor v0.1.0.

Aucune autre zone d’attention spécifique fournie ; l’analyse se concentre sur les éléments utiles à la migration.
