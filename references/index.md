# Index — JARVOS Recyclique v0.1.0

Refonte complete de Recyclique 1.4.4. Nouveau backend. Solo dev : Strophe. BMAD 6.0.3.

> **Agents — point d'entree unique.** Ne charge pas `references/` en entier.
> Lis cet index : il contient un abstract de chaque ressource.
> Charge uniquement ce que ta session necessite — les indications "(Charger si : …)" sont la pour ca.

---

## Etat et suivi

- **`ou-on-en-est.md`** — Etat actuel du projet, resume de la derniere session, prochaine etape logique.
  _(Charger si : tu arrives sans contexte, session de planification, ou debut d'une nouvelle conversation importante.)_

- **`todo.md`** — To-do de reflexion, recherche et agregations hors flux BMAD (hors epics/stories).
  _(Charger si : session d'ideation, de recherche ou de synthese conceptuelle.)_

- **`idees/`** — Kanban d'idees (un fichier par idee, stades a-conceptualiser, a-rechercher, a-creuser, a-faire, archive). Vue globale : **idees/index.md**. Gestion : skill **idees-kanban** (`.cursor/skills/idees-kanban/`).
  _(Charger si : Strophe donne une idee a noter, ajout de note / transition / archivage, ou session d'ideation / priorisation.)_

---

## Conventions et regles

- **`INSTRUCTIONS-PROJET.md`** — Conventions completes : nommage des fichiers, structure des sous-dossiers, regles de maintenance de l'index, format de `ou-on-en-est.md` et `todo.md`.
  _(Charger uniquement si : tu dois creer ou modifier un fichier dans `references/`.)_

- **`procedure-git-cursor.md`** — Procedure Git dans Cursor : ce que l'agent peut faire, ce que l'utilisateur fait, credentials, workflow et depannage.
  _(Charger si : operations Git, configuration, ou delegation au subagent Git.)_

- **`versioning.md`** — Convention de versions et tags (v0.1.0 → v1.0.0). Ancien repo 1.4.4.
  _(Charger si : release, tag Git, planification de version.)_

- **Subagent @git-specialist** — Expert Git du projet. Workflow et limites : voir `procedure-git-cursor.md`. Fichier : `.cursor/agents/git-specialist.md`.
  _(Charger si : delegation d'operations Git a l'agent specialise.)_

---

## Sous-dossiers

Chaque dossier liste son contenu dans son propre **index** : `references/<dossier>/index.md`. Le detail ne figure pas ici.

- **`artefacts/`** — Artefacts temporaires de handoff entre agents. Detail : **artefacts/index.md**.
  _(Charger : si un artefact est mentionne dans `ou-on-en-est.md` ou selon le besoin de la session.)_

- **`idees/`** — Kanban d'idees. Vue globale : **idees/index.md**. Gestion : skill idees-kanban.
  _(Charger : idee a capturer, note / transition / archivage, ou session d'ideation.)_

- **`recherche/`** — Prompts et reponses de recherche externe (Perplexity, Claude.ai, GPT, etc.). Detail : **recherche/index.md**.
  _(Charger : fichiers mentionnes dans ou-on-en-est ou sur demande explicite.)_

- **`ecosysteme/`** — References JARVOS_ecosysteme et JARVOS_fondations. Confidentiel. Gitignore. Detail : **ecosysteme/index.md**.
  _(Charger : sur demande explicite uniquement.)_

- **`ancien-repo/`** — Instructions git clone + guide analyse brownfield Recyclique 1.4.4. `repo/` gitignore.
  _(Charger : si la session porte sur l'historique, l'analyse brownfield ou l'import de decisions.)_

- **`vrac/`** — Fichiers non classes. Sensible. Gitignore. Pas d'index.
  _(Charger : sur demande explicite uniquement.)_
