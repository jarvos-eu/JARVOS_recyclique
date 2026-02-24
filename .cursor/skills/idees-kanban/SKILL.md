---
name: idees-kanban
description: Manages the ideas Kanban for JARVOS Recyclique. Creates idea files, adds dated notes, moves ideas between stages (a-conceptualiser, a-rechercher, a-creuser, a-faire, archive), and maintains references/idees/index.md. Use when the user says they have an idea to capture (e.g. "note une idee", "j'ai une idee", "note ça"), asks to add a note or transition or archive an idea, or during ideation or prioritization sessions.
---

# Kanban Idées — JARVOS Recyclique

Un fichier par idée. Le fichier **grandit** (sections datées), on ne réécrit pas. Le **dossier** = stade actuel. Toujours mettre à jour `references/idees/index.md` après chaque opération.

**Racine** : `references/idees/`. **Stades** : `a-conceptualiser/`, `a-rechercher/`, `a-creuser/`, `a-faire/`, `archive/`. **Nom fichier** : `YYYY-MM-DD_titre-court.md` (titre en minuscules, tirets).

---

## 0. Première utilisation (repo cloné, dossier ignoré)

Si `references/idees/` ou un sous-dossier manque (ex. clone d’un repo où `references/idees/` est dans .gitignore) : **créer toute l’arborescence** avant toute opération (créer idée, ajouter note, transitionner, archiver). Créer les dossiers `references/idees/`, `references/idees/a-conceptualiser/`, `a-rechercher/`, `a-creuser/`, `a-faire/`, `archive/`. Si `references/idees/index.md` n’existe pas, le créer avec le titre, la phrase de mise à jour par le skill, et la table avec la ligne placeholder `| _(aucune idée pour l'instant)_ | | | | |`.

---

## 1. Créer une idée

Quand Strophe dit une idée à noter (« j'ai une idée », « note ça », « note une idée », etc.) :

0. Si `references/idees/` ou `references/idees/index.md` n’existe pas, exécuter d’abord l’étape 0 ci-dessus.
1. Utiliser la **date du jour** (date système) pour `YYYY-MM-DD` dans le nom du fichier et dans la première section datée.
2. Choisir le stade initial (par défaut `a-conceptualiser` sauf indication : a-rechercher, a-creuser, a-faire).
3. Créer `references/idees/<stade>/YYYY-MM-DD_titre-court.md` en utilisant le template dans `.cursor/skills/idees-kanban/TEMPLATE.md`. Remplacer le titre (H1) et la section datée par l'idée brute + intention. Titre court = minuscules, tirets (ex. `export-pdf-bilans`).
4. Mettre à jour `references/idees/index.md` : si la table ne contient que la ligne placeholder `_(aucune idée pour l'instant)_`, remplacer cette ligne par la nouvelle (Fichier | Titre | Stade | Créé | Dernière MAJ) ; sinon ajouter une nouvelle ligne.

---

## 2. Ajouter une note

Sans changer de stade : ajouter dans le fichier idée une section `## YYYY-MM-DD — [qui]` avec le contenu, puis mettre à jour la colonne « Dernière MAJ » de ce fichier dans `references/idees/index.md`.

---

## 3. Transitionner (changer de stade)

1. Ajouter dans le fichier une section datée indiquant le passage au nouveau stade (ex. « Passage à a-faire »).
2. **Déplacer** le fichier vers le dossier du nouveau stade (commande native move/rename). Ne pas lire+écrire.
3. Mettre à jour la ligne dans `references/idees/index.md` : colonne « Stade » et « Dernière MAJ ».

---

## 4. Archiver

Idée intégrée (story, todo, décision, code) : ajouter une section datée « Intégrée — [où] », **déplacer** le fichier dans `references/idees/archive/`, mettre à jour `references/idees/index.md` (Stade = archive, Dernière MAJ).

---

## Index idees (vue globale)

Fichier : `references/idees/index.md`. Table markdown avec en-têtes :

| Fichier | Titre | Stade | Créé | Dernière MAJ |
|---------|-------|-------|------|--------------|

Une ligne par idée (tous stades). Création : remplacer la ligne placeholder par la première idée, puis ajouter des lignes. Ensuite : mettre à jour la ligne concernée à chaque note, transition ou archivage.

---

## Règles

- **Renommer / déplacer** : toujours commande native (move), pas read+write.
- **Contenu fichier idée** : ne jamais supprimer les sections existantes ; uniquement ajouter des sections datées.
- **Stades valides** : a-conceptualiser, a-rechercher, a-creuser, a-faire, archive.
