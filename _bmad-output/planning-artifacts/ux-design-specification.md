---
stepsCompleted: [step-01-init, step-02-strategy-v1-reuse]
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/research/technical-affichage-dynamique-peintre-extension-points-research-2026-02-25.md
  - references/ou-on-en-est.md
  - references/ancien-repo/checklist-import-1.4.4.md
  - references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md
  - references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md
  - references/artefacts/2026-02-26_01_analyse-separation-frontend-backend-recyclic.md
workflowType: 'ux-design'
strategy: 'v1-reuse-1.4.4-no-refonte'
project_name: JARVOS_recyclique
user_name: Strophe
date: '2026-02-26'
---

# Spécification UX — JARVOS_recyclique

**Auteur :** Strophe  
**Date :** 2026-02-26

---

## 1. Décision de stratégie UX (v1)

Ce document ne décrit **pas** une création de maquettes ou de parcours UX from scratch. La stratégie projet, déjà fixée dans le PRD et l'architecture, est la suivante :

- **v1.0** : réutilisation des **écrans existants de RecyClique 1.4.4** (devenue obsolète). Aucune refonte des écrans pour la v1.
- **Méthode d'import** : à chaque pioche dans le code 1.4.4, appliquer la règle **copy + consolidate + security** selon la checklist `references/ancien-repo/checklist-import-1.4.4.md`.
- **Objectif v1** : continuité d'usage pour La Clique, pas de rupture ; mêmes parcours (caisse, réception, admin) avec la nouvelle stack (React-Vite-TS, FastAPI, Paheko, Redis).

Les écrans et parcours sont donc **déjà définis par l'existant 1.4.4** ; ce document formalise cette stratégie, recense les sources de référence et décrit ce qui est **préparé dès la v1** pour une évolution ultérieure vers un affichage plus dynamique (v2+).

---

## 2. Périmètre des écrans v1 (référence 1.4.4)

### 2.1 Parcours et écrans couverts

| Domaine | Parcours | Écrans / workflows de référence | Source |
|--------|----------|----------------------------------|--------|
| **Caisse** | Ouverture session, saisie ventes, clôture | Session (entry → sale → exit), presets, paiements multiples, postes, rapports | `references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md` |
| **Réception** | Postes, tickets, lignes (poids, catégorie, destination) | Postes de réception, tickets de dépôt, lignes, exports CSV | `references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md` |
| **Admin / settings** | Gestion postes, sessions, rapports, paramètres | Workflows existants 1.4.4 à conserver et réécrire (architecture modulaire, sécurité) | Architecture ADR, section « Workflows et admin / settings RecyClique » |
| **Vie associative** | Placeholders v1 | Écrans minimalistes « vie asso » ; cœur (calendrier, événements) post-MVP | PRD, parcours J5 |
| **Compta (v1)** | Admin compta via Paheko | Pas d'écrans compta dans RecyClique en v1 ; interfaces compta dans RecyClique post-MVP | PRD, FR12 / FR13 |

Les **guides utilisateur** et la **liste des endpoints API** 1.4.4 sont dans `references/ancien-repo/` (voir index `references/ancien-repo/index.md`). Ils servent de référence pour le comportement attendu des écrans lors de l'import.

### 2.2 Contraintes d'usage v1

- **Navigateurs et devices** : Chrome, Firefox, Safari, Edge (versions récentes) ; postes fixes et tablettes (caisse, réception). PRD : « écrans caisse et réception utilisables sur tablette ».
- **Responsive** : v1 = mêmes écrans que 1.4.4 (copy + consolidate + security) ; pas de refonte layout pour la v1.
- **Accessibilité** : bonnes pratiques de base (contraste, navigation clavier) ; renforcement possible post-MVP (NFR-A1).
- **Mode caisse** : écran verrouillé sur le menu caisse uniquement ; déverrouillage par PIN par opérateur habilité (PRD, parcours J1, FR4, FR5).

---

## 3. Règle d'import des écrans (copy + consolidate + security)

À **chaque import** de code UI depuis 1.4.4 (composants, pages, styles), appliquer la checklist suivante. Référence complète : `references/ancien-repo/checklist-import-1.4.4.md`.

### 3.1 Copy (copie ciblée)

- Périmètre clair : quels fichiers/dossiers sont copiés et pour quelle fonctionnalité.
- Exclusions : pas de `node_modules/`, `.env`, secrets, caches, `dist/`, `build/`.
- Traçabilité : noter l'origine (chemin 1.4.4, tag/commit si pertinent) en commentaire ou dans un suivi d'import.

### 3.2 Consolidate (consolidation)

- Dépendances : ajouter au manifeste du nouveau projet (package.json, pyproject.toml) avec version explicite.
- Alignement avec le design modules (TOML, ModuleBase, EventBus, slots) et l'architecture cible (FastAPI, structure frontend par domaine).
- Pas de doublon avec le code déjà présent dans JARVOS_recyclique.

### 3.3 Security (sécurité)

- Aucun secret en dur ; utiliser variables d'environnement ou config sécurisée.
- Audit des fichiers importés (tokens, mots de passe, clés API).
- Vérification des licences et CVE sur les dépendances ajoutées.

---

## 4. Préparation pour un affichage dynamique (v2+)

En v1, on **n'implémente pas** d'écrans configurables ni d'intégration au service Peintre (JARVOS Mini). On **réserve la place** via des interfaces et des stubs, conformément au PRD (FR26) et à la recherche technique « affichage dynamique, extension points Peintre ».

### 4.1 Référence technique

Document de référence :  
`_bmad-output/planning-artifacts/research/technical-affichage-dynamique-peintre-extension-points-research-2026-02-25.md`

Résumé des recommandations :

- **Interfaces** à définir dès le socle front v1.0 :
  - `LayoutConfigService` : configuration de layout (écrans configurables par utilisateur ou par rôle en v2+).
  - `VisualProvider` : fourniture de visuels (placeholder en v1 ; intégration Peintre en v2+).
- **Implémentations stub** en v1 : layout fixe ou par défaut ; visuel placeholder. Enregistrement au **bootstrap** (Context ou factory) pour que les composants puissent appeler `useLayoutConfig()` / `useVisual()` sans erreur.
- **Slots** : réutiliser le pattern **ModuleSlot** déjà prévu dans le design modules ; les zones à contenu dynamique futur utilisent ces slots.
- **Emplacements suggérés** : `core/layout` ou `shared/services` pour les interfaces et stubs ; enregistrement dans `main.tsx` ou `AppProviders.tsx`.

### 4.2 Ce qui est « installé » en v1 (sans refonte des écrans)

| Élément | Rôle en v1 | Évolution v2+ |
|--------|------------|----------------|
| Interfaces `LayoutConfigService`, `VisualProvider` | Définies en TS ; stubs enregistrés au bootstrap | Implémentations réelles (API préférences, client Peintre ou BFF) |
| Slots (ModuleSlot) | Déjà prévus par le design modules ; pas de changement de structure des écrans | Contenu dynamique ou visuels Peintre injectés dans les slots |
| Bootstrap / Context | Enregistrement des stubs (layout fixe, visuel placeholder) | Bascule via config ou feature flag vers implémentations réelles |
| API préférences layout | Non implémentée en v1 | Route type `GET/PUT /api/users/me/preferences` (recherche technique) |

L'architecture (ADR) indique que les choix de structure frontend (slots, extension points, bootstrap) doivent **anticiper** cette évolution pour éviter une refonte coûteuse plus tard.

### 4.3 Roadmap résumée (recherche technique)

- **v1.0** : interfaces + stubs + enregistrement au bootstrap ; réutilisation des slots existants.
- **v2+** : API préférences (backend) + client `LayoutConfigService` réel ; client Peintre (ou BFF) pour `VisualProvider` ; layout configurable par utilisateur et visuels générés par Peintre.

---

## 5. Synthèse et liens avec les autres livrables

| Livrable | Rôle pour l'UX |
|----------|-----------------|
| **PRD** | Scope v1 (mêmes écrans que 1.4.4), parcours utilisateur (J1–J5), NFR accessibilité, responsive. |
| **Architecture (ADR)** | Structure frontend par domaine, slots, extension points, évolution « affichage plus dynamique », workflows admin/settings. |
| **Recherche technique Peintre / extension points** | Détail des interfaces, emplacements des stubs, roadmap v1 vs v2+. |
| **Checklist import 1.4.4** | Règle copy + consolidate + security à chaque pioche dans le code 1.4.4. |
| **Audits caisse / réception 1.4.4** | Référence des workflows et options (API, BDD, UI) pour les écrans à réimporter. |
| **Décision déploiement (artefact 2026-02-26_01)** | Un container RecyClique (front + middleware), SPA + API REST ; pas de bascule SSR pour v1. |

---

## 6. Prochaines étapes (implémentation)

1. **Socle front** : initialiser le frontend (Vite react-ts), structure par domaine (`caisse/`, `reception/`, `admin/`, `auth/`, `shared/`).
2. **Import des écrans** : piocher dans le code 1.4.4 écran par écran (ou module par module) en appliquant la checklist copy + consolidate + security.
3. **Extension points** : ajouter les interfaces `LayoutConfigService` et `VisualProvider` avec stubs et enregistrement au bootstrap dès que la structure de base est en place (recommandation recherche technique).
4. **Tests et accessibilité** : bonnes pratiques de base (contraste, clavier) sur les écrans caisse et réception.

Ce document sert de **référence unique** pour la stratégie UX v1 (réutilisation 1.4.4) et la préparation de l'affichage dynamique (v2+). Il ne remplace pas les audits détaillés ni la checklist d'import pour le travail au quotidien.
