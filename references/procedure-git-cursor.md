# Procedure Git Cursor — JARVOS_recyclique

Procedure etablie a partir des tests du 2026-02-24 (rapport `artefacts/2026-02-24_02_rapport-tests-git-cursor.md`). Environnement : Windows, Cursor.

---

## Ce que l'agent peut faire seul

En conditions reelles testees, l'agent peut executer en CLI :

- **Init / remote** : `git init`, `git remote add origin <URL>`, `git remote -v`
- **Lecture** : `git status`, `git branch`, `git log` (apres au moins un commit)
- **Stage** : `git add <fichier>` ou `git add .` — pas de timeout ni lock file observe
- **Commit** : `git commit -m "message"`
- **Push** : dans l'environnement ou les credentials sont deja configures (Credential Manager, token), `git push -u origin master` (ou la branche courante) a reussi depuis l'agent
- **Branches** : `git checkout -b <branche>`, `git checkout <branche>`, `git branch -D <branche>`
- **Annulation** : `git revert HEAD --no-edit`, merge local

Si le push echoue cote agent (auth, timeout), ne pas retenter en boucle : proposer les commandes exactes a Strophe (voir ci-dessous).

---

## Ce que Strophe fait a la main

- **Premier lien** : fournir l'URL du repo GitHub si le remote n'est pas encore configure (`git remote add origin <URL>`).
- **Credentials manquants** : si l'agent n'a pas acces (autre machine, subagent sans credentials), executer dans son terminal :
  - `git push -u origin master` (ou la branche concernee)
  - `git pull` si besoin
- **Validation** : verifier le depot distant apres un push important.

---

## Config credentials recommandee

- **Ce qui a fonctionne** : push HTTPS vers GitHub depuis le terminal Cursor, sans saisie de mot de passe. Les credentials sont fournis par l'environnement (Windows Credential Manager, token Git, ou configuration Cursor).
- **Si l'agent n'a pas acces** : donner a Strophe les commandes exactes a copier-coller dans son terminal (ex. `git push -u origin master`). Pas de retry automatique cote agent.

---

## Workflow type (commit utile)

1. **Stage** : `git add .` ou fichiers cibles.
2. **Message** : Conventional Commits — `feat(scope): description` / `fix(scope): description` / `docs(scope): description` / `chore(scope): description`.
3. **Commit** : `git commit -m "type(scope): message"`.
4. **Push** : l'agent peut lancer `git push -u origin <branche>` si les credentials sont disponibles ; sinon proposer la commande a Strophe.

Exemples de messages : `feat(auth): ajout login`, `fix(api): correction statut 404`, `docs(readme): mise a jour procedure`.

---

## Tags / releases

Convention des versions et tags : **references/versioning.md** (v0.1.0 → v1.0.0). Pour creer un tag : `git tag vX.Y.Z` puis `git push origin vX.Y.Z` (ou proposer a Strophe). Ne jamais creer de tag sans validation de l'utilisateur.

---

## Co-auteur Cursor (contributeur GitHub)

Cursor ajoute automatiquement un trailer `Co-authored-by: Cursor <cursoragent@cursor.com>` aux commits faits par l'agent. GitHub affiche alors un contributeur supplementaire (ex. « Cursor Adjoint » / « cursor-agent »).

- **Desactiver pour les futurs commits** : Cursor > Parametres (Ctrl+,) > **Agents > Attribution** — desactiver l'option ; **redemarrer Cursor** pour que ce soit pris en compte. A verifier apres chaque mise a jour de Cursor (le reglage peut revenir).
- **Retirer le contributeur de la liste GitHub** : la seule facon est de reecrire l'historique pour supprimer le trailer de tous les messages de commit, puis force-push. La liste des contributeurs est calculee par GitHub a partir des commits ; sans trailer, Cursor disparait. Voir ci-dessous (reecriture historique). **Ne faire le force-push qu'avec validation explicite de Strophe.**

**Reecriture historique (retirer Co-authored-by)** — a faire en local, puis `git push --force origin master` apres validation utilisateur :
```powershell
git filter-branch -f --msg-filter "sed '/^Co-authored-by: Cursor/d'" -- --all
```
(Sous PowerShell, guillemets doubles autour de la commande sed.) Apres quoi supprimer les refs de backup si tout est OK : `git for-each-ref --format="%(refname)" refs/original/ | ForEach-Object { git update-ref -d $_ }`.

---

## Depannage

- **PowerShell** : enchaîner les commandes avec `;` et non `&&` (ex. `git status; git branch`).
- **Remote manquant** : si `git push` indique « 'origin' does not appear to be a git repository », ajouter le remote : `git remote add origin https://github.com/jarvos-eu/JARVOS_recyclique.git` (ou l'URL fournie).
- **Fichier .git/index.lock** : si un add/commit a ete interrompu, supprimer le fichier `.git/index.lock` puis reessayer (non observe lors des tests).
- **Timeouts** : lors des tests, aucun timeout ; en cas d'echec reseau, proposer a Strophe d'executer push/pull dans son terminal.

---

**Voir aussi** : regle `.cursor/rules/git-workflow.mdc`, subagent `.cursor/agents/git-specialist.md`.
