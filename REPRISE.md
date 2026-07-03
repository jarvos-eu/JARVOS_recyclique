# REPRISE — JARVOS Recyclique

**project_id** : `jarvos-recyclique`  
**Mis à jour** : 2026-07-03

> **Fil Clio** — lire en début de session agent (signal `project-memory-signal.json`). Checklist onboarding détaillée : [`_bmad/ONBOARDING.md`](_bmad/ONBOARDING.md).

## Où on en est

Migration BMAD **6.2.1 → 6.9.0** + module **bmb** + alignement pack JARMES (TOML, shims, `.agents/skills/`). Le trio Mentor / Ariane / Clio est raccordé via `JARMES/jarmes-cockpit/global-bmad/`.

**Contexte agents** : `_bmad-output/project-context.md` (`status: complete`, règles stables depuis 2026-04-23 ; **relu 2026-07-03** post-migration BMAD 6.9).  
**Contrats DOX-lite** : hiérarchie `AGENTS.md` (racine + `peintre-nano/`, `recyclique/api/`, `contracts/`) — traversal parent → enfant avant édition code.  
**Point d'entrée doc** : `references/index.md` (ciblé, pas en entier).

| Couche | Fichier | Propriétaire |
|--------|---------|--------------|
| Programme métier (slim) | [`references/ou-on-en-est.md`](references/ou-on-en-est.md) | **Ariane** |
| État stories (grain fin) | [`_bmad-output/implementation-artifacts/sprint-status.yaml`](_bmad-output/implementation-artifacts/sprint-status.yaml) | pilotage BMAD |
| Guide pilotage | [`_bmad-output/planning-artifacts/guide-pilotage-v2.md`](_bmad-output/planning-artifacts/guide-pilotage-v2.md) | — |

## Idées & réflexion

- Kanban idées projet : [`references/idees-kanban/index.md`](references/idees-kanban/index.md)
- Todo opérateur / rappels : [`references/todo.md`](references/todo.md)

## Prochaine action

Selon **`sprint-status.yaml`** — pas de story imposée dans ce fil :

1. **Gate Epic 28** — stories 28.1–28.5 **done** ; `epic-28` reste `in-progress` jusqu'à clôture gate **B_EPIC28** (retests HITL terrain).
2. **Programme métier** — Ariane resync [`references/ou-on-en-est.md`](references/ou-on-en-est.md) après gate si besoin ; Epic 9 (ex. 9-7) **gelé** jusqu'à clôture Epic 28.
3. Gate QA95 lot 2 : **passée** — rapport [`references/artefacts/2026-07-03_02_qa95-post-context-jarvos-recyclique.md`](references/artefacts/2026-07-03_02_qa95-post-context-jarvos-recyclique.md).

## Risques / vigilance

- Skills BMAD : invoquer **`.agents/skills/`** uniquement (51 bundles). Sous `.cursor/skills/` : 4 skills projet seulement (`idees-kanban`, `traiter-depot`, etc.) — **aucun** `bmad-*` actif sur disque.  
- DOX-lite : traversal **`AGENTS.md` racine → enfant** avant édition dans `peintre-nano/`, `recyclique/api/`, `contracts/`.  
- `project_knowledge` = **`references/`** (pas `docs/`).  
- Archive PRD/epics pré-pivot : `_bmad-output/archive/2026-03-31_pivot-brownfield-recyclique-1.4.4/`.
