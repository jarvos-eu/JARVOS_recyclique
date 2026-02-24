# Rapport — Tests Git / Cursor (environnement local)

**Date** : 2026-02-24  
**Contexte** : Mission exécutée selon `2026-02-24_01_mission-agent-test-git-cursor.md`.  
**Environnement** : Windows, Cursor, agent en session.

---

## Phase 1 — Connexion du repo

| Étape | Commande / action | Résultat |
|--------|-------------------|----------|
| 1 | `git status` | Dépôt non initialisé (fatal: not a git repository). |
| 2 | `git init` | OK — dépôt initialisé. |
| 3 | `git remote add origin https://github.com/jarvos-eu/JARVOS_recyclique.git` | OK — URL fournie par Strophe. |
| 4 | `git remote -v` | OK — origin (fetch/push) configuré. |

**Livrable** : Repo local initialisé et connecté à GitHub. Premier push effectué en Phase 2 (test 4).

---

## Phase 2 — Résultats par test

| # | Action | Résultat | Détail |
|---|--------|----------|--------|
| 1 | Lecture seule | **OK** | `git status`, `git branch` OK. `git log -1` échoue tant qu’il n’y a pas de commit (comportement normal). |
| 2 | Stage | **OK** | `git add .gitignore` — OK. Warning LF/CRLF (normal sous Windows). Aucun timeout ni lock file. |
| 3 | Commit local | **OK** | `git commit -m "test: agent git"` — commit 854e261 créé. |
| 4 | Push | **OK** | `git push -u origin master` — réussi. Branche `master` poussée vers `origin`. Credentials disponibles dans l’environnement (Credential Manager ou équivalent). ~25 s. |
| 5 | Branche | **OK** | `git checkout -b test-agent-git` puis `git checkout master`. Création et bascule de branches OK. |
| 6 | Revert / annulation | **OK** | Sur branche `test-agent-git` : commit de test puis `git revert HEAD --no-edit`. Revert OK. Branche de test supprimée (`git branch -D test-agent-git`) pour ne pas polluer. |

Aucune commande en boucle ; aucun échec auth/timeout. Aucune commande à proposer à l’utilisateur pour exécution manuelle.

---

## Phase 3 — Synthèse

### Ce qui marche

- **Lecture** : `git status`, `git branch`, `git log` (après premier commit).
- **Stage** : `git add` (fichier ou `.`) sans timeout ni lock.
- **Commit** : `git commit -m "..."` depuis l’agent.
- **Push** : `git push -u origin master` — credentials pris en compte (HTTPS + Credential Manager ou token).
- **Branches** : `git checkout -b`, `git checkout <branch>`, `git branch -D`.
- **Revert** : `git revert HEAD --no-edit` exécutable par l’agent.

### Ce qui ne marche pas / à noter

- **Rien en échec** dans cette session. Sans remote configuré, `git push` échoue avec « 'origin' does not appear to be a git repository » (résolu après `git remote add origin <URL>`).
- **PowerShell** : utiliser `;` pour enchaîner les commandes, pas `&&`.

### Credentials

- **Ce qui a fonctionné** : push HTTPS vers GitHub réussi depuis le terminal Cursor. Les credentials sont fournis par l’environnement (Windows Credential Manager, token Git, ou configuration Cursor). L’agent n’a pas eu à saisir de mot de passe.
- **Recommandation** : pour une autre machine ou un subagent sans accès aux credentials, fournir les commandes exactes à exécuter par Strophe dans son terminal (comme prévu dans la mission).

### Recommandations workflow

| Qui | Quoi |
|-----|------|
| **Agent** | Init, remote add, status, add, commit, branches, revert, merge (côté local). Proposer `git push` ou le lancer si l’environnement a déjà les credentials. |
| **Strophe** | Fournir l’URL du repo au premier lien ; exécuter manuellement `git push` (ou `git pull`) si l’agent n’a pas accès aux credentials. |
| **Procédure** | Valider en conditions réelles : CLI Git depuis l’agent fonctionne ; MCP Git non nécessaire pour le quotidien. Documenter la procédure dans l’artefact prévu (`2026-02-24_03_mission-rediger-procedure-git.md`). |

---

## Contraintes respectées

- Aucun secret committé.
- Tests reversibles : branche dédiée `test-agent-git`, puis suppression après revert.
- Pas de retry en boucle sur les commandes.
