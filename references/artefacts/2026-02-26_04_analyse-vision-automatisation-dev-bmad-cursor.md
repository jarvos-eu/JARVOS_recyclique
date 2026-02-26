# Analyse critique — Vision automatisation développement BMAD + Cursor 2.5

**Date :** 2026-02-26  
**Contexte :** Vision « BMAD Autopilot » (run-epic → orchestrateur → SM → DEV → QA en boucle, hooks, plugins).  
**Objectif :** Analyse critique, faisabilité, améliorations et risques.

---

## 1. Synthèse exécutive

La vision est **globalement correcte et réalisable** avec les briques Cursor 2.5 (subagents asynchrones, hooks, plugins) et le format BMAD existant (`sprint-status.yaml`, workflows create-story / dev-story / code-review). Plusieurs points méritent **clarification technique** et **ajustements de conception** pour éviter des impasses. Une approche **incrémentale** (run-story puis run-epic, checkpoints humains obligatoires au début) est recommandée.

---

## 2. Ce qui est bien posé

- **sprint-status.yaml** : format lisible par machine (epic-X, story-X-Y, statuts backlog / ready-for-dev / in-progress / review / done). Déjà produit par `bmad-bmm-sprint-planning` et consommé par code-review pour mise à jour. Idéal comme source de vérité pour l’orchestrateur.
- **Subagents asynchrones** : confirmé Cursor 2.5 (forum + changelog). Un agent parent peut lancer des tâches en arrière-plan et enchaîner ; arborescence SM → DEV → QA cohérente avec la doc.
- **Hooks** : `subagentStart` / `subagentStop`, `afterFileEdit`, `beforeShellExecution`, `sessionStart`, etc. existent bien (Cursor Docs). Utiles pour audit, injection de contexte, et éventuellement chaînage.
- **Plugins** : packaging skills + subagents + MCP + hooks + rules dans un seul plugin, distribuable, aligné avec la roadmap « Dev Loop Automation » BMAD.
- **Limite Cloud vs local** : en local IDE (ton cas), tous les hooks sont disponibles ; pas de dépendance aux Cloud Agents pour la boucle autonome.

---

## 3. Points à clarifier ou corriger

### 3.1 Boucle « stop → orchestrateur »

La vision dit : *« Le hook `stop` lit le statut dans le fichier story et notifie l’orchestrateur »*.

- En pratique, **quand un subagent (Task tool) se termine, le parent reprend la main** avec le résultat du subagent (output). Le parent n’a pas besoin d’être « notifié » par un hook pour savoir que le subagent est fini.
- Le hook **`stop`** s’applique à la **fin de l’agent courant** (session ou tour), pas à « quand un subagent fils termine ». Pour la fin d’un **subagent**, le bon événement est **`subagentStop`**.
- **Recommandation :** utiliser **`subagentStop`** pour des side-effects (log, mise à jour d’un fichier d’état, métriques). La **décision** « story suivante ou reboucler » reste dans le **prompt de l’orchestrateur** : à chaque reprise après un subagent, il lit `sprint-status.yaml` + le fichier story et décide (approved → next story ; changes-requested → relancer DEV).

### 3.2 Statut « approved » / « changes-requested » dans la story

BMAD aujourd’hui :

- **Template story** : `Status: ready-for-dev` (puis in-progress, review, done).
- **Code-review** : met à jour le fichier story et `sprint-status.yaml` avec `done` ou `in-progress` (pas de champ explicite « approved » / « changes-requested »).

Pour une boucle 100 % machine, il faut un **champ dédié** interprétable par l’orchestrateur, par exemple :

- Dans le fichier story (frontmatter ou ligne fixe) : `ReviewResult: approved | changes-requested`.
- Le workflow **code-review** devrait **écrire** ce champ (ou un fichier `.review-result` à côté de la story) en plus de mettre à jour `Status` et `sprint-status.yaml`.

Sans ça, l’orchestrateur doit **inférer** depuis le texte du rapport de review ou les changements de statut — faisable mais fragile (parsing de prose).

### 3.3 Ordre des étapes (Validate Story avant Dev)

La vision enchaîne Create Story → Dev Story → Code Review. BMAD recommande **Validate Story** (optionnel) entre Create Story et Dev Story. Pour l’automatisation :

- **Option A :** inclure Validate Story dans la boucle (SM subagent : create-story puis validate-story) pour réduire les stories mal formées.
- **Option B :** ne pas l’automatiser au début et n’enchaîner que Create → Dev → CR ; ajouter Validate plus tard si le taux d’échec CR est élevé.

Recommandation : **Option B** pour le MVP de la boucle, puis ajouter Validate si besoin.

### 3.4 Où vit `sprint-status.yaml` ?

Le workflow BMAD pointe vers `{implementation_artifacts}/sprint-status.yaml`, soit `_bmad-output/implementation-artifacts/sprint-status.yaml`. Dans ton projet, ou-on-en-est indique que le fichier a été généré là. **À confirmer** que le Sprint Planning a bien écrit ce fichier (pas seulement en mémoire) et que l’orchestrateur le lit depuis ce chemin.

### 3.5 Skills vs slash commands BMAD

La vision met des « skills » (run-epic, create-story, dev-story, code-review) dans `.cursor/skills/`. Dans Cursor :

- Les **slash commands** sont plutôt définis dans `.cursor/commands/` (fichiers .md invocables).
- Les **skills** (`.cursor/skills/`) sont des fichiers lus par l’agent pour savoir *quand* et *comment* faire une action (ex. idees-kanban, traiter-depot).

Pour **invoker** un workflow BMAD (`bmad-bmm-create-story`, etc.), il faut soit :

- une **commande** qui appelle explicitement le workflow (ex. lecture du task help.md ou du workflow),  
- soit un **agent** (SM, DEV, QA) dont le prompt dit « quand on te demande Create Story, exécute le workflow _bmad/... create-story ».

Donc : **run-epic** = slash command (ou entrée de l’orchestrateur) ; **create-story / dev-story / code-review** = comportement des agents SM/DEV/QA ou commandes qui chargent les workflows. Mieux vaut ne pas tout appeler « skill » pour éviter la confusion avec les skills Cursor existants.

### 3.6 Hooks et environnement Windows

La vision montre des scripts shell (`check-story-status.sh`, `inject-bmad-context.sh`). Sous **Windows**, les hooks Cursor peuvent appeler des scripts ; il faut prévoir :

- soit des **scripts PowerShell** (`.ps1`) ou batch (`.cmd`) pour rester natif,
- soit un interpréteur (Git Bash, WSL) si tu gardes du bash.

Les exemples officiels sont en bash ; pour JARVOS_recyclique (Windows), prévoir une couche `.ps1` ou documenter l’usage de Git Bash pour les hooks.

---

## 4. Améliorations proposées

### 4.1 Contrat de statut machine-readable (story + code-review)

- Ajouter dans le **template story** (ou en frontmatter) un champ du type :  
  `ReviewResult: (empty | approved | changes-requested)`.
- Dans le **workflow code-review** : après la review, écrire ce champ (et éventuellement un résumé en une ligne) dans le fichier story ou dans un fichier dédié `{story_key}.review.json`.
- L’orchestrateur (ou un hook `subagentStop` en lecture seule) lit ce fichier pour décider sans parser le markdown.

### 4.2 Fichier d’état « run-epic » (lock + progression)

Pour éviter deux runs simultanés sur le même epic et pour reprendre après crash :

- Un fichier `_bmad-output/implementation-artifacts/.run-epic-state.json` (ou équivalent) avec par exemple :  
  `{ "epicId": "epic-03", "currentStoryKey": "3-2-...", "startedAt": "...", "status": "running" }`.
- L’orchestrateur le met à jour à chaque changement de story ; au démarrage de `/run-epic`, il vérifie qu’aucun `status: running` n’existe (ou demande reprise explicite).

### 4.3 Checkpoints humains configurables

- Au lieu de « laisser tourner » d’emblée, prévoir des **gates** : après chaque story, après chaque epic, ou après N stories.
- Exemple : variable dans un config (ou dans le prompt de l’orchestrateur) : `human_checkpoint: after_each_story | after_each_epic | none`. À chaque gate, l’orchestrateur s’arrête et affiche un résumé + « Continuer ? (oui / non / corriger manuellement) ».

### 4.4 Un seul agent « BMAD Runner » au lieu de quatre personas

Pour un premier prototype, un **seul agent** « BMAD Runner » peut suffire : il lit `sprint-status.yaml`, appelle en séquence (via sous-tâches ou en invoquant les workflows BMAD par lecture des instructions) Create Story → Dev Story → Code Review, et boucle. Les personas SM/DEV/QA deviennent utiles quand tu veux **séparer les modèles** (ex. SM rapide, DEV plus capable, QA autre modèle) ou les prompts très différents ; pour valider la boucle, un seul agent simplifie le débogage.

### 4.5 Rétrospective en fin d’epic

La vision prévoit bien « Fin d’epic → subagent SM → bmad-bmm-retrospective ». À préciser : le déclencheur est « dernière story de l’epic passée en `done` ». L’orchestrateur peut détecter ça en lisant `sprint-status.yaml` (toutes les stories de l’epic en `done`) puis lancer le subagent SM avec la commande/workflow retrospective.

---

## 5. Faisabilité

| Composant | Faisabilité | Note |
|-----------|-------------|------|
| Orchestrateur lit sprint-status, choisit la prochaine story | **Élevée** | YAML simple, chemins connus. |
| Subagent SM → create-story (workflow BMAD) | **Élevée** | Déjà invocable en manuel ; le subagent doit charger le workflow et les inputs (epic, story_key). |
| Subagent DEV → dev-story avec fichier story en contexte | **Élevée** | Workflow existant ; passer le chemin du fichier story en entrée. |
| Subagent QA / Code Review → code-review | **Élevée** | Idem, workflow existant. |
| Mise à jour sprint-status.yaml par code-review | **Déjà fait** | Workflow BMAD le fait. |
| Décision approved / changes-requested par orchestrateur | **Moyenne** | Facile si champ machine-readable (voir 4.1) ; sinon parsing fragile. |
| Hooks subagentStop / afterFileEdit pour chaînage | **Moyenne** | Hooks fonctionnent ; le « chaînage » peut être fait par le parent qui relit l’état après chaque subagent, sans hook. Les hooks servent surtout à audit / injection. |
| Boucle entière sans intervention (run-epic → fin d’epic) | **Moyenne** | Faisable une fois les points ci-dessus réglés ; risque de dérives (mauvaise story, review trop laxiste). Recommandation : checkpoints humains au début. |
| Plugin Cursor packagé (BMAD Autopilot) | **Moyenne** | Une fois la boucle stable en local, le packaging plugin est un travail d’intégration (skills + agents + hooks + règles) et de doc pour le Marketplace. |

En résumé : **faisable dès maintenant** pour une boucle « une story » ou « un epic avec checkpoints ». Une boucle totalement autonome sur plusieurs épics est faisable après avoir introduit le contrat de statut (4.1) et un peu d’état (4.2).

---

## 6. Risques et atténuations

- **Stories mal créées** : le SM génère une story incomplète ou hors scope. → Valider avec Validate Story (optionnel) ou checkpoint humain après Create Story au début.
- **Review trop laxiste** : le code-review passe en `done` sans vrais correctifs. → Utiliser un second LLM pour la review (déjà recommandé dans BMAD) ; ou checkpoint humain après chaque story au début.
- **Contexte perdu entre subagents** : chaque subagent repart avec un contexte limité. → Bien documenter dans le prompt de l’orchestrateur qu’il doit passer les chemins de fichiers (story, sprint-status, epics.md) et éventuellement un résumé en une phrase au subagent.
- **Hooks qui bloquent ou plantent** : un hook en exit 2 bloque l’action ; un hook qui timeout peut laisser l’IDE dans un état flou. → Garder les hooks simples (log, écriture fichier), éviter la logique critique dans les hooks au début.
- **sprint-status.yaml modifié par ailleurs** : si tu édites le fichier à la main pendant un run, l’orchestrateur peut se « perdre ». → Fichier d’état dédié (4.2) ou lecture seule du sprint-status sauf par les workflows BMAD.

---

## 7. Plan d’action suggéré (ordre)

1. **Vérifier** que `_bmad-output/implementation-artifacts/sprint-status.yaml` existe et contient bien les clés `development_status` avec les story keys (comme dans le template).
2. **Créer l’agent orchestrateur** (ou BMAD Runner) dans `.cursor/agents/` : prompt qui décrit la boucle, lecture de sprint-status, choix de la prochaine story, invocation des workflows (en les décrivant ou en pointant vers les task files BMAD).
3. **Boucle minimale** : une seule story — orchestrateur → Create Story (subagent SM) → Dev Story (subagent DEV) → Code Review (subagent DEV ou QA). Sans hooks au début. Valider que les fichiers story et sprint-status sont bien mis à jour.
4. **Introduire** le champ ReviewResult (ou fichier .review.json) dans le workflow code-review et dans le template story ; faire lire ce champ par l’orchestrateur pour décider « next » vs « reboucler ».
5. **Étendre** à « run-epic » : boucle sur toutes les stories d’un epic avec checkpoint humain après chaque story (ou après chaque N stories).
6. **Optionnel** : hooks `subagentStop` pour log / métriques ; `sessionStart` pour injecter project-context dans chaque subagent.
7. **Optionnel** : rétrospective en fin d’epic ; puis packaging plugin.

---

## 8. Conclusion

La vision est **réalisable et bien alignée** avec Cursor 2.5 et BMAD. Les principaux correctifs sont : utiliser **subagentStop** plutôt que **stop** pour réagir à la fin d’un subagent ; ajouter un **contrat machine-readable** pour le résultat de la review ; et clarifier **skills vs commands vs agents**. En partant d’une **boucle une story** avec checkpoints humains, puis en généralisant à run-epic avec gates configurables, tu limites les risques tout en validant rapidement la chaîne. Le packaging en plugin Cursor peut venir une fois cette boucle stable.
