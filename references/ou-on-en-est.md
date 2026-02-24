# Ou on en est — JARVOS Recyclique

Mis a jour : 2026-02-24 | Session : plan Git (procedure, subagent, regle)

## Etat actuel

Projet JARVOS Recyclique v0.1.0 initialise. Structure de travail et **workflow Git en place** (repo connecte a GitHub, procedure, subagent @git-specialist, regle Cursor).
Aucun code source encore. Aucune analyse brownfield lancee. Aucune recherche formalisee.

BMAD 6.0.3 installe. Cursor rules actives. Dossier `references/` operationnel.

## Derniere session

2026-02-24 — Plan Git termine (tests, procedure, subagent, regle).

Realise :
- Repo local connecte a `https://github.com/jarvos-eu/JARVOS_recyclique.git` ; tests valides (status, add, commit, push, branches, revert).
- `references/procedure-git-cursor.md` redige a partir du rapport ; revision (init/remote, liens vers regle et subagent).
- Subagent **@git-specialist** cree : `.cursor/agents/git-specialist.md` (workflow Conventional Commits, reference procedure).
- Regle **git-workflow.mdc** : `.cursor/rules/git-workflow.mdc` (delegation a @git-specialist ou commandes a l'utilisateur).
- Index `references/index.md` et artefacts a jour ; briefs 03–05 revises (numerotation, creation directe du subagent).

## Plan Git — termine

Les artefacts 01 a 05 ont ete executes. En place :
- Rapport : `references/artefacts/2026-02-24_02_rapport-tests-git-cursor.md`
- Procedure : `references/procedure-git-cursor.md`
- Subagent : `.cursor/agents/git-specialist.md` (invoquer via @git-specialist)
- Regle : `.cursor/rules/git-workflow.mdc`

Pour les operations Git au quotidien : deleguer a @git-specialist ou suivre la procedure.

---

## Prochaine etape

1. Renseigner l'URL du repo GitHub public Recyclique 1.4.4 dans `references/ancien-repo/README.md`.
2. Lancer le git clone quand pret pour l'analyse brownfield.
3. Commencer les recherches (marche, domaine, technique) via les agents BMAD.
4. Creer le Brief produit JARVOS Recyclique v0.1.0 (`/bmad-bmm-create-product-brief`).
