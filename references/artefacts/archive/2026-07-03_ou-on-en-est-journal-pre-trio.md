# Archive — journal `ou-on-en-est.md` (pré-trio lot 3a)

**Date archivage** : 2026-07-03  
**Auteur** : Ariane (worker programme)  
**Source** : `references/ou-on-en-est.md` (dernière révision **2026-05-30**)  
**Motif** : slim programme post-migration trio ; sections session / prochaine étape / spirale retirées du fichier actif.

**Remplacement actif** : [`references/ou-on-en-est.md`](../../ou-on-en-est.md) (version slim, bannière trio).  
**SoT epics/stories** : `_bmad-output/implementation-artifacts/sprint-status.yaml`.

---

## Derniere session

2026-05-27 — **Agent A clos + lancement Agent B (plan post-9.6)** :

Realise :
- Agent **A** : rapport [`2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md`](../../artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) + QA2 [`2026-05-27_01`](../../artefacts/2026-05-27_01_qa2-rapport-parite-plancher-v2-gestes-terrain.md) (gate 95 %).
- Decisions PO dans le plan : D33 = **parametre reglable** ; T3 obligatoire ; flux paiement legacy ; **GO DS** pour B.
- Plan orchestration QA2 : [`2026-05-26_04`](../../artefacts/2026-05-26_04_qa2-plan-post-9-6-plancher-compta.md).

A faire :
- **C2b** reporte (validation terrain quand possible) — voir § **A rappeler**.
- **Agent B** : create-story + dev liaison Paheko (`bmad-dev-story`) — lire plan § Agent B.

2026-05-26 — **Cloture Story 9.6 (Story Runner BMAD)** :

Realise :
- Cycle **CR1** CHANGES_REQUESTED → **DS** (guards `/admin/modules`, PATCH sans ETag si GET echoue) → **GATE** (pytest 22 + Vitest 47) → **QA** PASS → **CR2** APPROVE (`cr_loop=1`).
- Story [**9.6**](../../../_bmad-output/implementation-artifacts/9-6-config-admin-simple-modules.md) + `sprint-status.yaml` → **`done`**.
- Livrables : `/admin/modules`, API `module-config`, merge DEC-03 live-snapshot, **L-08** clos, `PATCH bandeau-live-slice` **deprecated**.

A faire (action humaine) :
- **Avant prod 2.0** : session verification **parite gestes** caisse / reception vs 1.4.4 (hors scope 9.6).
- **Epic 9 suite** : story **9.7** ou premier module metier via **cookbook** (cockpit compta, eco-organismes, etc.).

2026-05-26 — **Decision PM plancher v2.0 + lancement 9.6** :

Realise :
- Session `@bmad-agent-pm` : **Option C** (plancher + **9.6** d'abord ; HelloAsso parking ; modules incrementaux 2.0.1+).
- Alignement doc : [brief 02](../../artefacts/2026-05-26_02_brief-bmad-remise-a-flot-modules-9-6.md), `sprint-status.yaml` (`epic-9` + **9.6** `in-progress`), `epics.md` (note ordre 9.6), ce journal (§ strategie v2.0).
- Story [**9.6**](../../../_bmad-output/implementation-artifacts/9-6-config-admin-simple-modules.md) : enrichie puis promotion sprint **`in-progress`**.

A faire (action humaine) — *historique lancement 9.6 ; voir session cloture ci-dessus* :
- ~~**Nouveau chat** : `@bmad-dev-story` sur story 9.6~~ — **fait** (Story Runner 2026-05-26).
- **Avant prod 2.0** : session verification **parite gestes** caisse / reception vs 1.4.4 (hors scope 9.6).

2026-05-26 (matinee) — **Handoff BMAD modules v2 + addendum 23/05** :

Realise :
- Story 9.6 enrichie ; brief 02 ; QA2 plan post-addendum gate **96 %**.

2026-05-21 — **Brainstorm BMAD — module Réception v1** (`bmad-brainstorming`, progressive-flow) :

Réalisé :
- Session [**2026-05-21**](../../../_bmad-output/brainstorming/brainstorming-session-2026-05-21-180000.md) — **clôturée** (phases 1–4 : Question Storming → Mind Mapping → Morphological Analysis → Decision Tree).
- Périmètre v1 : REC-001, 002, 004, 008, 009, 012 ; REC-016 omnicanal → **parking v2**.
- Livrables : parcours utilisateurs, machine à états objet, inventaire matériel, modèle config admin (48 idées structurées).
- Entrée : recap [02](../../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md) + meetings 1246, 1301, 1401.

2026-05-21 — **Chantier BMAD — Liaison Paheko / compta caisse** (consolidation + validation, **pas** brainstorm UX fermeture) :

Réalisé :
- Session [**2026-05-21**](../../../_bmad-output/brainstorming/brainstorming-session-2026-05-21-paheko-compta-validation.md) — consolidation recherches Perplexity (3 passes) + terrain ; dossier [guide](../../migration-paheko/2026-05-21_guide-liaison-paheko-compta.md), [procédure clôture](../../migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md), [courrier Corinne+Caro](../../migration-paheko/2026-05-21_courrier-validation-compta-paheko-corinne-caro.md).
- **Statut :** **EN_ATTENTE_VALIDATION_COMPTABLE** (Corinne + Caro) — **pas de dev** ni brainstorm écran fermeture tant que non validé.
- **Suite prévue :** brainstorm parcours fermeture caisse (UX bénévole) → puis stories epic liaison Paheko v1.

2026-05-21 — **Terrain ressourcerie — transcription et matière produit** :

Réalisé :
- Chantier `.transcription/` (profil, inbox, **6** meetings 18–21 mai, AssemblyAI + drafts/finals).
- Recap exhaustif Réception + Liaison Paheko : [artefact 02](../../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md) ; transcriptions : [.transcription/README.md](../../../.transcription/README.md).
- Liaison Paheko compta : [guide](../../migration-paheko/2026-05-21_guide-liaison-paheko-compta.md) · [décisions](../../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) · [répertoire](../../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) · [procédure](../../migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md).

2026-05-21 — **Promotion chantier modules v2 dans PRD BMAD** :

Réalisé :
- Addendum PRD **§4.2.1** (+ §7.1, glossaire `module_key`) ; `core-architectural-decisions.md` ; note Epic 9 dans `epics.md` ; ADR-007 miroir **Accepted**.
- Synchronisation [`protocole-modules-recyclique/index.md`](../../protocole-modules-recyclique/index.md) et [`references/index.md`](../../index.md).

2026-05-20 — **Chantier mémoire sessions Jarvos (plan + phases 0–3)** :

Réalisé :
- Pack [`jarvos-agentique/`](../../jarvos-agentique/index.md), skill `jarvos-session-memory`, hooks `log/cursor-agent/`, scripts `jarvos-memoire-sessions/dev/`.
- Handoff : [artefact 07](../../artefacts/2026-05-21_07_contexte-chantier-memoire-jarvos.md).

---

2026-04-23 — **Epic 26 — Dette qualité API** : stories **26.1 … 26.5** livrées ; **`epic-26`** → **`done`** ; rétrospective [Epic 26 — 2026-04-23](../../../_bmad-output/implementation-artifacts/epic-26-retro-2026-04-23.md).

2026-04-22 — **Epic 25** : **25.1 … 25.15** livrées ; **`epic-25`** → **`done`** ; rétrospective [Epic 25 — 2026-04-22](../../../_bmad-output/implementation-artifacts/epic-25-retro-2026-04-22.md).

2026-04-21 — **Epic 24 — merge dans `master`**.

2026-04-21 — **Workflow événements caisse → Paheko** : idée Kanban archivée (socle Paheko livré).

2026-04-20 — **QA paramétrage comptable SuperAdmin (merge GitHub)** : PR **#1** ; bilan [`2026-04-20_bilan-fin-ecarts-qa-parametrage-comptable-superadmin.md`](../../artefacts/2026-04-20_bilan-fin-ecarts-qa-parametrage-comptable-superadmin.md).

2026-04-19 — **Epic 24 — Opérations spéciales caisse** : **24-1 … 24-10** **done** ; merge **2026-04-21**.

2026-04-18 — **Paheko outbox hardening v2** : trace [`2026-04-18_03_livraison-paheko-outbox-hardening-v2-plan-cloud.md`](../../artefacts/2026-04-18_03_livraison-paheko-outbox-hardening-v2-plan-cloud.md).

2026-04-13 — **Cloture documentaire (agent)** : correction section **Etat actuel** ; alignement guide-pilotage-v2 sur YAML.

2026-04-02 — **Piste B / Epic 1 — Stories 1.3 et 1.4** : specs multi-contextes + gouvernance OpenAPI.

2026-04-02 — **Epic 3 / Story 3.0 clôturée** : socle `peintre-nano/`.

2026-04-01 — **Guide de pilotage v2** + Sprint Planning BMAD relancé ; Correct Course alignement ADR P1/P2.

2026-02-26 — Sprint Planning complété (ancienne chaîne).

2026-02-26 — Create Architecture complété.

2026-02-26 — PRD complété et clarifications.

2026-02-25 — Product Brief complété.

2026-02-25 — Décisions matrice caisse/poids.

2026-02-25 — Schéma Paheko dev : plugins Caisse et Saisie au poids.

2026-02-25 — Schéma BDD Paheko dev.

2026-02-25 — Connexion BDD Recyclic dev, extraction schéma.

2026-02-25 — Decisions confrontation (push, Redis, source EEE).

2026-02-25 — Execution plan 2e passe sans BDD.

2026-02-25 — 2e passe spirale (recherches, analyse plugins).

2026-02-25 — Cloture 1re passe spirale.

2026-02-25 — Decisions 1re passe spirale (integration Paheko core, catalogue, IA/LLM).

2026-02-25 — Decisions calendrier, fichiers, RAG.

2026-02-25 — Analyse brownfield Paheko.

2026-02-24 — Analyst : doc officielle Paheko + prompts recherche.

---

## Ordre de priorite 1re passe (spirale) — historique

Ordre qui a ete suivi ; 1re passe cloturee (2026-02-25).

1. **Integration Paheko core** — perimetre, Docker, modules optionnels, ce qu'on branche.
2. **Calendrier / espace fichiers Paheko** — verifier capacites natives (eviter double conception).
3. **Catalogue modules Paheko** — croiser avec integration core, ce qui est installable.
4. **IA/LLM** — inventaire usages 1.4.4 + strategie (placeholder vs Nano/Mini).
5. **Restant Kanban** — nouvelles UI, module store, Le Fil, module correspondance, README, etc.

## Prochaine etape

> **Note (2026-05-21)** : **Réception** — brainstorm BMAD **clôturé** ([session 180000](../../../_bmad-output/brainstorming/brainstorming-session-2026-05-21-180000.md)) ; suite = atelier terrain Q1–Q6 puis PRD/epics module. **Liaison Paheko** — attendre retour **Corinne/Caro** sur le [courrier](../../migration-paheko/2026-05-21_courrier-validation-compta-paheko-corinne-caro.md) ([session validation](../../../_bmad-output/brainstorming/brainstorming-session-2026-05-21-paheko-compta-validation.md)), puis brainstorm **écran fermeture** ; en parallèle P1 modules (**story 9.6** Peintre) si reprise BMAD dev.

> **Note (2026-04-23)** : le **backlog BMAD exécutable** suivant se lit dans les **cinq** epics **`backlog`** (**9**, **10**, **12**, **20**, **21**) — voir aussi le paragraphe **Pilotage BMAD** dans **Etat actuel**. Choisir l'epic et la première story à promouvoir ; pas d'autre story « en cours » dans le YAML à cette date.

> **Note (2026-04-01)** : la ligne directrice **v2 brownfield** vit dans `_bmad-output/planning-artifacts/` (PRD, `epics.md`, `sprint-status.yaml`). Les étapes 1–3 ci-dessous sont l'historique **février 2026** ; l'état courant est dans **Dernière session** (sprint planning v2, Correct Course, alignement ADR P1/P2). Enchaînement logique aujourd'hui : **Create Story** (fichiers `.md` par clé) → **Dev Story** → **Code Review** ; optionnel : re-run **check implementation readiness** pour régénérer le rapport (un addendum 2026-04-01 documente déjà l'alignement ADR dans `implementation-readiness-report-2026-04-01.md`).

1. **Create Epics and Stories** (`/bmad-bmm-create-epics-and-stories`, agent PM John) : découper le PRD et l'architecture en épics et stories (fichier `epics.md`). Workflow en 4 étapes avec tours de réflexion et validation.
2. **Check Implementation Readiness** (`/bmad-bmm-check-implementation-readiness`, agent Architect Winston) : valider la cohérence PRD / UX / Architecture / Épics & Stories avant le sprint.
3. **Sprint Planning** (`/bmad-bmm-sprint-planning`, agent SM Bob) : produire `sprint-status.yaml` puis enchaîner le cycle Create Story → Dev Story → Code Review. **Fait (2026-02-26)** : `_bmad-output/implementation-artifacts/sprint-status.yaml` généré ; suite = créer des stories (fichiers .md) et lancer Dev Story / Code Review.

**Points de vigilance v0.1** : loader modules (TOML, ModuleBase), slots, convention tests frontend, versions Dockerfile/README — voir [checklist 2026-02-26_03](../../artefacts/2026-02-26_03_checklist-v0.1-architecture.md) et architecture.md (Gap Analysis).

**En cas de dérive** : si en cours de route une décision d'architecture ou de périmètre doit être revue (mauvaise architecture sur un point, changement de scope), utiliser le workflow **Correct Course** (`/bmad-bmm-correct-course`, agent SM Bob). Il analyse la situation et peut recommander : mise à jour du PRD, révision de l'architecture, mise à jour des épics/stories (`epics.md`), ou replanification du sprint (`sprint-status.yaml`). Les changements remontent depuis la base (décision) puis se propagent aux documents ; on peut ainsi remodifier et faire remonter même si une partie des stories est déjà réalisée.
