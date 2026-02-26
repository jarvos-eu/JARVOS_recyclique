# Doc officielle Paheko - Integration core (complement)

**Date :** 2026-02-24  
**Contexte :** Session Analyst - integration Paheko core ; complement a la cartographie 09 (guides internes).  
**Idee liee :** `references/idees-kanban/a-rechercher/2026-02-24_integration-paheko-core.md`  
**Session / conversation :** Analyst - Integration Paheko core doc et recherches

---

## Source

Doc officielle Paheko (fossil.kd2.org) : pages **Extensions** et **API** (version 1.3.17.1).

---

## Synthèse Extensions

- **Deux types** : **plugins** (PHP, acces API complet, creation tables, risque securite - ex. Caisse) ; **modules** (Brindille, depuis 1.3, stockage JSON, API limitee, pas de PHP execute).
- **Installation plugins** : fichier `.tar.gz` dans `data/plugins`, puis activation dans **Configuration → Extensions** (onglet Extensions inactives).
- **Officiels** : fournis avec Paheko (install + mises a jour). Code source : https://fossil.kd2.org/paheko-plugins/ (plugins), https://fossil.kd2.org/paheko-modules/ (modules).
- Sur Paheko.cloud : seuls les plugins officiels sont installables.

---

## Synthèse API

- **Activation** : Configuration → Fonctions avancees → API (identifiant + mot de passe).
- **Base** : `https://adresse_association/api/{chemin}/`, auth HTTP basique, reponses JSON (ou formulaire pour certains POST).
- **Chemins utiles** : `accounting/*` (years, charts, transaction GET/POST), `user/*` (categories, new, import, {ID}), `services/subscriptions/import`, `web/*` (list, page, html), `download` (BDD SQLite), `download/files` (ZIP des fichiers), `sql` (POST, SELECT uniquement).
- **Pas de chemins « caisse » / sessions de vente** dans cette page - la caisse etant un plugin, son API est a rechercher ailleurs (plugin ou autre doc).

---

## Fichiers

- Gestion native (accueil Paheko : « remplace NextCloud, Google Drive »). API : `download/files` pour tout recuperer en ZIP.

---

## Inconnues restantes → prompts Perplexity créés

| Inconnue | Fichier prompt (a executer dans Perplexity) |
|----------|---------------------------------------------|
| API Paheko caisse (endpoints, modeles, doc) | `references/recherche/2026-02-24_api-paheko-caisse_perplexity_prompt.md` |
| Extension Saisie au poids (fonctionnement, tables, API) | `references/recherche/2026-02-24_extension-saisie-poids-paheko_perplexity_prompt.md` |
| Version Paheko recommandee (stable, LTS, 1.3.x) | `references/recherche/2026-02-24_version-paheko-stable_perplexity_prompt.md` |
| Auth / SSO Paheko avec app externe (FastAPI) | `references/recherche/2026-02-24_auth-sso-paheko-app-externe_perplexity_prompt.md` |
| Catalogue plugins/modules officiels (liste, versions) | `references/recherche/2026-02-24_catalogue-plugins-modules-paheko_perplexity_prompt.md` |

Les reponses seront a enregistrer dans `references/recherche/` (fichiers `_reponse.md` ou `_reponse-1.md`) apres execution des recherches.

---

## Liens

- Cartographie guides (1re passe) : `references/artefacts/2026-02-24_09_cartographie-integration-paheko-core.md`
- Decision 08 : `references/artefacts/2026-02-24_08_decision-architecture-max-paheko.md`
- Idee : `references/idees-kanban/a-rechercher/2026-02-24_integration-paheko-core.md`
