# AGENTS — peintre-nano

## Purpose

Frontend **canon** Recyclique v2 : SPA React, TypeScript strict, Vite 6, Mantine 8, CSS Modules + `src/styles/tokens.css`. Proxy dev `/api` vers Recyclique API (voir `vite.config.ts`, env `PEINTRE_DEV_PROXY_TARGET`).

**Parent :** lire [`../AGENTS.md`](../AGENTS.md) avant d’éditer ici.

## Ownership

- **Strophe** — UX, priorités écrans, validation démo.
- **Agents** — domaines sous `src/domains/`, runtime `src/runtime/`, widgets `src/widgets/` ; alignement types OpenAPI générés.

## Local contracts

- **Stack figée :** React 18, TypeScript ~5.7 (`strict: true`, `noUnusedLocals`, `noUnusedParameters`), Vite 6, Vitest 3, Mantine 8.x — détail versions : [`../_bmad-output/project-context.md`](../_bmad-output/project-context.md).
- **Types API :** importer depuis `../contracts/openapi/generated/recyclique-api.ts` — ne pas recopier les DTO à la main.
- **Manifests CREOS :** démo `public/manifests/`, fixtures `src/fixtures/manifests/` ; lots reviewables sous `../contracts/creos/` — voir [`../contracts/README.md`](../contracts/README.md).
- **Interdit :** import runtime depuis `references/` (doc de cadrage uniquement).
- **Arborescence :** alignée sur [`../_bmad-output/planning-artifacts/architecture/project-structure-boundaries.md`](../_bmad-output/planning-artifacts/architecture/project-structure-boundaries.md) (Piste A).

## Work guidance

- Respecter `tsconfig.app.json` ; modules ES, pas d’extension `.ts` dans les imports.
- Matcher le style du dossier touché (patterns existants plutôt que nouvelle abstraction).
- Types / artefacts conceptuels : `src/types/`, `src/runtime/conceptual-artifacts.ts` ; chargement JSON / validation exhaustive : stories dédiées (voir README).
- Évolution API : régénérer les types (`contracts/openapi`) puis adapter les appels front — PR cohérente YAML + `generated/` + consommateurs.
- Setup et scripts détaillés : [`README.md`](README.md).

## Verification

```bash
cd peintre-nano
npm run lint    # tsc -b
npm run test    # Vitest — unitaires tests/unit/, suites tests/e2e/ (jsdom, pas Playwright)
npm run build   # tsc + build production
```

- **Unitaires :** `tests/unit/`.
- **« e2e » historique BMAD :** Vitest + Testing Library — portée dans [`tests/e2e/README.md`](tests/e2e/README.md).
- **Dev local :** `npm run dev` (port 4444 par défaut en compose).

Avant PR front : enchaîner **lint → test → build**. Pas de push sans OK Strophe ([`references/procedure-git-cursor.md`](../references/procedure-git-cursor.md)).
