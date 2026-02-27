# Story 10.1: Interfaces et stubs LayoutConfigService / VisualProvider (v1)



Status: review



<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->



## Story



En tant que **développeur ou intégrateur**,

je veux des **interfaces** (LayoutConfigService, VisualProvider) et des **implémentations stub** dans le frontend,

afin de brancher plus tard l'affichage dynamique et le service Peintre (FR26) sans refonte majeure.



## Acceptance Criteria



1. **Étant donné** la structure frontend (Epic 1),

   **quand** le code est en place,

   **alors** les interfaces `LayoutConfigService` et `VisualProvider` existent et sont utilisables par les modules ; des stubs sont livrés en v1 (FR26).

2. **Et** la structure et les slots permettent d'ajouter des implémentations réelles plus tard (v2+ : API préférences, client Peintre / JARVOS Mini).



## Tasks / Subtasks



- [x] Task 1 : Définir les interfaces TypeScript (AC: #1)

  - [x] 1.1 Définir `LayoutConfigService` : contrat pour fournir une config de layout (ex. `getLayout(context?: LayoutContext): Promise<LayoutConfig>` ou synchrone selon recherche).

  - [x] 1.2 Définir `VisualProvider` : contrat pour fournir un visuel (ex. `getVisual(context: VisualContext): Promise<VisualResult>` — URL ou blob, voir recherche).

  - [x] 1.3 Exporter les types depuis un barrel (ex. `shared/layout/types.ts`, `shared/visual/types.ts` ou `shared/services/`).

- [x] Task 2 : Implémenter les stubs (AC: #1)

  - [x] 2.1 Stub `LayoutConfigService` : retourner un layout fixe ou un JSON par défaut (pas de persistance en v1).

  - [x] 2.2 Stub `VisualProvider` : retourner une image/URL placeholder (pas d'appel à Peintre).

  - [x] 2.3 Placer les stubs dans des fichiers dédiés (ex. `layout-config.stub.ts`, `visual-provider.stub.ts`) sans mélanger avec le code métier.

- [x] Task 3 : Enregistrement au bootstrap (AC: #1, #2)

  - [x] 3.1 Créer un Context (ou une factory) qui expose l'implémentation à utiliser (LayoutConfigService, VisualProvider).

  - [x] 3.2 Au démarrage de l'app, point d'entrée actuel : `main.tsx` (MantineProvider, AuthProvider, CaisseProvider). Enregistrer les stubs comme implémentations par défaut.

  - [x] 3.3 Prévoir une config (env ou feature flag) pour basculer sur les implémentations réelles en v2+ (sans les implémenter dans cette story).

- [x] Task 4 : Hooks et consommation (AC: #1, #2)

  - [x] 4.1 Exposer des hooks `useLayoutConfig()` et `useVisual(context)` qui lisent l'implémentation depuis le Context.

  - [x] 4.2 S'assurer qu'aucun composant métier n'importe directement le stub ou un module Peintre — uniquement l'interface ou les hooks.
  - [x] 4.3 Écrire des tests unitaires co-locés (`*.test.ts` ou `*.test.tsx`) pour les hooks, avec Vitest + React Testing Library ; utiliser le stub pour éviter tout appel réseau.

- [x] Task 5 : Alignement avec les slots (AC: #2)

  - [x] 5.1 Documenter ou vérifier que les composants qui rendent dans un slot (`frontend/src/shared/slots/`) peuvent utiliser `useLayoutConfig()` / `useVisual()` pour le contenu futur ; pas de changement de structure des écrans en v1.



## Dev Notes



- **Référence technique obligatoire** : `_bmad-output/planning-artifacts/research/technical-affichage-dynamique-peintre-extension-points-research-2026-02-25.md` — emplacements des interfaces/stubs, roadmap v1 vs v2+, pattern stub-first, enregistrement au bootstrap.

- **Architecture** : Slots et extension points dans `frontend/src/shared/slots/` (déjà en place) ; ajouter layout et visual sous `frontend/src/shared/` (ex. `shared/layout/`, `shared/visual/` ou `shared/services/` selon convention projet). [Source: architecture.md — Frontend (Slots, extension points).]

- **Pattern** : Séparation contrat (interface) / implémentation (stub) ; injection au bootstrap via Context ou factory (type Backstage createApiRef/createApiFactory). Pas de dépendance directe des écrans vers Peintre ou le stub.

- **v1** : Pas de persistance de layout configurable (écrans fixes, copy 1.4.4). Pas d'appel au service Peintre. Stubs uniquement pour réserver la place.

- **Conventions projet** : Tests co-locés `*.test.tsx` (ou `*.test.ts` pour hooks purs), Vitest + React Testing Library + jsdom ; Mantine pour l'UI ; structure frontend par domaine (caisse, reception, auth, admin, shared). [Source: epics.md — Décisions architecturales ; .cursor/rules/architecture-et-checklist-v01.mdc.]



### Project Structure Notes



- **Interfaces** : `frontend/src/shared/layout/` et `frontend/src/shared/visual/` (ou `shared/services/layout`, `shared/services/visual`) — cohérent avec `frontend/src/shared/slots/`.

- **Stubs** : fichiers dédiés `*.stub.ts` dans les mêmes modules ou sous-dossier `__stubs__` selon convention du projet.

- **Bootstrap** : point d'entrée actuel `frontend/src/main.tsx` (MantineProvider, AuthProvider, CaisseProvider) ; y ajouter le Provider pour LayoutConfigService et VisualProvider.



### References



- [Source: research technical-affichage-dynamique-peintre-extension-points-research-2026-02-25.md] — Technology Stack (slots, extension points), Integration Patterns (contrat Peintre), Architectural Patterns (emplacements stubs, bootstrap), Implementation (roadmap v1.0, fichiers recommandés).

- [Source: epics.md] — Epic 10, Story 10.1, FR26.

- [Source: architecture.md] — Slots, extension points, évolution frontend.

- [Source: ux-design-specification.md] — Extension points v1 (interfaces + stubs), pas d'écrans configurables ni Peintre en v1.



## Dev Agent Record



### Agent Model Used



–



### Debug Log References



–



### Completion Notes List



- Interfaces LayoutConfigService et VisualProvider définies dans shared/layout/types.ts et shared/visual/types.ts avec contrats Promise (getLayout, getVisual). Barrel exports dans shared/layout et shared/visual.
- Stubs layout-config.stub.ts et visual-provider.stub.ts : layout fixe (breakpoints/cols), visuel placeholder (data URL SVG 1x1). Pas de persistance ni appel Peintre.
- DisplayServicesProvider dans shared/display-services injecte les deux services ; enregistrement dans main.tsx avec stubs. Config v2+ documentée (commentaire VITE_USE_REAL_DISPLAY_SERVICES).
- Hooks useLayoutConfig() et useVisual() exposés ; ils lisent le Context (aucun import direct stub dans le métier). Tests co-locés useLayoutConfig.test.tsx et useVisual.test.tsx (Vitest + RTL, stubs dans le provider).
- Slots README mis à jour : usage futur de useLayoutConfig() / useVisual() par les composants rendus dans un slot.



### File List



- frontend/src/shared/layout/types.ts
- frontend/src/shared/layout/index.ts
- frontend/src/shared/layout/layout-config.stub.ts
- frontend/src/shared/layout/useLayoutConfig.ts
- frontend/src/shared/layout/useLayoutConfig.test.tsx
- frontend/src/shared/visual/types.ts
- frontend/src/shared/visual/index.ts
- frontend/src/shared/visual/visual-provider.stub.ts
- frontend/src/shared/visual/useVisual.ts
- frontend/src/shared/visual/useVisual.test.tsx
- frontend/src/shared/display-services/DisplayServicesContext.tsx
- frontend/src/shared/display-services/index.ts
- frontend/src/shared/index.ts
- frontend/src/main.tsx
- frontend/src/shared/slots/README.md

