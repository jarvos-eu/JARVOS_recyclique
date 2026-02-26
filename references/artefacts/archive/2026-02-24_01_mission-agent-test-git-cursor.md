# Mission : Agent test Git / Cursor - environnement local

**Destinataire** : Un agent Cursor en session **vide** (sans BMAD) qui executera les tests dans l'environnement local du projet JARVOS_recyclique.  
**Objectif** : Determiner ce qui marche / ne marche pas avec Git dans Cursor (credentials, tokens, push, revert, etc.) et documenter la meilleure maniere de fonctionner.

---

## Contexte

- **Projet** : JARVOS_recyclique (racine du workspace).
- **Repo GitHub** : Deja cree par Strophe. L'URL sera fournie en session - remplacer `[URL_À_REMPLACER]` dans les commandes ou demander a Strophe.
- **Environnement** : Windows, Cursor. Les agents n'ont pas toujours acces aux credentials (SSH, token).
- **Suite aux recherches** : MCP Git non recommande pour le quotidien ; CLI + execution manuelle ou subagent. On valide en conditions reelles ici.

---

## Phase 1 - Connexion du repo

1. Verifier si un depot Git est deja initialise (`git status` ou presence de `.git`).
2. Si non : `git init`.
3. Renseigner l'URL du repo GitHub (Strophe la fournit) : `git remote add origin [URL]`.
4. Verifier : `git remote -v`.
5. Optionnel : premier push minimal pour valider la connexion (sinon attendre la phase 2).

**Livrable** : Repo local initialise et connecte a GitHub. Court compte-rendu : commandes executees, succes/echec, message d'erreur eventuel.

---

## Phase 2 - Batterie de tests (reversibles)

Tous les tests doivent etre **reversibles** : branche dediee ou commits de test ensuite annules (revert / reset), pour ne pas polluer l'historique principal.

Pour **chaque test** : executer, noter le resultat dans le rapport `references/artefacts/2026-02-24_02_rapport-tests-git-cursor.md`, puis annuler les effets si besoin.

| # | Action | Commande(s) typiques | Ce qu'on verifie |
|---|--------|----------------------|------------------|
| 1 | Lecture seule | `git status`, `git log -1`, `git branch` | Acces au repo et a Git. |
| 2 | Stage | `git add .` ou fichier cible | Timeout ? lock file ? |
| 3 | Commit local | `git commit -m "test: agent git"` | Commit possible depuis l'agent. |
| 4 | Push | `git push -u origin main` (ou `master`) | **Credentials** : SSH ou token. Succes ou erreur (auth, timeout). |
| 5 | Branche | `git checkout -b test-agent-git` puis retour `main` | Gestion des branches. |
| 6 | Revert / annulation | `git revert HEAD` ou `git reset --hard HEAD~1` (sur branche test) | Annulation propre. |

**Si une commande echoue (auth, timeout)** : ne pas retenter en boucle. Produire les **commandes exactes** a copier-coller pour que Strophe les execute dans son terminal, et noter l'echec dans le rapport B.

---

## Phase 3 - Synthese dans l'Artefact B

Renseigner dans le fichier **rapport** : `references/artefacts/2026-02-24_02_rapport-tests-git-cursor.md`

- **Ce qui marche** : quelles commandes passent (lecture ? commit ? push ?).
- **Ce qui ne marche pas** : erreurs, timeouts, lock files.
- **Credentials** : ce qui a fonctionne (token HTTPS, SSH, Credential Manager, etc.) ou "agent n'a pas acces, commandes proposees a l'utilisateur".
- **Recommandations** : qui fait quoi (agent vs Strophe), workflow a retenir pour la procedure finale.

---

## Contraintes

- Ne pas committer de secrets (tokens, cles) dans le repo.
- Commandes destructrices (force push, reset hard) uniquement sur branche de test, et annuler apres.
- Pas de boucle de retry sur les commandes qui echouent - proposer les commandes a l'utilisateur.

---

## Suite prevue (passation a d'autres agents)

Une fois les tests valides et le rapport B complete, les etapes suivantes sont decrites dans des artefacts de ce dossier (a executer dans l'ordre) :

1. **Rediger la procedure** : suivre `references/artefacts/2026-02-24_03_mission-rediger-procedure-git.md`.
2. **Creer le subagent** : suivre `references/artefacts/2026-02-24_04_brief-create-subagent-git.md` (Strophe lance /create-subagent).
3. **Creer la regle et finaliser l'index** : suivre `references/artefacts/2026-02-24_05_mission-creer-regle-git-workflow.md`.
