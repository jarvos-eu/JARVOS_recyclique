# Implementation Readiness Assessment Report

**Date:** 2026-02-26
**Project:** JARVOS_recyclique

---
stepsCompleted: [step-01-document-discovery, step-02-prd-analysis, step-03-epic-coverage-validation, step-04-ux-alignment, step-05-epic-quality-review, step-06-final-assessment]
filesIncluded:
  prd: prd.md
  architecture: architecture.md
  epics: epics.md
  ux: ux-design-specification.md
---

## Step 1: Document Discovery — Inventaire

### A. PRD

**Documents entiers :**
- `prd.md` (37 330 bytes, 2026-02-26 14:53)

**Documents fragmentés :** Aucun.

### B. Architecture

**Documents entiers :**
- `architecture.md` (36 366 bytes, 2026-02-26 20:20)

**Documents fragmentés :** Aucun.

### C. Epics & Stories

**Documents entiers :**
- `epics.md` (61 290 bytes, 2026-02-26 20:32)

**Documents fragmentés :** Aucun.

### D. UX Design

**Documents entiers :**
- `ux-design-specification.md` (9 565 bytes, 2026-02-26 14:41)

**Documents fragmentés :** Aucun.

### Autres fichiers dans `planning-artifacts`

- `product-brief-JARVOS_recyclique-2026-02-25.md`
- `validation-report-2026-02-26.md`
- `sprint-change-proposal-2026-02-26.md`
- Dossiers : `research/`, backups `normalize_typographic_backup_*`

---

## PRD Analysis

### Functional Requirements

**FR1** : Un opérateur habilité peut démarrer une session de caisse (avec fond de caisse) sur un poste donné.  
**FR2** : Un opérateur habilité peut enregistrer des ventes (lignes, catégories, quantités, prix, poids éventuels, paiements multi-moyens) pendant la session.  
**FR3** : Un opérateur habilité peut clôturer la session de caisse (comptage physique, totaux, écart éventuel) et déclencher le contrôle et la sync comptable.  
**FR4** : Le système peut restreindre l'accès au menu caisse uniquement lorsque le poste est en mode caisse (écran verrouillé sur la caisse).  
**FR5** : Une personne habilitée peut déverrouiller la session (ou quitter le mode caisse) en saisissant son code PIN.  
**FR6** : Le système peut gérer plusieurs lieux et plusieurs caisses (multi-sites, multi-caisses).  
**FR7** : Le système peut pousser chaque ticket de vente vers Paheko (push par ticket, file résiliente) sans double saisie compta.  
**FR7b** : Le système peut permettre la saisie caisse hors ligne (buffer local) et synchroniser les tickets vers Paheko au retour en ligne (file Redis Streams côté backend).  
**FR8** : Un opérateur peut ouvrir un poste de réception et créer des tickets de dépôt.  
**FR9** : Un opérateur peut saisir des lignes de réception (poids, catégorie, destination) sur un ticket.  
**FR10** : Le système conserve la réception comme source de vérité matière/poids (aucune sync manuelle obligatoire vers Paheko).  
**FR11** : Le système peut synchroniser les données caisse (sessions, tickets, lignes, paiements) vers Paheko à la clôture (contrôle totaux, syncAccounting). Une session RecyClique = une session Paheko par caisse.  
**FR12** : Un responsable compta peut administrer la compta via l'interface Paheko (v1) en attendant les interfaces RecyClique.  
**FR13** : (Post-MVP) Un responsable compta peut effectuer les opérations compta (bilan, rapprochement, scan factures, notes de frais) depuis RecyClique.  
**FR13b** : Le système peut gérer un mapping prédéfini entre RecyClique et Paheko (moyens de paiement, catégories caisse, sites/emplacements, etc.) pour la v1 ; périmètre figé lorsque BDD et instance dev sont stabilisées.  
**FR14** : Un administrateur peut démarrer un poste (caisse ou réception) avec un compte administrateur (ou équivalent).  
**FR15** : Le système peut associer un code PIN à chaque personne habilitée à la caisse pour le déverrouillage de session.  
**FR16** : (v0.1) Le système peut authentifier les utilisateurs terrain via JWT (FastAPI) et les utilisateurs admin via Paheko (auth séparée).  
**FR17** : (v0.2+) Le système peut offrir un SSO entre RecyClique et Paheko (à documenter).  
**FR18** : Un admin technique peut déployer et configurer l'instance (RecyClique en un container : front + middleware, Paheko, PostgreSQL, Redis) via Docker Compose.  
**FR19** : Un admin technique peut configurer le canal push RecyClique → Paheko (endpoint, secret, résilience).  
**FR20** : Le système peut conserver les tickets non poussés en file (Redis Streams) et les repousser après indisponibilité de Paheko (retry sans perte).  
**FR21** : Un utilisateur peut accéder à des écrans ou placeholders « vie associative » depuis RecyClique (calendrier, activités à dérouler post-MVP).  
**FR22** : Le système peut produire et conserver les données déclaratives (poids, flux, catégories, périodes) dans RecyClique pour les déclarations éco-organismes.  
**FR23** : (Post-MVP) Le système peut exposer un module décla éco-organismes (exports, multi-éco-organismes) depuis RecyClique.  
**FR24** : Le système peut charger et activer des modules RecyClique via configuration (TOML, ModuleBase, EventBus Redis Streams, slots React).  
**FR25** : Le système peut faire coexister des plugins Paheko et des modules RecyClique pour activer de nouvelles fonctionnalités (combinaison des deux écosystèmes).  
**FR26** : Le système peut exposer des points d'extension (LayoutConfigService, VisualProvider) avec implémentations stub en v1, pour brancher affichage dynamique et service Peintre (JARVOS Mini).  
**FR27** : (Post-MVP) Le système peut gérer un fonds documentaire RecyClique (statutaire, com, prise de notes, stockage K-Drive ou volume dédié) ; évolution JARVOS Nano/Mini pour recherche et édition intelligentes.

**Total FRs :** 28 (FR1–FR27 + FR7b).

### Non-Functional Requirements

**NFR-P1** : L'enregistrement d'une vente (saisie + envoi) se termine en moins de 2 secondes dans des conditions normales.  
**NFR-P2** : La clôture de session ne bloque pas l'opérateur plus de 10 secondes ; le push et la sync comptable peuvent s'achever en arrière-plan.  
**NFR-S1** : Les échanges RecyClique ↔ Paheko (push) passent par HTTPS avec un secret partagé ; aucun secret en clair dans les requêtes.  
**NFR-S2** : Les secrets (endpoint plugin, credentials) sont gérés via variables d'environnement ou secrets manager, pas en dur dans le code.  
**NFR-S3** : Accès caisse restreint par mode verrouillé (menu caisse seul) et déverrouillage par PIN par opérateur habilité.  
**NFR-S4** : Données personnelles (utilisateurs, adhésions) conformes au RGPD dans le périmètre géré par Paheko/RecyClique.  
**NFR-I1** : La file de push (Redis Streams) garantit qu'aucun ticket n'est perdu en cas d'indisponibilité temporaire de Paheko ; retry jusqu'à succès (ou traitement manuel documenté).  
**NFR-I2** : Les écritures compta (syncAccounting) respectent la configuration Paheko (comptes, exercice, moyens de paiement) ; la config Paheko est la référence.  
**NFR-A1** : Bonnes pratiques d'accessibilité de base (contraste, navigation clavier) pour les écrans caisse et réception ; renforcement possible post-MVP.

**Total NFRs :** 9.

### Additional Requirements

- **Contraintes techniques** : Un container RecyClique (front + middleware), Paheko séparé ; monorepo ; Docker Compose ; SPA/PWA ; REST FastAPI ; JSON ; montants en centimes ; poids en kg (réception) / conversion vers Paheko (g si besoin) ; EventBus Redis Streams côté serveur.
- **Compliance** : Déclarations éco-organismes (RecyClique source) ; comptabilité conforme Paheko ; RGPD (utilisateurs, adhésions).
- **Intégrations** : Paheko (compta, plugin, API), Redis (EventBus + file push), compatibilité workflows Paheko.
- **Risques et mitigations** : perte de données (Redis Streams, retry), écart caisse/compta (contrôle clôture), non-conformité décla (module dédié), accès non autorisé (mode verrouillé + PIN), fuite de secret (HTTPS, env).
- **Périmètre v1** : parité 1.4.4 + sync caisse ↔ Paheko ; réception hors ligne et politique fichiers hors v1.
- **Traçabilité** : tableau FR → Parcours (J1–J5) ; matrice RBAC (rôles vs caisse, réception, compta, admin, vie asso).

### PRD Completeness Assessment

Le PRD est complet et structuré : Executive Summary, Classification, Success Criteria, Product Scope (MVP / Growth / Vision), User Journeys (5 parcours avec exigences révélées), matrice RBAC, Domain-Specific Requirements (Compliance, contraintes techniques, intégrations, risques), FR/NFR numérotés, traçabilité FR → Parcours, références projet. Les FR et NFR sont explicites et couvrent caisse, réception, compta, auth, déploiement, vie asso, éco-organismes, architecture modulaire et gestion documentaire (post-MVP). Les périmètres v1 / post-MVP / v0.1–v0.2+ sont clairement indiqués. Idéal pour la validation de couverture par les epics.

---

## Epic Coverage Validation

### Epic FR Coverage Extracted (from epics.md)

FR1: Epic 4 — Démarrer session de caisse  
FR2: Epic 4 — Enregistrer ventes (lignes, catégories, paiements)  
FR3: Epic 4 — Clôturer session et déclencher contrôle + sync  
FR4: Epic 2 — Restreindre menu caisse (mode verrouillé)  
FR5: Epic 2 — Déverrouiller par PIN  
FR6: Epic 4 — Multi-sites, multi-caisses  
FR7: Epic 4 — Push par ticket vers Paheko  
FR7b: Epic 4 — Saisie caisse hors ligne + sync au retour  
FR8: Epic 5 — Ouvrir poste réception, créer tickets dépôt  
FR9: Epic 5 — Saisir lignes réception (poids, catégorie, destination)  
FR10: Epic 5 — Réception source de vérité matière/poids  
FR11: Epic 4 — Sync caisse vers Paheko à la clôture (syncAccounting)  
FR12: Epic 6 — Administrer compta via Paheko (v1)  
FR13: (Post-MVP) Epic 6 ou évolution ultérieure  
FR13b: Epic 3 — Mapping RecyClique↔Paheko  
FR14: Epic 2 — Démarrer poste avec compte admin  
FR15: Epic 2 — PIN par opérateur caisse  
FR16: Epic 2 — Authentification JWT (terrain) et Paheko (admin)  
FR17: Epic 2 — SSO RecyClique↔Paheko (phase ultérieure)  
FR18: Epic 1 — Déployer et configurer instance (Docker Compose)  
FR19: Epic 3 — Configurer canal push (endpoint, secret, résilience)  
FR20: Epic 4 — File Redis Streams et retry sans perte  
FR21: Epic 6 — Placeholders vie associative  
FR22: Epic 7 — Données déclaratives (poids, flux, catégories, périodes)  
FR23: (Post-MVP) Epic 7 — Module décla éco-organismes  
FR24: Epic 1 — Charger modules (TOML, ModuleBase, EventBus, slots)  
FR25: Epic 1 — Coexistence plugins Paheko et modules RecyClique  
FR26: Epic 8 — Points d'extension (LayoutConfigService, VisualProvider) stubs v1  
FR27: (Post-MVP) Epic 8 — Fonds documentaire RecyClique  

**Total FRs dans les epics :** 28.

### FR Coverage Analysis

| FR   | Couverture epic        | Statut   |
|------|------------------------|----------|
| FR1  | Epic 4                 | Couvert  |
| FR2  | Epic 4                 | Couvert  |
| FR3  | Epic 4                 | Couvert  |
| FR4  | Epic 2                 | Couvert  |
| FR5  | Epic 2                 | Couvert  |
| FR6  | Epic 4                 | Couvert  |
| FR7  | Epic 4                 | Couvert  |
| FR7b | Epic 4                 | Couvert  |
| FR8  | Epic 5                 | Couvert  |
| FR9  | Epic 5                 | Couvert  |
| FR10 | Epic 5                 | Couvert  |
| FR11 | Epic 4                 | Couvert  |
| FR12 | Epic 6                 | Couvert  |
| FR13 | Epic 6 (post-MVP)      | Couvert  |
| FR13b| Epic 3                 | Couvert  |
| FR14 | Epic 2                 | Couvert  |
| FR15 | Epic 2                 | Couvert  |
| FR16 | Epic 2                 | Couvert  |
| FR17 | Epic 2 (phase ultérieure) | Couvert  |
| FR18 | Epic 1                 | Couvert  |
| FR19 | Epic 3                 | Couvert  |
| FR20 | Epic 4                 | Couvert  |
| FR21 | Epic 6                 | Couvert  |
| FR22 | Epic 7                 | Couvert  |
| FR23 | Epic 7 (post-MVP)      | Couvert  |
| FR24 | Epic 1                 | Couvert  |
| FR25 | Epic 1                 | Couvert  |
| FR26 | Epic 8                 | Couvert  |
| FR27 | Epic 8 (post-MVP)      | Couvert  |

### Exigences manquantes

Aucun FR du PRD n'est absent des epics. Tous les FR (y compris FR7b, FR13b et les post-MVP FR13, FR23, FR27) ont une epic assignée.

### Statistiques de couverture

- **Total FRs PRD :** 28  
- **FRs couverts dans les epics :** 28  
- **Taux de couverture :** 100 %

---

## UX Alignment Assessment

### Statut du document UX

**Trouvé** : `ux-design-specification.md` (planning-artifacts).

### Alignement UX ↔ PRD

- **Stratégie v1** : réutilisation des écrans RecyClique 1.4.4 (copy + consolidate + security), cohérent avec le PRD (MVP, parité 1.4.4, pas de refonte UX v1).
- **Parcours** : caisse, réception, admin/settings, vie asso (placeholders), compta v1 via Paheko — alignés sur les parcours J1–J5 et FR4, FR5, FR12, FR21.
- **Contraintes** : navigateurs, responsive, accessibilité (NFR-A1), mode caisse verrouillé + PIN — tous présents dans le PRD.
- **Extension points (FR26)** : UX spec référence la recherche technique Peintre, interfaces LayoutConfigService et VisualProvider, stubs v1 ; cohérent avec le PRD.

### Alignement UX ↔ Architecture

- **Structure frontend** : par domaine (caisse, reception, auth, admin, shared), slots, extension points — décrits dans l'architecture (Project Structure, Évolution frontend).
- **Référence croisée** : l'architecture cite explicitement la spécification UX et la recherche technique Peintre ; la spec UX cite l'ADR et la checklist import 1.4.4.
- **Évolution v2+** : interfaces + stubs au bootstrap, pas de refonte des écrans en v1 — aligné avec l'architecture (anticipation évolution, pas de refonte coûteuse).

### Problèmes d'alignement

Aucun écart identifié entre UX, PRD et architecture. La stratégie v1 (réutilisation 1.4.4) et la préparation des extension points sont cohérentes entre les trois documents.

### Avertissements

Aucun. Le document UX existe, est à jour et aligné avec le PRD et l'architecture.
