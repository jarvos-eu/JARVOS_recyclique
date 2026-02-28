# Checklist — Import de code depuis RecyClique 1.4.4

**Usage :** À appliquer **à chaque fois** qu'on réutilise du code du repo 1.4.4 (piocher au fur et à mesure). Le refactor ne reprend pas tout d'un coup ; cette checklist sécurise et cadre chaque import.

**Référence :** [references/ancien-repo/index.md](index.md) (analyse brownfield, structure, modèles). Design cible modules : [references/artefacts/2026-02-24_07_design-systeme-modules.md](../artefacts/2026-02-24_07_design-systeme-modules.md).

---

## 1. Copy (copie ciblée)

- [ ] **Périmètre clair** : quels fichiers ou dossiers sont copiés, et pourquoi (fonctionnalité, règle métier, composant).
- [ ] **Exclusions** : ne pas copier `node_modules/`, `.env`, `.env.*`, tout fichier contenant des secrets, caches (`__pycache__/`, `.pyc`, `dist/`, `build/`), dossiers de déploiement sensibles.
- [ ] **Traçabilité** : noter l'origine (chemin dans 1.4.4, commit ou tag si pertinent) dans un commentaire ou un fichier de suivi d'import si le projet en tient un.

---

## 2. Consolidate (consolidation avant intégration)

- [ ] **Dépendances** : lister les dépendances (Python, JS, etc.) introduites par l'import ; les ajouter au manifeste du nouveau projet (pyproject.toml, package.json) avec version explicite, pas de doublon.
- [ ] **Alignement design** : si le code touche à des modules ou services, vérifier la cohérence avec le design système de modules (artefact 07) et l'architecture cible (FastAPI, Paheko, EventBus, etc.).
- [ ] **Pas de doublon** : s'assurer que la logique ou le code n'existe pas déjà dans le nouveau repo sous une autre forme.

---

## 3. Security (sécurité)

- [ ] **Aucun secret en dur** : pas de tokens, mots de passe, clés API, URLs avec credentials dans le code. Remplacer par variables d'environnement ou config chargée de façon sécurisée.
- [ ] **Audit des fichiers sensibles** : parcourir les fichiers importés pour repérer `.env`, `secret`, `password`, `api_key`, `token` (en clair). Supprimer ou externaliser avant tout commit.
- [ ] **Dépendances** : vérifier les licences et, si possible, les CVE connues sur les dépendances ajoutées (outils type `pip audit`, `npm audit`, ou manuel).
- [ ] **Git** : ne jamais committer de secrets. Rappel : [references/procedure-git-cursor.md](../procedure-git-cursor.md). En cas de fuite, invalider les secrets et les renouveler.

---

## Quand utiliser cette checklist

À chaque **pioche** dans le code 1.4.4 (copie de fichiers ou de blocs vers le nouveau projet), valider mentalement ou par écrit les trois blocs Copy, Consolidate, Security avant de considérer l'import terminé. L'objectif est d'obtenir le **même rendu** que 1.4.4 tout en passant le code par une **analyse de cohérence** (Consolidate) et une **analyse de sécurité** (Security) — pas de reprise brute sans contrôle.
