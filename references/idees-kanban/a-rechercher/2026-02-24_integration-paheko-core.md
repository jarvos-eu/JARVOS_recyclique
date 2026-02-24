# Integration Paheko core

---

## 2026-02-24 — Mary (brainstorm migration)

Dual-backend Recyclic + Paheko : Docker setup, modules Paheko optionnels, auth/users natif Paheko, comptabilité asso. Lien vers `references/migration-paeco/`. Cartographier ce qui existe déjà dans les guides et ce qui reste à valider.

Intention : a-rechercher

---

## 2026-02-24 — Decision « max Paheko » + agenda recherche

**Decision** : Paheko = backend financier et matiere complet. Recyclic = surcouche UX + workflow terrain. On utilise toute l'API Paheko (caisse native, extension Saisie au poids). Artefact : `references/artefacts/2026-02-24_08_decision-architecture-max-paheko.md`.

**Agenda de recherche** : (1) API Paheko caisse — endpoints, modeles, sessions, ventes, paiements ; (2) Extension Saisie au poids — fonctionnement, tables, API lecture/ecriture ; (3) Catalogue modules Paheko optionnels ; (4) Analyse dumps BDD production Recyclic + Paheko (quand disponibles) pour correspondances reelles.

---

## 2026-02-24 — Cartographie 1re passe (session migration)

Cartographie realisee : contenu des guides migration-paeco (architecture, Docker, extensions listees, middleware). Artefact : `references/artefacts/2026-02-24_09_cartographie-integration-paheko-core.md`. Points a valider : version Paheko cible, un seul compose monorepo, auth/users Recyclic–Paheko. Agenda 2e passe inchange (API caisse, Saisie au poids, catalogue, dumps).

---

## 2026-02-24 — Doc officielle Paheko + prompts recherche (Analyst)

Artefact `references/artefacts/2026-02-24_10_doc-officielle-paheko-integration-core.md` : synthese doc officielle (Extensions + API 1.3.17.1), inconnues restantes. Cinq prompts Perplexity crees (reponses a venir) : `2026-02-24_api-paheko-caisse_perplexity_prompt.md`, `2026-02-24_extension-saisie-poids-paheko_perplexity_prompt.md`, `2026-02-24_version-paheko-stable_perplexity_prompt.md`, `2026-02-24_auth-sso-paheko-app-externe_perplexity_prompt.md`, `2026-02-24_catalogue-plugins-modules-paheko_perplexity_prompt.md`.
