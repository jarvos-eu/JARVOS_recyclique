# Ou on en est — JARVOS Recyclique

Mis à jour : 2026-07-04

> **Bannière trio (lot 3a)**
>
> | Couche | Fichier | Writer |
> |--------|---------|--------|
> | **SoT programme** (epics/stories) | [`sprint-status.yaml`](../_bmad-output/implementation-artifacts/sprint-status.yaml) (`last_updated: 2026-06-07`) | **Ariane** |
> | **Fil session** | [`REPRISE.md`](../REPRISE.md) | **Clio** |
> | **Journal archivé** (sessions, prochaine étape historique, spirale 1re passe) | [`artefacts/archive/2026-07-03_ou-on-en-est-journal-pre-trio.md`](artefacts/archive/2026-07-03_ou-on-en-est-journal-pre-trio.md) | archive |

**Périmètre par version** : voir [references/versioning.md](versioning.md). **Ce dépôt Git** = développement **JARVOS Recyclique v2.0** ; la prod actuelle **1.4.4** vit dans **un autre dépôt** (référence brownfield : `recyclique-1.4.4/` dans ce mono-repo).

## Pilotage BMAD — renvoi canonique

**Ne pas recopier la liste des epics ici.** État instantané : clé racine `last_updated` + bloc `development_status` dans [`sprint-status.yaml`](../_bmad-output/implementation-artifacts/sprint-status.yaml).

| Thème | Instantané YAML (2026-06-07) |
|-------|------------------------------|
| Epics **done** | 1–8, 11, 13–19, 22–27, 25–26 |
| **Epic 9** | `in-progress` — **9.6**, **9.10–9.13** `done` ; **9.7 gelée** (priorité Epic 28) |
| **Epic 28** | `in-progress` — **28.1–28.5** `done` ; gate **B_EPIC28** ; rétro / retests HITL avant **10.7 / 10.8** |
| Epics **backlog** | 10, 12, 20, 21 |

**Guide multi-chantiers** : [_bmad-output/planning-artifacts/guide-pilotage-v2.md](../_bmad-output/planning-artifacts/guide-pilotage-v2.md). **Backlog terrain beta** : [references/revision/index.md](revision/index.md).

## Bascule BMAD (2026-03-31)

Les sorties BMAD **actives** (`_bmad-output/planning-artifacts/`, `_bmad-output/implementation-artifacts/`) ont été **réinitialisées** pour repartir sur une nouvelle ligne (évolution incrémentale depuis `recyclique-1.4.4` stabilisé).

**Archive pivot** : `_bmad-output/archive/2026-03-31_pivot-brownfield-recyclique-1.4.4/`. Explications : [_bmad-output/README.md](../_bmad-output/README.md). Dans les journaux **datés d'avant le 2026-03-31**, préfixer les chemins `_bmad-output/planning-artifacts/` ou `implementation-artifacts/` par l'archive ci-dessus.

**Migration BMAD 6.9 + trio JARMES (2026-07)** : fil technique dans [`REPRISE.md`](../REPRISE.md) ; skills BMAD sous `.agents/skills/`.

## État actuel (résumé)

Mono-repo v2 : `recyclique/api/`, `peintre-nano/`, `contracts/`. Analyses brownfield **1.4.4** et **Paheko** dans `references/`. Workflow Git en place.

### Epic 28 — stabilisation beta terrain

Source backlog : [`references/revision/`](revision/index.md). Stories **28.1–28.5** **done** (caisse P0, profil/PIN self-service, réception hub/poste, admin débruîté, édition sites/postes). Sync [`epic-28-stabilisation-beta-terrain/00_SYNC_STATUS.md`](../_bmad-output/implementation-artifacts/epic-28-stabilisation-beta-terrain/00_SYNC_STATUS.md) : gate **B_EPIC28** **done** côté livrables ; **0 P0 ouvert** dans revision ; **retests HITL** Strophe avant enchaînement Epic **10.7 / 10.8**. `epic-28` reste `in-progress` jusqu'à rétrospective.

### Epic 9 — modules complémentaires

**9.6** config admin simple, **9.10** liaison Paheko clôture, **9.11–9.13** comptage pièces/billets (v2.0.2) : **done**. **Story 9.7** (ACL minimales) en **backlog gelé** jusqu'à clôture narrative Epic 28 (commentaire YAML bloc epic-28).

**Repère Epics 6–10** (captures, matrice) : pack [`2026-04-08_02`](artefacts/2026-04-08_02_pack-lecture-epics-6-10-et-corpus-captures.md) + tableau [`2026-04-08_03`](artefacts/2026-04-08_03_tableau-ultra-operationnel-epics-6-10.md) — grain fin toujours dans le YAML.

## Stratégie livraison v2.0 (décision 2026-05-26)

| Jalon | Contenu |
|-------|---------|
| **v2.0 (plancher)** | Équivalence **robuste** avec **1.4.4** en prod : caisse, réception, compta, parcours livrés ; socle modules `/admin/modules` (**9.6** **done**) |
| **Parité gestes (critère plancher)** | Rapport [`2026-05-26_03`](artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) + QA2 [`2026-05-27_01`](artefacts/2026-05-27_01_qa2-rapport-parite-plancher-v2-gestes-terrain.md). **C2b HITL terrain** = à faire (stack locale + bénévole) — plan [post-9.6](../.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md) § C2b. **Pas** tag `v2.0.0` avant C2b. |
| **Chantier parité beta v2.0** | Checklist [`2026-05-30_01`](artefacts/2026-05-30_01_checklist-chantier-parite-v2-beta-1.4.4.md) — à cocher avant beta bénévoles ; lié [`besoins-terrains.md`](besoins-terrains.md). |
| **v2.0.1, v2.0.2…** | Un module métier à la fois ; **9.10** **done** (2026-05-27) ; **9.11–9.13** **done** (2026-06-06) ; tag **v2.0.1** après C2b + gate Coordinateur |
| **HelloAsso** | **Parking** — stories 9.4/9.5 = doc / arbitrage sans dev large |
| **Ordre Epic 9** | Voir `epics.md` § Epic 9 et YAML ; **9.7+ gelé** par Epic 28 |

## Chantiers actifs pertinents

| Chantier | Entrée |
|----------|--------|
| Plan post-9.6 (plancher / compta) | [`.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md`](../.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md) — Agent A/B **clos** ; **C2b** pending |
| Protocole modules v2 | [`protocole-modules-recyclique/index.md`](protocole-modules-recyclique/index.md) — P0 clos ; brief [`2026-05-26_02`](artefacts/2026-05-26_02_brief-bmad-remise-a-flot-modules-9-6.md) |
| Mémoire sessions Jarvos | [`jarvos-agentique/index.md`](jarvos-agentique/index.md) — phases 0–3 livrées ; QA2 mémoire pending |
| Terrain / réception / Paheko | Addendum [`2026-05-23_01`](artefacts/2026-05-23_01_addendum-transcripts-1423-visions-rec-pko.md) ; brainstorm réception **clôturé** ; liaison Paheko — validation comptable en attente |
| Migration cockpit trio | [`2026-07-03_03`](artefacts/2026-07-03_03_proposition-migration-cockpit-local-trio.md) |
| **Peintre v0.1** (peintre-nano → moteur agnostique) | **Annoncé 2026-07-04 — préparation seulement** — [`2026-07-04_01`](artefacts/2026-07-04_01_preparation-chantier-peintre-v0-1.md) · pack PEINTRE : `peintre-nano/docs/dossier-architecte-peintre-v0-1/` · Kanban `IDEA-2026-07-04-001` · **GO exécution après HITL + arbitrage vs Epic 28/C2b** |
| Postes partagés / PIN (Epic 27) | **done** — runbook [`2026-05-29_04`](artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md) |

**Stratégie recherche : spirale.** 1re passe **clôturée** (2026-02-25). Dumps BDD : `references/dumps/` (gitignore) — schémas Recyclic et Paheko documentés.

## A rappeler (Strophe)

| Quand | Quoi | Où |
|-------|------|-----|
| **Reprise chantier parité beta** | Cocher checklist sections A–H + backlog BC-01..12 | [`2026-05-30_01`](artefacts/2026-05-30_01_checklist-chantier-parite-v2-beta-1.4.4.md) |
| **Epic 28 — retests HITL** | Valider retests listés dans revision avant gates **10.7 / 10.8** | [`revision/index.md`](revision/index.md) · sync [`00_SYNC_STATUS`](../_bmad-output/implementation-artifacts/epic-28-stabilisation-beta-terrain/00_SYNC_STATUS.md) |
| **Quand stack locale + bénévole dispo** | **C2b** — 30 min, 4 scénarios OK/KO (caisse, paiement, clôture, réception) | Plan [post-9.6](../.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md) § **C2b** |
| **Après C2b** | Lire synthèse rapport 03 : écarts **P1 clavier** → backlog **13.8** si KO | [`2026-05-26_03`](artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) |
| **Avant tag v2.0.0** | C2b complet + décision PO sur écarts restants | Plan § Ordre global |
| **Après clôture Epic 28** | Reprendre **9.7** (ACL minimales) ou prioriser via Story Runner | `sprint-status.yaml` § epic-9 |
| **Session(s) dédiée(s) — chantier Peintre v0.1** | Reprendre le tableau **5 sessions** dans [`REPRISE.md`](../REPRISE.md) § « Sessions à reprendre » — ventilation pack → HITL → promotion BMAD → arbitrage timing → exécution | [`2026-07-04_01`](artefacts/2026-07-04_01_preparation-chantier-peintre-v0-1.md) · Kanban `IDEA-2026-07-04-001` · **pas démarré 2026-07-04** |
