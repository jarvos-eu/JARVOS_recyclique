# Mission : Creer la regle Git workflow et finaliser l'index (Artefact E)

**Destinataire** : N'importe quel agent (Analyst, PM, Dev, ou session generique). Cette creation ne passera plus par l'agent qui a cree les premiers artefacts.  
**Prealable** : Le subagent Git (Artefact D) doit etre cree via /create-subagent. Le fichier `references/procedure-git-cursor.md` doit exister.  
**Objectif** : Creer `.cursor/rules/git-workflow.mdc` et mettre a jour `references/index.md`.

---

## Livrable 1 : .cursor/rules/git-workflow.mdc

Creer le fichier avec le format Cursor rules (frontmatter YAML + contenu).

**Contenu a ecrire :**

```markdown
---
description: Workflow Git pour JARVOS_recyclique - delegation au subagent ou commandes a l'utilisateur
alwaysApply: true
---

# Workflow Git - JARVOS_recyclique

Pour toute operation Git (commit, push, PR) dans ce projet :

1. **Si le subagent Git est configure** : deleguer a @git-specialist (ou le nom du subagent cree). Lui demander d'appliquer le workflow decrit dans references/procedure-git-cursor.md.

2. **Sinon** : proposer a l'utilisateur les commandes exactes a executer dans son terminal (staging, commit avec message Conventional Commits, push). Ne pas executer git push soi-meme si les credentials ne sont pas accessibles. S'appuyer sur references/procedure-git-cursor.md pour le format des messages et l'ordre des commandes.

Ne jamais faire de push (ni force push) sans validation explicite de l'utilisateur, sauf si la procedure-git-cursor.md prevoit une exception documentee.
```

Verifier que le fichier existe bien dans `.cursor/rules/` et que le frontmatter est valide (description, alwaysApply: true).

---

## Livrable 2 : Mise a jour de references/index.md

Ajouter une ligne dans la section **Conventions et regles** (apres l'entree `procedure-git-cursor.md`), ou dans une courte section dediee si tu preferes :

- **Subagent Git** : invocable via @git-specialist (ou le nom reel). Procedure et comportement : voir `procedure-git-cursor.md`. Fichier agent : `.cursor/agents/` (nom a confirmer selon Cursor).

Exemple d'entree au meme format que les autres :

```markdown
- **Subagent @git-specialist** - Expert Git du projet. Workflow et limites : voir `procedure-git-cursor.md`. Fichier : `.cursor/agents/` (selon version Cursor).
  _(Charger si : delegation d'operations Git a l'agent specialise.)_
```

Ne pas supprimer ni modifier les autres entrees.

---

## Verification

- Le fichier `.cursor/rules/git-workflow.mdc` est lisible et contient bien alwaysApply: true.
- L'index references/index.md contient une entree pour la procedure (deja ajoutee a l'etape 5) et une pour le subagent Git (ajout ici).

Apres cette mission, le plan Git (artefacts A a E) est termine. Les agents BMAD (Dev, etc.) pourront s'appuyer sur la regle et sur @git-specialist.
