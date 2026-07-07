# REPRISE — JARVOS Recyclique

**project_id** : `jarvos-recyclique`  
**Mis à jour** : 2026-07-07

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

- Kanban idées projet : [`docs/ideas/kanban/INDEX.md`](docs/ideas/kanban/INDEX.md)
- Todo opérateur / rappels : [`references/todo.md`](references/todo.md)
- **🔴 P0 URGENCE — Assistance décla Ecologic T2** : [`IDEA-2026-07-07-001`](docs/ideas/kanban/IDEA-2026-07-07-001.md) · dump reçu · [`2026-07-07_mission-assistance-decla-ecologic-t2-2026.md`](references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/2026-07-07_mission-assistance-decla-ecologic-t2-2026.md)
- **🔴 P0 — Bot Discord pilote La Clique** : [`IDEA-2026-07-05-002`](docs/ideas/kanban/IDEA-2026-07-05-002.md) · CH-LACLIQUE-BOT-001 · **bloqué gate Ombre/CREOS** · Discord→Hermes→Ombre→Cursor · spec [`JARMES/docs/programme/CH-LACLIQUE-BOT-001-spec.md`](../../../JARMES/docs/programme/CH-LACLIQUE-BOT-001-spec.md)

## Mission urgence — assistance décla Ecologic T2 2026 *(filé Clio, 2026-07-07)*

**Statut :** `en cours` — dump BDD **reçu** 2026-07-07 · **prochaine étape** : `pg_restore` miroir RO → requêtes T2 → CSV complément  
**Échéance indicative :** ~30/07/2026 (T2 Ecologic)  
**État ODS T2 :** entrées **`LIV` 9/9** renseignées · sorties **`DEC_REE` 8/9 vides** (PAM partiel 0,25 t)  
**Intention :** dump + ODS + mode d'emploi → **`Complément-DEC_REE-T2-2026.csv`** + **`HITL-questions-decla-ecologic-t2-2026.md`** — **sans inventer**.

| Entrée | Chemin |
|--------|--------|
| **Racine mission** *(regroupée éco-org 2026-07-07)* | [`…/2026-T2/2026-07-07_mission-assistance-decla-ecologic-t2-2026.md`](references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/2026-07-07_mission-assistance-decla-ecologic-t2-2026.md) |
| **Spec détaillée** | [`references/artefacts/2026-07-07_06_mission-assistance-decla-ecologic-t2-recyclic-144.md`](references/artefacts/2026-07-07_06_mission-assistance-decla-ecologic-t2-recyclic-144.md) |
| **ODS + mode d'emploi** | [`…/2026-T2/`](references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/) — `DeclarationESS-ECOLOGIC-2T2026.ods` · [`MODE-EMPLOI`](references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md) |
| **Dump canon** *(gitignore)* | `references/_depot/recyclic_db_export_20260707_152448.dump` |
| **Dump archive** | `references/_depot/recyclic_db_export_20260411_172643.dump` |
| **Kanban P0** | [`IDEA-2026-07-07-001`](docs/ideas/kanban/IDEA-2026-07-07-001.md) |
| **Index éco-org** | [`references/eco-organismes/index.md`](references/eco-organismes/index.md) |

**Contexte session 2026-07-07** *(liens — pas de substance ici)* : grilles champs + calendrier partenaires ([`eco-organismes/`](references/eco-organismes/)) · cadrages patch 1.4.5 Ecomaison / Ecologic / Refashion ([`_03`](references/artefacts/2026-07-07_03_cadrage-patch-1.4.5-ecomaison.md) · [`_04`](references/artefacts/2026-07-07_04_cadrage-patch-1.4.5-ecologic.md) · [`_05`](references/artefacts/2026-07-07_05_cadrage-patch-1.4.5-refashion.md)) — mission **hors** livraison 1.4.5, raccourci terrain avant industrialisation.

**Prompt reprise (coller en tête de chat) :**

```
Mission urgence — décla Ecologic T2 2026 La Clique.
Charger : …/2026-T2/2026-07-07_mission-assistance-decla-ecologic-t2-2026.md
         + references/artefacts/2026-07-07_06_mission-assistance-decla-ecologic-t2-recyclic-144.md
         + DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md (même dossier)
Dump : references/_depot/recyclic_db_export_20260707_152448.dump
→ pg_restore miroir read-only → requêtes T2 → Complément-DEC_REE-T2-2026.csv
Règle : rien inventer — chaque trou → HITL pour Strophe.
```

---

## Session 2026-07-07 (fin) — ventilation K-Drive headless

**Statut :** documenté, **non déployé** — chantier infra VPS à part ; levier futur **mode AIDE** bot Discord (post-gate CREOS), en attente V2 produit.

| Entrée | Chemin |
|--------|--------|
| Runbook (ex-`_depot`) | [`references/artefacts/2026-07-07_08_installation-kdrive-headless-vps.md`](references/artefacts/2026-07-07_08_installation-kdrive-headless-vps.md) |
| Bot Discord pilote | [`IDEA-2026-07-05-002`](docs/ideas/kanban/IDEA-2026-07-05-002.md) · cadrage [`2026-07-05_02`](references/artefacts/2026-07-05_02_cadrage-bot-discord-la-clique-pilote.md) |

---

## Prochaine action

**Urgence terrain (2026-07-07) :** mission assistance décla Ecologic T2 — dump reçu ; **restore miroir** + requêtes T2 (voir dossier [`2026-T2/`](references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/)).

Sinon, selon **`sprint-status.yaml`** — pas de story imposée dans ce fil :

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
