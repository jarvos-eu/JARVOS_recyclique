# État et schémas — BMAD Autopilot

Ce document décrit les fichiers d'état utilisés par l'orchestrateur et les subagents BMAD Autopilot. Référence pour les agents et pour la reprise après escalade ou échec.

**Emplacement** : `_bmad-output/implementation-artifacts/` (même répertoire que `sprint-status.yaml` et les fichiers story `{story_key}.md`).

---

## 1. `.run-epic-state.json`

**Créé et mis à jour par** : l'orchestrateur uniquement.

**Rôle** : Éviter deux runs simultanés sur le même epic ; permettre la reprise après crash ou pause.

**Schéma** :

```json
{
  "epicId": "epic-1",
  "currentStoryKey": "1-1-initialiser-le-frontend-vite-react-ts-et-la-structure-des-dossiers-par-domaine",
  "startedAt": "2026-02-26T12:00:00Z",
  "status": "running",
  "lastFailure": {
    "phase": "dev",
    "storyKey": "1-2-...",
    "at": "2026-02-26T12:30:00Z"
  },
  "lastSteps": [
    { "step": "create-story", "storyKey": "1-1-...", "phase": "create-story", "completedAt": "..." }
  ]
}
```

**Champs** :

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `epicId` | string | oui | Identifiant de l'epic (ex. epic-1). |
| `currentStoryKey` | string | oui | Clé de la story en cours (ex. 1-1-initialiser-le-...). |
| `startedAt` | string (ISO 8601) | oui | Date/heure de début du run. |
| `status` | "running" \| "paused" | oui | running = boucle en cours ; paused = arrêt ou fin. |
| `lastFailure` | object | non | Présent si un subagent a échoué après retry : phase, storyKey, at. |
| `lastSteps` | array | non | Traçabilité optionnelle : step, storyKey, phase, completedAt. |
| `lastStoryCompleted` | string | non | En mode run-story, story_key qui vient d'être terminée (pour résumé). |

**Comportement** : Au démarrage de `/run-epic`, l'orchestrateur lit ce fichier. Si `status: "running"`, il propose reprise ou arrêt. À chaque changement de story, il met à jour `currentStoryKey` et garde `status: "running"`. En fin d'epic ou sur échec, il met `status: "paused"` et optionnellement `lastFailure`. En mode `/run-story` (une story), en fin de boucle il met aussi `status: "paused"` et peut renseigner `lastStoryCompleted` (story_key terminée) pour traçabilité.

---

## 2. `{story_key}.agent-state.json`

**Créé et mis à jour par** : les subagents (bmad-sm, bmad-dev, bmad-revisor, bmad-qa) en cas d'escalade ; l'orchestrateur met à jour `questions[].answer` après réponse humaine.

**Rôle** : État de reprise et requête Human-in-the-Loop (HITL). Une question en attente = une entrée dans `questions[]` avec `answer: null`. L'orchestrateur traite **une question à la fois** (la première sans answer), valide la réponse, met à jour l'état, re-spawne le subagent.

**Schéma** :

```json
{
  "storyKey": "1-1-initialiser-le-frontend-vite-react-ts-et-la-structure-des-dossiers-par-domaine",
  "phase": "dev",
  "lastCompletedStep": "step-3-implement-api",
  "blockedAt": "step-4-integrate-frontend",
  "blockReason": "no_resource",
  "questions": [
    {
      "id": "q1",
      "question": "Quel endpoint utiliser pour le health check ?",
      "context": "Architecture mentionne /health ou /ready, pas de détail dans le code existant.",
      "answer": null
    }
  ],
  "artifactsProduced": ["frontend/src/App.tsx", "frontend/vite.config.ts"]
}
```

**Champs** :

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `storyKey` | string | oui | Clé de la story (identique au nom du fichier story sans .md). |
| `phase` | string | oui | create-story \| validate \| dev \| revision \| code-review. |
| `lastCompletedStep` | string | non | Dernière étape terminée (pour reprendre après). |
| `blockedAt` | string | en escalade | Étape où le blocage a eu lieu. |
| `blockReason` | string | en escalade | no_resource \| manual_test_required \| human_review_required \| critical_decision \| subagent_failed. |
| `questions` | array | oui | Liste de { id, question, context, answer }. answer = null = requête en attente. |
| `artifactsProduced` | array | non | Fichiers déjà créés/modifiés (éviter de refaire). |

**Comportement** : Si le subagent **termine sans escalader**, il doit **réécrire** le fichier avec `questions: []` ou **supprimer** le fichier, pour que l'orchestrateur ne relise pas une ancienne escalade. Après chaque Task, l'orchestrateur lit ce fichier pour la story courante ; s'il existe et qu'au moins une question a `answer: null`, il met la cascade en pause et affiche la première question.

---

## 3. `{story_key}.review.json`

**Créé par** : le subagent bmad-qa (Code Review) uniquement, **après** exécution du workflow BMAD code-review.

**Rôle** : Contrat machine-readable pour la décision orchestrateur : approved → story suivante ; changes-requested → reboucler Dev → Revision → Code Review.

**Schéma** :

```json
{
  "reviewResult": "approved",
  "summary": "Implémentation conforme à la story. Tests et structure OK."
}
```

**Champs** :

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `reviewResult` | "approved" \| "changes-requested" | oui | Résultat de la review. |
| `summary` | string | oui | Résumé court (pour affichage et pour instruction de correction si changes-requested). |

**Comportement** : L'orchestrateur lit ce fichier après chaque Code Review. Si changes-requested, il relance Task(bmad-dev) avec instruction de corriger (en s'appuyant sur summary), puis Revision puis Code Review. Si approved, il passe à la story suivante ou fin d'epic.

---

## 4. Convention des story_key

Les clés de story sont celles du fichier `sprint-status.yaml`, section `development_status`. Format typique : `{epicNum}-{storyNum}-{slug}` (ex. `1-1-initialiser-le-frontend-vite-react-ts-et-la-structure-des-dossiers-par-domaine`). Les noms de fichiers sont : `{story_key}.md`, `{story_key}.agent-state.json`, `{story_key}.review.json`.

---

## 5. Références

- Vision et décisions HITL/ReviewResult : `references/artefacts/2026-02-26_04_analyse-vision-automatisation-dev-bmad-cursor.md` (§5).
- Plan d'implémentation : voir le plan BMAD Autopilot dans Cursor (`.cursor/plans/` ou lien du plan).
- Orchestrateur : `.cursor/agents/bmad-orchestrator.md`.
- Commandes : `.cursor/commands/run-epic.md`, `.cursor/commands/run-story.md`.
