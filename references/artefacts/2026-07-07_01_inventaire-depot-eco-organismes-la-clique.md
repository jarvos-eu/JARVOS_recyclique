# Inventaire dépôt K-Drive — éco-organismes La Clique

**Date :** 2026-07-07  
**Source :** `references/_depot/EcoOrganismes.zip` (K-Drive La Clique)  
**Destination :** `references/eco-organismes/` (116 fichiers ventilés)  
**Contexte :** matière première module décla + patch **1.4.5** (stats / préparation décla La Clique)

---

## 1. Ce qu'il y avait dans le zip

Gros dossier « bazar » K-Drive, **5 blocs** :

| Bloc | Fichiers ~ | Rôle |
|------|------------|------|
| **ECOmaison** | ~45 | Priorité — DEA, Jouets, ABJ ; déclarations T4 2025 + T1 2026 |
| **ECOlogic** | ~35 | EEE (ASL, écrans, PAM…) ; T4 2025 + T1 2026 en cours |
| **RE-Fashion** | ~5 | Textile — conventionnement, AMI |
| **VALDELIA** | ~3 | DEA mobilier **professionnel** — conventionnement (pas emballages) |
| **recyclivre** | ~4 | Livres — conventions |
| **transverse** | ~3 | Synthèse filières, FDF fonds réemploi, capture écran |

---

## 2. Où c'est rangé

Tout est sous **`references/eco-organismes/partenaires/<partenaire>/`** :

- **`referentiels-officiels/`** — docs partenaire (MO, guides, PNG tri)
- **`declarations-la-clique/2025-T4/`** et **`2026-T1/`** — ce qu'elles ont **déjà rempli** (Excel, factures, CSV pro forma)
- **`divers/`** — reste Refashion non trié finement

Index navigable : [`references/eco-organismes/index.md`](../eco-organismes/index.md).

---

## 3. Matière première eco-maison (patch)

### Déjà déclaré — T4 2025 (or pour le mapping)

Fichiers **`RECYCLIC`** dans `partenaires/ecomaison/declarations-la-clique/2025-T4/` :

- Entrées : Ameublement, Jardin, Jouets, Matériel brico (xlsx)
- Sorties : Ameublement, Brico outil, Jouets, Entretien aménagement jardin (xlsx)

→ Ce sont les **tableaux de vérité** : comment La Clique agrège aujourd'hui vers les catégories eco-maison. À lire pour construire le mapping config pilote.

### En cours — T1 2026

Même dossier partenaire, sous-dossier `2026-T1/` : entrées par filière (Copie xlsx), sorties par sous-catégorie officielle (jeux intérieur, ameublement, jardin, plein air, société), factures et PDF soutiens REP.

### Référentiels

Modes opératoires ESS (2025 / 2026), guides partenariat, schémas bennes — déjà partiellement dupliqués dans `recyclique-1.4.4/docs/eco-organismes/` ; ici version **terrain La Clique**.

---

## 4. L'autre partenaire (Ecologic)

`partenaires/ecologic/declarations-la-clique/` — preuve qu'elles gèrent **plusieurs** éco-organismes en parallèle. Hors patch immédiat eco-maison ; utile pour la vision module agnostique (Epic 9).

---

## 5. Prochaines étapes suggérées

| # | Action | Livrable |
|---|--------|----------|
| 1 | Ouvrir les xlsx **RECYCLIC T4 2025** | Liste colonnes + lignes catégories → brouillon mapping YAML |
| 2 | Croiser avec catégories Recyclique actuelles (export admin catégories) | Matrice boutique → eco-maison |
| 3 | Relier au besoin LCQ-001…003 | Spec endpoints stats / page préparation décla 1.4.5 |
| 4 | Optionnel | Script lecture xlsx → CSV mapping (hors scope cette nuit) |

**Zip source :** reste dans `_depot/` (gitignore) ; contenu ventilé versionné sous `references/eco-organismes/`.

---

## 6. Volume Git

Un fichier volumineux : `ECO MAISON ENTREES MATERIEL BRICO RECYCLIC.xlsx` (~5,6 Mo). À surveiller si le repo grossit ; acceptable pour matière pilote unique.
