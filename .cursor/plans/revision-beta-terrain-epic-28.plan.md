---
name: Stabilisation beta terrain Epic 28
overview: Convertir `references/revision/` en corrections BMAD livrées via Epic 28, puis préparer les gates beta Epic 10.
todos:
  - id: wave-a
    content: "Vague A — préparation backlog et sync Epic 28"
    status: completed
  - id: wave-b
    content: "Vague B — exécution séquentielle stories 28.1 à 28.5"
    status: pending
  - id: wave-c
    content: "Vague C — préparation gates Epic 10.7 / 10.8 après retests HITL"
    status: pending
isProject: false
---

# Plan — Stabilisation beta terrain `Epic 28`

## Métadonnées chantier

| Champ | Valeur |
|-------|--------|
| `chantier_root` | `D:\Users\Strophe\Documents\1-IA\La Clique Qui Recycle\JARVOS_recyclique\_bmad-output\implementation-artifacts\epic-28-stabilisation-beta-terrain` |
| `sync_file` | `D:\Users\Strophe\Documents\1-IA\La Clique Qui Recycle\JARVOS_recyclique\_bmad-output\implementation-artifacts\epic-28-stabilisation-beta-terrain\00_SYNC_STATUS.md` |
| `plan_mode` | `meta-orchestrateur` |
| `epic_id` | `epic-28` |
| `source_backlog` | `references/revision/index.md` + `references/revision/domaines/*.md` |
| `gate_final` | `Epic 10.7` puis `Epic 10.8`, uniquement si retests HITL prioritaires OK |

## Règles d’orchestration

- Une seule story de dev active à la fois sur le dépôt.
- L’ordre canonique est `28.1 -> 28.2 -> 28.3 -> 28.4 -> 28.5`.
- Chaque story doit rappeler les IDs `REV-*` couverts.
- Après chaque story : mettre à jour `references/revision/` sur `Investigé` / `Corrigé` pour les items effectivement traités.
- `Validé HITL` reste manuel par Strophe.
- Si une story révèle un arbitrage produit large, sortir en `NEEDS_HITL` au lieu d’absorber ce sujet dans le même run.

## Vague A — Préparation backlog et sync

**Objectif :** amener `Epic 28` au point où l’Epic Runner peut enchaîner proprement les stories.

| Étape | Mode Task | Worker | Fichiers autorisés |
|-------|-----------|--------|-------------------|
| 1 | Série | setup-worker | `epics.md`, `sprint-status.yaml`, `00_SYNC_STATUS.md`, ce plan |
| 2 | Série | story-seed-worker | `references/revision/index.md`, `domaines/*.md`, futurs story files `28-*.md` |
| 3 | Série | epic-runner-brief-worker | `.cursor/agents/bmad-epic-runner.md`, `references/automatisation-bmad/epic-story-runner-spec.md`, ce plan |

**Sorties attendues :**

- `00_SYNC_STATUS.md` initialisé ;
- si nécessaire, story seeds `28-1`…`28-5` prêtes ou jalonnées ;
- brief de lancement `epic-28` prêt pour `@bmad-epic-runner`.

**QA2 :** non obligatoire sur cette vague documentaire légère. Gate : `A_PREP = done`.

## Vague B — Exécution séquentielle `Epic 28`

> **Norme d’orchestration :** la Vague B est exécutée **exclusivement** par `@bmad-epic-runner epic-28`, en série `28.1 → 28.5`. Le meta-orchestrateur ne spawn **jamais** de Story Runners `28.x` en parallèle ; les tableaux ci-dessous sont une **check-list illustrative** des étapes attendues par story (CS → VS → DS → gates → QA → CR → sync `revision/`).

**Prérequis :** `A_PREP = done` dans le sync.

**Override long-run :** série uniquement — **jamais parallèle** sur les stories de dev ; une seule story active à la fois sur le dépôt ; le meta-orchestrateur délègue la Vague B à `@bmad-epic-runner` (pas de double chemin meta-orchestrateur + Epic Runner en concurrence).

**Lancement canonique :**

```text
@bmad-epic-runner epic-28
```

*(Chemin optionnel / déconseillé : lancer manuellement un Story Runner `28.x` hors Epic Runner — réservé au déblocage HITL ponctuel, pas à l’orchestration normale.)*

### Story 28.1 — Caisse P0 *(check-list illustrative)*

| Étape | Mode Task | Worker *(illustratif)* | Fichiers autorisés |
|-------|-----------|------------------------|-------------------|
| 1 | Série | story-runner-28-1 | fichiers story `28-1*`, surfaces caisse backend/front, `references/revision/domaines/caisse.md` |
| 2 | Série | qa2-worker-28-1 | scope story 28.1 uniquement |
| 3 | Série | revision-sync-28-1 | `references/revision/domaines/caisse.md`, `references/revision/index.md` si statut P0 changé |

### Story 28.2 — Profil / PIN / sortie PWA *(check-list illustrative)*

| Étape | Mode Task | Worker *(illustratif)* | Fichiers autorisés |
|-------|-----------|------------------------|-------------------|
| 1 | Série | story-runner-28-2 | fichiers story `28-2*`, shell transverse, profil/PIN, PWA réception, `revision/domaines/transverse.md`, `admin.md`, `reception.md` |
| 2 | Série | qa2-worker-28-2 | scope story 28.2 uniquement |
| 3 | Série | revision-sync-28-2 | fichiers `revision/` couverts par la story |

### Story 28.3 — Réception terrain *(check-list illustrative)*

| Étape | Mode Task | Worker *(illustratif)* | Fichiers autorisés |
|-------|-----------|------------------------|-------------------|
| 1 | Série | story-runner-28-3 | fichiers story `28-3*`, surfaces réception, `revision/domaines/reception.md` |
| 2 | Série | qa2-worker-28-3 | scope story 28.3 uniquement |
| 3 | Série | revision-sync-28-3 | fichiers `revision/` couverts par la story |

### Story 28.4 — Admin humain *(check-list illustrative)*

| Étape | Mode Task | Worker *(illustratif)* | Fichiers autorisés |
|-------|-----------|------------------------|-------------------|
| 1 | Série | story-runner-28-4 | fichiers story `28-4*`, surfaces admin/modules/santé, `revision/domaines/admin.md`, `transverse.md` |
| 2 | Série | qa2-worker-28-4 | scope story 28.4 uniquement |
| 3 | Série | revision-sync-28-4 | fichiers `revision/` couverts par la story |

### Story 28.5 — Sites / postes *(check-list illustrative)*

| Étape | Mode Task | Worker *(illustratif)* | Fichiers autorisés |
|-------|-----------|------------------------|-------------------|
| 1 | Série | story-runner-28-5 | fichiers story `28-5*`, surfaces admin `sites` / `cash-registers`, `revision/domaines/admin.md` |
| 2 | Série | qa2-worker-28-5 | scope story 28.5 uniquement |
| 3 | Série | revision-sync-28-5 | fichiers `revision/` couverts par la story |

**QA2 :** après chaque story, scope borné au périmètre touché. Cible `>= 90`, préférer `95` sur les stories 28.1 et 28.2.

**Gate :** `B_EPIC28 = done` quand les cinq stories sont livrées, QA/CR passés, et que la liste des retests HITL restants est explicite.

## Vague C — Préparation des gates beta

**Prérequis :**

- `B_EPIC28 = done` dans le sync ;
- retests HITL prioritaires réalisés ou planifiés explicitement par Strophe ;
- aucun P0 ouvert résiduel sur les items traités par Epic 28.

| Étape | Mode Task | Worker | Fichiers autorisés |
|-------|-----------|--------|-------------------|
| 1 | Série | epic10-7-prep-worker | `epics.md`, `sprint-status.yaml`, `references/revision/index.md`, `references/artefacts/*beta*` pertinents |
| 2 | Série | epic10-8-prep-worker | mêmes fichiers + preuves QA/HITL Epic 28 |
| 3 | Série | release-readiness-sync-worker | `00_SYNC_STATUS.md`, notes readiness Epic 10 |

**Résultat attendu :**

- package propre pour lancer `Epic 10.7` ;
- puis `Epic 10.8` quand les preuves terrain sont jugées suffisantes.

**QA2 :** criticité `high` si des docs readiness sont modifiés. Gate : `C_GATES_READY = done`.

## Prompt utilisateur type

```text
Exécute le plan @.cursor/plans/revision-beta-terrain-epic-28.plan.md en mode meta-orchestrateur :
1 session, sync sur `_bmad-output/implementation-artifacts/epic-28-stabilisation-beta-terrain/00_SYNC_STATUS.md`,
Epic 28 story par story, QA2 après chaque story, pas de parallèle sur les stories de dev,
HITL seulement si arbitrage produit ou blocage réel.
```

## Sync protocol — marquage `00_SYNC_STATUS.md`

Mettre à jour `00_SYNC_STATUS.md` **à la fin de chaque vague ou story**, pas en avance.

| Clé sync | Quand marquer `done` | Prérequis |
|----------|----------------------|-----------|
| `A_PREP` | Fin Vague A | `epics.md` §28, `sprint-status.yaml` epic-28, plan et sync initialisés |
| `B_28_1` | Story 28.1 `done` + QA/CR passés + sync `revision/` caisse | `A_PREP = done` |
| `B_28_2` | Story 28.2 `done` + QA/CR passés + sync `revision/` transverse/admin/réception (PWA) | `B_28_1 = done` |
| `B_28_3` | Story 28.3 `done` + QA/CR passés + sync `revision/` réception | `B_28_2 = done` |
| `B_28_4` | Story 28.4 `done` + QA/CR passés + sync `revision/` admin/transverse | `B_28_3 = done` |
| `B_28_5` | Story 28.5 `done` + QA/CR passés + sync `revision/` sites/postes | `B_28_4 = done` |
| `B_EPIC28` | Les cinq stories 28.x `done`, QA/CR passés, liste retests HITL restants explicite | `B_28_5 = done` |
| `C_GATES_READY` | Package readiness Epic 10.7/10.8 documenté ; retests HITL prioritaires planifiés ou faits | `B_EPIC28 = done` ; **0 P0 ouvert** dans `references/revision/index.md` (ou exceptions listées par Strophe) |

Ne jamais marquer `B_28_n` ou `B_EPIC28` avant la clôture BMAD réelle de la story correspondante.

## Anti-patterns spécifiques à ce chantier

- Démarrer `9.7` ou `10.7` avant `28.1`.
- Lancer plusieurs Story Runners `28.x` en parallèle.
- Marquer une story `done` sans synchroniser les `REV-*` couverts.
- Fermer un item `revision/` en `Validé HITL` sans retest Strophe.
- Fusionner dans `28.4` ou `28.5` des sujets de vision long terme comme `REV-ADMIN-10`.
