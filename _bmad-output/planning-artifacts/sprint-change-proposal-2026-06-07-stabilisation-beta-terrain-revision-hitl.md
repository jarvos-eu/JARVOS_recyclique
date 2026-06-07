# Sprint Change Proposal — Stabilisation beta terrain depuis `references/revision/`

Date: 2026-06-07
Mode: Batch
Statut: Approved
Approbation utilisateur: yes

## 1. Issue Summary

### Déclencheur validé

Le registre `references/revision/` consolide désormais un backlog terrain vivant issu de la revue HITL du 2026-06-07. Ce registre remonte des problèmes multi-domaines qui ne sont pas de simples détails UX, mais des écarts bloquants entre la v2 livrée et l’exploitabilité réelle sur le terrain.

Les blocages les plus urgents sont :

- `REV-CAISSE-02` — fermeture caisse sans effet ;
- `REV-CAISSE-05` / `REV-CAISSE-06` — montant visible mais finalisation inutilisable ;
- `REV-CAISSE-10` — held sale vs encaissement ;
- `REV-CAISSE-12` — caisse virtuelle bloquée par une session réelle ;
- `REV-RECEPTION-02` — PWA réception sans retour menu ;
- `REV-TRANSVERSE-01` + `REV-ADMIN-01` — chaîne `Mon profil` / PIN opérateur cassée.

### Nature du changement

- Ce n’est pas un bug isolé porté par une story unique.
- Ce n’est pas non plus un nouveau chantier produit autonome.
- Il s’agit d’un **rebaselining de stabilisation beta** : transformer un registre terrain vivant en backlog BMAD exécutable, sans réécrire artificiellement l’historique des epics déjà `done`.

### Evidence

- `references/revision/index.md` liste **6 P0** ouverts au moment du déclenchement.
- `references/revision/domaines/caisse.md` montre que plusieurs blocages critiques se concentrent autour de la même chaîne session -> ticket -> encaissement -> clôture.
- `references/revision/domaines/reception.md` confirme un blocage PWA réel sur la sortie de l’écran réception.
- `references/revision/domaines/admin.md` et `transverse.md` confirment que le flux PIN est incomplet côté v2 malgré les briques déjà livrées côté postes partagés.
- Les epics `6`, `7`, `13`, `17`, `19`, `21`, `27` donnent des fondations pertinentes, mais ne portent pas aujourd’hui un backlog explicite de correction post-HITL.

## 2. Impact Analysis

### 2.1 Impact sur les epics existants

#### Epic 6 — Caisse terrain

Impact: fort, mais sans rollback.

Ce qui reste valide :

- la base métier caisse ;
- le chemin brownfield-first ;
- les premiers parcours vente / remboursement / clôture ;
- l’intention d’exploitabilité terrain.

Ce qui devient insuffisant :

- la preuve d’exploitabilité ne couvre plus les cas terrain observés le 2026-06-07 ;
- les statuts `done` n’impliquent pas fermeture effective des `REV-CAISSE-*` ;
- les régressions `held sale`, finalisation et reprise de session ne sont pas portées comme backlog actif.

Conclusion :

- ne pas rouvrir ni réécrire l’Epic 6 ;
- ajouter un epic correctif qui s’appuie sur lui comme socle métier.

#### Epic 12 — Parité UI réception

Impact: direct.

Cet epic backlog est le plus proche pour la réception, mais il ne couvre pas à lui seul la sortie PWA bloquée ni la logique transverse de navigation.

Conclusion :

- réutiliser Epic 12 comme référence de périmètre réception ;
- ne pas lui faire absorber toute la stabilisation beta multi-domaines.

#### Epic 17 — Sites et postes

Impact: partiel.

Les stories `17.x` ont permis de porter `sites` et `cash-registers`, mais les retours terrain montrent que l’édition et le retour au hub restent incomplets pour l’usage réel.

Conclusion :

- traiter les corrections comme une nouvelle tranche de stabilisation ;
- ne pas prétendre que `17.2` couvrait déjà toute l’exploitabilité terrain.

#### Epic 21 — Users admin

Impact: direct.

Le flux `Mon profil` / PIN self-service relève fonctionnellement de la famille `users`, mais le backlog `21.x` n’a pas été activé, alors que le besoin est désormais bloquant pour le terrain.

Conclusion :

- l’épic de stabilisation doit explicitement réactiver ce sous-domaine ;
- `Epic 21` reste une dépendance logique, pas le bon véhicule unique pour la vague entière.

#### Epic 27 — Postes partagés + PIN + PWA installable

Impact: direct mais non contradictoire.

Epic 27 a livré l’infrastructure PWA / PIN / device, mais la revue terrain révèle deux écarts résiduels :

- le flux humain `Mon profil` n’est pas accessible ;
- la PWA réception peut piéger l’utilisateur sans sortie.

Conclusion :

- ne pas rouvrir Epic 27 comme si ses stories étaient fausses ;
- créer une tranche de stabilisation au-dessus de cette fondation.

#### Epic 9 — Modules complémentaires v2

Impact: faible à moyen.

Les surfaces `Admin modules` sont concernées par du bruit UX, du jargon et un bug d’enregistrement, mais ces problèmes restent secondaires par rapport aux P0 terrain caisse / réception.

Conclusion :

- ne pas laisser `9.7` ou la suite d’Epic 9 préempter la priorité beta ;
- intégrer les surfaces modules dans une story de débruitage admin, après fermeture des P0.

#### Epic 10 — Gates beta / readiness

Impact: fort mais différé.

Les stories `10.7` et `10.8` restent la bonne fin de chaîne pour la beta, mais elles ne doivent pas démarrer tant que le backlog `revision/` n’est pas converti en corrections livrées et retestées.

Conclusion :

- l’épic de stabilisation doit précéder les gates Epic 10 ;
- la fermeture des P0 du registre devient un prérequis implicite de `10.7`.

### 2.2 Conflits documentaires et de pilotage

#### Conflit backlog

Le dépôt possède un registre terrain vivant (`references/revision/`) mais aucun epic de correction explicitement relié à ce registre.

Impact :

- divergence entre backlog produit terrain et backlog BMAD ;
- impossible de lancer un long run propre sans phase de traduction.

#### Conflit de preuve

Plusieurs epics sont `done`, alors que des items terrain homologues sont toujours ouverts.

Impact :

- le statut YAML ne peut plus être lu comme preuve suffisante de stabilité terrain ;
- il faut distinguer clairement `done BMAD` et `Validé HITL`.

#### Conflit d’orchestration

Le besoin utilisateur porte sur un run autonome multi-domaines, alors que les runners BMAD imposent une discipline **une story active à la fois** sur le dépôt.

Impact :

- impossible de lancer 4 stories de dev en parallèle sur le même repo sans perdre la cohérence ;
- il faut structurer le long run en vagues séquentielles.

## 3. Recommended Approach

### Choix retenu

**Direct adjustment with explicit corrective epic.**

Le bon compromis n’est ni de rouvrir les epics clos, ni de laisser `revision/` comme simple pense-bête terrain. Il faut injecter un **nouvel epic dédié** de stabilisation beta terrain.

### Nouvel epic recommandé

**Epic 28 — Stabiliser la beta terrain depuis le registre `references/revision/`**

Objectif :

- transformer les `REV-*` prioritaires en stories BMAD exécutables ;
- fermer les P0/P1 critiques par vagues ;
- garder la validation HITL séparée de la validation code / QA / CR.

### Découpage stories recommandé

1. `28.1` — stabiliser la caisse terrain P0 : session, finalisation, clôture, held sale, virtuel ;
2. `28.2` — rétablir `Mon profil`, PIN et sortie PWA minimale ;
3. `28.3` — rendre la réception terrain exploitable en hub et poste ;
4. `28.4` — débruiter les surfaces admin pilotes pour humains ;
5. `28.5` — rétablir l’édition et la navigation `sites` / `postes`.

### Risque

Risque moyen :

- plusieurs stories traversent plusieurs domaines techniques ;
- certains écarts peuvent relever d’un bug réel, d’un gap de parité, ou d’un arbitrage produit ;
- la validation finale dépend de retests terrain manuels.

### Timeline / séquençage

- Phase 1 : création de l’epic correctif + injection backlog ;
- Phase 2 : exécution story par story via Epic Runner ;
- Phase 3 : retests HITL + mise à jour `revision/` ;
- Phase 4 : seulement ensuite, `Epic 10.7` puis `10.8`.

## 4. Detailed Change Proposals

### 4.1 `epics.md`

Ajouter un **Epic 28** après Epic 27, avec :

- périmètre explicitement borné au registre `references/revision/` ;
- ordre de stories imposé ;
- interdiction de paralléliser les stories de dev ;
- obligation de mapper chaque story à des IDs `REV-*`.

**Annexe normative :** le tableau de couverture `REV-*` (couverts / différés / hors epic) vit dans **`epics.md` §Epic 28** — source de vérité pour le mapping REV→story.

### 4.2 `sprint-status.yaml`

Ajouter :

- `epic-28: backlog`
- stories `28-1` à `28-5` en `backlog`
- `epic-28-retrospective: optional`

Mettre à jour :

- `last_updated` racine ;
- journal commenté en tête pour tracer l’ajout de l’épic.

### 4.3 Orchestration

Créer un plan `.cursor/plans/` dédié au long run `Epic 28`, avec :

- une vague A de préparation / sync ;
- une vague B d’exécution story par story ;
- une vague C de gate beta via Epic 10 ;
- un `00_SYNC_STATUS.md` associé.

### 4.4 Registre `references/revision/`

Pas de modification structurelle requise immédiatement.

Règle proposée :

- l’agent coche `Investigé` puis `Corrigé` quand une story livre effectivement un fix ;
- Strophe garde la main sur `Validé HITL`.

## 5. Implementation Handoff

### Scope classification

**Moderate**

Il faut réorganiser le backlog d’exécution sans refaire PRD ni architecture de fond.

### Handoff recipients

- **Scrum / pilotage BMAD** : injecter l’epic et le séquencement ;
- **Epic Runner** : exécuter Epic 28 story par story ;
- **Story Runner** : create -> validate -> dev -> gates -> QA -> CR ;
- **Strophe** : retest HITL et fermeture réelle du registre.

### Success criteria

- Epic 28 existe dans `epics.md` et `sprint-status.yaml`.
- Le plan de long run est prêt à être lancé.
- Les stories 28.x correspondent à des groupes cohérents de `REV-*` (mapping normatif : annexe **`epics.md` §Epic 28**).
- La séquence `Epic 28 -> retests HITL -> Epic 10.7 -> Epic 10.8` est explicitement documentée.
- **Gate mesurable Epic 10 :** `0` P0 ouvert dans `references/revision/index.md` au moment de lancer `10.7`, ou exceptions explicitement listées et acceptées par Strophe avant `10.7`.

## 6. Decision

Le changement est **approuvé** comme réorganisation du backlog et de l’orchestration.

La prochaine action recommandée est :

1. injecter `Epic 28` dans `epics.md` ;
2. injecter ses statuts dans `sprint-status.yaml` ;
3. créer le plan de long run ;
4. lancer ensuite `@bmad-epic-runner` sur `epic-28`.

### État post-approbation (2026-06-07)

| Livrable | Statut |
|----------|--------|
| `epics.md` §Epic 28 (stories 28.1–28.5, mapping `REV-*`) | **Réalisé** |
| `sprint-status.yaml` bloc `epic-28` | **Réalisé** |
| Plan `.cursor/plans/revision-beta-terrain-epic-28.plan.md` | **Réalisé** |
| `epic-28-stabilisation-beta-terrain/00_SYNC_STATUS.md` | **Réalisé** (initialisé) |

**Prochaine action :** exécuter la **Vague A** du plan (si pas encore `A_PREP = done`), puis lancer **`@bmad-epic-runner epic-28`** pour la Vague B (série 28.1→28.5). Annexe normative mapping REV→story : **`epics.md` §Epic 28**.
