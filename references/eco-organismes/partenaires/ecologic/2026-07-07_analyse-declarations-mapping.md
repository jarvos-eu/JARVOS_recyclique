# Analyse déclarations — Ecologic (La Clique)

**Date :** 2026-07-07  
**Partenaire :** Ecologic — **DEEE / ESS** (PAM, écrans, gros électro, ASL, ABJ thermique)  
**Sources :** `declarations-la-clique/2025-T4/` (ODS/XLSX) + `2026-T1/` (xlsx/csv) + `referentiels-officiels/`

---

## Résumé exécutif

Ecologic couvre les **équipements électriques et électroniques** hors ameublement Ecomaison. La Clique déclare déjà **deux trimestres** : T4 2025 via **grilles manuelles** (poids par enlèvement / période) et **T1 2026** via exports Recyclique + saisie plateforme (pro forma validée **218,87 € HT**). Le chaînage actuel est **hybride** : exports ticket/caisse bruts, puis **agrégation manuelle** vers les codes officiels Ecologic — aucun filtrage automatique par filière dans les xlsx T1.

---

## Obligations déclaration

- Déclaration **trimestrielle** sur le portail Ecologic (MO ESS 2025/2026 dans `referentiels-officiels/`).
- Deux familles d’opérations visibles dans le pro forma T1 :
  - **`LIV`** — enlèvement / logistique filière (ex. 20,40 €/unité PAM).
  - **`DEC_REE`** — tonnage réemploi ESS (barèmes 561 €/t PAM, 550 €/t ASL-CAT1, etc.).
- Contrat **point d’apport** signé (avril 2024) + photobook ASL, flux ESS, guide enlèvement SI Fusion.

**Statut La Clique :** opérationnel ; T1 2026 **en cours / quasi bouclé** (facture + CSV pro forma avril 2026).

---

## Inventaire dépôt

### T4 2025 — `declarations-la-clique/2025-T4/`

| Fichier | Format | Rôle |
|---------|--------|------|
| `DeclarationEcologic-EntreesDepot-4T2025-1.ods` | Matrice dates × filières | **Entrées dépôt** — une ligne = période d’enlèvement, colonnes = tonnes par filière |
| `DeclarationEcologic-Sorties-4T2025-1.ods` / `.xlsx` | Idem | **Sorties** — même structure + ligne **TOTAL 4T 2025** |

**Colonnes officielles T4 (entrées et sorties) :**

| Colonne grille | Code pro forma T1 | Filière |
|----------------|-----------------|---------|
| PAM | PAM | Petits appareils en mélange |
| ECRANS | ECR | Écrans |
| GHF | GHF | Gros électro hors froid |
| GF | GEF | Gros électro froid |
| ASL-CAT1 o-o | ASL-CAT1 | Articles sport & loisirs — cat. 1 |
| ASL-CAT2 | ASL-CAT2 | ASL — cat. 2 |
| ABJ-TON Auto | ABJ-TONA | Tondeuses autoportées |
| ABJ-TON Marchant | ABJ-TONM | Tondeuses marchantes |
| ABJ-AUTres | ABJ-AUT | Autres outils jardin thermiques |

**Totaux T4 2025 (ligne TOTAL sorties ODS, tonnes) :**

| PAM | ECR | GHF | GF | ASL-C1 | ASL-C2 | ABJ-A | ABJ-M | ABJ-aut |
|-----|-----|-----|----|--------|--------|-------|-------|---------|
| 136,63 | 4,94 | 74 | 32 | 44,56 | 9,18 | 0 | 0 | 5,41 |

Somme colonnes **entrées dépôt** (même grille, hors ligne TOTAL) : PAM **1 602,9** · ECR **354,5** · GHF **229** · GF **184** · ASL-C1 **129** · ASL-C2 **140,7** · ABJ-aut **335** (tondeuses auto/marchant = 0).

### T1 2026 — `declarations-la-clique/2026-T1/`

**Entrées (7 xlsx)** — export Recyclique ticket/ligne :

| Fichier | Colonnes | Lignes | Poids total |
|---------|----------|--------|-------------|
| `Entrée ASL CAT 1/2 T1 2026` | date, cat. secondaire, poids, notes | 2 276 | **14 205 kg** |
| `Entrée Ecran / GEF / GEHF / PAM` | + colonne `destination` | 2 276 | **14 205 kg** |
| `Entrée autres ABJ Thermique` | idem | 2 278 | **14 205 kg** |

**Sorties (6 xlsx)** — export ventes caisse :

| Fichier | Colonnes | Lignes | Poids total |
|---------|----------|--------|-------------|
| ASL CAT1, ASL CAT2, ECRAN, PAM, ABJ | variables (`Cat. principale`, `Quantité`…) | ~2 997 | **6 038,55 kg** |
| GHF | sans cat. principale | 2 910 | **5 872,74 kg** |

**Pro forma / facturation :**

| Fichier | Contenu |
|---------|---------|
| `pro forma déclaration T1 2026.csv` | Détail par code × type ope (`LIV` / `DEC_REE`) |
| `liste_pro_forma (1).csv` | Synthèse facture PRFOPE-MO REE-007442 — **218,87 € HT** |
| `FACTURE T1 2026` (pdf/docx) | Pièce comptable |

---

## Workflow terrain observé

```text
Recyclique                          Ecologic
──────────                          ────────
Tickets entrée  ──export xlsx──►   (tous flux, non filtré)
Ventes caisse   ──export xlsx──►   (toutes ventes, quasi identique par filière)
                                         │
                                         ▼
                                  Agrégation manuelle
                                  → codes PAM/ECR/GHF…
                                  → types LIV + DEC_REE
                                         │
                                         ▼
                                  Portail + pro forma CSV
```

**T4 2025** : pas d’export Recyclique — saisie directe des tonnes par **créneau d’enlèvement** Ecologic.

**T1 2026** : exports Recyclique = **matière brute** ; la déclaration finale ne reprend qu’une **fraction** du poids exporté (ex. PAM déclaré **2,223 t** vs catégorie boutique « Petits appareils em mélange » **2 224 kg** dans l’export brut **14,2 t** total).

---

## Mapping brouillon — catégories Recyclique → codes Ecologic

| Catégorie secondaire Recyclique (extrait T1) | Poids T1 (kg) | Code Ecologic cible | Confiance |
|---------------------------------------------|---------------|---------------------|-----------|
| `1- Petits appareils em melange(PAM)` | 2 224 | **PAM** | **Forte** — libellé explicite + cohérent pro forma |
| *(à mapper via photobook ASL)* | — | **ASL-CAT1** / **ASL-CAT2** | Moyenne — pas de préfixe ASL dans l’export |
| *(écrans — cat. à identifier)* | — | **ECR** | Faible — 81 kg déclarés LIV |
| *(gros froid / hors froid)* | — | **GEF** / **GHF** | Faible — colonnes séparées T1, `GF` seul en T4 |
| *(tondeuses)* | — | **ABJ-TONA/M** | Nulle T1 (0 t) ; historique T4 sorties |
| `A -Textile Divers`, `A - Livres Divers`, `A - Cuisine Divers`… | > 5 500 | **Hors Ecologic** | **Ecomaison / autre REP** — polluent les exports |
| `NE PLUS UTILISER Rangement et plan…` | 1 531 | **À reclasse** | Dette technique catégories |

**Pro forma T1 2026 — volumes déclarés (tonnes) :**

| Code | LIV | DEC_REE | Coût (€) |
|------|-----|---------|----------|
| PAM | 2,223 | 0,184 | 148,57 |
| GHF | 0,282 | 0 | 5,75 |
| GEF | 0,214 | 0,018 | 14,47 |
| ECR | 0,081 | 0,012 | 8,38 |
| ASL-CAT1 | 0,110 | 0,050 | 27,50 |
| ASL-CAT2 | 0,202 | 0,012 | 4,20 |
| ABJ-AUT | 3,000* | 2,000* | 10,00 |
| ABJ-TONA/M | 0 | 0 | 0 |

\*Unités ABJ-AUT en **pièces** (pas tonnes) dans le CSV — à confirmer dans le MO.

---

## Cas particuliers

- **Double REP** : les exports « par filière Ecologic » contiennent **tout le magasin** (textile, livres, cuisine…) — le tri Ecologic vs Ecomaison se fait **après export**, pas dans Recyclique.
- **ASL CAT1 vs CAT2** : fichiers entrée quasi identiques (1 048 lignes différentes sur 2 276) mais **même poids total** — risque de doublon, pas de règle de split visible.
- **Sorties** : 5 fichiers sur 6 ont **exactement les mêmes 2 997 lignes / 6 038,55 kg** ; seul GHF diffère légèrement — les exports ne sont **pas ventilés** par filière.
- **T4 → T1** : passage d’une saisie **manuelle par enlèvement** à des exports **ticket/caisse** sans couche mapping — rupture de méthode.
- **Référentiels** : photobook ASL, flux ESS PDF, notice déclarations 2025/2026 = source pour affiner ASL/ABJ.

---

## Gaps / questions

1. **Aucun YAML / table mapping** Recyclique → codes Ecologic (contrairement au besoin patch 1.4.5 eco-maison).
2. **Exports non filtrés** : chaque xlsx « Entrée PAM » = dump complet → charge de tri manuel.
3. **Schémas sorties hétérogènes** (4 à 6 colonnes selon filière) — complique un générateur unique.
4. **Catégories obsolètes** (`NE PLUS UTILISER…`) encore présentes dans les agrégats.
5. **Sémantique ABJ-AUT** : pièces vs tonnes dans le pro forma.
6. **GF vs GEF/GEHF** : nomenclature T4 (`GF`) vs T1 (`GEF` + `GEHF`) à harmoniser.
7. **Validation** : croiser pro forma avec stats dashboard LCQ-001…003 (sous-catégories + type sortie vente/don/recyclage).

---

## Pistes module Recyclique (Epic 9 / post 1.4.5)

| Priorité | Action | Livrable |
|----------|--------|----------|
| 1 | Flag `eco_organisme: ecologic` + `code_decla` sur catégories | YAML pilote (comme eco-maison) |
| 2 | Export entrées **pré-filtré** par code (PAM, ECR, ASL-CAT1…) | Endpoint stats / export décla |
| 3 | Export sorties avec **type flux** (vente / don / recyclage) | LCQ-002 |
| 4 | Reprendre photobook ASL pour règles CAT1/CAT2 | Matrice sous-catégories |
| 5 | Conserver compatibilité **LIV + DEC_REE** | Modèle opération agnostique multi-partenaire |

**Hors scope immédiat patch 1.4.5** (priorité Ecomaison), mais ce dossier prouve le **multi-éco-organismes** et alimente la vision module agnostique.

---

## Fichiers de référence

- Index partenaire : [`references/eco-organismes/index.md`](../../index.md)
- Vision module : [`references/vision-projet/vision-module-decla-eco-organismes.md`](../../../vision-projet/vision-module-decla-eco-organismes.md)
- Inventaire dépôt : [`references/artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md`](../../../artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md)
- Analyse brute (script 2026-07-07) : `log/cursor-agent/ecologic-analysis-full.txt`
