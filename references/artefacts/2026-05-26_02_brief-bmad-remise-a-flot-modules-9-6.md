# Brief BMAD — Remise a flot Epic 9 / modularite v2 / Story 9.6

**Date :** 2026-05-26  
**Demandeur :** Strophe  
**Usage :** copier-coller dans un chat `@bmad-agent-pm` (John), `bmad-help`, ou session BMAD Master.  
**Ne pas committer** sans demande explicite de Strophe.

---

## Mission pour l'agent

1. **Lire** les references ci-dessous (ordre strict pour le volet modules).
2. **Diagnostiquer** l'ecart entre l'etat reel du depot et `sprint-status.yaml` / epics / PRD.
3. **Proposer** (puis executer si demande) :
   - promotion Story **9.6** : `ready-for-dev` → `in-progress` → `done` ;
   - ordre des stories Epic **9** vs priorites terrain (5 fils roadmap) ;
   - mise a jour `sprint-status.yaml`, `ou-on-en-est.md`, epics si necessaire ;
   - prochaines stories **create-story** pour modules metier (cookbook, 1 `module_key` a la fois).
4. **Ne pas rouvrir** les decisions HITL listees en section « Figé ».
5. **Trancher** l'arbitrage ordre Epic 9 (Options A/B/C) — ne pas assumer silencieusement.

---

## Decision PM (2026-05-26 — Strophe + John)

| Sujet | Decision |
|-------|----------|
| **Arbitrage Epic 9** | **Option C (hybride)** : dev **9.6** maintenant ; stories metier 9.1–9.5 sans dev jusqu'aux gates (EC Paheko, etc.) ; **HelloAsso** = **parking** module (ne pas perdre — 9.4/9.5 doc seulement) |
| **Plancher** | **v2.0** dans **ce depot** = equivalence robuste prod **1.4.4** (autre depot Git) + socle pour brancher les modules |
| **Versions suivantes** | **2.0.1**, **2.0.2**… = **un module a la fois** apres plancher |
| **Priorites modules post-9.6** | Cockpit compta, eco-organismes, etc. (pas HelloAsso en premier) |
| **Parite gestes terrain** | Caisse, reception, raccourcis clavier = **strictement** comme 1.4.4 ; verification terrain **hors** 9.6, critere de cloture plancher |
| **Doc alignee** | `sprint-status.yaml`, `ou-on-en-est.md`, `epics.md` (note ordre 9.6) |

---

## Decisions figees (HITL — ne pas rouvrir)

| ID | Decision |
|----|----------|
| ADR-007 | **Accepted** — abandon v0.1 (TOML, `ModuleBase`, EventBus module) → v2 CREOS + JSON `module_key` + routers explicites |
| DEC-03 | JSON `module_key` **fait foi** sur `sites.configuration` |
| F1 | API `module-config` = **interne Recyclique** jusqu'a stabilisation Story 9.6 |
| F3 | 1 `module_key` = 1 package backend |
| Hors scope v2 | Pas marketplace v2 ; pas zip/install magique ; pas 2e module comptage (T-MET-1) dans 9.6 |

Sources :
- [`references/artefacts/2026-05-20_06_reco-hitl-post-bouclage-modules-v2.md`](2026-05-20_06_reco-hitl-post-bouclage-modules-v2.md)
- [`_bmad-output/planning-artifacts/architecture/2026-05-20-adr-007-reconciliation-modularite-v01-v02.md`](../../_bmad-output/planning-artifacts/architecture/2026-05-20-adr-007-reconciliation-modularite-v01-v2.md)
- [`references/protocole-modules-recyclique/07-MOD-adr-reconciliation-v01-v02.md`](../protocole-modules-recyclique/07-MOD-adr-reconciliation-v01-v02.md)

---

## Etat du chantier modules v2 (2026-05-26)

### Fait (P0 doc + backend T-MOD-3)

| Livrable | Fichier |
|----------|---------|
| Pack protocole (GO doc ~96 %) | [`references/protocole-modules-recyclique/index.md`](../protocole-modules-recyclique/index.md) |
| QA2 global chantier | [`references/protocole-modules-recyclique/qa2-rapport-global-chantier-modules-2026-05-20.md`](../protocole-modules-recyclique/qa2-rapport-global-chantier-modules-2026-05-20.md) |
| PRD §4.2.1 + §7.1 + glossaire `module_key` | [`_bmad-output/planning-artifacts/prd.md`](../../_bmad-output/planning-artifacts/prd.md) |
| Décisions core archi | [`_bmad-output/planning-artifacts/architecture/core-architectural-decisions.md`](../../_bmad-output/planning-artifacts/architecture/core-architectural-decisions.md) |
| OpenAPI fusionne | [`contracts/openapi/recyclique-api.yaml`](../../contracts/openapi/recyclique-api.yaml) |
| Handler + tests (5 passed) | [`recyclique/api/src/recyclic_api/modules/module_config/`](../../recyclique/api/src/recyclic_api/modules/module_config/) · [`recyclique/api/tests/test_module_config_site.py`](../../recyclique/api/tests/test_module_config_site.py) |
| Schema pilote | [`references/config-modules-site-id/schemas/kpi-live-banner.v1.json`](../config-modules-site-id/schemas/kpi-live-banner.v1.json) |
| Promotion PRD (2026-05-21) | [`references/ou-on-en-est.md`](../ou-on-en-est.md) |

### A faire — Story 9.6 (gros morceau)

| Element | Detail |
|---------|--------|
| **Story enrichie** | [`_bmad-output/implementation-artifacts/9-6-config-admin-simple-modules.md`](../../_bmad-output/implementation-artifacts/9-6-config-admin-simple-modules.md) |
| **Statut story file** | `ready-for-dev` (enrichi 2026-05-26) |
| **Statut sprint YAML** | **A aligner** : `9-6-livrer-la-config-admin…` → `ready-for-dev` + `last_updated: 2026-05-26` |

**Perimetre 9.6 :**
- UI Peintre **`/admin/modules`** (activation + reglages simples)
- Merge config PostgreSQL P2 + ordre merge manifest → PG → JSON (DEC-03)
- Migration bandeau : toggle Epic 4.5 / localStorage → `module_key=kpi-live-banner`
- Cloture **L-08** (fin triple autorite activation)
- Tests backend P1 (IDOR, 401, If-Match → 422, Cache-Control)

**Matrice gaps :** [`references/protocole-modules-recyclique/15-MOD-matrice-gaps-bmad-story-9-6.md`](../protocole-modules-recyclique/15-MOD-matrice-gaps-bmad-story-9-6.md)

---

## Matiere produit post-23/05 (addendum)

**Addendum synthese :** [`references/artefacts/2026-05-23_01_addendum-transcripts-1423-visions-rec-pko.md`](2026-05-23_01_addendum-transcripts-1423-visions-rec-pko.md) — **+24 idees** (VIS-001…020, ORG/WFL 1423), pont REC/PKO avec recap 21/05.

**Finaux transcription :**
- [`.transcription/meetings/2026-05-23-terrain-1423/final/2026-05-23-terrain-1423.md`](../../.transcription/meetings/2026-05-23-terrain-1423/final/2026-05-23-terrain-1423.md)
- [`.transcription/meetings/2026-05-23-recyclique-bilans-audit-visions/final/2026-05-23-recyclique-bilans-audit-visions.md`](../../.transcription/meetings/2026-05-23-recyclique-bilans-audit-visions/final/2026-05-23-recyclique-bilans-audit-visions.md)

**Recap base (ne pas regonfler — addendum §7.1) :** [`references/artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md`](2026-05-21_02_recap-idees-paheko-reception-terrain.md)

**Option P2 — QA2 contractuel :** addendum §7.5 recommande un QA2 sur le final **1423** si registre contractuel ; draft existant sous le meeting (`qa2-draft-fusion.md` si present). **Non bloquant** pour dev 9.6 ; a lancer si le fil workflows/org devient engage.

---

## Ordre de lecture obligatoire (modules — session dev)

1. [`references/artefacts/2026-05-20_05_notes-architecte-loup-de-mer-modules-v2.md`](2026-05-20_05_notes-architecte-loup-de-mer-modules-v2.md) — **primordial**
2. [`references/artefacts/2026-05-20_06_reco-hitl-post-bouclage-modules-v2.md`](2026-05-20_06_reco-hitl-post-bouclage-modules-v2.md)
3. [`references/artefacts/2026-05-20_04_reponse-architecte-bouclage-modules-v2.md`](2026-05-20_04_reponse-architecte-bouclage-modules-v2.md)
4. [`references/protocole-modules-recyclique/06-MOD-cookbook-nouveau-module-optionnel.md`](../protocole-modules-recyclique/06-MOD-cookbook-nouveau-module-optionnel.md)
5. Story 9.6 enrichie (lien ci-dessus)
6. [`_bmad-output/planning-artifacts/epics.md`](../../_bmad-output/planning-artifacts/epics.md) — Epic 9, Story 9.6 (~L2124) + note modularite L1995

---

## Arbitrage ordre Epic 9 vs chantier modules (P0 PM)

Deux ordres **coexistent** :

| Source | Ordre | Portee |
|--------|-------|--------|
| **HITL reco 06** + pack modules | T-MOD-3 → **Story 9.6** → cookbook 2e module | **Infra modularite v2** |
| **`epics.md` Epic 9 L1998** | 9-2 mappings → adherents → HelloAsso 9-4/9-5 → **9.6** → 9-7 ACL → 9-8 | **Backlog BMAD officiel** |

**Options (tranche 2026-05-26) :**

- **A (infra-first)** : dev **9.6** maintenant ; stories 9-1…9-5 en doc/brainstorm parallele.
- **B (epic-strict)** : 9-2 → … → 9-5 avant 9.6 — retarde L-08 et migration toggle bandeau. **Rejetee.**
- **C (hybride)** : dev 9.6 immediat + create-story metier Epic 9 sans dev jusqu'a gate EC Paheko / arbitrage HelloAsso. **Retenue.**

---

## Roadmap PM — 5 fils

| Fils | Contenu | Priorite |
|------|---------|----------|
| **A — Infra modules** | Story **9.6** puis cookbook | HITL 06 ; **Option C retenue** (2026-05-26) |
| **B — Reception v1** | Brainstorm 21/05 + addendum §4 | VIS-010, 017, 019, 020 |
| **C — Paheko / compta** | Gate **EC** + VIS-018, VIS-019 | Pas dev sans validation ; PKO-001…025 base |
| **D — Workflows / org** | 1423 + VIS-009/010/019/020 | Session dediee ; hors 9.6 |
| **E — Liaison Paheko v1** | **D1 porteur** — fermeture caisse → ecritures | [`references/migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md`](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) ; **apres** gate EC fil C |

**Gate EC Paheko :**
- [`_bmad-output/brainstorming/brainstorming-session-2026-05-21-paheko-compta-validation.md`](../../_bmad-output/brainstorming/brainstorming-session-2026-05-21-paheko-compta-validation.md) — **EN_ATTENTE_VALIDATION_COMPTABLE**
- [`references/migration-paheko/2026-05-21_courrier-validation-compta-paheko-corinne-caro.md`](../migration-paheko/2026-05-21_courrier-validation-compta-paheko-corinne-caro.md)

---

## Questions PM (addendum §6 + plan)

1. Perimetre v1 Reception : VIS-010/017/019/020 **in** or **parking** ?
2. **VIS-018** : entites minimum v1 sans sur-modeliser ?
3. **VIS-011** + **VIS-002** : PIN seul v1 ou multi-modal des la conception ?
4. **VIS-019** : politique modification workflow (bloquer / migrer / fork) ?
5. **WFL-002** vs **VIS-010** : meme module ou deux couches ?
6. Frontiere RecyClique / Jarvos / echo-eco (VIS-009, 012, 015) ?
7. Ordre Epic 9 : Option **A / B / C** ? → **C** (2026-05-26)

---

## Pieges loup de mer (synthese 9.6)

| # | Piege | Action |
|---|-------|--------|
| 2 | Copier toggle 4.5 | JSON `module_key` uniquement |
| 3 | Page orpheline | `/admin/modules` dans navigation CREOS |
| 5 | Renommer `getLiveSnapshot` | **Interdit** |
| 7 | Compta dans JSON config | Payload = prefs UI / activation seulement |

Registre : [`references/protocole-modules-recyclique/18-MOD-config-modules-crosswalk.md`](../protocole-modules-recyclique/18-MOD-config-modules-crosswalk.md)

---

## Contexte sprint BMAD global

| Fichier | Role |
|---------|------|
| [`_bmad-output/implementation-artifacts/sprint-status.yaml`](../../_bmad-output/implementation-artifacts/sprint-status.yaml) | Pilotage stories |
| [`references/ou-on-en-est.md`](../ou-on-en-est.md) | Journal projet |
| [`_bmad-output/planning-artifacts/guide-pilotage-v2.md`](../../_bmad-output/planning-artifacts/guide-pilotage-v2.md) | Pilotage v2 |
| [`references/artefacts/2026-04-08_02_pack-lecture-epics-6-10-et-corpus-captures.md`](2026-04-08_02_pack-lecture-epics-6-10-et-corpus-captures.md) | Pack Epics 6–10 |

---

## Livrables attendus de l'agent BMAD

1. **Rapport etat des lieux** (1 page) : coherence sprint-status ↔ stories ↔ PRD ↔ pack modules.
2. **Decision prioritisation** : ordre Epic 9 (A/B/C) + ordre des 5 fils.
3. **Actions sprint** : aligner YAML, promouvoir 9.6 si Option A ou C.
4. **Plan stories suivantes** apres 9.6 : premier `module_key` metier via cookbook ?
5. **Checklist non-regression doc** : grep PRD stale, index pack a jour.

---

## Skills / agents BMAD recommandes

| Etape | Agent / skill |
|-------|----------------|
| Diagnostic + priorisation | `@bmad-agent-pm` ou `bmad-help` |
| Validation story 9.6 | `bmad-create-story` mode Validate |
| Implementation 9.6 | `bmad-dev-story` |
| Revue post-livraison | `bmad-code-review` |
| Sprint sync | `bmad-sprint-planning` / `bmad-sprint-status` |

---

## Index projet

[`references/index.md`](../index.md) — charger selon type de session.

---

*Brief genere 2026-05-26 — post-QA2 plan addendum 23/05 (gate 96 %).*
