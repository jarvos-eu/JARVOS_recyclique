# To-do reflexion / recherche — JARVOS Recyclique

> Tâches **hors flux BMAD** (hors epics/stories). Kanban idées : [`docs/ideas/kanban/INDEX.md`](../docs/ideas/kanban/INDEX.md).
>
> **Spirale 1 — clos (2026-02-25).** Items ouverts ci-dessous = **post-v2**, **gated** (Epic 28 / C2b) ou **réflexion** sans story dédiée.

---

## Prochaines sessions (fil Clio)

> Détail session par session : [`REPRISE.md`](../REPRISE.md) § « Sessions à reprendre — chantier Peintre v0.1 ».
>
> **Branche ouverte (2026-07-07) :** mission urgence **T2 Ecologic** — **pas de story BMAD** (patch 1.4.5, Epic 9, Peintre v0.1) tant que l'assistance décla est en cours.

- [ ] **🔴 P0 URGENCE — Assistance décla Ecologic T2 2026** — dump reçu · **pg_restore miroir RO** → requêtes T2 → CSV complément `DEC_REE` (8/9 cases) · échéance ~**30/07/2026** · entrée [`2026-07-07_mission-assistance…`](eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/2026-07-07_mission-assistance-decla-ecologic-t2-2026.md) · spec [`2026-07-07_06`](artefacts/2026-07-07_06_mission-assistance-decla-ecologic-t2-recyclic-144.md) · [`IDEA-2026-07-07-001`](../docs/ideas/kanban/IDEA-2026-07-07-001.md)
- [ ] **🔴 P0 — Bot Discord pilote La Clique** — CH-LACLIQUE-BOT-001 · **bloqué gate Ombre/CREOS** · Discord→Hermes→Ombre→Cursor · spec [`JARMES/docs/programme/CH-LACLIQUE-BOT-001-spec.md`](../../../JARMES/docs/programme/CH-LACLIQUE-BOT-001-spec.md) · [`IDEA-2026-07-05-002`](../docs/ideas/kanban/IDEA-2026-07-05-002.md)
- [ ] **S1** — Ventiler pack PEINTRE + zip `_depot` → `references/dossier-architecte-peintre-v0-1/` (@depot-specialist)
- [ ] **S2** — HITL questions ouvertes (`09-PEINTRE-risques-et-questions-hitl.md`)
- [ ] **S3** — Promotion PRD `06` → epics/stories BMAD
- [ ] **S4** — Arbitrage timing vs Epic 28 / C2b (Mentor → Ariane)
- [ ] **S5** — GO exécution → @bmad-epic-runner (épics A → B → C)

Entrée : [`artefacts/2026-07-04_01`](artefacts/2026-07-04_01_preparation-chantier-peintre-v0-1.md) · Kanban [`IDEA-2026-07-04-001`](../docs/ideas/kanban/IDEA-2026-07-04-001.md)

---

## Patch 1.4.5 éco-organismes (gated)

> **Gelé** tant que mission assistance T2 Ecologic **en cours** — cadrages prêts (3 partenaires), **implémentation patch = branche suivante**.

- [ ] **Patch 1.4.5 La Clique** — après clôture mission T2 · cadrages [`03`](artefacts/2026-07-07_03_cadrage-patch-1.4.5-ecomaison.md) / [`04`](artefacts/2026-07-07_04_cadrage-patch-1.4.5-ecologic.md) / [`05`](artefacts/2026-07-07_05_cadrage-patch-1.4.5-refashion.md) · index [`eco-organismes/`](eco-organismes/index.md)

---

## Ouvert

- [ ] **Chantier Peintre v0.1** (`peintre-nano` → moteur agnostique) — annoncé 2026-07-04 ; **pas démarré** — entrée : [`artefacts/2026-07-04_01`](artefacts/2026-07-04_01_preparation-chantier-peintre-v0-1.md) · pack PEINTRE : `peintre-nano/docs/dossier-architecte-peintre-v0-1/` (move → `references/` à faire) · Kanban [`IDEA-2026-07-04-001`](../docs/ideas/kanban/IDEA-2026-07-04-001.md) · séquencer vs Epic 28 / C2b avant GO exécution.
- [ ] Front caisse/réception (futur) — quand on s'en empare : brainstorm + cadrage BMAD ; **pas d'exécution automatique avant décision** — entrée : [artefact 2026-03-26_01](artefacts/2026-03-26_01_blueprint-layout-workflow-ecrans.md) ; à reverser dans `architecture.md` + `epics.md` (Epic 8) avant Create Story.
- [ ] v0.1 — Checklist architecture : loader modules (TOML, ModuleBase) — **partiellement couvert** par protocole modules / Epic 9 ; reliquat : [artefact 2026-02-26_03](artefacts/2026-02-26_03_checklist-v0.1-architecture.md) (à revisiter post-v2).
- [ ] Politique fichiers — suivi Kanban [`IDEA-2026-02-25-001`](../docs/ideas/kanban/IDEA-2026-02-25-001.md) · artefact [`2026-02-25_02`](artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md)
- [ ] Presets / boutons rapides (Don, Recyclage, Déchèterie…) — matrice éco vs non-éco à documenter
- [ ] Module correspondance — détail champs/règles post-v2 (BDD + instance dev)

## Infra VPS / agents

> Chantiers infra **hors flux BMAD** — utiles agents / Hermes ; **en attente V2 produit** pour intégration bot. **P1 proche** : derrière urgence T2 Ecologic et gate CREOS bot.

- [ ] **🟠 P1 proche — K-Drive headless VPS — déploiement miroir La Clique** — clone local kSuite sur VPS (client desktop AppImage) pour agents / scripts ; levier futur mode **AIDE** bot Discord (post-gate CREOS) · runbook [`2026-07-07_08`](artefacts/2026-07-07_08_installation-kdrive-headless-vps.md) · cadrage bot [`2026-07-05_02`](artefacts/2026-07-05_02_cadrage-bot-discord-la-clique-pilote.md) · chantier fichiers [`2026-02-25_02`](artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md) · kanban [`IDEA-2026-07-05-002`](../docs/ideas/kanban/IDEA-2026-07-05-002.md)
  - [ ] Setup OAuth initial (VNC / première connexion GUI)
  - [ ] Service **systemd** (démarrage auto, logs)
  - [ ] Test **list / read** Python sur miroir local
  - [ ] Garde-fous **permissions** (zones RO, périmètre écriture agents)

## Spirale 1 — clos (2026-02-25)

- [x] Repo 1.4.4, brownfield, PRD, architecture, versioning v0.1.0
- [x] Recherches Paheko (modules, auth, API caisse, saisie au poids, version 1.3.19.x)
- [x] Décisions sync financière, source de vérité caisse, granularité push (Redis Streams)
- [x] Dumps BDD + instance Paheko dev + confrontation RecyClique vs Paheko
- [x] Checklist import 1.4.4, inventaire usages LLM 1.4.4
- [x] Stratégie LLM/IA — couvert par Kanban [`IDEA-2026-02-24-002`](../docs/ideas/kanban/IDEA-2026-02-24-002.md) (placeholder v0.1.0)
- [x] Peintre gardien du seuil — suivi Kanban [`IDEA-2026-05-20-001`](../docs/ideas/kanban/IDEA-2026-05-20-001.md) · pack L-16 / T-PEINT-1
- [x] Structure de travail, plan Git (2026-02-24)
