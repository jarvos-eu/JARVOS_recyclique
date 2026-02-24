# Mission : Rediger la procedure Git Cursor (Artefact C)

**Destinataire** : N'importe quel agent (Analyst, PM, ou session generique). Cette creation ne passera plus par l'agent qui a cree les premiers artefacts.  
**Prealable** : Le rapport des tests Git (Artefact B) doit etre **rempli et valide** par Strophe.  
**Objectif** : Produire `references/procedure-git-cursor.md` et mettre a jour `references/index.md`.

---

## Entrees a lire

1. **Rapport des tests** : [references/artefacts/2026-02-24_02_rapport-tests-git-cursor.md](references/artefacts/2026-02-24_02_rapport-tests-git-cursor.md)  
   Lire ce fichier en entier. Ne pas supposer qu'il est dans le contexte — le charger explicitement.

2. **Index actuel** : [references/index.md](references/index.md) — pour y ajouter une entree sans dupliquer le format.

---

## Livrable 1 : references/procedure-git-cursor.md

Creer le fichier a la racine de `references/`. Structure et contenu a produire a partir du rapport B :

- **Titre** : Procedure Git Cursor — JARVOS_recyclique
- **Ce que l'agent peut faire seul** : lister les commandes qui ont reussi (ex. status, add, commit). Si le rapport indique que push echoue cote agent, le dire clairement.
- **Ce que Strophe fait a la main** : ex. push, ou toute commande exigeant credentials. Reprendre la section "Recommandations" du rapport.
- **Config credentials recommandee** : ce qui a fonctionne (token HTTPS, SSH, Credential Manager) ; ou indiquer "commandes a executer par l'utilisateur dans son terminal".
- **Workflow type** : etapes pour un commit utile (staging, message Conventional Commits, push si possible). Format : feat/fix/docs/chore(scope): message.
- **Depannage** : timeouts, fichiers .git/index.lock, PowerShell vs Git Bash si pertinent. Reprendre la section "Depannage" du rapport si remplie.

Rediger en francais. Rester concret et actionnable. Ne pas inventer de resultats — se baser uniquement sur le rapport B.

---

## Livrable 2 : Mise a jour de references/index.md

Ajouter une entree dans la section **Conventions et regles** (apres INSTRUCTIONS-PROJET.md), au meme format que les autres :

```markdown
- **`procedure-git-cursor.md`** — Procedure Git dans Cursor : ce que l'agent peut faire, ce que l'utilisateur fait, credentials, workflow et depannage.
  _(Charger si : operations Git, configuration, ou delegation au subagent Git.)_
```

Ne pas supprimer ni modifier les autres entrees.

---

## Suite apres cette mission

Une fois C cree et l'index mis a jour : creer le subagent (artefact 04) puis la regle et l'index (artefact 05) — `2026-02-24_04_brief-create-subagent-git.md`, puis `2026-02-24_05_mission-creer-regle-git-workflow.md`.
