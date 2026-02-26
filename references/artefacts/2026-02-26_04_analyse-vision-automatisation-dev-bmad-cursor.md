# Analyse critique — Vision automatisation développement BMAD + Cursor 2.5

**Date :** 2026-02-26  
**Révision :** 2026-02-26 (vision consolidée, Validate Story, découpage complexité, parallélisation, HITL, Revision, analyse critique et décisions complémentaires).  
**Contexte :** Vision « BMAD Autopilot » (commande slash unique → cascade subagents → SM → Validate → DEV → **Revision** → CR, hooks, découpage stories complexes, dev parallèle).  
**Objectif :** Analyse critique, faisabilité, améliorations et risques. Référence pour la branche `experiment/bmad-autopilot`.

---

## 1. Synthèse exécutive

La vision est **globalement correcte et réalisable** avec les briques Cursor 2.5 (subagents asynchrones, hooks, plugins) et le format BMAD existant (`sprint-status.yaml`, workflows create-story / validate / dev-story / code-review). Plusieurs points méritent **clarification technique** et **ajustements de conception** pour éviter des impasses. Une approche **incrémentale** (run-story puis run-epic, checkpoints humains au début) est recommandée. La **vision consolidée** (§2) intègre une commande slash unique, la validation systématique des stories, une **relecture (Revision)** par un autre agent après implémentation, le découpage des stories complexes en sous-stories, le développement en parallèle lorsque les dépendances le permettent, et un **Human-in-the-Loop (HITL)** par escalade : état persistant par story, validation des réponses humaines par l'orchestrateur, reprise via nouveau subagent.

---

## 2. Vision consolidée (cible)

Ce que l'on vise, en une seule entrée utilisateur :

- **Une commande slash** (ex. `/run-epic epic-03` ou `/run-story`) déclenche toute la chaîne. Pas une succession de commandes manuelles.
- **Cascade d'agents intelligents, chacun en subagent** pour ne pas polluer le contexte principal :
  1. **Create Story** (subagent SM) : produit le fichier story à partir de `epics.md` et `sprint-status.yaml`.
  2. **Validate Story** (subagent SM ou dédié) : vérifie que la story est bien créée selon les recommandations BMAD (checklist create-story), corrige ou complète si besoin.
  3. **Dev Story** (subagent DEV) : implémentation à partir du fichier story.
  4. **Revision** (subagent Revisor ou second DEV) : relecture de la sortie du DEV — exécute uniquement le workflow `.cursor/commands/revision.md` (relire livrable, sources et doc, vérifier complétude/cohérence/erreurs, corriger). **Pas** le même agent que celui qui a implémenté (éviter l'auto-relecture) ; pas le protocole QA complet.
  5. **Code Review** (subagent DEV ou QA) : review adversarial BMAD, mise à jour du statut et de `sprint-status.yaml`.
- Le résultat **remonte** après chaque subagent ; l'orchestrateur décide de l'étape suivante (story suivante, reboucler sur la même story si changes-requested, ou fin d'epic).
- **Hooks** (quand disponibles) pour enchaînement, audit ou injection de contexte (`subagentStop`, `sessionStart`, etc.).
- **Stories peu complexes** : au moment de la **création**, si la story prévue est trop grosse (nombre d'AC, composants, dépendances), le SM la **découpe en plusieurs sous-stories** et met à jour `epics.md` / `sprint-status.yaml` en conséquence. BMAD prévoit déjà « stories sized for single dev agent completion » (create-epics-and-stories, step-03) ; on formalise cette règle dans le prompt du SM Create Story.
- **Parallélisation** : lorsque plusieurs stories peuvent être développées sans dépendance entre elles (et idéalement sans chevauchement de zones de code), l'orchestrateur **spawne plusieurs subagents DEV en parallèle**, puis attend leurs résultats. Pour chaque story la séquence reste **DEV → Revision → Code Review** : après le batch des N DEV, l'orchestrateur lance les N Revisions (en parallèle ou en séquentiel selon choix), puis les N Code Review de la même façon, avant de passer au batch suivant ou à la story suivante.
- **Revision après implémentation** : après Dev Story, une **relecture** (workflow `/revision`) est faite par un **subagent différent** (Revisor ou second DEV), pas par l'agent qui a écrit le code — pour éviter le biais d'auto-relecture (le même agent qui révise son propre code trouve toujours des « erreurs » à corriger). Le revisor exécute uniquement `.cursor/commands/revision.md` ; il ne fait pas le Code Review adversarial (qui reste l'étape suivante). Optionnel : utiliser un modèle différent pour le revisor (ex. plus rapide) pour renforcer l'asymétrie d'information.
- **Human-in-the-Loop (HITL)** : en cas de question critique (aucune ressource dans le code/docs), test manuel requis ou review humaine, le subagent **escalade** en écrivant son état et ses questions dans un fichier d'état dédié, puis termine. L'orchestrateur affiche la demande à l'humain, **valide** la réponse avant de l'enregistrer, puis **spawne un nouveau** subagent (même type) avec l'état mis à jour pour qu'il reprenne au bon endroit. Pas d'aller-retour direct avec le subagent : tout passe par l'orchestrateur et l'état persistant.

Réutilisation des **workflows BMAD existants** : on ne réinvente pas create-story, validate (checklist create-story), dev-story ni code-review ; les subagents **exécutent** ces workflows en chargeant les instructions depuis `_bmad/` (même contenu que les commandes `/bmad-bmm-create-story`, etc.).

---

## 3. Ce qui est bien posé

- **sprint-status.yaml** : format lisible par machine (epic-X, story-X-Y, statuts backlog / ready-for-dev / in-progress / review / done). Déjà produit par `bmad-bmm-sprint-planning` et consommé par code-review pour mise à jour. Idéal comme source de vérité pour l'orchestrateur.
- **Subagents asynchrones** : confirmé Cursor 2.5 (forum + changelog). Un agent parent peut lancer des tâches en arrière-plan et enchaîner ; arborescence SM → DEV → QA cohérente avec la doc.
- **Hooks** : `subagentStart` / `subagentStop`, `afterFileEdit`, `beforeShellExecution`, `sessionStart`, etc. existent bien (Cursor Docs). Utiles pour audit, injection de contexte, et éventuellement chaînage.
- **Plugins** : packaging skills + subagents + MCP + hooks + rules dans un seul plugin, distribuable, aligné avec la roadmap « Dev Loop Automation » BMAD.
- **Limite Cloud vs local** : en local IDE (ton cas), tous les hooks sont disponibles ; pas de dépendance aux Cloud Agents pour la boucle autonome.

---

## 4. Points à clarifier ou corriger

### 4.1 Boucle « stop » vs « subagentStop »

La vision dit : *« Le hook `stop` lit le statut dans le fichier story et notifie l'orchestrateur »*.

- En pratique, **quand un subagent (Task tool) se termine, le parent reprend la main** avec le résultat du subagent (output). Le parent n'a pas besoin d'être « notifié » par un hook pour savoir que le subagent est fini.
- Le hook **`stop`** s'applique à la **fin de l'agent courant** (session ou tour), pas à « quand un subagent fils termine ». Pour la fin d'un **subagent**, le bon événement est **`subagentStop`**.
- **Recommandation :** utiliser **`subagentStop`** pour des side-effects (log, mise à jour d'un fichier d'état, métriques). La **décision** « story suivante ou reboucler » reste dans le **prompt de l'orchestrateur** : à chaque reprise après un subagent, il lit `sprint-status.yaml` + le fichier story (et éventuellement ReviewResult) et décide (approved → next story ; changes-requested → relancer DEV).

### 4.2 Statut « approved » / « changes-requested » dans la story

BMAD aujourd'hui ne produit pas de champ machine-readable pour le résultat de la review : `Status` passe à `done` ou `in-progress`, mais l'orchestrateur ne peut pas distinguer « approuvé proprement » de « corrections demandées » sans parser le rapport.

**Décision** : voir §5.1 — fichier `{story_key}.review.json` produit par le workflow code-review. Le fichier story BMAD n'est pas modifié.

### 4.3 Ordre des étapes : Validate Story dans la boucle

La vision consolidée inclut **Validate Story** entre Create Story et Dev Story. BMAD fournit la checklist de validation (`create-story/checklist.md`).

**Décision** : Le subagent Validate Story charge **`create-story/checklist.md`** et l'applique à la story créée (relit la story, vérifie contre epics/architecture, corrige ou complète). Pas de workflow validate séparé obligatoire pour le MVP — la checklist seule suffit. Vérifier dans `_bmad/bmm/workflows/4-implementation/` ou via les commandes BMAD (ex. bmad-bmm-create-story en mode Validate) si un workflow validate-story existe ; le subagent peut l'utiliser si oui, sinon appliquer uniquement la checklist.

### 4.4 Où vit `sprint-status.yaml` ?

**Décision** : Le workflow BMAD utilise `{implementation_artifacts}/sprint-status.yaml`, soit `_bmad-output/implementation-artifacts/sprint-status.yaml`. Fichier **confirmé présent** (produit par Sprint Planning). L'orchestrateur lit et met à jour ce chemin. Les fichiers story, `{story_key}.review.json` et `{story_key}.agent-state.json` vivent dans le même répertoire.

### 4.5 Commands vs skills vs agents BMAD

La vision met des « skills » (run-epic, create-story, dev-story, code-review) dans `.cursor/skills/`. Dans Cursor :

- Les **slash commands** sont plutôt définis dans `.cursor/commands/` (fichiers .md invocables).
- Les **skills** (`.cursor/skills/`) sont des fichiers lus par l'agent pour savoir *quand* et *comment* faire une action (ex. idees-kanban, traiter-depot).

Pour **invoker** un workflow BMAD (`bmad-bmm-create-story`, etc.), il faut soit :

- une **commande** qui appelle explicitement le workflow (ex. lecture du task help.md ou du workflow),  
- soit un **agent** (SM, DEV, QA) dont le prompt dit « quand on te demande Create Story, exécute le workflow _bmad/... create-story ».

Donc : **run-epic** = slash command (`.cursor/commands/`) qui lance l'orchestrateur ; **create-story / dev-story / code-review** = workflows BMAD exécutés par les subagents en chargeant les instructions depuis `_bmad/`. Les commandes existantes (`/bmad-bmm-create-story`, etc.) restent utilisables en manuel ; les subagents réutilisent le **même contenu** (workflow.yaml, instructions, template).

### 4.6 Hooks et environnement Windows

**Décision** : Pour JARVOS_recyclique (Windows), utiliser des **scripts PowerShell** (`.ps1`) pour les hooks au niveau projet (`.cursor/hooks/`). Éviter le bash seul ; documenter le chemin des scripts (ex. `.cursor/hooks/script.ps1`) depuis `.cursor/hooks.json`. Si un hook doit appeler un binaire ou un script externe, privilégier l'appel PowerShell natif.

---

## 5. Améliorations proposées

### 5.1 Contrat de statut machine-readable (story + code-review)

**Décision** : Fichier dédié **`{story_key}.review.json`** dans `implementation-artifacts`. **Qui l'écrit** : le subagent Code Review, via une **instruction dans son prompt** (après avoir exécuté le workflow BMAD code-review, écrire ce fichier avec `reviewResult` et `summary`). On ne modifie pas le workflow dans `_bmad/` ; l'agent CR applique le workflow puis écrit le JSON. L'orchestrateur lit ce fichier pour décider « next » vs « reboucler ».

### 5.2 Fichier d'état « run-epic » (lock + progression)

Pour éviter deux runs simultanés sur le même epic et pour reprendre après crash :

- Un fichier `_bmad-output/implementation-artifacts/.run-epic-state.json` (ou équivalent) avec par exemple :  
  `{ "epicId": "epic-03", "currentStoryKey": "3-2-...", "startedAt": "...", "status": "running" }`.
- L'orchestrateur le met à jour à chaque changement de story ; au démarrage de `/run-epic`, il vérifie qu'aucun `status: running` n'existe (ou demande reprise explicite).
- **Observabilité (optionnel)** : ajouter dans ce fichier un tableau `lastSteps: [{ step, storyKey, phase, completedAt }]` pour traçabilité minimale (qui a fait quoi, quand).

### 5.3 Checkpoints humains configurables

- Au lieu de « laisser tourner » d'emblée, prévoir des **gates** : après chaque story, après chaque epic, ou après N stories.
- Exemple : variable dans un config (ou dans le prompt de l'orchestrateur) : `human_checkpoint: after_each_story | after_each_epic | none`. À chaque gate, l'orchestrateur s'arrête et affiche un résumé + « Continuer ? (oui / non / corriger manuellement) ».

### 5.4 Un seul agent « BMAD Runner » en MVP

Pour un premier prototype, un **seul agent** « BMAD Runner » peut suffire : il lit `sprint-status.yaml`, appelle en séquence (via subagents) Create Story → Validate Story → Dev Story → **Revision** → Code Review, et boucle. Les personas SM/DEV/QA deviennent utiles quand tu veux **séparer les modèles** (ex. SM rapide, DEV plus capable, QA autre modèle) ou les prompts très différents ; pour valider la boucle, un seul agent simplifie le débogage.

### 5.5 Rétrospective en fin d'epic

La vision prévoit « Fin d'epic → subagent SM → bmad-bmm-retrospective ». Le déclencheur est « dernière story de l'epic passée en `done` ». L'orchestrateur peut détecter ça en lisant `sprint-status.yaml` (toutes les stories de l'epic en `done`) puis lancer le subagent SM avec le workflow retrospective.

### 5.6 Découpage des stories complexes (cible vision)

Au moment de la **création** de la story, le SM doit veiller à ce qu'elle soit **la moins complexe possible**. Si la story prévue est trop grosse (nombre d'AC, composants touchés, dépendances), **ne pas produire une seule story** : produire **plusieurs sous-stories**, mettre à jour `epics.md` et `sprint-status.yaml` en conséquence. BMAD prévoit déjà « stories sized for single dev agent completion » et « Size stories appropriately » (`_bmad/bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-03-create-stories.md`). À formaliser dans le **prompt du subagent Create Story** (ou dans un skill) : **heuristique** « une story = un flux utilisateur ou un composant cohérent ; si plus de 5 AC ou plus de 3 composants distincts, envisager de découper en sous-stories ». Les seuils (5, 3) sont indicatifs ; à affiner en projet. Règle « si complexe → découper en sous-stories et créer N fichiers story, mettre à jour epics + sprint-status ».

### 5.7 Parallélisation du développement (cible vision)

Lorsque plusieurs stories peuvent être développées **sans dépendance** entre elles (et idéalement en touchant des **zones de code disjointes** pour limiter les conflits Git), l'orchestrateur peut **spawner plusieurs subagents DEV en parallèle**, un par story. **Graphe de dépendances** : par défaut déduire de l'**ordre des stories** dans l'epic (story N dépend des stories 1..N-1 déjà `done`). Champ optionnel `dependsOn` dans epics ou dans la story peut être ajouté plus tard pour des cas explicites. Pour chaque story la séquence reste **DEV → Revision → Code Review**. Après le batch des N DEV, l'orchestrateur enchaîne les N Revisions (en parallèle ou en séquentiel), puis les N Code Review, avant de passer au batch suivant. À chaque « batch », l'orchestrateur identifie les stories dont les dépendances sont satisfaites, lance N subagents DEV en parallèle, attend la fin de tous, puis lance les Revisions puis les CR. Risque : conflits Git ; atténuation en ne parallélisant que des stories sur chemins/modules disjoints, ou en acceptant merge manuel.

### 5.8 Human-in-the-Loop (HITL) — Décisions

**Pourquoi** : questions critiques sans ressource dans le code/docs, tests manuels requis, reviews humaines. On ne peut pas faire d'aller-retour conversationnel avec un subagent (il termine et rend la main). Donc l'humain ne parle qu'à l'orchestrateur ; le subagent **escalade** en écrivant son état, puis un **nouveau** subagent (même type) reprend en lisant cet état.

**Décision — Où écrire l'état** : **Fichier dédié par story** `{story_key}.agent-state.json` dans `_bmad-output/implementation-artifacts/` (même répertoire que le fichier story). On ne met pas l'état dans le fichier story pour garder le Markdown lisible et le parsing simple. Le fichier story reste le livrable métier ; l'état d'escalade/reprise est à part.

**Décision — Contenu du fichier d'état** : Un seul fichier contient à la fois l'état de reprise et la requête humaine en cours. Schéma minimal :

```json
{
  "storyKey": "3-1-xxx",
  "phase": "dev",
  "lastCompletedStep": "step-3-implement-api",
  "blockedAt": "step-4-integrate-frontend",
  "blockReason": "no_resource",
  "questions": [
    { "id": "q1", "question": "...", "context": "...", "answer": null }
  ],
  "artifactsProduced": ["path/to/file1", "path/to/file2"]
}
```

- **phase** : create-story | validate | dev | **revision** | code-review  
- **lastCompletedStep** : identifiant de la dernière étape terminée (pour reprendre après).  
- **blockedAt** : étape où le blocage a eu lieu.  
- **blockReason** : no_resource | manual_test_required | human_review_required | critical_decision  
- **questions** : tableau ; la requête en attente = la question dont **answer** est **null**. Quand l'humain a répondu, l'orchestrateur écrit la réponse dans **answer** ; le prochain subagent lit le fichier et continue. **Plusieurs questions** : traiter **une requête à la fois** (la première question avec `answer: null`) ; après réponse, l'orchestrateur met à jour l'état et re-spawne ; si une autre question reste sans answer, la prochaine reprise la montrera.  
- **artifactsProduced** (optionnel) : fichiers déjà créés/modifiés pour éviter de refaire.

Pas de fichier `.human-input-request.json` séparé : la requête en attente est la question avec `answer: null` dans ce même fichier.

**Décision — Validation de la réponse humaine** : **Règles fixes uniquement** (pas de LLM pour juger). L'orchestrateur vérifie : (1) réponse non vide et non triviale (« ok » seul si la question demandait du détail) ; (2) si la question proposait des **options**, la réponse est l'une d'elles ou une reformulation claire. Si **invalide** : renvoyer à l'humain sans modifier l'état ni relancer le subagent. Si **valide** : mettre à jour `questions[i].answer`, puis spawner un **nouveau** subagent avec instruction de reprise.

**Contrat de reprise** : Lors du re-spawn, l'orchestrateur passe au subagent : (1) chemin du fichier story ; (2) chemin du fichier `{story_key}.agent-state.json` ; (3) instruction explicite : « Reprends à l'étape {blockedAt}. Les réponses humaines sont dans le fichier d'état (questions[].answer). Ne refais pas les étapes déjà dans lastCompletedStep / artifactsProduced. » Le nouveau subagent charge l'état et la story, voit où il s'est arrêté et les réponses, et continue.

**Checkpoints planifiés** : En plus de l'escalade ad hoc, l'orchestrateur peut imposer des **gates** (ex. après Create Story, après Code Review) : il s'arrête, affiche le livrable, et n'enchaîne qu'après « Continuer » ou « Modifier puis continuer ». C'est du HITL planifié, pas une question posée par le subagent.

**Décision — Détection « awaiting human input »** : Après **chaque** fin de subagent, l'orchestrateur lit le fichier `{story_key}.agent-state.json` (story en cours). Si le fichier existe et qu'au moins une entrée de `questions[]` a **answer: null**, considérer que le subagent a escaladé : **pause** la cascade, afficher **une seule** requête à l'humain (la première question sans answer). Après réponse et validation, mettre à jour l'état, re-spawner le subagent ; s'il reste d'autres questions sans answer, elles seront traitées au prochain cycle (une à la fois).

**Décision — Comportement quand il n'y a pas d'escalade** : Pour éviter qu'un ancien fichier d'état (avec des questions déjà répondues) soit relu et interprété à tort comme une nouvelle escalade, le subagent qui **termine avec succès sans escalader** doit soit **réécrire** le fichier `{story_key}.agent-state.json` avec `questions: []` (ou sans question en attente), soit **supprimer** le fichier. Ainsi l'orchestrateur, en relisant le fichier après chaque subagent, voit soit une requête en attente (au moins une question avec answer: null), soit aucun fichier / plus de question en attente, et enchaîne normalement.

### 5.9 Revision après Dev Story (relecture par autre agent)

**Constat** : La commande `.cursor/commands/revision.md` demande de relire la sortie récente, les sources et la doc, de vérifier omissions/incohérences/erreurs et de corriger. Si c'est le **même** agent DEV qui vient d'implémenter et qui exécute `/revision`, il fait une **auto-relecture** — il trouve alors souvent des « erreurs » à corriger (biais, ou sur-correction). BMAD recommande déjà un autre LLM pour la code review (asymétrie d'information).

**Décision** : Insérer une étape **Revision** **après** Dev Story et **avant** Code Review. Elle est effectuée par un **subagent différent** (Revisor, ou second DEV en contexte vierge) qui **n'a pas** écrit le code. Ce subagent reçoit : chemin du fichier story, liste des fichiers modifiés (File List de la story ou sortie git), et l'instruction d'exécuter le workflow de `.cursor/commands/revision.md` (relire livrable, sources et doc, vérifier complétude/cohérence/erreurs, corriger, produire le résumé). Il ne fait **pas** le protocole QA complet ni la review adversarial — celle-ci reste l'étape Code Review (workflow BMAD). La Revision ne met pas à jour `sprint-status.yaml` ; seul le Code Review le fait. Optionnel : utiliser un modèle différent pour le revisor (ex. plus rapide) pour renforcer l'asymétrie.

**Flux** : Create Story → Validate Story → Dev Story (DEV_impl) → **Revision** (Revisor / DEV_revisor) → Code Review (adversarial).

---

## 6. Faisabilité

| Composant | Faisabilité | Note |
|-----------|-------------|------|
| Orchestrateur lit sprint-status, choisit la prochaine story | **Élevée** | YAML simple, chemins connus. |
| Subagent SM → create-story (workflow BMAD) | **Élevée** | Déjà invocable en manuel ; le subagent doit charger le workflow et les inputs (epic, story_key). |
| Subagent DEV → dev-story avec fichier story en contexte | **Élevée** | Workflow existant ; passer le chemin du fichier story en entrée. |
| Revision (relecture par autre subagent, workflow revision.md) | **Élevée** | Un second subagent (Revisor) avec instruction de charger `.cursor/commands/revision.md` et de l'appliquer aux fichiers produits par DEV_impl ; pas de modification sprint-status. |
| Subagent QA / Code Review → code-review | **Élevée** | Idem, workflow existant. |
| Mise à jour sprint-status.yaml par code-review | **Déjà fait** | Workflow BMAD le fait. |
| Décision approved / changes-requested par orchestrateur | **Moyenne** | Facile si champ machine-readable (voir 5.1) ; sinon parsing fragile. |
| Validate Story dans la boucle (subagent dédié) | **Élevée** | Checklist et workflow BMAD existants ; le subagent charge les mêmes instructions. |
| Découpage story complexe → sous-stories | **Moyenne** | Règle à formaliser dans le prompt SM ; mise à jour epics + sprint-status à prévoir. |
| Parallélisation DEV (plusieurs stories sans dépendance) | **Moyenne** | Subagents async OK ; graphe de dépendances et règles de conflit à définir. |
| HITL : état reprise + escalade + validation réponse | **Moyenne** | Fichier état par story, orchestrateur valide réponse puis re-spawn ; à formaliser dans les prompts subagent et orchestrateur. |
| Hooks subagentStop / afterFileEdit pour chaînage | **Moyenne** | Hooks fonctionnent ; le « chaînage » peut être fait par le parent qui relit l'état après chaque subagent, sans hook. Les hooks servent surtout à audit / injection. |
| Boucle entière sans intervention (run-epic → fin d'epic) | **Moyenne** | Faisable une fois les points ci-dessus réglés ; risque de dérives (mauvaise story, review trop laxiste). Recommandation : checkpoints humains au début. |
| Plugin Cursor packagé (BMAD Autopilot) | **Moyenne** | Une fois la boucle stable en local, le packaging plugin est un travail d'intégration (skills + agents + hooks + règles) et de doc pour le Marketplace. |

En résumé : **faisable dès maintenant** pour une boucle « une story » ou « un epic avec checkpoints ». Une boucle totalement autonome sur plusieurs épics est faisable après avoir introduit le contrat de statut (5.1) et un peu d'état (5.2).

---

## 7. Risques et atténuations

- **Stories mal créées** : le SM génère une story incomplète ou hors scope. → **Validate Story** dans la boucle (subagent dédié) pour corriger avant Dev ; checkpoint humain après Create Story possible au début.
- **Review trop laxiste** : le code-review passe en `done` sans vrais correctifs. → **Revision** par un autre agent avant Code Review (relecture fraîche) ; utiliser un second LLM pour la review (déjà recommandé dans BMAD) ; ou checkpoint humain après chaque story au début.
- **Contexte perdu entre subagents** : chaque subagent repart avec un contexte limité. → Bien documenter dans le prompt de l'orchestrateur qu'il doit passer les chemins de fichiers (story, sprint-status, epics.md) et éventuellement un résumé en une phrase au subagent.
- **Hooks qui bloquent ou plantent** : un hook en exit 2 bloque l'action ; un hook qui timeout peut laisser l'IDE dans un état flou. → Garder les hooks simples (log, écriture fichier), éviter la logique critique dans les hooks au début.
- **sprint-status.yaml modifié par ailleurs** : si tu édites le fichier à la main pendant un run, l'orchestrateur peut se « perdre ». → Fichier d'état dédié (5.2) ou lecture seule du sprint-status sauf par les workflows BMAD.
- **Parallélisation : conflits Git** : deux DEV modifient les mêmes fichiers. → Ne paralléliser que des stories sur zones disjointes ; ou accepter merge manuel et revue avant commit.
- **HITL : subagent n'écrit pas l'état** : le subagent termine sans écrire le fichier d'état ou avec un état incomplet. → Inclure dans le prompt du subagent l'obligation d'écrire `{story_key}.agent-state.json` **avant** de terminer en cas de blocage ; l'orchestrateur vérifie la présence du fichier et la cohérence (question avec answer null) avant d'afficher à l'humain.
- **Subagent en échec (crash, timeout, output incohérent)** : **Retry une fois** (relancer le même subagent avec les mêmes entrées). Si échec à nouveau, **escalade humaine** : l'orchestrateur s'arrête, affiche « Subagent X (phase Y) a échoué ; reprise manuelle ou abandon de la story ? » et écrit le statut pour reprise ultérieure : dans **`.run-epic-state.json`** ajouter par ex. `"lastFailure": { "phase": "dev", "storyKey": "...", "at": "..." }` et passer `status` à `"paused"` ; optionnellement écrire dans `{story_key}.agent-state.json` un bloc indiquant l'échec (ex. `blockReason: "subagent_failed"`) pour que la reprise manuelle ou le prochain run sache où reprendre.

---

## 8. Plan d'action suggéré (ordre)

1. **Vérifier** que `_bmad-output/implementation-artifacts/sprint-status.yaml` existe et contient bien les clés `development_status` avec les story keys (comme dans le template).
2. **Créer la commande slash** (ex. `/run-epic` ou `/run-story`) dans `.cursor/commands/` : elle charge le task de l'orchestrateur (lecture sprint-status, boucle Create → Validate → Dev → **Revision** → CR).
3. **Créer l'agent orchestrateur** (ou BMAD Runner) dans `.cursor/agents/` : prompt qui décrit la cascade (subagent Create Story, subagent Validate Story, subagent Dev Story, **subagent Revision**, subagent Code Review), lecture de sprint-status, choix de la prochaine story, réutilisation des workflows BMAD (`_bmad/bmm/workflows/4-implementation/...`) et de la commande revision (`.cursor/commands/revision.md`).
4. **Boucle minimale** : une seule story — Create Story (subagent) → Validate Story (subagent) → Dev Story (subagent) → **Revision** (subagent Revisor ou second DEV, **pas** le même que DEV_impl) → Code Review (subagent). Sans hooks au début. Valider que les fichiers story et sprint-status sont bien mis à jour.
5. **Introduire** le fichier `{story_key}.review.json` (ReviewResult) : instruction dans le prompt du subagent Code Review pour écrire ce fichier après la review ; faire lire ce fichier par l'orchestrateur pour décider « next » vs « reboucler ».
6. **HITL** : définir le schéma `{story_key}.agent-state.json` et l'obligation pour chaque subagent d'écrire cet état avant de terminer en cas d'escalade ; orchestrateur : détection requête (question avec answer null), affichage à l'humain, **validation** de la réponse, mise à jour de l'état, re-spawn du subagent avec instruction de reprise.
7. **Étendre** à « run-epic » : boucle sur toutes les stories d'un epic avec checkpoint humain après chaque story (ou après chaque N stories).
8. **Règle découpage** : dans le prompt du SM Create Story (ou skill), ajouter la règle « si story trop complexe → découper en sous-stories, mettre à jour epics + sprint-status ».
9. **Optionnel** : parallélisation — graphe de dépendances, spawn de plusieurs DEV en parallèle pour stories sans dépendance.
10. **Optionnel** : hooks `subagentStop` pour log / métriques ; `sessionStart` pour injecter project-context dans chaque subagent.
11. **Optionnel** : rétrospective en fin d'epic ; puis packaging plugin.

---

## 9. Conclusion

**Décisions tranchées (référence rapide)**  
- **ReviewResult** : fichier `{story_key}.review.json` écrit par le subagent Code Review (instruction dans son prompt après le workflow BMAD) ; pas de modification du workflow dans _bmad/.  
- **État HITL / reprise** : fichier `{story_key}.agent-state.json` (état + questions/réponses) ; pas de second fichier requête.  
- **Validation réponse humaine** : règles fixes uniquement (non vide, option valide si applicable) ; pas de LLM. Une question à la fois.  
- **Reprise** : nouveau subagent avec chemin story + chemin état + instruction « Reprends à … ».  
- **Validate Story** : subagent charge create-story/checklist.md et l'applique ; pas de workflow validate séparé obligatoire pour le MVP.
- **Graphe dépendances** (parallélisation) : par défaut ordre des stories dans l'epic ; dependsOn optionnel plus tard.
- **Échec subagent** : retry une fois puis escalade humaine ; écrire `lastFailure` et `status: paused` dans `.run-epic-state.json`, optionnellement `blockReason: subagent_failed` dans agent-state.
- **Observabilité** : optionnel, lastSteps[] dans .run-epic-state.json.
- **Détection escalade** : après chaque subagent, orchestrateur lit agent-state.json ; si question avec answer null, pause et afficher une requête (la première sans answer). **Sans escalade** : le subagent qui réussit réécrit le fichier avec `questions: []` ou supprime le fichier.
- **Phase** (état HITL) : inclure **revision** (create-story | validate | dev | revision | code-review).
- **Revision** : après Dev Story, **autre** subagent (Revisor ou second DEV) exécute `.cursor/commands/revision.md` sur la sortie du DEV_impl ; pas d'auto-relecture. Puis Code Review adversarial.    
- **Hooks Windows** : scripts PowerShell (`.ps1`) au niveau projet.  
- **Commande slash** : `.cursor/commands/` ; workflows BMAD chargés par les subagents depuis `_bmad/`.

La vision **consolidée** (commande slash unique, cascade Create → Validate → Dev → **Revision** → CR en subagents, découpage des stories complexes, parallélisation quand possible, **HITL par escalade** : état persistant par story, validation des réponses par l'orchestrateur, reprise via nouveau subagent) est **réalisable et bien alignée** avec Cursor 2.5 et BMAD. La **Revision** par un autre agent (revision.md) évite l'auto-relecture du DEV ; le Code Review adversarial reste l'étape suivante. Décisions retenues : **subagentStop** pour les hooks de fin de subagent ; **fichiers dédiés** pour ReviewResult et état d'escalade ; **PowerShell** pour les hooks en projet Windows ; **orchestrateur** comme seul interlocuteur humain, avec validation de la réponse avant re-spawn. **Branche d'expérimentation :** `experiment/bmad-autopilot`.

---

## 10. Zones d'ombre et prérequis (Phase 0)

À clarifier **avant** ou **au début** de la fabrication :

- **Invocation des subagents** : mécanisme exact pour qu'un agent parent lance un subagent avec un prompt et des entrées (story path, instruction). Dans ce projet, vérifier les **tools Cursor disponibles** (ex. **mcp_task** avec subagent_type generalPurpose, explore, shell, etc.) et le format d'invocation (prompt, paramètres) ; à lire dans la doc Cursor ou en inspectant les tools du projet.
- **Lien commande slash → orchestrateur** : quel fichier dans `.cursor/commands/` pour `/run-epic` ou `/run-story`, et comment la commande déclenche l'agent orchestrateur (nom du fichier, format, référence à un agent). Doc Cursor sur les commands.
- **Prompts des personas** : contenu minimal des fichiers `.cursor/agents/` pour SM, DEV, Revisor, QA (référence aux workflows BMAD, chemins, obligation d'écrire agent-state en cas d'escalade, et de réécrire/supprimer le fichier quand pas d'escalade). À rédiger en Phase 1.

Prérequis à vérifier en Phase 0 : `sprint-status.yaml` présent dans `_bmad-output/implementation-artifacts/` avec `development_status` ; chemins `implementation_artifacts` et `planning_artifacts` accessibles ; présence de `epics.md` et des workflows dans `_bmad/bmm/workflows/4-implementation/`.
