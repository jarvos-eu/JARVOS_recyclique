# Sprint Change Proposal — Correction de cap Epic 2 et alignement vision architecturale

**Date :** 2026-02-26  
**Workflow :** Correct Course (4-implementation)  
**Projet :** JARVOS_recyclique  
**Mode :** Incrémental (validation section par section)

---

## 1. Résumé du problème

### 1.1 Déclencheur

L'**Epic 2 (Authentification et contrôle d'accès)** a connu une dérive sur les stories 2.1 et 2.2 :

- La **story 2.2** (« Démarrer un poste caisse ou réception pour un lieu/caisse donné ») supposait l'existence des référentiels **sites** et **postes de caisse** sans qu'aucune story ne les livre.
- Les stories étaient rédigées en mode **greenfield** alors que le projet est un **refactor brownfield** (RecyClique 1.4.4, checklist import).

Un **revert** des stories 2.1 et 2.2 (et du code Epic 1 par sécurité) a été effectué. Un travail de **triage conceptuel** a ensuite été mené pour combler l'absence de vision architecturale : à quoi sert l'API RecyClique, qui stocke quoi (RecyClique vs Paheko), et quelle logique derrière chaque écran.

### 1.2 Contexte de découverte

- **Quand / comment** : pendant l'implémentation de l'Epic 2, constat que « démarrer un poste caisse » exige des entités (sites, cash_registers) non encore livrées.
- **Preuves** : artefacts de triage datés du 26 février 2026 (catalogue qui stocke quoi, périmètre API v1, traçabilité écran → données + appels API) constituent désormais la référence pour la conception avant de recoder.

### 1.3 Livrables du triage (nouvelle base de conception)

| Référence | Fichier | Rôle |
|-----------|---------|------|
| **Artefact 08** | `references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md` | Pour chaque entité métier : où sont stockées les données (RecyClique / Paheko / les deux), qui est source de vérité. Synthèse « qui crée / qui lit ». |
| **Artefact 09** | `references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md` | Liste des endpoints v1 par domaine ; source des données ; cas « RecyClique appelle Paheko » (ouverture session, vente, clôture). |
| **Artefact 10** | `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` | Pour 29 écrans/flux : route(s), permissions, données affichées, appels API au chargement, actions utilisateur → endpoint + payload. |

---

## 2. Analyse d'impact

### 2.1 Impact sur les epics

| Epic | Impact | Détail |
|------|--------|--------|
| **Epic 2** | **Fort** | Stories 2.1 et 2.2 à réécrire ou découper ; référentiel sites + cash_registers à livrer avant « Démarrer un poste caisse ». Références explicites aux artefacts 08, 09, 10 et à la checklist import. |
| **Epic 4** (Caisse) | **Moyen** | Dépend de l'Epic 2 et du référentiel sites/cash_registers. Stories à lier aux artefacts et à l'audit caisse 1.4.4. |
| **Epic 5** (Réception) | **Moyen** | Lier aux artefacts et à l'audit réception 1.4.4 ; postes de réception sans dépendance sites en BDD (artefact 10). |
| **Epic 6** (Admin) | **Moyen** | Écrans admin (sites, postes caisse) déjà décrits dans traçabilité ; cohérence avec périmètre API v1. |
| **Epics 1, 3, 7, 8** | **Faible** | Ajout de références aux artefacts et règle refactor dans les sections concernées. |

### 2.2 Impact sur les stories

- **Story 2.1** : à conserver (JWT) avec précision que les utilisateurs terrain sont en RecyClique (artefact 08). Référence à la checklist import pour tout code issu de 1.4.4.
- **Story 2.2** : soit **découper** en 2.2a (référentiel sites + cash_registers), 2.2b (ouverture session caisse), 2.2c (ouverture poste réception) ; soit ajouter une **story dédiée** (ex. 2.0 ou 2.1bis) « Référentiel minimal sites + postes de caisse » **avant** la story actuelle 2.2.
- **Stories caisse / réception / admin** : indiquer pour chaque story métier le livrable = **migration/copie** depuis 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md`, et les références 1.4.4 (audits, liste endpoints, data-models-api).

### 2.3 Conflits avec les artefacts

| Artifact | Conflit | Action proposée |
|----------|---------|------------------|
| **PRD** | Périmètre API v1 et utilisateurs terrain en RecyClique déjà cohérents ; libellés à renforcer. | Ajouter en Références projet les artefacts 08, 09, 10 ; mention explicite « migration/copie 1.4.4 » dans Product Scope / Implementation Considerations. |
| **Architecture** | Déjà alignée (sources de vérité, API REST). | Ajouter référence aux artefacts 08, 09, 10 dans Project Context ou Références. |
| **epics.md** | Pas de référence aux artefacts ni règle refactor ; trou du référentiel lieu/caisse. | Modifications détaillées en section 4. |
| **UX** | Traçabilité écran → API (artefact 10) complète la spec UX. | Référencer l'artefact 10 dans la spec UX (section Références ou Périmètre écrans). |

### 2.4 Impact technique

- **Code** : aucun changement de code dans cette proposition ; uniquement mise à jour des artéfacts de planification (epics.md, éventuellement PRD/architecture).
- **Déploiement** : inchangé.
- **BDD** : les modèles sites et cash_registers sont déjà décrits dans le catalogue (artefact 08) et la liste endpoints (artefact 09) ; leur création relève d'une story dédiée avant 2.2.

---

## 3. Approche recommandée

### 3.1 Option retenue : **Ajustement direct** (modifier/ajouter des stories et des références)

- **Direct Adjustment** : modifier et compléter `epics.md` (références aux artefacts 08, 09, 10 ; règle refactor ; story ou sous-stories pour le référentiel sites + cash_registers). Ajuster si besoin le PRD et l'architecture (références et libellés).
- **Pas de rollback** supplémentaire : le revert est déjà fait.
- **Pas de réduction de scope MVP** : le périmètre reste parité 1.4.4 + sync.

### 3.2 Justification

- Effort **modéré** (rédaction et mise à jour de documents).
- Risque **faible** : les décisions sont figées dans les artefacts 08, 09, 10.
- Alignement immédiat de la planification avec la vision architecturale et la règle brownfield (checklist import).
- Évite qu'une future story suppose à nouveau un référentiel non livré.

### 3.3 Effort et risques

- **Effort** : Moyen (1 à 2 h de mise à jour ciblée des artéfacts).
- **Risque** : Faible.
- **Impact planning** : réordonnancement léger des stories Epic 2 (et dépendances Epic 4) ; pas de report de livraison majeur si les stories sont bien découpées.

---

## 4. Propositions de modifications détaillées

### 4.1 Modifications de `_bmad-output/planning-artifacts/epics.md`

#### 4.1.1 Entrée de document : références aux artefacts 08, 09, 10

**Emplacement :** En tête du document (après l'Overview ou dans la section « Décisions architecturales de référence »).

**Action :** Ajouter un bloc **« Références vision architecturale (triage 2026-02-26) »** :

- `references/artefacts/2026-02-26_08_catalogue-qui-stocke-quoi-recyclic-paheko.md` — qui stocke quoi (RecyClique vs Paheko), source de vérité.
- `references/artefacts/2026-02-26_09_perimetre-api-recyclique-v1.md` — périmètre API v1, endpoints, cas RecyClique → Paheko.
- `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` — écran → données, appels API, actions.

À utiliser pour toute story touchant au métier caisse, réception, auth, admin, catégories.

#### 4.1.2 Règle refactor brownfield

**Emplacement :** Section « Décisions architecturales de référence (v0.1) » ou nouvelle section **« Refactor reference »**.

**Texte proposé :**

- Pour toute story qui touche au métier **caisse, réception, auth, admin** : indiquer la **référence 1.4.4** (fichiers dans `references/ancien-repo/` et `references/migration-paeco/audits/`) et préciser que le **livrable = migration/copie** selon `references/ancien-repo/checklist-import-1.4.4.md`.
- Optionnel : tenir une **liste des référentiels** (sites, cash_registers, catégories, etc.) et de la **story qui les livre en premier**, pour éviter qu'une story suppose un référentiel non encore livré.

#### 4.1.3 Corriger le trou du référentiel lieu/caisse (Epic 2)

**Option A (recommandée) :** Ajouter une **story dédiée** avant la story actuelle 2.2 :

- **ID suggéré :** 2.1bis ou 2.0.
- **Titre :** « Référentiel minimal sites + postes de caisse (modèles + API, aligné 1.4.4) ».
- **Contenu :** Modèles et API pour `sites` et `cash_registers` (CRUD minimal) ; alignement sur 1.4.4 (audit caisse, liste endpoints v1.4.4, data-models-api). Références explicites : artefact 08, artefact 09 (sections Sites, Postes de caisse), `references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md`.
- **Critères d'acceptation :** Endpoints GET/POST/PATCH/DELETE pour `/v1/sites` et `/v1/cash-registers` ; tables `sites`, `cash_registers` en BDD RecyClique ; livrable = migration/copie selon checklist import 1.4.4.

**Option B :** Découper la story 2.2 actuelle en sous-stories :

- **2.2a** — Référentiel sites + cash_registers (modèles + API), avec références 1.4.4 (audit caisse, liste endpoints).
- **2.2b** — Ouverture session caisse (pour un lieu/caisse donné), avec références artefact 09 (POST cash-sessions), artefact 10 (écran Ouverture session).
- **2.2c** — Ouverture poste réception, avec références artefact 10 (Ouverture poste réception).

Chaque sous-story indique **livrable = migration/copie** selon `references/ancien-repo/checklist-import-1.4.4.md`.

#### 4.1.4 Stories Epic 2 existantes : ajout des références

- **Story 2.1 (JWT) :** Ajouter que les utilisateurs terrain sont stockés en RecyClique (artefact 08) ; référence checklist import pour tout code auth issu de 1.4.4.
- **Story 2.2 (actuelle), si non découpée :** Ajouter prérequis « Story 2.0 ou 2.1bis livrée (référentiel sites + cash_registers) » ; références artefact 09 (cash-sessions, cash-registers), artefact 10 (Dashboard caisses, Ouverture session), audit caisse 1.4.4.
- **Stories 2.3 à 2.5 :** Ajouter référence aux artefacts 08, 10 lorsque pertinent (ex. 2.3 PIN, 2.4 mode verrouillé).

#### 4.1.5 Epics 4, 5, 6 : références dans les sections concernées

- **Epic 4 (Caisse) :** En tête d'épic et dans les stories 4.1 à 4.5 : références à l'artefact 08 (sessions, ventes, push), artefact 09 (endpoints sales, cash-sessions, close), artefact 10 (écrans caisse), `references/migration-paeco/audits/audit-caisse-recyclic-1.4.4.md`, checklist import. Préciser **livrable = migration/copie** selon checklist.
- **Epic 5 (Réception) :** Références artefact 08, 09, 10 (réception), `references/migration-paeco/audits/audit-reception-poids-recyclic-1.4.4.md`, checklist import. Livrable = migration/copie.
- **Epic 6 (Admin) :** Références artefact 10 (écrans admin : sites, postes caisse, utilisateurs, etc.), artefact 09 (admin), checklist import.

#### 4.1.6 Liste des référentiels et story « qui livre en premier » (optionnel)

**Emplacement :** Nouvelle sous-section en tête d'epics.md ou dans « Refactor reference ».

**Contenu suggéré :**

| Référentiel | Story qui livre en premier |
|-------------|-----------------------------|
| Sites | 2.0 / 2.1bis ou 2.2a |
| Postes de caisse (cash_registers) | 2.0 / 2.1bis ou 2.2a |
| Catégories | Epic 3 ou story dédiée catégories (à préciser selon ordre de priorité) |
| Presets | Story caisse (Epic 4) ou admin (à trancher) |
| Utilisateurs terrain | Story 2.1 (JWT) + modèle users déjà en RecyClique (artefact 08) |

---

### 4.2 Modifications éventuelles du PRD (`_bmad-output/planning-artifacts/prd.md`)

- **Section Références projet :** Ajouter les trois artefacts 08, 09, 10 avec une courte description (catalogue qui stocke quoi ; périmètre API v1 ; traçabilité écran → API).
- **Product Scope / Implementation Considerations :** Renforcer la phrase sur l'import 1.4.4 : « À chaque pioche dans le code 1.4.4, appliquer la checklist `references/ancien-repo/checklist-import-1.4.4.md` (copy + consolidate + security) ; le livrable des stories métier caisse/réception/auth/admin est une **migration/copie** depuis 1.4.4, pas une conception from scratch. »

---

### 4.3 Modifications éventuelles de l'architecture (`_bmad-output/planning-artifacts/architecture.md`)

- **Project Context Analysis ou Références :** Ajouter les artefacts 08, 09, 10 comme documents de référence pour la répartition des données (RecyClique vs Paheko) et le périmètre API v1.

---

### 4.4 Modifications éventuelles de la spec UX (`_bmad-output/planning-artifacts/ux-design-specification.md`)

- **Section Références ou Périmètre des écrans :** Référencer `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` comme traçabilité détaillée écran → données + appels API pour le refactor.

---

## 4bis. Exécution — Refonte complète d'epics.md (2026-02-26)

Suite à la validation du brief de révision (`references/artefacts/2026-02-26_11_brief-revision-ordre-construction.md`), `epics.md` a été **entièrement refondu** avec la structure suivante :

| Epic | Titre | Statut |
|------|-------|--------|
| Epic 1 | Socle technique et déploiement | ✅ Inchangé (LIVRÉ) |
| Epic 2 | **Référentiels métier** (Sites, Postes, Catégories, Presets) | NOUVEAU |
| Epic 3 | Authentification, users, PIN, RBAC et démarrage des postes | Restructuré (ex-Epic 2) |
| Epic 4 | **Canal push Paheko** (config + worker Redis Streams) | NOUVEAU/EXTRAIT |
| Epic 5 | Caisse et synchronisation Paheko | Restructuré (ex-Epic 4, prérequis enrichis) |
| Epic 6 | Réception et flux matière | Restructuré (ex-Epic 5) |
| Epic 7 | Correspondance et mapping RecyClique ↔ Paheko | Restructuré (ex-Epic 3 stories 3.2+3.3) |
| Epic 8 | Administration, compta v1 et vie associative | Restructuré (ex-Epic 6, étendu) |
| Epic 9 | Données déclaratives et éco-organismes | Restructuré (ex-Epic 7) |
| Epic 10 | Extension points et évolution | Restructuré (ex-Epic 8) |

**Ajouts transversaux :**
- Section « Ordre de construction — couches de dépendances »
- Section « Règle refactor brownfield » avec table de références 1.4.4 par domaine
- Section « Table des référentiels — story de livraison » (qui livre quoi en premier)
- Références artefacts 08, 09, 10 dans toutes les epics/stories concernées
- Prérequis explicites dans chaque epic et chaque story critique
- **SSO RecyClique ↔ Paheko** : prévu en **phase ultérieure** ; story **Epic 3 — 3.6** (documentation et objectif) pour préparer l'authentification unifiée (FR17) ; pas d'implémentation en v1, spec à rédiger pour v0.2+.

---

## 5. Handoff pour la suite

### 5.1 Périmètre du changement

- **Minor / Moderate :** Les modifications sont limitées aux **artéfacts de planification** (epics.md, et optionnellement PRD, architecture, UX). Aucun code à modifier dans cette étape.
- **Classification proposée :** **Moderate** — réorganisation des stories et ajout de références ; impact sur le backlog et l'ordre d'exécution des stories Epic 2  (nouvelle structure en 10 epics, Epic 2 = Référentiels en premier).

### 5.2 Responsables

- **Application des modifications à epics.md (et PRD/architecture/UX) :** Strophe ou un agent (Cursor/BMAD) avec instruction de suivre ce Sprint Change Proposal à la lettre.
- **Validation finale :** Strophe (approbation du document et des édits à appliquer).

### 5.3 Critères de succès

- [ ] Le trou du référentiel lieu/caisse est comblé (Epic 2 Référentiels métier, stories 2.1 Sites et 2.2 Postes de caisse).
- [ ] Les stories Epic 2, 3, 5, 6, 7, 8 concernées indiquent les références 1.4.4 et checklist import où pertinent.
- [ ] Liste des référentiels et story « qui livre en premier » ajoutée (table en tête d'epics.md).
- [ ] Optionnel : PRD, architecture, UX mis à jour avec les références aux artefacts 08, 09, 10.

### 5.4 Prochaines étapes

1. **Valider** ce Sprint Change Proposal (oui / non / réviser). ✅ **Approuvé** (2026-02-26) sous réserve mention SSO — SSO RecyClique ↔ Paheko inclus en phase ultérieure (Epic 3 Story 3.6, documentation et objectif).
2. **Appliquer** les modifications à `epics.md` (effectuée le 2026-02-26 — refonte complète en 10 epics).
3. **Reprendre** le développement à partir de l'**Epic 2** (Référentiels métier), story **2.1 (Sites)**, puis 2.2, 2.3, 2.4, puis **Epic 3** story **3.1 (Users + JWT)**, etc., selon l'ordre de construction en tête d'epics.md.
4. **Tracer** dans le suivi projet que la correction de cap a été appliquée (date, document de référence : ce fichier).

---

*Document généré par le workflow Correct Course (4-implementation).*
