---
name: Post-9.6 plancher et compta
overview: Orchestration parallèle Agent A (parité plancher 2.0) et Agent B (liaison Paheko 2.0.1), avec délégation Task + QA2 sur les livrables, sync Coordinateur.
todos:
  - id: agent-a-done
    content: "Agent A — rapport 03 + QA2 OK (fait 2026-05-27)"
    status: completed
  - id: po-decisions-b
    content: "Décisions PO § ci-dessous — lues par Agent B via ce plan (pas de message Strophe)"
    status: completed
  - id: agent-b-ds
    content: "Agent B — create-story + dev liaison Paheko (GO DS dans plan)"
    status: completed
  - id: hitl-c2b
    content: "Strophe — C2b REPORTÉ (stack locale + bénévole) — checklist § C2b du plan"
    status: pending
  - id: coord-sync-doc
    content: "Coordinateur — C3 sync journal après C2b (sync partielle post-B faite 2026-05-27)"
    status: pending
isProject: false
---

# Plan post-9.6 — Agent A / Agent B

## Où on en est (2026-05-27)

| Rôle | Statut |
|------|--------|
| **Agent A** | **Terminé** — rapport [`2026-05-26_03_…`](references/artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) + QA2 OK |
| **Agent B** | **Terminé (2026-05-27)** — story `9-10` **done** ; QA2 96 % P0=0 ; CR APPROVE |
| **Strophe** | **C2b reporté** — quand stack locale + bénévole (checklist § C2b) ; voir aussi `ou-on-en-est.md` § A rappeler |

## Démarrage rapide

| Rôle | Instruction |
|------|-------------|
| **Agent B** | *« Tu es **Agent B**. Lis ce plan : § **Décisions PO Strophe** puis § **Agent B**. »* |
| **Strophe** | **Plus tard** — § C2b (ne bloque pas le lancement de B). |
| **Coordinateur** | **C3** sync doc après C2b et/ou fin story B. |

**Un chat = un rôle.** Agent A : **clos** (ne pas relancer sauf correctif rapport).

**Gate C0bis (cible à obtenir, avant C1) :** publier le rapport [references/artefacts/2026-05-26_04_qa2-plan-post-9-6-plancher-compta.md](references/artefacts/2026-05-26_04_qa2-plan-post-9-6-plancher-compta.md) sur disque avec **P0 plan = 0** et score ≥ 95 %. Ce gate n’est **pas** acquis par défaut — **C1 interdit** tant que ce rapport n’existe pas avec ces critères.

```mermaid
flowchart TB
  C0bis[C0bis_gate_plan_QA2]
  C0[C0_commit_9_6]
  C1[C1_lancer_A_B]
  Coord[Coordinateur]
  A[Agent_A]
  B[Agent_B]
  PauseB[Pause_DS_B]
  HITL[HITL_Strophe_C2b]
  C2a[C2a_rapport_QA2]
  C2b[C2b_signoff]
  C3[C3_sync_doc]
  C0bis --> C0 --> C1
  C1 --> Coord
  Coord --> A
  Coord --> B
  A --> TaskA[Task_sous_agents]
  A --> QA2A[qa2_rapport_03_seul]
  B --> TaskB[Task_sous_agents]
  B --> QA2B[qa2_story_code]
  A -.->|ecart_bloquant_fermeture| PauseB
  PauseB -.-> B
  QA2A --> C2a --> HITL --> C2b
  QA2B --> Coord
  C2b --> C3
```

*Vue orchestration complète (C0bis→C3, pause B, HITL). Les flèches pointillées = C-sync.*

---

## Contexte (commun)

- **9.6** : `done` — [`9-6-config-admin-simple-modules.md`](_bmad-output/implementation-artifacts/9-6-config-admin-simple-modules.md).
- **Produit** : dépôt = **v2.0** ; prod réf. = **1.4.4** (autre Git) ; **2.0.1+** = un module à la fois ; **HelloAsso**, **9.1**, **9.7** = pas maintenant.
- **Brief 02 — fil E (EC)** : avant **C1**, lire la **dérogation EC** (gate waived dev / blocking prod) dans [`references/artefacts/2026-05-26_02_brief-bmad-remise-a-flot-modules-9-6.md`](references/artefacts/2026-05-26_02_brief-bmad-remise-a-flot-modules-9-6.md) — évite de relancer le débat comptable au lancement des chats A/B.

---

## Règles d’orchestration (Agent A et B)

1. **Parent = routeur** — déléguer le travail lourd via **`Task`** (`explore` / `generalPurpose`, modèle **auto**). Ne pas ingérer tout le repo dans le chat parent.
2. **QA sur chaque livrable** — invoquer **`@qa2-orchestrator`** avec brief aligné sur `C:\Users\Strophe\.cursor\skills\qa2-agent\workflow.md` (+ `workflow-loop.md` si boucle) et gabarit `C:\Users\Strophe\.cursor\skills\qa2-agent\references\qabrief-template.md`. **Gate score ≥ 95 %** ; **P0 ouvert dans le rapport QA2 = gate non atteint** même si le score affiché est ≥ 95 % (`workflow-loop.md`).
3. **Owners fichiers**

| Fichier | Owner |
|---------|--------|
| `references/artefacts/2026-05-26_02_brief-bmad-remise-a-flot-modules-9-6.md` | Coordinateur (sync C3 ; lecture A/B) |
| `references/artefacts/2026-05-26_03_*` | Agent A |
| `_bmad-output/implementation-artifacts/*liaison-paheko*` | Agent B |
| `references/ou-on-en-est.md`, `sprint-status.yaml` | Coordinateur |
| `references/protocole-modules-recyclique/` | Agent B si cookbook ; A lecture seule |

4. **Sync A ↔ B** — **D33 tranché** (§ Décisions PO) : plus de pause DS pour D33. **T3** = dans le scope story B (voir § Décisions PO).

---

## Décisions PO Strophe (2026-05-27) — **Agent B : lire avant create-story / DS**

*Strophe n’a pas à recopier ce bloc dans le chat B — il est dans le plan.*

| Sujet | Décision |
|-------|----------|
| **D33 (seuil écart espèces)** | **Paramètre réglable** par site (settings admin), défaut suggéré **2 €** — unifie terrain + Paheko en v2. Ne pas figer 0,05 € seul ni 2 € en dur sans setting. |
| **T3 (lot compta écart 658/758)** | **Obligatoire** dans la story liaison (batch builder). |
| **Écran paiement** | Garder le **même flux de gestes** qu’en 1.4.4 (saisie, Enter, enchaînement) ; les ajouts v2 OK si le geste de départ reste identique. Backlog **13.8** si écart après C2b — **pas** dérogation large. |
| **GO DS Agent B** | **Oui** — `bmad-dev-story` autorisé ; copier les 3 lignes ci-dessus dans la story (AC ou § contexte). |
| **C-sync D33** | **Levé** — décision PO ci-dessus remplace l’attente Coordinateur sur D33. |

---

## C2b — Validation terrain Strophe (simple)

**Statut : REPORTÉ** (2026-05-27) — à faire **quand la stack locale tourne** et qu’un bénévole est disponible. **Ne bloque pas** le lancement d’Agent B. **Bloque** le tag **`v2.0.0`** (plancher prod).

**Rappel :** section aussi dans [`references/ou-on-en-est.md`](../references/ou-on-en-est.md) § **A rappeler**.

**Ce n’est pas dans le gros rapport sous forme de cases à cocher** — le rapport a une section vide « Validation humaine » (fin du fichier `…03_…`, ~l.292). **Tu coches ici**, dans le plan.

**Comment faire :** 30 min, Peintre (`localhost:4444`) vs legacy (`localhost:4445`) si possible. Pour chaque ligne : **OK** ou **KO** (+ une phrase si KO).

| # | Scénario (30 min max) | OK / KO | Note |
|---|------------------------|---------|------|
| 1 | **Vente rapide** : 3 catégories clavier → poids/prix → Enter → paiement espèces Enter | | |
| 2 | **Paiement** : même enchaînement saisie / Enter qu’avant (flux legacy) | | |
| 3 | **Fermeture caisse** : compter, valider (geste global compréhensible) | | |
| 4 | **Réception** : une saisie ticket + grille catégories clavier | | |

**Quand c’est fait :** remplir aussi le tableau « Validation humaine » en **bas** du rapport `2026-05-26_03_…` (date + signataire Strophe), ou écrire « C2b OK » dans le chat Coordinateur.

**Tag v2.0.0** : seulement après cette checklist **OK** (ou KO documentés). **Après C2b :** relire le rapport `03` — si KO sur paiement/clavier → story **13.8** ; sinon rien d’urgent pour B.

---

## Coordinateur

| Étape | Action | Gate / DoD |
|-------|--------|------------|
| **C0bis** | **Cible** gate qualité de ce plan : **publier** le rapport [`references/artefacts/2026-05-26_04_qa2-plan-post-9-6-plancher-compta.md`](references/artefacts/2026-05-26_04_qa2-plan-post-9-6-plancher-compta.md) avec **P0 plan = 0**, score ≥ 95 % (boucle QA2 plan si besoin). Non acquis tant que le fichier n’existe pas sur disque avec ces critères. | **Bloquant** avant C1 — **C1 interdit** sinon |
| **C0** | Commit jalon **9.6** — `@git-specialist` ou manuel : `feat(modules): close story 9.6 …` | **Recommandé fort** ; **obligatoire** si le dépôt a des changements 9.6 non commités |
| **C1** | Ouvrir 2 chats Agent A / B (§ Démarrage rapide) | C0bis OK |
| **C2a** | Rapport A livré + QA2 rapport ≥ 95 %, P0 rapport = 0 | Chemins : `references/artefacts/2026-05-26_03_*` |
| **C2b** | **Strophe** — checklist **§ C2b** de ce plan (4 lignes OK/KO) | Sign-off dans plan ou bas du rapport `…03_…` |
| **C3** | Sync `ou-on-en-est.md`, `brief 02`, `sprint-status.yaml` | **Prérequis : C2b complété** (sign-off HITL Strophe). Story B `done` + QA2 B ≥ 95 % si DS engagé ; **interdit tag `v2.0.0`** tant que **C2b** non fait |

**Checklist livrables Coordinateur (avant C3)**

| Livrable | Chemin | Gate |
|----------|--------|------|
| Rapport parité plancher | `references/artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md` | QA2 ≥ 95 %, P0 = 0 |
| Sign-off parité | section « validation humaine » du rapport ou message Strophe | C2b |
| Story liaison Paheko | `_bmad-output/implementation-artifacts/*liaison-paheko*` | VS OK, pytest vert, QA2 ≥ 95 %, CR APPROVE |

### C-sync — fermeture caisse (A → Coordinateur → B)

| Champ | Valeur |
|-------|--------|
| **Déclencheur** | Agent A classe un écart **bloquant** sur le parcours **fermeture caisse** (sévérité P0 dans le rapport ou section « impact Agent B ») |
| **Émetteur** | Agent A (chat A) |
| **Artefact alerte** | Ligne dans le rapport `…03_…` § « impact Agent B » **+** message Coordinateur : chemin rapport, extrait écart, horodatage |
| **Pause DS B** | Agent B **arrête** `bmad-dev-story` / merge ; story peut rester en `in-progress` |
| **Critère GO Coordinateur** | Coordinateur tranche : (1) écart non bloquant pour 2.0.1 → GO DS ; (2) correctif A d’abord → B attend ; (3) dérogation PO documentée dans la story B |
| **Délai cible** | Réponse Coordinateur **&lt; 24 h ouvrées** ; au-delà, B reste en pause (pas de DS silencieux) |
| **Escalade J+1** | Si pas de réponse Coordinateur à **J+1** (24 h ouvrées) après alerte C-sync : Agent A **relance** Coordinateur ; Agent B **maintient** la pause DS ; Coordinateur documente la tranche (GO / attendre A / dérogation PO) dans le chat et la story B |
| **Reprise B** | GO explicite dans le chat Coordinateur **copié** en note story (AC ou commentaire) ; puis reprise DS au step interrompu |

**C1** : lancer A et B en parallèle **sous réserve** règle §5 (DS B conditionné).

---

## Agent A — Parité plancher 2.0

**Statut : TERMINÉ (2026-05-27).** Ne pas relancer sauf correctif demandé par Coordinateur.

**Tu es Agent A.** (Référence historique — mission close.)

**Objectif :** rapport d’écarts caisse + réception (workflows, raccourcis clavier) vs **1.4.4**.

**Livrable :** [`references/artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md`](references/artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md)  
Colonnes : parcours | legacy | Peintre | écart | sévérité | owner | dérogation PO.

**Prérequis dépôt legacy :** le clone / chemin **`recyclique-1.4.4/`** (prod réf. **1.4.4**, autre Git) doit être accessible avant `Task` explore — sinon STOP Coordinateur.

**Références (Task explore, ne pas tout charger en parent) :**

- [`sprint-change-proposal-2026-04-12-parite-caisse-legacy-stricte.md`](_bmad-output/planning-artifacts/sprint-change-proposal-2026-04-12-parite-caisse-legacy-stricte.md)
- [`2026-04-10_03_matrice-parite-ui-pilotes-peintre.md`](references/artefacts/2026-04-10_03_matrice-parite-ui-pilotes-peintre.md)
- [`guide-pilotage-v2.md`](_bmad-output/planning-artifacts/guide-pilotage-v2.md) (caisse)
- `peintre-nano/`, **`recyclique-1.4.4/`** (référence obligatoire), `contracts/creos/manifests/`

**Enchaînement**

> **Pont D33 / D29 (fermeture caisse — lecture A, implémentation B)**  
> - **D33** (écart espèces / fonds) : tolérance cible **±2 €** ; au-delà → écart documenté, sévérité à trancher (C-sync si bloquant pour B).  
> - **D29** (agrégats clôture) : ventiler **T1 / T2 / T3** ; comparer legacy **1.4.4** vs Peintre sur ces blocs.  
> - **Tension legacy vs D33** : legacy peut tolérer **0,05 €** sur certains arrondis — **ne pas** calquer D33 sur 0,05 € sans décision PO ; noter l’écart dans le rapport § fermeture caisse.

1. `Task` **explore** — cartographie parcours + fichiers (incl. **fermeture caisse**).
2. Rédaction du rapport `…03_…md` (section dédiée **fermeture caisse** avant fin de rédaction si parallèle B).
3. `@qa2-orchestrator` — **`scope_paths` = uniquement** [`references/artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md`](references/artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) ; les refs citées dans le rapport **ne sont pas** dans le scope QA2 (le worker s’appuie sur le texte du livrable). Gate **95 %**, **P0 = 0**.
4. Si blocage **fermeture caisse** → § « impact Agent B » + alerte Coordinateur (**C-sync**).
5. Retour Coordinateur : chemin rapport, résumé 5 lignes, écarts P0.

**Hors scope :** code métier, 9.7, modules optionnels.

**Fin A (C2a) :** QA2 rapport ≥ 95 %, P0 = 0. **C2b** (HITL Strophe) = hors chat A — Coordinateur trace le sign-off.

---

## Agent B — Liaison Paheko clôture v1 (2.0.1)

**Tu es Agent B.** Exécute uniquement cette section.

**Objectif :** story BMAD + implémentation **fermeture caisse → écritures Paheko** ; comptes en **settings** paramétrables (7070, 7541, 53x, 5112…).

**Epic 23** (`/admin/compta` expert) : **done** — ne pas refaire 23-2/23-3.

**Gate EC — dérogation (décision Strophe 2026-05-26, brief 02 fil E)** : le brainstorming officiel reste en attente comptable, mais le **fil E (liaison Paheko v1)** peut avancer **avec comptes en settings paramétrables** et hypothèses EC documentées dans la story ; validation Corinne/Caro reste requise avant prod réelle des écritures sensibles.

| Identifiant gate | Statut plan | Effet sur ce plan |
|------------------|-------------|-------------------|
| **`EN_ATTENTE_VALIDATION_COMPTABLE`** ([`brainstorming-session-2026-05-21-paheko-compta-validation.md`](_bmad-output/brainstorming/brainstorming-session-2026-05-21-paheko-compta-validation.md)) | **waived** pour dev story + DS v1 | Story + code liaison **autorisés** ; hypothèses EC + settings obligatoires |
| Validation écrite Corinne/Caro (courrier 2026-05-21) | **blocking** pour prod / tag module « validé EC » | Hors scope livraison technique v1 ; pas de blocage `bmad-create-story` / DS sous dérogation |

**Références (Task explore d’abord) :**

- [`2026-04-15_prd-recyclique-caisse-compta-paheko.md`](references/migration-paheko/2026-04-15_prd-recyclique-caisse-compta-paheko.md)
- [`2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md`](references/migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md)
- [`2026-05-21_procedure-cloture-liaison-paheko-recyclique.md`](references/migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md)
- [`06-MOD-cookbook`](references/protocole-modules-recyclique/06-MOD-cookbook-nouveau-module-optionnel.md), [`05-MOD-registre`](references/protocole-modules-recyclique/05-MOD-registre-module-key.md) — pas de compta dans JSON `module-config` (loup de mer #7)

**MVP sans module comptage D5 (tranché)** : **v1 dégradée** — pas de module D5 ; à la clôture, **écart espèces / fonds** saisi **manuellement** par l’admin (champ checklist ou écran minimal documenté dans la story) ; les écritures Paheko partent des agrégats T1/T2/T3 + cet écart. **Report DS** du module comptage pièces = phase 2 explicite dans la story (hors AC v1).

> **Pont D33 / D29 — décision PO 2026-05-27 (§ Décisions PO ci-dessus, obligatoire en story)**  
> - **D33** : seuil écart espèces = **setting paramétrable** (défaut 2 €), utilisé terrain + règle Paheko.  
> - **D29** : **T1 + T2 + T3** obligatoires (T3 = kind batch 658/758 — était absent, à implémenter).  
> - **Paiement** : ne pas casser le flux clavier legacy (saisie / Enter) — voir § Décisions PO.

**Enchaînement**

1. **Lire § Décisions PO Strophe** (ce plan) — avant tout create-story.
2. `Task` **explore** — synthèse MVP v1 (T1/T2/T3, settings comptes + seuil D33, écart manuel admin, hors D5).
3. `bmad-create-story` — slug type `…-liaison-paheko-cloture-caisse-v1` ; **inclure** décisions PO dans la story.
4. VS validate — **max 2 retries** ; si 2 échecs → escalade Coordinateur.
5. **`bmad-dev-story`** — **GO DS** (décision PO dans le plan) ; déléguer DS en `Task` si contexte lourd.
6. **Gate pytest** : suite **verte** obligatoire ; `timeout_sec` **≥ 330** (ne pas descendre sous 330 s).
7. `@qa2-orchestrator` — **`scope_paths` = uniquement** le fichier story `_bmad-output/implementation-artifacts/*liaison-paheko*`. Gate **95 %**, **P0 = 0**.
8. `bmad-code-review` via `Task` si besoin.
9. Retour Coordinateur : chemin story, statut, risques EC.

**Hors scope v1 :** éco-org 9.1, HelloAsso, **module comptage D5** (phase 2), UX bénévole clôture élaborée (phase 2).

**Fin B :** story `done` + CR APPROVE + QA2 ≥ 95 %, P0 = 0.

**Pause DS** : uniquement si Coordinateur annule le GO PO — sinon enchaîner.

---

## Hors scope commun

9.7, 9.1, HelloAsso (parking). Tag **`v2.0.0` interdit** avant **C2b** (sign-off parité) **et** décision Coordinateur. Tag **`v2.0.1` interdit** avant **C2b** **et** rapport A QA2 ≥ 95 % avec **P0 rapport = 0** (`…03_…`) ; **`v2.0.1`** = story liaison Paheko (Agent B) après ces gates.

---

## Ordre global (mis à jour 2026-05-27)

1. ~~Agent A~~ **fait**.  
2. ~~**Agent B**~~ **fait** (story `9-10-liaison-paheko-cloture-caisse-v1` **done**).  
3. **Strophe** : **C2b plus tard** (§ C2b + `ou-on-en-est` § A rappeler).  
4. **Coordinateur** : **C3** sync journal (apres B et/ou apres C2b).  
5. Tag **v2.0.0** : apres **C2b** seulement. Tag **v2.0.1** : apres story B **done**.
