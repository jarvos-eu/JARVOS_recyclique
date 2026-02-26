# Story 1.1: Initialiser le frontend (Vite React TS) et la structure des dossiers par domaine

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'**admin technique ou développeur**,
je veux **un frontend RecyClique initialisé avec Vite (template react-ts) et une arborescence par domaine (caisse, reception, auth, admin, shared)**,
afin de **disposer d'une base TypeScript stricte et d'une structure prête pour l'import 1.4.4 et les slots**.

## Acceptance Criteria

1. **Étant donné** un environnement avec Node et npm (ou pnpm/yarn) disponibles  
   **Quand** j'exécute `npm create vite@latest frontend -- --template react-ts` (ou équivalent) et j'organise `frontend/src/` en sous-dossiers par domaine (caisse, reception, auth, admin, shared, core, types)  
   **Alors** le projet frontend build sans erreur (`npm run build`)  
   **Et** les conventions de nommage (composants PascalCase, hooks camelCase) et la structure sont documentées ou alignées avec l'architecture (Project Structure).

## Tasks / Subtasks

- [x] Task 1 : Initialiser le projet Vite React TypeScript (AC: #1)
  - [x] Exécuter `npm create vite@latest frontend -- --template react-ts` à la racine du repo (ou créer `frontend/` puis initialiser depuis le parent)
  - [x] `cd frontend && npm install` pour installer les dépendances
  - [x] Vérifier que `npm run build` réussit sur le template par défaut
- [x] Task 2 : Créer l'arborescence par domaine sous `frontend/src/` (AC: #1)
  - [x] Créer les dossiers : `caisse/`, `reception/`, `auth/`, `admin/`, `shared/`, `core/`, `types/`
  - [x] Déplacer ou adapter le contenu existant (ex. `App.tsx`, `main.tsx`) pour que l'app démarre sans erreur
  - [x] Laisser des fichiers placeholder (ex. `index.ts` ou un composant minimal) dans chaque domaine si nécessaire pour que la structure soit claire
- [x] Task 3 : Vérifier le build et les conventions (AC: #1)
  - [x] S'assurer que `npm run build` termine sans erreur
  - [x] Appliquer / documenter les conventions : composants en PascalCase, hooks et fonctions en camelCase (voir architecture)
  - [x] Aligner la structure avec `_bmad-output/planning-artifacts/architecture.md` section Project Structure & Boundaries (frontend/src par domaine)

## Dev Notes

- **Stack** : Vite + React + TypeScript (template officiel `react-ts`). Pas de framework de test inclus par défaut dans le template ; Vitest / React Testing Library pourront être ajoutés dans une story ultérieure (convention tests frontend à trancher en v0.1 — checklist épic 1).
- **Structure cible** (architecture) : `frontend/src/` avec sous-dossiers par domaine : `api/`, `auth/`, `caisse/`, `reception/`, `admin/`, `shared/`, `core/`, `types/`. Composants d'un module dans le dossier du module ; composants partagés dans `shared/`. Build output : `frontend/dist/` (servi plus tard par FastAPI — Story 1.2).
- **Nommage** (Implementation Patterns, architecture) : composants et fichiers composants **PascalCase** (ex. `UserCard.tsx`) ; hooks et fonctions **camelCase** (ex. `useSessionCaisse`) ; variables **camelCase** ; constantes **UPPER_SNAKE** si constantes globales.
- **État** : pas de state management global à introduire dans cette story ; React state + Context(s) par domaine viendront avec les stories métier. La structure doit seulement être prête (dossiers, points d'entrée).
- **Slots / extension points** : la structure doit anticiper les slots React et l'évolution vers layout configurable (LayoutConfigService, VisualProvider en stubs v1 — Story 8.1) ; prévoir la place dans l'arborescence sans implémenter les stubs dans cette story.
- **Import 1.4.4** : cette story pose la base ; l'import du code existant (copy + consolidate + security) sera traité dans des stories ultérieures. Ne pas copier l'ancien frontend ici.

### Project Structure Notes

- Alignement avec l'arborescence décrite dans `architecture.md` (§ Complete Project Directory Structure, § Structure Patterns, § Requirements to Structure Mapping).
- Frontend uniquement dans cette story : pas de création de `api/` ni de Docker ; un seul container et montage des statics seront faits en Story 1.2 et 1.3.
- Les dossiers `core/` et `types/` sont listés dans l'architecture (frontend) pour utilitaires partagés et types TS ; les garder vides ou avec un export minimal si besoin pour que le build reste valide.

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.1]
- [Source: _bmad-output/planning-artifacts/architecture.md — Starter Template Evaluation, Initialization Command]
- [Source: _bmad-output/planning-artifacts/architecture.md — Implementation Patterns & Consistency Rules, Naming Patterns (Frontend), Structure Patterns (Project Organization)]
- [Source: _bmad-output/planning-artifacts/architecture.md — Project Structure & Boundaries, Complete Project Directory Structure]
- [Source: _bmad-output/planning-artifacts/epics.md — Additional Requirements, Starter / Epic 1 Story 1 (Architecture)]

## Dev Agent Record

### Agent Model Used

bmad-dev (subagent)

### Debug Log References

(aucun)

### Completion Notes List

- Projet Vite créé avec `npm create vite@latest frontend -- --template react-ts` (sous Windows le template livré était vanilla TS ; React et @vitejs/plugin-react ont été ajoutés manuellement pour obtenir l'équivalent react-ts). `npm run build` réussit.
- Arborescence sous `frontend/src/` : `api/`, `auth/`, `caisse/`, `reception/`, `admin/`, `shared/`, `core/`, `types/`, chacun avec un `index.ts` placeholder. `App.tsx` et `main.tsx` laissés à la racine de `src/` pour que l'app démarre sans erreur.
- Conventions documentées dans `frontend/README.md` (PascalCase composants, camelCase hooks/fonctions, référence architecture). Build final vérifié.

### File List

- frontend/package.json (modifié — dépendances React + plugin-react)
- frontend/package-lock.json (modifié)
- frontend/tsconfig.json (modifié — jsx: react-jsx)
- frontend/vite.config.ts (nouveau)
- frontend/index.html (modifié — root, script main.tsx)
- frontend/README.md (nouveau — structure et conventions)
- frontend/src/App.tsx (nouveau)
- frontend/src/main.tsx (nouveau)
- frontend/src/style.css (existant, conservé)
- frontend/src/api/index.ts (nouveau)
- frontend/src/auth/index.ts (nouveau)
- frontend/src/caisse/index.ts (nouveau)
- frontend/src/reception/index.ts (nouveau)
- frontend/src/admin/index.ts (nouveau)
- frontend/src/shared/index.ts (nouveau)
- frontend/src/core/index.ts (nouveau)
- frontend/src/types/index.ts (nouveau)
- frontend/src/main.ts (supprimé)
- frontend/src/counter.ts (supprimé)

## Senior Developer Review (AI)

- **Date** : 2026-02-26
- **Résultat** : Approuvée
- **AC** : AC#1 validé (build OK, structure par domaine, conventions documentées dans README).
- **Tasks** : Toutes les tâches marquées [x] vérifiées (fichiers lus, build exécuté).
- **Git vs File List** : frontend/ est untracked ; la File List reflète correctement les fichiers créés/modifiés.
- **Findings LOW (recommandations optionnelles)** : index.html `title` = "frontend" (recommandation : "RecyClique") ; `lang="en"` (recommandation : "fr") ; style.css contient des classes inutilisées du template (#app, .logo, .card). Aucun HIGH/MEDIUM.

### Change Log

- 2026-02-26 : Code review (QA) — approuvée ; AC et tasks validés, findings LOW uniquement (recommandations polish).
- 2026-02-26 : Story 1.1 implémentée — frontend Vite React TS initialisé, arborescence par domaine (api, auth, caisse, reception, admin, shared, core, types), conventions documentées, build OK.
