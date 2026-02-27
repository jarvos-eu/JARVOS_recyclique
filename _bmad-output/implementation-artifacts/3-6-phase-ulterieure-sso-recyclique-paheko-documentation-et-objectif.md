# Story 3.6: Phase ulterieure SSO RecyClique–Paheko — documentation et objectif

Status: review

<!-- Phase ulterieure : critères = rédaction spec/documentation (objectif SSO, options, contraintes Paheko). Pas d'implémentation en v1. -->

## Story

En tant qu'**admin technique**,
je veux **une documentation pour le SSO entre RecyClique et Paheko**,
afin de **préparer l'authentification unifiée en phase ultérieure**.

## Contexte

- **FR17** : (Phase ultérieure) Le système peut offrir un SSO entre RecyClique et Paheko (à documenter).
- En v1 : auth terrain via JWT (RecyClique), admin via Paheko (auth séparée). Le SSO n'est pas implémenté ; cette story livre uniquement la **spécification / documentation** pour une phase ultérieure.

## Acceptance Criteria

1. **Étant donné** les choix d'auth actuels (JWT terrain, Paheko admin séparé)  
   **Quand** le périmètre phase ultérieure inclut le SSO  
   **Alors** un document décrit **l'objectif** du SSO RecyClique–Paheko (cas d'usage, bénéfices, périmètre cible).

2. **Étant donné** les contraintes techniques Paheko (auth, API, plugins)  
   **Quand** on envisage un SSO  
   **Alors** le document décrit les **options** possibles (ex. OAuth2, JWT partagé, session proxy, etc.) avec avantages/inconvénients et compatibilité Paheko.

3. **Étant donné** l'écosystème RecyClique + Paheko  
   **Quand** on prépare l'implémentation future  
   **Alors** le document décrit les **contraintes Paheko** (limites auth, intégration, déploiement) et les prérequis pour une future implémentation.

4. **Étant donné** cette story  
   **Quand** elle est livrée  
   **Alors** le livrable se limite à la **rédaction de la spec/documentation** ; **aucune implémentation** en v1 (pas de code SSO, pas de changement auth).

## Tasks / Subtasks

- [x] Task 1 (AC: 1, 2, 3) — Rédaction du document SSO
  - [x] Rechercher et résumer les mécanismes d'auth et d'intégration Paheko (doc officielle, plugins, API).
  - [x] Rédiger la section « Objectif » (cas d'usage, bénéfices, périmètre).
  - [x] Rédiger la section « Options » (scénarios SSO possibles, compatibilité Paheko).
  - [x] Rédiger la section « Contraintes Paheko » (limites, prérequis déploiement/config).
- [x] Task 2 (AC: 4) — Livraison et emplacement
  - [x] Placer le document dans `references/artefacts/` avec le nommage `YYYY-MM-DD_NN_sso-recyclique-paheko-spec.md` (ex. `2026-02-27_01_sso-recyclique-paheko-spec.md`) et mettre à jour `references/artefacts/index.md`.
  - [x] Vérifier qu'aucun code d'implémentation SSO n'est livré dans le cadre de cette story.

## Dev Notes

- **Phase ulterieure** : pas de développement auth/SSO en v1. Les critères sont uniquement documentaires.
- **Références utiles** : artefact 08 (§2.1 utilisateurs), artefact 09 (§3.2/3.3 auth), FR16/FR17 dans `epics.md` ; documentation Paheko (auth, plugins) à consulter pour les contraintes.
- **Livrable** : un fichier markdown (ou équivalent) de spec/documentation SSO ; pas de modification du code FastAPI, frontend ou Paheko.

### Project Structure Notes

- Document de spec : à placer dans `references/artefacts/` avec la convention `YYYY-MM-DD_NN_titre-court.md` (ex. `2026-02-27_01_sso-recyclique-paheko-spec.md`). Mettre à jour `references/artefacts/index.md` à chaque ajout (voir `references/INSTRUCTIONS-PROJET.md`). Ne pas utiliser `doc/` pour ce livrable (réservé à la communication publique).

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 3, Story 3.6, FR17]
- [Source: _bmad-output/planning-artifacts/epics.md — FR Coverage Map FR17]
- [Source: references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md — §2.1 utilisateurs]
- [Source: references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md — §3.2/3.3 auth]

## Dev Agent Record

### Agent Model Used

bmad-dev (subagent)

### Debug Log References

—

### Completion Notes List

- Livrable = rédaction spec uniquement (pas de code). Document créé : `references/artefacts/2026-02-27_01_sso-recyclique-paheko-spec.md` avec les sections : Objectif SSO RecyClique–Paheko, Options techniques, Contraintes Paheko, Recommandations. Index `references/artefacts/index.md` mis à jour. Aucun agent-state (livraison sans blocage).

### File List

- `references/artefacts/2026-02-27_01_sso-recyclique-paheko-spec.md` (créé)
- `references/artefacts/index.md` (modifié — entrée nouvel artefact)
- `_bmad-output/implementation-artifacts/3-6-phase-ulterieure-sso-recyclique-paheko-documentation-et-objectif.md` (modifié — statut, tasks, Dev Agent Record)
