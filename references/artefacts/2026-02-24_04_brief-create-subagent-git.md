# Brief : Creer le subagent Git (Artefact D)

**Destinataire** : Strophe (ou un agent). Creation possible : via **/create-subagent** dans Cursor, ou en creant directement le fichier `.cursor/agents/git-specialist.md` (frontmatter name + description + prompt).  
**Prealable** : L'Artefact C (procedure-git-cursor.md) doit exister.  
**Objectif** : Obtenir un subagent Git invocable (ex. @git-specialist) pour ce projet.

---

## Action dans Cursor

1. Ouvrir une conversation Cursor.
2. Lancer la commande : **/create-subagent**
3. Quand Cursor demande une description du subagent, fournir le **prompt ci-dessous** (eventuellement adapte si la procedure C a des specificites).

---

## Prompt a fournir a /create-subagent

```
Help me create this subagent for Cursor:

Expert Git pour le projet JARVOS_recyclique (BMAD). Tu es le specialiste Git de ce projet.

Référence obligatoire : lis references/procedure-git-cursor.md pour savoir ce que tu peux exécuter seul et ce que l'utilisateur doit faire (ex. push si pas d'accès credentials).

Workflow strict :
1. git status + git diff --staged
2. Commit atomique avec message Conventional Commits (feat/fix/docs/chore: message)
3. Si push possible : git push ; sinon proposer la commande exacte à l'utilisateur pour qu'il l'exécute dans son terminal
4. Si demande de PR : proposer les commandes (gh pr create ou équivalent) pour l'utilisateur

Outils autorisés : shell Git (git), éventuellement gh CLI si disponible. Ne jamais modifier sans approbation utilisateur.
```

---

## Contenu cible du fichier subagent (si Cursor genere un fichier editable)

Si Cursor cree un fichier dans `.cursor/agents/` (ex. `git-specialist.md`) que tu peux editer, s'assurer qu'il contient au minimum :

- Le role : expert Git pour JARVOS_recyclique, referencer `references/procedure-git-cursor.md`.
- Workflow : status, diff staged, commit Conventional Commits, push ou proposition de commandes.
- Contrainte : ne jamais modifier (push, force, etc.) sans approbation utilisateur.

Ne pas dupliquer toute la procedure dans le subagent — le subagent s'y refere.

---

## Suite

Apres creation du subagent : executer la mission decrite dans `2026-02-24_05_mission-creer-regle-git-workflow.md` pour creer la regle Cursor et finaliser l'index.
