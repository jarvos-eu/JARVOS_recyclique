# REPRISE — JARVOS Recyclique

**project_id** : `jarvos-recyclique`  
**Mis à jour** : 2026-07-04

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

## Sessions à reprendre — chantier Peintre v0.1 *(filé Clio, 2026-07-04)*

**Statut ce soir :** annoncé et cadré — **pas démarré** ; à reprendre dans une ou plusieurs sessions dédiées (après arbitrage timing vs Epic 28 / C2b).

**Entrée unique :** [`references/artefacts/2026-07-04_01_preparation-chantier-peintre-v0-1.md`](references/artefacts/2026-07-04_01_preparation-chantier-peintre-v0-1.md)

| # | Session future | Qui / quoi | Déclencheur |
|---|--------------|------------|-------------|
| 1 | Ventilation pack PEINTRE | @depot-specialist — move `peintre-nano/docs/dossier-architecte-peintre-v0-1/` → `references/dossier-architecte-peintre-v0-1/` + zip `_depot/2026-07-04_01_pack-architecte-micro-workflows-navigation-raccourcis.zip` | « ventile le pack PEINTRE » |
| 2 | HITL cadrage | Strophe — `09-PEINTRE-risques-et-questions-hitl.md` · décisions → `07-PEINTRE-adr-decisions.md` | après ventilation |
| 3 | Promotion BMAD | bmad-create-epics-and-stories — PRD `06` → epic(s) + stories + `sprint-status.yaml` | GO Strophe post-HITL |
| 4 | Arbitrage programme | Mentor → **Ariane** — quand enchaîner vs Epic 28 / C2b / parité beta | avant GO exécution |
| 5 | Exécution Piste A | @bmad-epic-runner → @bmad-story-runner — épics A → B → C (E différable) | GO exécution explicite |

**Kanban :** [`IDEA-2026-07-04-001`](docs/ideas/kanban/IDEA-2026-07-04-001.md) (`refining`) · workflows/raccourcis : [`IDEA-2026-03-31-001`](docs/ideas/kanban/IDEA-2026-03-31-001.md) (`ready`)

**Todo opérateur :** [`references/todo.md`](references/todo.md) (item ouvert en tête de liste).

**Prompt reprise (coller en tête de chat) :**

```
Reprise chantier Peintre v0.1 — session <N> du tableau REPRISE.md.
Charger : references/artefacts/2026-07-04_01_preparation-chantier-peintre-v0-1.md
puis peintre-nano/docs/dossier-architecte-peintre-v0-1/index.md (ou references/… si move fait).
Pas d'exécution code sans GO Strophe sur le timing.
```

## Risques / vigilance

- Skills BMAD : invoquer **`.agents/skills/`** uniquement (51 bundles). Sous `.cursor/skills/` : 4 skills projet seulement (`idees-kanban`, `traiter-depot`, etc.) — **aucun** `bmad-*` actif sur disque.  
- DOX-lite : traversal **`AGENTS.md` racine → enfant** avant édition dans `peintre-nano/`, `recyclique/api/`, `contracts/`.  
- `project_knowledge` = **`references/`** (pas `docs/`).  
- Archive PRD/epics pré-pivot : `_bmad-output/archive/2026-03-31_pivot-brownfield-recyclique-1.4.4/`.
