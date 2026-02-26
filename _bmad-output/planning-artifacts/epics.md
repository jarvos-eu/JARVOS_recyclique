---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories, step-04-final-validation]
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
  - references/artefacts/2026-02-26_01_analyse-separation-frontend-backend-recyclic.md
  - references/artefacts/2026-02-26_02_track-enterprise-multi-utilisateur.md
  - references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md
  - references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md
  - references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md
  - references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md
  - references/artefacts/2026-02-26_11_brief-revision-ordre-construction.md
  - references/ancien-repo/checklist-import-1.4.4.md
  - references/ou-on-en-est.md
  - references/versioning.md
lastEdited: '2026-02-26'
editHistory:
  - date: '2026-02-26'
    changes: >
      Refonte complète de l'ordre des epics (Correct Course). Epic 1 inchangé.
      Ajout Epic 2 Référentiels métier (couche manquante). Réorganisation en 10 epics
      selon l'ordre de construction en couches (référentiels → auth → postes → canal push →
      caisse → réception → correspondance → admin → déclaratif → extension points).
      Ajout sections "Ordre de construction", "Règle refactor brownfield", "Table des référentiels".
      Références artefacts 08, 09, 10 et checklist import dans toutes les epics/stories concernées.
---

# JARVOS_recyclique - Epic Breakdown

## Overview

Ce document fournit le découpage complet en epics et stories pour JARVOS_recyclique, construit **en couches de dépendances** (fondations → métier → synchronisation → administration). La cible est la **première version en production** (parité 1.4.4 + sync Paheko, sans rupture).

**Epic 1 livré.** Le reste suit l'ordre ci-dessous : chaque couche dépend de la précédente. On ne commence pas par les murs avant les fondations.

**Human in the Loop (HITL)** : chaque epic (3 à 10) contient une section « Human in the Loop — moments possibles ». L'Epic 7 (correspondance) a des HITL **obligatoires**. Les autres epics ont des HITL **recommandés** ou **optionnels**.

---

## Décisions architecturales de référence

**S'appliquent à toutes les épiques et stories.** Tout agent ou workflow travaillant sur le projet doit avoir ces décisions sous les yeux.

| Décision | Contenu court |
|----------|----------------|
| **Convention tests frontend** | Tests **co-locés** : `*.test.tsx` (ou `*.test.ts`) à côté du composant. Pas de dossier `__tests__` au niveau module. |
| **Outil tests frontend** | **Vitest + React Testing Library + jsdom**. Scripts : `npm run test` (watch), `npm run test:run` (CI). E2E hors périmètre v0.1 ; si E2E plus tard = **Playwright**. |
| **Versions stack** | Python 3.12, Node 20 LTS. Figées dans le Dockerfile et README. PostgreSQL 16, Redis 7, Paheko (image officielle). |
| **Loader modules et slots** | `api/config/modules.toml`, `api/core/modules/`, `api/workers/`, `frontend/src/shared/slots/`. Ne pas recréer une autre convention. |
| **Styling / UI frontend** | **Mantine** (alignement RecyClique 1.4.4). Pas de Tailwind ni autre lib UI sans décision. |
| **Module correspondance (FR13b)** | Reporté à l'Epic 7 (stories 7.1/7.2). Ne pas trancher le détail avant BDD + instance dev + analyste. |

**Références uniques :**
- Architecture complète : `_bmad-output/planning-artifacts/architecture.md`
- Checklist v0.1 : `references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md`
- Rétro Epic 1 : `_bmad-output/implementation-artifacts/epic-1-retro-2026-02-26.md`

---

## Ordre de construction — couches de dépendances

```
Couche 0  [FAIT]  Epic 1  — Socle Docker / FastAPI / Frontend / Modules
Couche 1          Epic 2  — Référentiels métier (Sites, Postes, Catégories, Presets)
Couche 2          Epic 3  — Authentification, Users, PIN, RBAC, Démarrage postes
Couche 3  [//]    Epic 4  — Canal push Paheko (parallèle possible avec Epic 3)
Couche 4          Epic 5  — Caisse et synchronisation (dépend de 1+2+3)
Couche 5          Epic 6  — Réception et flux matière (dépend de 1+2)
Couche 6          Epic 7  — Correspondance et mapping (dépend de Epic 5 stable + HITL)
Couche 7          Epic 8  — Administration, compta v1, vie associative
Couche 8          Epic 9  — Données déclaratives et éco-organismes
Couche 9  [//]    Epic 10 — Extension points / stubs (parallèle possible)
```

**Règle de précédence :** Une story ne peut pas être commencée si une story d'une couche inférieure dont elle dépend n'est pas livrée. Les trous de dépendance sont la cause première du revert Epic 2. La table des référentiels ci-dessous formalise cette règle.

---

## Règle refactor brownfield

> **Pour toute story qui touche au métier caisse, réception, auth, admin, catégories :**
> le livrable est une **migration/copie** depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md` (copy + consolidate + security).
> Ce n'est **pas** une conception from scratch.

**Références 1.4.4 à charger selon le domaine :**

| Domaine | Références |
|---------|------------|
| Caisse (sessions, ventes, clôture) | `references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md`, `references/ancien-repo/v1.4.4-liste-endpoints-api.md`, `references/ancien-repo/data-models-api.md` |
| Réception (postes, tickets, lignes) | `references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md` |
| Auth, Users, Permissions | `references/ancien-repo/data-models-api.md`, `references/ancien-repo/fonctionnalites-actuelles.md` |
| Catégories, Presets | `references/ancien-repo/data-models-api.md`, `references/ancien-repo/v1.4.4-liste-endpoints-api.md` |
| Correspondance RecyClique ↔ Paheko | `references/migration-paeco/audits/matrice-correspondance-caisse-poids.md`, `references/artefacts/2026-02-25_08_session-confrontation-recyclic-paheko.md` |

**Artefacts de vision architecturale (à charger pour toute story métier) :**

| Artefact | Rôle |
|----------|------|
| `references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md` | Qui stocke quoi (RecyClique vs Paheko), source de vérité par entité |
| `references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md` | Endpoints v1 par domaine, source données, cas RecyClique → Paheko |
| `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` | Pour 29 écrans : route, permissions, données, appels API, actions → endpoints |

---

## Table des référentiels — story de livraison

> Avant de commencer une story qui suppose l'existence d'un référentiel, vérifier que la story qui le livre est marquée done.

| Référentiel | Table BDD | Livré par | Utilisé par |
|-------------|-----------|-----------|-------------|
| Sites | `sites` | Story **2.1** | Stories 2.2, 3.4, 5.1 |
| Postes de caisse | `cash_registers` | Story **2.2** | Stories 3.4, 5.1 |
| Catégories | `categories` | Story **2.3** | Stories 2.4, 5.2, 6.2, 9.1 |
| Presets | `preset_buttons` | Story **2.4** | Story 5.2 |
| Users + roles | `users`, `groups`, `permissions` | Story **3.1** | Stories 3.2–3.6, toutes les stories auth |

---

### Functional Requirements

FR1: Un opérateur habilité peut démarrer une session de caisse (avec fond de caisse) sur un poste donné.
FR2: Un opérateur habilité peut enregistrer des ventes (lignes, catégories, quantités, prix, poids éventuels, paiements multi-moyens) pendant la session.
FR3: Un opérateur habilité peut clôturer la session de caisse (comptage physique, totaux, écart éventuel) et déclencher le contrôle et la sync comptable.
FR4: Le système peut restreindre l'accès au menu caisse uniquement lorsque le poste est en mode caisse (écran verrouillé sur la caisse).
FR5: Une personne habilitée peut déverrouiller la session (ou quitter le mode caisse) en saisissant son code PIN.
FR6: Le système peut gérer plusieurs lieux et plusieurs caisses (multi-sites, multi-caisses).
FR7: Le système peut pousser chaque ticket de vente vers Paheko (push par ticket, file résiliente) sans double saisie compta.
FR7b: Le système peut permettre la saisie caisse hors ligne (buffer local) et synchroniser les tickets vers Paheko au retour en ligne (file Redis Streams côté backend).
FR8: Un opérateur peut ouvrir un poste de réception et créer des tickets de dépôt.
FR9: Un opérateur peut saisir des lignes de réception (poids, catégorie, destination) sur un ticket.
FR10: Le système conserve la réception comme source de vérité matière/poids (aucune sync manuelle obligatoire vers Paheko).
FR11: Le système peut synchroniser les données caisse (sessions, tickets, lignes, paiements) vers Paheko à la clôture (contrôle totaux, syncAccounting). Une session RecyClique = une session Paheko par caisse.
FR12: Un responsable compta peut administrer la compta via l'interface Paheko (v1) en attendant les interfaces RecyClique.
FR13: (Post-MVP) Un responsable compta peut effectuer les opérations compta depuis RecyClique.
FR13b: Le système peut gérer un mapping prédéfini entre RecyClique et Paheko (moyens de paiement, catégories, sites/emplacements) ; périmètre à figer lorsque BDD et instance dev sont stabilisées.
FR14: Un administrateur peut démarrer un poste (caisse ou réception) avec un compte administrateur (ou équivalent).
FR15: Le système peut associer un code PIN à chaque personne habilitée à la caisse pour le déverrouillage de session.
FR16: (Phase initiale) Le système peut authentifier les utilisateurs terrain via JWT (FastAPI) et les utilisateurs admin via Paheko (auth séparée).
FR17: (Phase ultérieure) Le système peut offrir un SSO entre RecyClique et Paheko (à documenter).
FR18: Un admin technique peut déployer et configurer l'instance via Docker Compose.
FR19: Un admin technique peut configurer le canal push RecyClique → Paheko (endpoint, secret, résilience).
FR20: Le système peut conserver les tickets non poussés en file (Redis Streams) et les repousser après indisponibilité de Paheko (retry sans perte).
FR21: Un utilisateur peut accéder à des écrans ou placeholders « vie associative » depuis RecyClique.
FR22: Le système peut produire et conserver les données déclaratives (poids, flux, catégories, périodes) dans RecyClique pour les déclarations éco-organismes.
FR23: (Post-MVP) Le système peut exposer un module décla éco-organismes (exports, multi-éco-organismes) depuis RecyClique.
FR24: Le système peut charger et activer des modules RecyClique via configuration (TOML, ModuleBase, EventBus Redis Streams, slots React).
FR25: Le système peut faire coexister des plugins Paheko et des modules RecyClique.
FR26: Le système peut exposer des points d'extension (LayoutConfigService, VisualProvider) avec implémentations stub en v1.
FR27: (Post-MVP) Le système peut gérer un fonds documentaire RecyClique distinct de la compta/factures Paheko.

### NonFunctional Requirements

NFR-P1: L'enregistrement d'une vente (saisie + envoi) se termine en moins de 2 secondes dans des conditions normales.
NFR-P2: La clôture de session ne bloque pas l'opérateur plus de 10 secondes ; le push et la sync comptable peuvent s'achever en arrière-plan.
NFR-S1: Les échanges RecyClique ↔ Paheko passent par HTTPS avec un secret partagé ; aucun secret en clair dans les requêtes.
NFR-S2: Les secrets sont gérés via variables d'environnement ou secrets manager, pas en dur dans le code.
NFR-S3: Accès caisse restreint par mode verrouillé et déverrouillage par PIN par opérateur habilité.
NFR-S4: Données personnelles (utilisateurs, adhésions) conformes au RGPD dans le périmètre géré par Paheko/RecyClique.
NFR-I1: La file de push (Redis Streams) garantit qu'aucun ticket n'est perdu en cas d'indisponibilité temporaire de Paheko ; retry jusqu'à succès.
NFR-I2: Les écritures compta (syncAccounting) respectent la configuration Paheko (comptes, exercice, moyens de paiement).
NFR-A1: Bonnes pratiques d'accessibilité de base (contraste, navigation clavier) pour les écrans caisse et réception.

### Additional Requirements

**Infrastructure et déploiement :**
- Docker Compose : RecyClique (un container), Paheko (SQLite), PostgreSQL (RecyClique), Redis. Une instance par ressourcerie.
- Config via variables d'environnement / secrets manager ; pas de secrets en dur.

**API et patterns :**
- API REST, JSON ; montants en centimes ; poids en kg (réception) / conversion vers Paheko (g si besoin).
- BDD : snake_case (tables pluriel, index idx_{table}_{colonne}).
- API : endpoints pluriel snake_case ; erreur = `{ "detail": "..." }` ; dates ISO 8601.
- Frontend : composants PascalCase, hooks/fonctions camelCase ; état immuable ; isLoading/isPending.
- Événements Redis : dot.lowercase (ex. `pos.ticket.created`) ; payload JSON snake_case ; idempotence et acks après traitement.

**Règle brownfield (rappel) :**
- Livrable de chaque story métier = migration/copie depuis 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md`.
- Artefacts de référence : 08 (qui stocke quoi), 09 (périmètre API v1), 10 (traçabilité écran → API).

**UX v1 :**
- Mêmes écrans que RecyClique 1.4.4 (copy + consolidate + security) ; pas de refonte UX pour la v1.
- Extension points (LayoutConfigService, VisualProvider) en stubs v1.
- Référence : `_bmad-output/planning-artifacts/ux-design-specification.md`.

**Logging et observabilité :**
- Logs structurés (JSON) ; request_id propagé front → back ; pas de données sensibles.
- Health check : app up, BDD RecyClique, Redis ping, Paheko joignable.
- Audit log : table `audit_events` (ouvertures/fermetures caisse, clôtures, connexions, modifications config sensibles).

### FR Coverage Map

FR1: Epic 5 — Démarrer session caisse
FR2: Epic 5 — Enregistrer ventes (lignes, catégories, paiements)
FR3: Epic 5 — Clôturer session et déclencher contrôle + sync
FR4: Epic 3 — Restreindre menu caisse (mode verrouillé)
FR5: Epic 3 — Déverrouiller par PIN
FR6: Epic 2 (modèles sites+caisses) + Epic 5 (multi-sites gestion sessions)
FR7: Epic 4 (push) + Epic 5 (déclenchement)
FR7b: Epic 5 — Saisie caisse hors ligne + sync au retour
FR8: Epic 6 — Ouvrir poste réception, créer tickets dépôt
FR9: Epic 6 — Saisir lignes réception (poids, catégorie, destination)
FR10: Epic 6 — Réception source de vérité matière/poids
FR11: Epic 5 — Sync caisse vers Paheko à la clôture (syncAccounting)
FR12: Epic 8 — Administrer compta via Paheko (v1)
FR13: (Post-MVP)
FR13b: Epic 7 — Mapping RecyClique↔Paheko
FR14: Epic 2 (modèle cash_registers) + Epic 3 (démarrage poste avec compte admin)
FR15: Epic 3 — PIN par opérateur caisse
FR16: Epic 3 — Authentification JWT terrain et Paheko admin
FR17: Epic 3 — SSO RecyClique↔Paheko (phase ultérieure, documentation)
FR18: Epic 1 — Déployer et configurer instance (Docker Compose)
FR19: Epic 4 — Configurer canal push (endpoint, secret, résilience)
FR20: Epic 4 (file Redis) + Epic 5 (retry)
FR21: Epic 8 — Placeholders vie associative
FR22: Epic 9 — Données déclaratives (poids, flux, catégories, périodes)
FR23: (Post-MVP) Epic 9 — Module décla éco-organismes
FR24: Epic 1 — Charger modules (TOML, ModuleBase, EventBus, slots)
FR25: Epic 1 — Coexistence plugins Paheko et modules RecyClique
FR26: Epic 10 — Points d'extension (LayoutConfigService, VisualProvider) stubs v1
FR27: (Post-MVP) Epic 10 — Fonds documentaire RecyClique

### Epic List

- **Epic 1**: Socle technique et déploiement ✅ LIVRÉ
- **Epic 2**: Référentiels métier (Sites, Postes de caisse, Catégories, Presets)
- **Epic 3**: Authentification, users, PIN, RBAC et démarrage des postes
- **Epic 4**: Canal push Paheko (config + worker Redis Streams)
- **Epic 5**: Caisse et synchronisation Paheko
- **Epic 6**: Réception et flux matière
- **Epic 7**: Correspondance et mapping RecyClique ↔ Paheko
- **Epic 8**: Administration, compta v1 et vie associative
- **Epic 9**: Données déclaratives et éco-organismes
- **Epic 10**: Extension points et évolution

---

## Epic 1: Socle technique et déploiement ✅ LIVRÉ

Permettre à l'admin technique de déployer et faire tourner l'instance (RecyClique + Paheko + PostgreSQL + Redis), avec structure frontend (Vite React TS) et API (FastAPI), health check, et base pour le chargement de modules (TOML, ModuleBase, EventBus Redis Streams, slots React).

**Contexte déploiement :** Paheko a déjà été déployé en Docker avec le dump de prod intégré (instance dev/local existante). Les stories suivantes s'appuient sur cette hypothèse.

**FRs couverts :** FR18, FR24, FR25.

*Stories 1.1 à 1.5 livrées. Référence : `_bmad-output/implementation-artifacts/epic-1-retro-2026-02-26.md`.*

---

## Epic 2: Référentiels métier

Livrer les entités de base dont dépendent toutes les stories métier : sites, postes de caisse, catégories et presets. Ces modèles BDD et leurs API CRUD sont les **fondations business** ; rien ne peut être construit sans eux.

**Prérequis :** Epic 1 livré.

**Règle :** Toutes les stories de cet epic = migration/copie depuis 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md`.

**Références transversales :** artefact 08 (§2.2, §2.5, §2.6), artefact 09 (§3.4, §3.8, §3.9, §3.12), `references/ancien-repo/data-models-api.md`.

**FRs couverts :** FR6 (partiel — modèles), FR14 (partiel — modèle cash_registers).

### Human in the Loop — moments possibles

| # | Moment | Ton intervention |
|---|--------|-----------------|
| **HITL-2.0** | Avant de lancer l'Epic 2 | **Optionnel** : confirmer que la stack Epic 1 est opérationnelle (health check OK). |
| **HITL-2.x** | Après chaque story 2.x | **Optionnel** : confirmer le livrable avant d'enchaîner. |

### Story 2.1: Sites — modèle BDD + API CRUD

En tant qu'admin ou développeur,
je veux une table `sites` en BDD RecyClique et les endpoints CRUD correspondants,
afin que les postes de caisse et les sessions puissent être rattachés à un site.

**Prérequis :** Epic 1 livré. Migrations Alembic (ou équivalent) initialisées dans `api/db/`.

**Critères d'acceptation :**

**Étant donné** un environnement RecyClique opérationnel (Epic 1)  
**Quand** la migration crée la table `sites` (id, name, is_active, created_at, updated_at)  
**Alors** les endpoints `GET /v1/sites`, `GET /v1/sites/{site_id}`, `POST /v1/sites`, `PATCH /v1/sites/{site_id}`, `DELETE /v1/sites/{site_id}` répondent correctement  
**Et** la structure respecte les conventions snake_case (artefact 08 §2.2, artefact 09 §3.4) ; livrable = migration/copie 1.4.4.

### Story 2.2: Postes de caisse — modèle BDD + API CRUD

En tant qu'admin ou développeur,
je veux une table `cash_registers` et les endpoints CRUD + statut,
afin de pouvoir démarrer des sessions de caisse sur des postes identifiés par site.

**Prérequis :** Story 2.1 livrée (sites).

**Critères d'acceptation :**

**Étant donné** la table `sites` existante  
**Quand** la migration crée la table `cash_registers` (id, site_id FK, name, location, is_active, enable_virtual, enable_deferred)  
**Alors** les endpoints `GET /v1/cash-registers`, `GET /v1/cash-registers/{register_id}`, `GET /v1/cash-registers/status`, `POST /v1/cash-registers`, `PATCH /v1/cash-registers/{register_id}`, `DELETE /v1/cash-registers/{register_id}` fonctionnent  
**Et** le champ `site_id` fait référence à un site existant (FK) ; livrable = migration/copie 1.4.4 (audit caisse §1.3 Postes).

### Story 2.3: Catégories — modèle BDD + API CRUD, hiérarchie et visibilité

En tant qu'admin ou développeur,
je veux une table `categories` avec hiérarchie parent/enfant et indicateurs de visibilité (caisse/réception),
afin que les lignes de vente et de réception puissent référencer des catégories métier.

**Prérequis :** Epic 1 livré.

**Critères d'acceptation :**

**Étant donné** un environnement RecyClique opérationnel  
**Quand** la migration crée `categories` (id, name, parent_id nullable, official_name, is_visible_sale, is_visible_reception, display_order, display_order_entry, deleted_at)  
**Alors** les endpoints de base fonctionnent : `GET /v1/categories`, `GET /v1/categories/hierarchy`, `GET /v1/categories/{id}`, `POST /v1/categories`, `PUT /v1/categories/{id}`, `DELETE /v1/categories/{id}` (soft delete), `POST /v1/categories/{id}/restore`, `GET /v1/categories/sale-tickets`, `GET /v1/categories/entry-tickets`, `PUT /v1/categories/{id}/visibility`, `PUT /v1/categories/{id}/display-order`  
**Et** la hiérarchie (parent_id auto-référentielle) est requêtable ; livrable = migration/copie 1.4.4 (artefact 08 §2.5, artefact 09 §3.9).  
**Note :** L'import/export CSV des catégories est reporté à l'Epic 8 (admin avancé).

### Story 2.4: Presets (boutons rapides caisse) — modèle BDD + API CRUD

En tant qu'admin ou développeur,
je veux une table `preset_buttons` et les endpoints CRUD + liste des actifs,
afin que l'écran caisse puisse charger les boutons rapides au démarrage.

**Prérequis :** Story 2.3 livrée (catégories).

**Critères d'acceptation :**

**Étant donné** la table `categories` existante  
**Quand** la migration crée `preset_buttons` (id, name, category_id FK nullable, preset_price, button_type, sort_order, is_active)  
**Alors** les endpoints fonctionnent : `GET /v1/presets`, `GET /v1/presets/active`, `GET /v1/presets/{id}`, `POST /v1/presets`, `PATCH /v1/presets/{id}`, `DELETE /v1/presets/{id}`  
**Et** `GET /v1/presets/active` retourne uniquement les presets is_active=true, triés par sort_order ; livrable = migration/copie 1.4.4 (artefact 08 §2.6, artefact 09 §3.12, audit caisse §1.3 Presets).

---

## Epic 3: Authentification, users, PIN, RBAC et démarrage des postes

Permettre aux utilisateurs de s'authentifier (JWT terrain, Paheko admin), à un admin de démarrer un poste (caisse ou réception), et aux opérateurs caisse d'utiliser un PIN pour déverrouiller la session ; le système restreint l'accès au menu caisse en mode caisse (écran verrouillé).

**Prérequis :** Epic 2 livré (sites + cash_registers nécessaires pour le démarrage de postes).

**Règle :** Livrable = migration/copie 1.4.4 pour auth, users, groups, permissions. Artefact 08 §2.1, artefact 09 §3.2/3.3, artefact 10 §4.

**FRs couverts :** FR4, FR5, FR14, FR15, FR16, FR17 (phase ultérieure).

### Human in the Loop — moments possibles

| # | Moment | Ce que l'agent a produit | Ton intervention |
|---|--------|---------------------------|------------------|
| **HITL-3.0** | Avant de lancer l'Epic 3 | — | **Optionnel** : confirmer que l'Epic 2 (référentiels) est OK. |
| **HITL-3.1** | Après Story 3.1 (users + JWT) | Login/logout, JWT. | **Optionnel** : valider la politique JWT (durée de vie token, refresh) si des choix ont été faits. |
| **HITL-3.2** | Après Story 3.2 (groupes/permissions) | Modèle RBAC, permissions API. | **Optionnel** : valider que la matrice RBAC (PRD) est bien implémentée. |
| **HITL-3.3** | Après Story 3.3 (PIN) | Gestion PIN, déverrouillage. | **Recommandé** : trancher la **politique PIN** (longueur min, blocage après X échecs, durée). |
| **HITL-3.4** | Après Story 3.4 (démarrage poste) | API démarrage poste caisse/réception. | **Optionnel** : valider le flux multi-sites (choix lieu/caisse) avant 3.5. |
| **HITL-3.5** | Après Story 3.5 (mode verrouillé) | Restriction menu caisse, routes masquées. | **Optionnel** : valider que la liste des écrans « caisse » est alignée avec la matrice RBAC. |

### Story 3.1: Users, JWT et gestion de compte (terrain)

En tant qu'opérateur terrain,
je veux me connecter à RecyClique avec un identifiant et un mot de passe et recevoir un token JWT,
afin d'accéder aux fonctionnalités selon mon rôle.

**Prérequis :** Epic 1 livré.

**Critères d'acceptation :**

**Étant donné** les tables users, user_sessions, login_history, registration_request créées par migration  
**Quand** je soumets mes identifiants à `POST /v1/auth/login`  
**Alors** l'API retourne un JWT (access token + refresh token) ; les requêtes avec le token sont reconnues (FR16)  
**Et** les endpoints de compte fonctionnent : logout, refresh, forgot-password, reset-password, PIN login (`POST /v1/auth/pin`) ; `GET/PUT /v1/users/me` (profil, password, PIN) ; secrets et config JWT en env (NFR-S2)  
**Et** livrable = migration/copie 1.4.4 (artefact 08 §2.1, artefact 09 §3.2/3.3, artefact 10 §4.1 à 4.6).

### Story 3.2: Groupes, permissions et RBAC

En tant qu'admin,
je veux pouvoir assigner des rôles et des permissions aux utilisateurs via des groupes,
afin de contrôler l'accès aux différentes fonctionnalités de l'application.

**Prérequis :** Story 3.1 livrée (users).

**Critères d'acceptation :**

**Étant donné** les tables groups, permissions, user_groups, group_permissions créées  
**Quand** un utilisateur possède les permissions requises et envoie son JWT  
**Alors** le middleware API valide le token **et** les permissions avant d'accéder à la ressource  
**Et** les endpoints d'admin groupes/permissions fonctionnent (`GET/POST/PUT/DELETE /v1/admin/groups`, `/v1/admin/permissions`) ; la matrice RBAC du PRD est implémentée (opérateur caisse, réception, responsable compta/admin, admin technique, bénévole)  
**Et** livrable = migration/copie 1.4.4 (artefact 08 §2.1).

### Story 3.3: Gestion des PIN opérateur caisse et déverrouillage de session

**HITL (recommandé)** : après livraison, valider la politique PIN (longueur min, blocage après X échecs) — voir HITL-3.3.

En tant qu'opérateur habilité à la caisse,
je veux avoir un code PIN personnel et pouvoir déverrouiller la session caisse en le saisissant,
afin que seul un opérateur autorisé puisse sortir du mode caisse.

**Prérequis :** Story 3.1 livrée (users + PIN).

**Critères d'acceptation :**

**Étant donné** une personne habilitée à la caisse avec un PIN configuré  
**Quand** le poste est en mode caisse verrouillé et que je saisis mon PIN correct  
**Alors** la session se déverrouille ; un PIN incorrect ne déverrouille pas (FR5, FR15)  
**Et** l'association PIN / utilisateur est gérée de façon sécurisée (hash, NFR-S3) ; livrable = migration/copie 1.4.4.

### Story 3.4: Démarrer un poste (caisse ou réception) avec un compte administrateur

En tant qu'administrateur,
je veux démarrer un poste de caisse ou de réception en sélectionnant le site et la caisse,
afin qu'un opérateur puisse ensuite utiliser ce poste.

**Prérequis :** Story 3.1 (auth) + Epic 2 stories 2.1 et 2.2 (sites + cash_registers).

**Critères d'acceptation :**

**Étant donné** un utilisateur avec rôle admin authentifié, et des sites + postes existants (Epic 2)  
**Quand** je demande l'ouverture d'un poste caisse ou réception pour un site/caisse donné  
**Alors** le poste est enregistré et l'état est disponible (FR14) ; l'action est tracée (audit_events)  
**Et** en multi-sites/multi-caisses, le site et la caisse sont correctement associés au poste ; livrable = migration/copie 1.4.4 (artefact 08 §2.2, artefact 09 §3.8, artefact 10 §5.1).

### Story 3.5: Mode caisse verrouillé — restriction du menu à la caisse uniquement

En tant qu'opérateur en poste caisse,
je veux que l'écran soit verrouillé sur le menu caisse uniquement tant que la session n'est pas déverrouillée par PIN,
afin de garantir que seules les actions caisse sont possibles sur ce poste.

**Prérequis :** Stories 3.3 (PIN) et 3.4 (poste démarré).

**Critères d'acceptation :**

**Étant donné** un poste en mode caisse actif  
**Quand** je navigue dans l'application sans avoir déverrouillé par PIN  
**Alors** seul le menu caisse est accessible ; les autres routes sont inaccessibles (FR4)  
**Et** le déverrouillage exige le PIN d'un opérateur habilité (Story 3.3) ; comportement cohérent avec la matrice RBAC ; livrable = migration/copie 1.4.4 (artefact 10 §5.1).

### Story 3.6: (Phase ultérieure) SSO RecyClique–Paheko — documentation et objectif

En tant qu'admin technique,
je veux une documentation pour le SSO entre RecyClique et Paheko,
afin de préparer l'authentification unifiée en phase ultérieure.

**Critères d'acceptation :**

**Étant donné** les choix d'auth actuels (JWT terrain, Paheko admin séparé)  
**Quand** le périmètre phase ultérieure inclut le SSO  
**Alors** un document décrit l'objectif, les options et les contraintes Paheko (FR17)  
**Et** cette story peut se limiter à la rédaction de la spec (pas d'implémentation en v1).

---

## Epic 4: Canal push Paheko

Configurer et rendre opérationnel le canal de communication RecyClique → Paheko : endpoint sécurisé, worker Redis Streams, retry sans perte. C'est le **pont technique** entre les deux systèmes ; il doit être opérationnel avant la première session de caisse.

**Prérequis :** Epic 1 livré (Redis opérationnel, Paheko joignable).  
**Parallèle possible :** Peut démarrer en parallèle de l'Epic 3 (ne dépend pas de l'auth).  
**Précondition Epic 5 :** Ce canal doit être opérationnel (story 4.2 livrée) avant la story 5.1 (Ouvrir session caisse avec push Paheko).

**FRs couverts :** FR19, FR20 (partiel).

### Human in the Loop — moments possibles

| # | Moment | Ton intervention |
|---|--------|-----------------|
| **HITL-4.0** | Avant de lancer l'Epic 4 | **Optionnel** : confirmer que Paheko est accessible depuis le réseau Docker (instance dev). |
| **HITL-4.1** | Après Story 4.2 (premier push réussi) | **Recommandé** : valider manuellement que le push d'un message test arrive bien dans Paheko et que la réponse est correcte avant d'enchaîner Epic 5. |

### Story 4.1: Configuration du canal push (endpoint, secret, résilience)

En tant qu'admin technique,
je veux configurer l'endpoint du plugin Paheko, le secret partagé et les paramètres de résilience,
afin que le worker puisse envoyer les tickets de façon sécurisée.

**Critères d'acceptation :**

**Étant donné** une instance RecyClique et Paheko déployées  
**Quand** je configure via `.env` l'URL du plugin, le secret et les options de retry  
**Alors** la config est chargée par `api/config/settings.py` (Pydantic Settings) ; aucun secret en clair dans les requêtes (NFR-S1, NFR-S2)  
**Et** la résilience (nb tentatives, backoff) est documentée (FR19).

### Story 4.2: Worker Redis Streams — consumer → plugin Paheko

En tant que système,
je veux un worker qui consomme la file Redis Streams et envoie les événements au plugin Paheko,
afin que chaque ticket de vente soit traité de façon résiliente.

**Prérequis :** Story 4.1 livrée.

**Critères d'acceptation :**

**Étant donné** une file Redis Streams configurée et le plugin Paheko accessible  
**Quand** un événement est publié dans la file (type `pos.ticket.created` ou similaire)  
**Alors** le worker le consomme, appelle le plugin Paheko (HTTPS, secret partagé) et ACK après succès (NFR-I1)  
**Et** en cas d'échec, le message reste en file et est repris selon la config retry (FR20) ; les erreurs sont loguées (niveau error + request_id)  
**Et** le worker démarre avec l'application (ou comme process séparé selon l'archi workers) ; sa santé est visible dans le health check.

---

## Epic 5: Caisse et synchronisation Paheko

Permettre à un opérateur habilité de gérer des sessions de caisse (ouverture avec fond de caisse, saisie des ventes, clôture avec comptage et contrôle), en multi-sites/multi-caisses, avec push par ticket vers Paheko et sync comptable à la clôture.

**Prérequis :**
- Epic 2 livrée (sites, cash_registers, catégories, presets)
- Epic 3 livrée (auth + postes démarrés + PIN + mode verrouillé)
- Epic 4 livrée (canal push opérationnel + HITL-4.1 validé)

**Règle :** Livrable = migration/copie 1.4.4. Artefact 08 §2.3, artefact 09 §3.6/3.7, artefact 10 §5, audit caisse 1.4.4.

**FRs couverts :** FR1, FR2, FR3, FR6, FR7, FR7b, FR11, FR20.

### Human in the Loop — moments possibles

| # | Moment | Ce que l'agent a produit | Ton intervention |
|---|--------|---------------------------|------------------|
| **HITL-5.0** | Avant de lancer l'Epic 5 | — | **Recommandé** : confirmer que les Epics 2, 3, 4 sont OK et que le canal push a été testé (HITL-4.1). |
| **HITL-5.1** | Après Story 5.1 (Sessions) | Ouverture session, multi-caisses. | **Optionnel** : valider le flux multi-caisses avant 5.2. |
| **HITL-5.2** | Après Story 5.2 (Ventes + push) | Tickets, lignes, paiements, premier push. | **Recommandé** : confirmer que le format payload et la réponse Paheko sont acceptables avant d'enchaîner 5.3. |
| **HITL-5.3** | Après Story 5.3 (Clôture) | Clôture, contrôle totaux, syncAccounting. | **Recommandé** : valider la **séquence clôture** avec un test manuel ou une démo avant de considérer l'Epic 5 « bouclée ». |
| **HITL-5.4** | Avant Story 5.4 (Hors ligne) | — | **Décision** : trancher si la saisie hors ligne est dans le périmètre v1 ou reportée. |

### Story 5.1: Ouverture et fermeture de session de caisse (multi-sites/multi-caisses)

En tant qu'opérateur caisse (poste démarré par un admin),
je veux ouvrir une session de caisse avec un fond de caisse pour un site/caisse donnés, et pouvoir la fermer,
afin de tenir une caisse par point de vente.

**Critères d'acceptation :**

**Étant donné** un poste caisse actif (Epic 3) et un site/caisse identifiés (Epic 2)  
**Quand** j'ouvre une session avec un montant de fond de caisse  
**Alors** la session est créée en BDD RecyClique (table `cash_sessions` : id, operator_id, register_id, site_id, initial_amount, status, opened_at) ; une session Paheko correspondante est créée via le plugin (canal push Epic 4) (FR1, FR6)  
**Et** les sessions sont listables (`GET /v1/cash-sessions`) et tracées (audit_events) ; chaque caisse a sa session ; livrable = migration/copie 1.4.4 (artefact 10 §5.2).

### Story 5.2: Enregistrement des ventes et push par ticket vers Paheko

En tant qu'opérateur caisse,
je veux enregistrer des ventes (tickets avec lignes et paiements multi-moyens) et que chaque ticket soit poussé automatiquement vers Paheko,
afin qu'aucun ticket ne soit perdu et que la compta reçoive les ventes sans double saisie.

**Prérequis :** Story 5.1 livrée (session ouverte) + Epic 2 (catégories, presets).

**Critères d'acceptation :**

**Étant donné** une session de caisse ouverte  
**Quand** j'ajoute des lignes à un ticket (catégorie, quantité, prix en centimes, poids éventuel) et je saisis un ou plusieurs paiements  
**Alors** le ticket et les lignes sont persistés en BDD RecyClique (tables `sales`, `sale_items`, `payment_transactions`) (FR2)  
**Et** le ticket est ajouté à la file Redis Streams ; le worker (Epic 4) consomme la file et envoie au plugin Paheko (HTTPS + secret) (FR7, NFR-S1, NFR-I1)  
**Et** le temps de réponse pour enregistrer une vente reste < 2 s en conditions normales (NFR-P1) ; en cas d'échec Paheko, retry sans perte (FR20) ; livrable = migration/copie 1.4.4 (artefact 08 §2.3, artefact 09 §3.6, artefact 10 §5.3).

### Story 5.3: Clôture de session (comptage physique, totaux, écart) et syncAccounting

En tant qu'opérateur caisse,
je veux clôturer ma session en saisissant le comptage physique et les totaux, et déclencher le contrôle et la sync comptable vers Paheko,
afin que la caisse soit bouclée et la compta à jour sans double saisie.

**Prérequis :** Story 5.2 livrée.

**Critères d'acceptation :**

**Étant donné** une session de caisse avec des tickets (certains poussés, d'autres en file)  
**Quand** je lance la clôture et saisis les totaux (closing_amount, actual_amount, variance_comment)  
**Alors** un contrôle des totaux RecyClique vs Paheko est effectué ; la sync comptable (syncAccounting) est déclenchée côté Paheko ; la session est marquée clôturée (FR3, FR11)  
**Et** l'opérateur n'est pas bloqué plus de 10 s ; push et sync en arrière-plan (NFR-P2) ; écritures compta respectent la config Paheko (NFR-I2) ; livrable = migration/copie 1.4.4 (artefact 10 §5.4).

### Story 5.4: (Optionnel v1) Saisie caisse hors ligne et synchronisation au retour

**HITL (décision) :** trancher si cette story est dans le périmètre v1 ou reportée — voir HITL-5.4.

En tant qu'opérateur caisse,
je veux pouvoir enregistrer des ventes en local quand le réseau est indisponible, puis synchroniser les tickets vers Paheko au retour en ligne,
afin de ne pas bloquer la vente en cas de coupure.

**Critères d'acceptation :**

**Étant donné** un frontend avec buffer local (ex. IndexedDB) et une file Redis Streams côté backend  
**Quand** le frontend est hors ligne, je continue à saisir des ventes ; au retour en ligne, les tickets sont envoyés  
**Alors** les tickets sont bien en file et traités comme en Story 5.2 ; aucune perte de donnée (FR7b)  
**Et** si reporté, la story est marquée optionnelle ou déplacée en post-v1.

---

## Epic 6: Réception et flux matière

Permettre à un opérateur d'ouvrir un poste de réception, de créer des tickets de dépôt et de saisir des lignes (poids, catégorie, destination). La réception reste source de vérité matière/poids dans RecyClique, sans sync manuelle obligatoire vers Paheko.

**Prérequis :**
- Epic 2 story 2.3 livrée (catégories)
- Epic 3 story 3.4 livrée (démarrage poste réception)

**Note :** Epic 6 peut démarrer en parallèle d'Epic 5 (pas de dépendance sur le canal push ni sur la caisse).

**Règle :** Livrable = migration/copie 1.4.4. Artefact 08 §2.4, artefact 09 §3.10, artefact 10 §6, audit réception 1.4.4.

**FRs couverts :** FR8, FR9, FR10.

### Human in the Loop — moments possibles

| # | Moment | Ton intervention |
|---|--------|-----------------|
| **HITL-6.0** | Avant de lancer l'Epic 6 | **Optionnel** : confirmer que l'Epic 3 (poste réception) est OK. |
| **HITL-6.1** | Après Story 6.1 ou 6.2 | **Optionnel** : valider les listes de valeurs (catégories, destinations) avant de figer l'UI. |

### Story 6.1: Ouverture de poste de réception et création de tickets de dépôt

En tant qu'opérateur réception (poste démarré par un admin),
je veux ouvrir un poste de réception et créer des tickets de dépôt,
afin d'enregistrer les entrées matière de façon traçable.

**Critères d'acceptation :**

**Étant donné** un utilisateur autorisé avec un poste réception actif (Epic 3)  
**Quand** j'ouvre un poste de réception et je crée un nouveau ticket de dépôt  
**Alors** le poste (`poste_reception`) et le ticket (`ticket_depot`) sont enregistrés en BDD RecyClique (FR8) ; le ticket est listable via `GET /v1/reception/tickets`  
**Et** aucune sync manuelle vers Paheko n'est requise (FR10) ; livrable = migration/copie 1.4.4 (artefact 10 §6.1/6.2).

### Story 6.2: Saisie des lignes de réception (poids, catégorie, destination)

En tant qu'opérateur réception,
je veux saisir sur chaque ticket des lignes avec poids (kg), catégorie et destination,
afin que les flux matière soient disponibles pour les déclarations et le suivi.

**Critères d'acceptation :**

**Étant donné** un ticket de dépôt ouvert  
**Quand** j'ajoute des lignes avec poids_kg, category_id et destination  
**Alors** les lignes (`ligne_depot`) sont persistées en BDD RecyClique (FR9, FR10)  
**Et** les données sont disponibles pour exports ou déclarations ; bonnes pratiques accessibilité (NFR-A1) ; livrable = migration/copie 1.4.4 (artefact 08 §2.4, artefact 10 §6.4).

### Story 6.3: Export CSV et stats live réception

En tant qu'opérateur ou admin réception,
je veux exporter les données d'un ticket en CSV et consulter les KPI réception en temps réel,
afin de suivre les flux matière sans quitter RecyClique.

**Critères d'acceptation :**

**Étant donné** des tickets et lignes de réception existants  
**Quand** je clique « Export CSV » sur un ticket ou les lignes d'une période  
**Alors** le fichier est généré et téléchargeable (`POST /v1/reception/tickets/{id}/download-token`, `GET .../export-csv`, `GET /v1/reception/lignes/export-csv`)  
**Et** `GET /v1/reception/stats/live` retourne les KPI de réception en temps réel ; livrable = migration/copie 1.4.4 (artefact 09 §3.10, artefact 10 §6.5).

---

## Epic 7: Correspondance et mapping RecyClique ↔ Paheko

Configurer le mapping entre les référentiels RecyClique (moyens de paiement, catégories, sites) et leurs équivalents Paheko, pour que les pushes caisse produisent les bonnes écritures comptables. **Chantier de découverte et de décisions métier — HITL obligatoires avant les stories 7.1 et 7.2.**

**Prérequis :** Epic 5 tournant + BDD RecyClique et instance Paheko stabilisées (condition pour les HITL).

**FRs couverts :** FR13b.

### Contexte — chantier correspondance (pas entièrement automatisable)

Pour que RecyClique pousse correctement vers Paheko, il faut décider des options Paheko à activer et figer les correspondances (champs, règles) avant d'implémenter les stories 7.1 et 7.2. Ce travail de découverte produit inventaires et matrices, mais les **choix** (config par défaut, arbitrages mapping) doivent être validés par Strophe ou l'analyste.

**Ressources à charger pour les sessions correspondance :**
- `references/migration-paeco/audits/matrice-correspondance-caisse-poids.md`
- `references/migration-paeco/audits/` (audits caisse et réception Paheko)
- `references/dumps/schema-paheko-dev.md`, `references/dumps/schema-recyclic-dev.md`
- `references/artefacts/2026-02-25_05_grille-confrontation-recyclic-paheko.md`
- `references/artefacts/2026-02-25_08_session-confrontation-recyclic-paheko.md`

### Human in the Loop — moments **obligatoires**

| # | Moment | Ce que l'agent a produit | Ton intervention |
|---|--------|---------------------------|------------------|
| **HITL-7.0** | Avant de lancer l'Epic 7 | — | **Décider** si le chantier découverte est à faire maintenant : lancer une session (agent + toi) pour inventaire Paheko et mise à jour de la matrice. |
| **HITL-7.1** | Après inventaire / première matrice | Inventaire des options Paheko, tableau des champs et workflows. | **Valider** les options Paheko à activer en v1 et **trancher les configs par défaut** (moyens de paiement, catégories par défaut, emplacements). |
| **HITL-7.2** | Après matrice détaillée (correspondance champs) | Matrice ou doc : RecyClique → Paheko champ par champ. | **Valider** les décisions de mapping. Signer pour figer le périmètre v1. |
| **HITL-7.3** | Avant de créer stories 7.1 et 7.2 | Spec « Config Paheko par défaut + correspondance » complète. | **Valider** que la spec est complète et donner le feu vert pour l'implémentation. |

**Résumé :** Ne pas enchaîner 7.1 et 7.2 en automatique sans avoir franchi HITL-7.1, 7.2 et 7.3.

### Story 7.1: Modèle et stockage du mapping RecyClique ↔ Paheko

**Prérequis HITL :** HITL-7.1, 7.2, 7.3 franchis (décisions mapping figées).

En tant qu'admin technique ou responsable compta,
je veux que le système gère un mapping configurable entre les référentiels RecyClique et leurs équivalents Paheko,
afin que le push caisse produise les bonnes écritures compta.

**Critères d'acceptation :**

**Étant donné** la spec de correspondance validée (HITL-7.3)  
**Quand** le périmètre exact du mapping est figé (moyens de paiement, catégories, sites/emplacements)  
**Alors** les entités ou tables de mapping existent en BDD avec les champs de correspondance Paheko  
**Et** les données peuvent être créées/mises à jour via API ; la config Paheko reste la référence (NFR-I2, FR13b).

### Story 7.2: Interface ou API d'administration du mapping

**Prérequis HITL :** idem Story 7.1.

En tant qu'admin ou responsable compta,
je veux consulter et modifier le mapping via une interface ou une API RecyClique,
afin de configurer à l'avance tout ce qui est nécessaire pour la sync caisse.

**Critères d'acceptation :**

**Étant donné** le modèle de mapping (Story 7.1)  
**Quand** j'accède à l'écran ou à l'API d'administration du mapping  
**Alors** je peux lister et éditer les correspondances (RecyClique → Paheko)  
**Et** les modifications sensibles sont tracées (audit_events) ; périmètre documenté dans la story.

---

## Epic 8: Administration, compta v1 et vie associative

Permettre l'administration complète de l'application (utilisateurs, sites, postes, sessions, rapports, paramètres, BDD) ; accès compta via Paheko en v1 ; placeholders vie associative.

**Prérequis :** Toutes les couches précédentes (Epics 2 à 6 au minimum).

**Note :** Les APIs de base (users, sites, cash_registers, categories) sont déjà en place (Epics 2 et 3). Cet epic ajoute les **interfaces admin complètes** (import/export catégories, gestion groupes, rapports, etc.) et les **écrans admin complexes**.

**Règle :** Livrable = migration/copie 1.4.4. Artefact 10 §7.

**FRs couverts :** FR12, FR21.

### Human in the Loop — moments possibles

| # | Moment | Ton intervention |
|---|--------|-----------------|
| **HITL-8.0** | Avant de lancer l'Epic 8 | **Optionnel** : confirmer que caisse (Epic 5) et réception (Epic 6) sont en place. |
| **HITL-8.1** | Après Story 8.1 (users admin complet) | **Optionnel** : valider le niveau de détail des écrans admin. |
| **HITL-8.2** | Après Story 8.3 (placeholders vie asso) | **Optionnel** : valider le niveau de détail des placeholders. |

### Story 8.1: Administration complète des utilisateurs

En tant qu'admin,
je veux les écrans complets d'administration des utilisateurs (liste, détail, pending, approve/reject, groupes, audit),
afin de gérer les accès à RecyClique.

**Critères d'acceptation :**

**Étant donné** les APIs users/groups/permissions existantes (Epic 3)  
**Quand** j'accède à `/admin/users`  
**Alors** les écrans de liste, détail, pending, approve/reject, changement rôle/statut/groupes, reset password/PIN sont opérationnels  
**Et** livrable = migration/copie 1.4.4 (artefact 10 §7.2/7.3).

### Story 8.2: Administration sites, postes, sessions et rapports caisse

En tant qu'admin,
je veux les écrans complets d'administration des sites, des postes de caisse, du gestionnaire de sessions et des rapports caisse,
afin de piloter les opérations de caisse et d'accéder aux rapports.

**Critères d'acceptation :**

**Étant donné** les APIs sites/cash-registers/cash-sessions existantes (Epics 2 et 5)  
**Quand** j'accède aux écrans admin correspondants  
**Alors** la gestion sites, postes (CRUD), gestionnaire de sessions (filtres, pagination), rapports par session et export bulk sont opérationnels  
**Et** livrable = migration/copie 1.4.4 (artefact 10 §7.4/7.5/7.6/7.7).

### Story 8.3: Import/export catégories et admin avancé

En tant qu'admin,
je veux importer et exporter des catégories (CSV) et accéder à l'interface d'administration avancée des catégories,
afin de gérer facilement le référentiel EEE/décla.

**Critères d'acceptation :**

**Étant donné** la table `categories` existante (Epic 2) et les endpoints de base  
**Quand** j'accède à l'écran admin catégories  
**Alors** les actions import/export CSV (template, analyze, execute), hard delete, restauration et breadcrumb sont opérationnelles  
**Et** livrable = migration/copie 1.4.4 (artefact 10 §8.1).

### Story 8.4: Réception admin, santé, audit log, logs email, paramètres

En tant qu'admin,
je veux les écrans de réception admin (stats, rapports, tickets), santé, audit log, logs email et paramètres,
afin de surveiller l'instance et de configurer les seuils.

**Critères d'acceptation :**

**Étant donné** les APIs correspondantes existantes  
**Quand** j'accède aux sections admin réception, santé, audit, logs et paramètres  
**Alors** tous les écrans listés dans l'artefact 10 §7.8/7.9 sont opérationnels  
**Et** livrable = migration/copie 1.4.4.

### Story 8.5: BDD (export, purge, import) et import legacy

En tant qu'admin technique,
je veux les actions BDD (export, purge, import) et l'interface d'import legacy CSV,
afin de maintenir et migrer les données.

**Critères d'acceptation :**

**Étant donné** les permissions super-admin  
**Quand** j'utilise les actions BDD  
**Alors** export, purge transactions et import fonctionnent ; l'interface import legacy (analyze, execute, validate, preview) est opérationnelle  
**Et** livrable = migration/copie 1.4.4 (artefact 10 §7.10) ; scope import legacy à confirmer produit.

### Story 8.6: Accès et documentation pour l'administration compta via Paheko (v1)

En tant que responsable compta,
je veux savoir comment accéder à l'interface Paheko pour administrer la compta en v1,
afin de faire la compta pendant que les interfaces RecyClique ne sont pas encore disponibles.

**Critères d'acceptation :**

**Étant donné** une instance avec RecyClique et Paheko déployés et la caisse synchronisée (Epic 5)  
**Quand** je consulte la documentation ou l'aide RecyClique  
**Alors** l'accès à l'interface Paheko pour la compta est documenté (URL, rôle requis) (FR12)  
**Et** un lien ou une redirection depuis RecyClique peut être ajouté si pertinent.

### Story 8.7: Écrans ou placeholders « vie associative » dans RecyClique

En tant qu'utilisateur (ex. bénévole),
je veux accéder à des écrans ou placeholders « vie associative » depuis RecyClique,
afin d'avoir un point d'entrée unique sans ouvrir Paheko.

**Critères d'acceptation :**

**Étant donné** un utilisateur connecté avec accès vie asso  
**Quand** je navigue vers la section vie associative  
**Alors** des écrans ou placeholders sont affichés (FR21) ; le parcours complet sera déroulé en growth.

---

## Epic 9: Données déclaratives et éco-organismes

Permettre au système de produire et conserver les données déclaratives (poids, flux, catégories, périodes) dans RecyClique pour les déclarations éco-organismes.

**Prérequis :** Epic 5 (flux ventes caisse) + Epic 6 (flux réception/poids).

**FRs couverts :** FR22, FR23 (post-MVP).

### Human in the Loop — moments possibles

| # | Moment | Ton intervention |
|---|--------|-----------------|
| **HITL-9.0** | Avant de lancer l'Epic 9 | **Recommandé** : valider le **périmètre déclaratif v1** (champs, périodes, alignement éco-organismes) avant de modéliser. |

### Story 9.1: Modèle et persistance des données déclaratives

**HITL (recommandé)** : valider le périmètre déclaratif v1 avant ou au début de cette story — voir HITL-9.0.

En tant que système,
je veux stocker les données nécessaires aux déclarations éco-organismes dans RecyClique,
afin qu'elles soient la source de vérité pour les déclarations officielles.

**Critères d'acceptation :**

**Étant donné** les flux réception et caisse opérationnels (Epics 5, 6) et les catégories mappées (Epic 2)  
**Quand** des données déclaratives sont produites (agrégats par période, catégorie, flux)  
**Alors** elles sont persistées en BDD RecyClique (tables ou vues dédiées) ; exports ou requêtes pour déclarations possibles (FR22)  
**Et** traçabilité et périmètre documentés.

### Story 9.2: (Post-MVP) Module décla éco-organismes

En tant que responsable,
je veux utiliser un module RecyClique dédié aux déclarations éco-organismes,
afin de produire les déclarations officielles sans quitter RecyClique.

**Critères d'acceptation :**

**Étant donné** les données déclaratives (Story 9.1) et le périmètre post-MVP  
**Quand** le module décla est activé  
**Alors** je peux exporter ou soumettre les données selon le format attendu (FR23)  
**Et** la story est marquée post-MVP.

---

## Epic 10: Extension points et évolution

Exposer des points d'extension (LayoutConfigService, VisualProvider) avec implémentations stub en v1 pour brancher ultérieurement affichage dynamique et service Peintre (JARVOS Mini). Peut démarrer en parallèle de n'importe quelle couche une fois le frontend structuré.

**Prérequis :** Epic 1 livré (structure frontend en place).

**FRs couverts :** FR26, FR27 (post-MVP).

### Human in the Loop — moments possibles

| # | Moment | Ton intervention |
|---|--------|-----------------|
| **HITL-10.0** | Avant de lancer l'Epic 10 | **Optionnel** : confirmer que la recherche technique Peintre est à jour. |

### Story 10.1: Interfaces et stubs LayoutConfigService / VisualProvider (v1)

En tant que développeur ou intégrateur,
je veux des interfaces (LayoutConfigService, VisualProvider) et des implémentations stub dans le frontend,
afin de brancher plus tard l'affichage dynamique et le service Peintre sans refonte majeure.

**Critères d'acceptation :**

**Étant donné** la structure frontend (Epic 1)  
**Quand** le code est en place  
**Alors** les interfaces LayoutConfigService et VisualProvider existent et sont utilisables par les modules ; des stubs sont livrés en v1 (FR26)  
**Et** la structure et les slots permettent d'ajouter des implémentations réelles plus tard ; référence : `_bmad-output/planning-artifacts/research/technical-affichage-dynamique-peintre-extension-points-research-2026-02-25.md`.

### Story 10.2: (Post-MVP) Fonds documentaire RecyClique

En tant qu'organisation,
je veux gérer un fonds documentaire RecyClique (statutaire, com, prise de notes) distinct de la compta/factures Paheko,
afin de centraliser la doc et préparer l'évolution JARVOS Nano/Mini.

**Critères d'acceptation :**

**Étant donné** la politique fichiers (artefact 2026-02-25_02) et le périmètre post-MVP  
**Quand** le fonds documentaire est implémenté  
**Alors** le stockage (volume dédié ou K-Drive) et la frontière avec Paheko sont définis (FR27)  
**Et** la story est post-MVP.
