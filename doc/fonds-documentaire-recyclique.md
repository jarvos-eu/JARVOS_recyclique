# Fonds documentaire RecyClique (post-MVP)

**Story :** 10.2 — Fonds documentaire RecyClique  
**FR27 :** (Post-MVP) Le système peut gérer un fonds documentaire RecyClique distinct de la compta/factures Paheko.  
**Référence politique fichiers :** `references/artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md`

---

## 1. Périmètre et frontière avec Paheko

### 1.1 Ce qui relève du fonds RecyClique

Le **fonds documentaire RecyClique** couvre les documents de la vie associative et de la communication qui ne sont pas des pièces comptables :

| Catégorie | Exemples | Stockage |
|-----------|----------|----------|
| **Statutaire** | Statuts, PV d’AG, règlement intérieur, décisions du CA | Fonds RecyClique |
| **Communication** | Supports com, visuels, communiqués, newsletters (hors envoi Paheko) | Fonds RecyClique |
| **Prise de notes** | Comptes-rendus réunions, notes internes, fiches processus | Fonds RecyClique |

Ces documents restent dans le **périmètre RecyClique** : pas de mélange avec la compta ni les factures gérées par Paheko.

### 1.2 Ce qui reste dans Paheko

| Catégorie | Exemples | Stockage |
|-----------|----------|----------|
| **Compta / factures** | Factures fournisseurs, reçus, pièces jointes aux écritures comptables | Paheko (contexte `transaction/`, API comptabilité) |
| **Documents membres** | Pièces jointes aux fiches membres, imports CSV | Paheko (contexte `user/`, `documents/`) |
| **Web / site asso** | Pages, pièces jointes aux pages | Paheko (contexte `web/`) |

La frontière est claire : **compta et factures = Paheko** ; **statutaire, com, prise de notes = fonds RecyClique**. On ne duplique pas la gestion fichiers de Paheko ; le fonds RecyClique reste distinct et dédié à la vie asso / évolution JARVOS Nano-Mini.

---

## 2. Stockage du fonds documentaire

### 2.1 Options retenues (à configurer par instance)

- **Volume dédié (Docker)** : répertoire monté en volume dans le container RecyClique (ex. `./data/fonds-documentaire`), chemin configurable via `api/config/settings.py`. Adapté au déploiement mono-instance et à la lecture locale (RAG, recherche).
- **K-Drive (ou équivalent)** : stockage partagé type K-Drive / Nextcloud si la politique documentaire de l’instance le prévoit ; backend à brancher via la même configuration (voir chantier fichiers).
- **Autre backend** : selon la politique documentaire (artefact 2026-02-25_02), d’autres backends peuvent être ajoutés (Nextcloud, local réseau, etc.).

### 2.2 Critères

- **Lecture / RAG** : le stockage doit permettre une lecture fiable des fichiers par l’application RecyClique (et, en évolution, par un module RAG / JARVOS Nano-Mini).
- **Écriture** : cohérente avec la frontière Paheko (pas d’écriture des pièces compta dans le fonds RecyClique ; pas d’écriture des documents statutaire/com dans les contextes Paheko compta).
- **Configuration** : un seul chemin (ou une config par backend) dédié au fonds documentaire, distinct des répertoires Paheko et des statics RecyClique.

### 2.3 Emplacement technique (recommandation v1)

- **Config** : dans `api/config/settings.py`, une variable du type `FONDS_DOCUMENTAIRE_ROOT` (ou section `[fonds_documentaire]` avec `backend` et `path` / `url`).
- **Stockage physique** : à la racine du projet ou dans un volume Docker, ex. `data/fonds-documentaire/` (créé au premier déploiement, ignoré par Git si contenu sensible).

---

## 3. Accès au fonds : API cible (spécification)

En post-MVP, l’accès au fonds peut être **implémenté** (endpoints réels) ou **reporté** en ne livrant que la spécification ci-dessous. Dans les deux cas, l’API cible est la suivante.

### 3.1 Principes

- **Dépôt** : un responsable (ou un rôle dédié) peut déposer des fichiers dans des catégories prédéfinies (statutaire, com, prise de notes).
- **Consultation** : lecture listage + téléchargement par chemin logique ou identifiant ; respect de la matrice « qui dépose quoi où » (voir artefact 2026-02-25_02).
- **Sécurité** : authentification RecyClique (JWT), autorisation par rôle (RBAC) ; pas d’exposition directe du système de fichiers sans contrôle.

### 3.2 Endpoints API cible (REST)

| Méthode | Chemin (préfixe `/api`) | Description |
|--------|--------------------------|-------------|
| `GET` | `/fonds-documentaire/` ou `/fonds-documentaire/categories` | Liste des catégories (statutaire, com, prise de notes) et/ou arborescence lisible. |
| `GET` | `/fonds-documentaire/{categorie}` | Liste des documents (métadonnées) d’une catégorie. |
| `GET` | `/fonds-documentaire/{categorie}/{id}` ou `/{categorie}/{path}` | Téléchargement ou métadonnées d’un document. |
| `POST` | `/fonds-documentaire/{categorie}` | Dépôt d’un fichier (multipart/form-data) dans la catégorie. |
| `DELETE` | `/fonds-documentaire/{categorie}/{id}` | Suppression (selon droits). |

- **Formats** : JSON pour les listes et métadonnées ; binaire pour le téléchargement ; multipart pour l’upload.
- **Contraintes** : types MIME et tailles à définir dans la politique documentaire ; pas de pièces compta/factures dans ces endpoints.

### 3.3 Matrice « qui dépose quoi où »

Voir la section **Matrice qui dépose quoi où** dans `references/artefacts/2026-02-25_02_chantier-fichiers-politique-documentaire.md`, mise à jour dans le cadre de cette story.

---

## 4. Évolutions prévues

- **JARVOS Nano / Mini** : le fonds documentaire est la base envisagée pour l’indexation et la recherche (RAG) dans les documents de la vie asso.
- **Chantier fichiers** : alignement avec les backends multiples (K-Drive, Nextcloud, volume Docker) et la matrice vivante par instance (artefact 2026-02-25_02).
- Aucune migration 1.4.4 spécifique fonds documentaire ; tout est aligné sur le chantier fichiers et l’évolution produit.

---

*Document produit dans le cadre de la story 10.2 (post-MVP).*
