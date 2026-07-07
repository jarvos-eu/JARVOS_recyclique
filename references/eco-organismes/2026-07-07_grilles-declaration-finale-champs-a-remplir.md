# Grilles déclaration finale — champs à remplir (La Clique / Recyclique)

**Date :** 2026-07-07  
**Périmètre :** saisie **finale** trimestrielle (portail / synthèse validée) — **pas** le workflow amont (tri, tickets, bennes, conventionnement).  
**Sources :** dépôts `references/eco-organismes/partenaires/*/declarations-la-clique/`, analyses `2026-07-07_analyse-declarations-mapping.md`, PDF synthèses `0535813_*`, pro forma Ecologic T1, `recyclique-1.4.4/docs/eco-organismes/01-fiche-eco-maison.md`.  
**Extraction brute :** `log/cursor-agent/grilles-declaration-finale-extract.json`, `log/cursor-agent/ecomaison-final.json`.

**Lien patch :** Epic 9 / stats La Clique — voir [vision module](../vision-projet/vision-module-decla-eco-organismes.md) et besoins LCQ-001…003 ([feedback dashboard](../artefacts/2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md)).

---

## Résumé exécutif

| Partenaire | Où se remplit | Champs tonnage/volume obligatoires (décla finale) | Période | Urgence patch Recyclique | Champ le plus critique |
|------------|---------------|---------------------------------------------------|---------|--------------------------|-------------------------|
| **Ecomaison** | Extranet `https://extranet-reemploi-reutilisation.eco-mobilier.fr` → 3 déclarations (EA, JJ, BJ) | **14** (6 DEA + 4 JJ + 4 BJ) | Trimestre civil | **P0** — T1 2026 en cours | DEA entrées « Total éléments d'ameublement » (**2,035 t** T4 validé) |
| **Ecologic** | Portail Ecologic (MO ESS) + pro forma | **18** volumes (9 codes × `LIV` + `DEC_REE`) ; unité **t** sauf ABJ-AUT (**pièces**) | Trimestre civil | **P1** — T1 quasi bouclé | PAM `LIV` (**2,223 t** T1 2026 pro forma) |
| **Refashion** | Portail `https://refashion.fr` (DPAV) | **≥ 4 par PAV** (collecte + destinations) × nb PAV | Trimestre + 40 j | **P2** — convention en cours, pas de grille remplie au dépôt | Tonnage TLC Usagés collectés **par PAV** (méthodo ventes/dons si pas de balance) |

**Lecture :** les chiffres « obligatoires » comptent les **cases de volume** effectivement saisies sur la déclaration validée ; les colonnes « canaux de collecte » Ecomaison (déchèterie, distributeurs…) sont à **0** pour La Clique et ne sont pas des saisies terrain.

---

## § Ecomaison (DEA / JJ / ABJ)

### 1. Où se remplit

| Élément | Détail |
|---------|--------|
| **Plateforme** | Extranet réemploi : `extranet-reemploi-reutilisation.eco-mobilier.fr` |
| **Compte La Clique** | N° `0535813` — Association Eco de LA CLIQUE (SIRET `98905144600015`) |
| **Calendrier** | Ouverture ~**15ᵉ jour** du mois suivant le trimestre, fenêtre **45 jours** (MO ESS fév. 2026) |
| **Livrables post-validation** | 3 PDF synthèse `0535813_13251202431_EA.pdf`, `_JJ.pdf`, `_BJ.pdf` + facture/appel de fonds (ex. T4 : 155,95 € HT EA) |
| **Préparation terrain** | Exports Recyclique xlsx RECYCLIC (entrées tickets, sorties caisse) — **non** déposés tels quels |

### 2. Tableau « case à remplir » — filière DEA (Éléments d'ameublement)

| Libellé officiel (exact — PDF T4 2025) | Flux | Unité | Période | Source calcul Recyclique | Exemple T4 2025 |
|----------------------------------------|------|-------|---------|--------------------------|-----------------|
| **Total éléments d'ameublement** — colonne « Apports volontaires et autres collectes hors points Ecomaison » | Gisement (entrée) | **t** | Trimestre | `SUM(poids_kg)` tickets catégories DEA sur période → `/1000` ; mapper `category_label` / `* Assises`, `1- Assises`, `3- Rangement…`, `A - Meuble Divers` → filière EA ; exclure textile, EEE, livres | **2,035 t** |
| **Assises/Sièges** — « Total des sorties (réemploi/ré-utilisation) » | Réemploi | **t** | Trimestre | Ventes + dons matière : `SUM(poids_kg)` caisse reclasse `assise` / `* Assises` / `1- Assises` + alias chaises | **0,330 t** |
| **Couchages** | Réemploi | **t** | Trimestre | Idem : `couchage`, `* Couchage`, `2- Couchage` | **0,124 t** |
| **Décoration textile** | Réemploi | **t** | Trimestre | `déco textile`, `* Décoration textile`, `4- Eléments de décoration textile` | **0,042 t** |
| **Rangements** | Réemploi | **t** | Trimestre | `rangement`, `* Rangement` ; **entrées** peuvent fusionner rangement+plan de pose — **sorties** scindées | **0,175 t** |
| **Tables et plans de travail** | Réemploi | **t** | Trimestre | `plan de pose` + `plan de travail` + `*Plan de pose , plan de travail` | **0,059 t** |

**Sous-total DEA : 6 champs** (1 entrée + 5 sorties).

### 3. Tableau — filière Jouets (JJ)

| Libellé officiel | Flux | Unité | Période | Source Recyclique | Exemple T4 2025 |
|------------------|------|-------|---------|-------------------|-----------------|
| **Jouets en mélange** — apports volontaires | Gisement | **t** | Trimestre | Tickets JJ : `1- Jeux de plein air`, `2- Jeux société et puzzle`, `3- autres jeux d'intérieur`, `A - Jeux Divers` | **0,227 t** |
| **Autres jeux d'intérieur** | Réemploi | **t** | Trimestre | Sorties caisse : libellés `autres jeux d'intérieur`, `3- autres jeux d'intérieur` | **0,087 t** |
| **Jeux de plein air** | Réemploi | **t** | Trimestre | `jeux de plein air`, `1- Jeux de plein air` | **0,002 t** |
| **Jeux de société et puzzles** | Réemploi | **t** | Trimestre | `jeux de société`, `2- Jeux société et puzzle` | **0,025 t** |

**Sous-total JJ : 4 champs**.

### 4. Tableau — filière Brico-Jardin (BJ)

| Libellé officiel | Flux | Unité | Période | Source Recyclique | Exemple T4 2025 |
|------------------|------|-------|---------|-------------------|-----------------|
| **Articles d'aménagement et d'entretien du jardin** | Gisement | **t** | Trimestre | Entrées : `2- Materiel destinés à l'aménagement du jardin` | **0,005 t** |
| **Matériel de bricolage dont l'outillage à main** | Gisement | **t** | Trimestre | `1- Materiel de bricolage`, `A - Outillage Divers`, `* Outillage à main` | **0,125 t** |
| **Articles d'aménagement et d'entretien du jardin** | Réemploi | **t** | Trimestre | Sorties ABJ jardin (ventes) — reclassement manuel depuis export caisse | **0,003 t** |
| **Matériel de bricolage dont l'outillage à main** | Réemploi | **t** | Trimestre | Sorties outillage / brico | **0,009 t** |

**Sous-total BJ : 4 champs**.

### 5. Exemple rempli — T4 2025 (PDF validés)

Synthèse **EA** (`0535813_13251202431_EA.pdf`) :

- Entrées totales DEA : **2,035 t** — soutien entrée 30 €/t → 61,05 € HT  
- Sorties réemploi totales : **0,730 t** — soutien 130 €/t → 94,90 € HT  
- **Total facture T4 EA : 155,95 € HT**

Détail sorties : Assises 0,330 · Couchages 0,124 · Déco textile 0,042 · Rangements 0,175 · Tables/plans 0,059 (t).

**JJ** : entrée 0,227 t · sorties 0,114 t (0,087 + 0,002 + 0,025) — facture **58,11 € HT**.  
**BJ** : entrée 0,130 t · sorties 0,012 t — facture **7,50 € HT**.

Cohérence exports Recyclique T4 : entrées ameublement xlsx total **2,035 t** (colonne `poids_Tn`) ; sorties reclassees manuellement dans `SORTIES RECYCLIC Ameublement.xlsx` (feuille `Détails Tickets`, colonnes `Catégorie Principale` / libellés reclassement, `Poids (kg)`).

### 6. Ce qui N'est PAS à remplir (La Clique)

| Élément | Raison |
|---------|--------|
| Colonnes entrées « Points permanents Ecomaison », « Collecte détenteurs pro », « Porte à porte »… | Toujours **0** sur synthèses T4 — apports volontaires boutique uniquement |
| **Recyclage benne** / Carte Pro | Données **côté Ecomaison** (benne) — absent des exports Recyclique |
| Textiles, livres, cuisine, EEE, ASL dans exports caisse | **Autres REP** — filtrés manuellement avant saisie |
| Lignes `TOTAL` / commentaires en bas des xlsx sorties | Annotations opérateur, pas des cases portail |
| Facture | Émise **après** validation (montant = synthèse) — pas une case de tonnage |

### 7. Gaps Recyclique → Ecomaison

| Gap | Impact |
|-----|--------|
| Pas de YAML `recyclique_category → code_ecomaison` | Reclassement manuel chaque trimestre |
| Exports T1 = dump complet magasin (~17 t/fichier) vs ~3,5 t déclarables | Risque sur-déclaration si pas de filtre |
| **LCQ-003** : dons matière non ventilés en kg | Sous-déclaration réemploi possible |
| Unités mixtes : `poids_Tn` (T4 entrées) vs `poids_kg` (T1) | Erreur ×1000 |
| Fusion entrée « Rangement + plan de pose » vs 5 sorties DEA | Règle de split à coder |
| Catégories `NE PLUS UTILISER…` encore dans les exports | Bruit agrégats |

---

## § Ecologic (PAM, ECR, GHF, GEF, ASL, ABJ)

### 1. Où se remplit

| Élément | Détail |
|---------|--------|
| **Plateforme** | Portail Ecologic (MO ESS 2025/2026 dans `referentiels-officiels/`) |
| **Modèle T4 2025** | Grilles ODS manuelles `DeclarationEcologic-EntreesDepot-4T2025-1.ods` / `Sorties-4T2025-1.ods` — **matrice dates × filières** |
| **Modèle T1 2026** | Saisie portail → pro forma CSV `pro forma déclaration T1 2026.csv` (validée **218,87 € HT**, PRFOPE-MO REE-007442) |
| **Préparation** | Exports ticket/caisse Recyclique par filière (fichiers « Entrée PAM », « SORTIES GHF »…) — **bruts, non filtrés** |

### 2. Codes officiels (colonnes grille T4 = codes pro forma T1)

| Colonne grille T4 | Code pro forma T1 | Filière |
|-------------------|-------------------|---------|
| PAM | PAM | Petits appareils en mélange |
| ECRANS | ECR | Écrans |
| GHF | GHF | Gros électroménager hors froid |
| GF | GEF | Gros électroménager froid |
| ASL-CAT1 o-o | ASL-CAT1 | Articles sport & loisirs cat. 1 |
| ASL-CAT2 | ASL-CAT2 | ASL cat. 2 |
| ABJ-TON Auto | ABJ-TONA | Tondeuses autoportées |
| ABJ-TON Marchant | ABJ-TONM | Tondeuses marchantes |
| ABJ-AUTres | ABJ-AUT | Autres outils jardin thermiques |

### 3. Tableau « case à remplir » — déclaration finale T1 (portail / pro forma)

Pour **chaque code**, deux types d'opération (`Type ope` dans le CSV) :

| Libellé officiel | Flux métier | Unité | Période | Source Recyclique | Exemple T1 2026 déclaré |
|------------------|-------------|-------|---------|-------------------|-------------------------|
| **PAM** — `LIV` | Enlèvement / logistique (gisement dépôt) | **t** | Trimestre | Entrées tickets : cat. `1- Petits appareils em melange(PAM)` filtrées période + destination ≠ magasin seul ; agrégat `/1000` | **2,223** |
| **PAM** — `DEC_REE` | Réemploi ESS | **t** | Trimestre | Sorties ventes PAM (vente caisse, cat. PAM / EEE) | **0,184** |
| **ECR** — `LIV` | Enlèvement | **t** | Trimestre | Entrées écrans (`2- Ecrans`…) | **0,081** |
| **ECR** — `DEC_REE` | Réemploi | **t** | Trimestre | Sorties écrans | **0,012** |
| **GHF** — `LIV` | Enlèvement | **t** | Trimestre | `3- Gros électroménager hors froid (GEMHF)` | **0,282** |
| **GHF** — `DEC_REE` | Réemploi | **t** | Trimestre | Sorties GHF | **0,000** |
| **GEF** — `LIV` | Enlèvement | **t** | Trimestre | `4- Gros électroménager froid (GEMF)` | **0,214** |
| **GEF** — `DEC_REE` | Réemploi | **t** | Trimestre | Sorties gros froid | **0,018** |
| **ASL-CAT1** — `LIV` | Enlèvement | **t** | Trimestre | Photobook ASL + règles CAT1 (pas de libellé explicite unique en export) | **0,110** |
| **ASL-CAT1** — `DEC_REE` | Réemploi | **t** | Trimestre | Sorties ASL ventilées CAT1 | **0,050** |
| **ASL-CAT2** — `LIV` | Enlèvement | **t** | Trimestre | Idem CAT2 | **0,202** |
| **ASL-CAT2** — `DEC_REE` | Réemploi | **t** | Trimestre | Sorties ASL CAT2 | **0,012** |
| **ABJ-TONA** — `LIV` | Enlèvement | **t** ou **pièces** | Trimestre | Tondeuses autoportées | **0** |
| **ABJ-TONA** — `DEC_REE` | Réemploi | **t** ou **pièces** | Trimestre | — | **0** |
| **ABJ-TONM** — `LIV` / `DEC_REE` | Idem | **t** ou **pièces** | Trimestre | Tondeuses marchantes | **0** |
| **ABJ-AUT** — `LIV` | Enlèvement | **pièces** | Trimestre | `3- Autres ABJ thermique` — **unité pièces** dans pro forma | **3** |
| **ABJ-AUT** — `DEC_REE` | Réemploi | **pièces** | Trimestre | Sorties ABJ thermique | **2** |

**Total : 18 cases volume** (9 codes × 2 opérations). Les cases à 0 restent **à confirmer** sur le portail mais ne génèrent pas de coût.

### 4. Grille T4 2025 — entrées dépôt / sorties (référence historique)

**Entrées dépôt** (`DeclarationEcologic-EntreesDepot-4T2025-1.ods`) :

- **Lignes** = créneaux d'enlèvement (ex. « Du 23 septembre » / « Au 31 decemb inclus »)  
- **Colonnes** = PAM, ECRANS, GHF, GF, ASL-CAT1 o-o, ASL-CAT2, ABJ-TON Auto, ABJ-TON Marchant, ABJ-AUTres  
- **Unité** : **tonnes** par cellule  
- **Pas d'export Recyclique** — saisie directe pesées enlèvements Ecologic

**Sorties T4** — ligne **TOTAL 4T 2025** (tonnes déclarées finales) :

| PAM | ECR | GHF | GF | ASL-C1 | ASL-C2 | ABJ-A | ABJ-M | ABJ-aut |
|-----|-----|-----|----|--------|--------|-------|-------|---------|
| 136,63 | 4,94 | 74 | 32 | 44,56 | 9,18 | 0 | 0 | 5,41 |

### 5. Exemple rempli — T1 2026 (pro forma validé)

Extrait `pro forma déclaration T1 2026.csv` :

| Code | Type | Volume | Coût unitaire | Coût total |
|------|------|--------|---------------|------------|
| PAM | LIV | 2,223 t | 20,40 € | 45,35 € |
| PAM | DEC_REE | 0,184 t | 561,00 € | 103,22 € |
| GEF | LIV | 0,214 t | 20,40 € | 4,37 € |
| GEF | DEC_REE | 0,018 t | 561,00 € | 10,10 € |
| … | … | … | … | … |

**Total HT : 218,87 €** — cohérent avec export brut PAM tickets **2 224 kg** (`1- Petits appareils em melange(PAM)`) vs **14,2 t** dump complet fichier.

### 6. Ce qui N'est PAS à remplir

| Élément | Raison |
|---------|--------|
| Textile, livres, cuisine, meubles Ecomaison dans exports « Entrée PAM » | Hors périmètre Ecologic |
| Lignes entières de sorties caisse non ventilées (2 997 lignes identiques sur 5 fichiers T1) | Export Recyclique ≠ case portail — reclassement manuel |
| Totaux intermédiaires ODS T4 par enlèvement | Workflow amont ; seule la **ligne TOTAL** + pro forma fait foi |
| `DEC_REE` sur enlèvements purement logistiques sans réemploi | Peut rester à **0** (ex. GHF T1) |

### 7. Gaps Recyclique → Ecologic

| Gap | Impact |
|-----|--------|
| Aucun flag `eco_organisme: ecologic` sur catégories | Filtre manuel post-export |
| ASL CAT1 vs CAT2 : pas de split fiable dans les tickets | Photobook ASL requis en config |
| Sorties : schémas colonnes hétérogènes (4–6 col.) | Générateur unique difficile |
| `GF` (T4) vs `GEF`/`GEHF` (T1) | Harmonisation nomenclature |
| Destination ticket (`MAGASIN` / `RECYCLAGE` / `DECHETERIE`) non exploitée en décla | `LIV` vs `DEC_REE` mal auto-distribué |
| ABJ-AUT en **pièces** vs tonnes | Unité à traiter à part dans le patch |

---

## § Refashion (TLC — DPAV)

### 1. Où se remplit

| Élément | Détail |
|---------|--------|
| **Plateforme** | Portail `https://refashion.fr` (extranet DPAV) |
| **Convention** | Contrat-type DPAV ESS 2024 + formulaire `demande_conventionnement_DPAV_refashion_2025_vdef.pdf` |
| **Cartographie PAV** | `Matrice point d'apport.xls` — colonnes : type PAV, adresse, horaires, GPS |
| **Délai** | **40 jours** après fin de trimestre (art. 12.3 contrat) |
| **État La Clique** | **Aucune déclaration trimestrielle remplie** au dépôt — conventionnement en cours |

### 2. Champs obligatoires (contrat + formulaire)

D'après **art. 12.1–12.3** du contrat DPAV ESS 2024 et formulaire conventionnement :

| Libellé officiel / obligation | Flux | Unité | Période | Source Recyclique cible | Exemple dépôt |
|-------------------------------|------|-------|---------|-------------------------|---------------|
| **Quantités de TLC Usagés collectés** — **par PAV** (art. 12.1.b) | Gisement (collecte REP) | **t** (agrégat kg) | Trimestre | `SUM(poids_kg)` tickets + dons textile **hors TLC d'Occasion** ; cat. `👕 Textiles`, `A -Textile Divers`, chaussures/linge si ventilés ; **par site PAV** | *Non rempli* — méthodo « enregistrement ventes et dons » probable |
| **Liste PAV** — adresse, type (matrice) | Référentiel | — | Continu | Entité `pav_refashion` liée au site boutique | Matrice vide (1 ligne header) |
| **Réemploi local** — justificatifs cession (art. 12.2) | Réemploi | **t** | Trimestre | Ventes boutique textile + dons structures (LCQ-003) ; exclure pièces « occasion » non-déchet | *Non rempli* |
| **Remise opérateur de tri / repreneur** (annexe 6) — identité, quantités, nature **Écrémé** / **Original** | Sortie tri / recyclage | **t** | Trimestre | Sorties surplus TLC vers SIRET repreneur ; pas dans Recyclique aujourd'hui | *Non rempli* |
| **Collectes ponctuelles** (annexe 4) | Gisement ponctuel | **t** | ≤ 3 mois | Événements / camion — si applicable | N/A si boutique seule |

**Minimum opérationnel pour 1 PAV (boutique) : ~4 cases** (collecte + réemploi local + export tri + éventuel écrémé) — à affiner sur l'extranet une fois conventionné.

### 3. Méthodologie sans balance homologuée (formulaire)

Cases à cocher / documenter à la convention :

- Enregistrement des **ventes et dons** ← **aligné Recyclique** (caisse + tickets don −18 ans kg)  
- Reconstitution par **borne de collecte**  
- Reconstitution par **sacs collectés**

### 4. Exemple rempli

**Aucun exemple chiffré** dans le dépôt. Proxy export T1 Ecomaison (pollution textile) : catégorie `A -Textile Divers` **~2 867 kg** sur un dump non filtré — **ne pas** reporter tel quel : périmètre REP textile ≠ tout le magasin.

### 5. Ce qui N'est PAS à remplir

| Élément | Raison |
|---------|--------|
| **TLC d'Occasion** (non déchets au dépôt) | Exclus soutien collecte ch. II.C (art. 13) |
| Articles **mouillés / souillés** | Exclus collecte |
| **Décoration textile** type rideaux Ecomaison DEA | Autre REP — voir [categories-decla](../../migration-paheko/categories-decla-eco-organismes.md) |
| **Cintres** seuls | Ambigu EA / hors TLC |
| Dossier **AMI TLC 2025** RNRR | Cofinancement projet — pas décla REP |

### 6. Gaps Recyclique → Refashion

| Gap | Impact |
|-----|--------|
| Pas de déclaration type ni capture portail | Format colonnes exact inconnu |
| Pas de liste repreneurs SIRET (annexe 6) | Blocage convention |
| Stats textile sans split don / vente / tri (LCQ-001…003) | Méthodo « ventes et dons » incomplète |
| Pas d'entité **PAV** | Impossible ventiler par point d'apport |
| Dons textile −18 ans : kg sans € en caisse | À inclure explicitement dans agrégat collecte |

---

## § Comment Recyclique doit calculer — formules transverses

### Principes communs

```text
Période décla     = trimestre civil (T1 jan–mar … T4 oct–déc)
Filtre partenaire = mapping YAML catégorie → {ecomaison|ecologic|refashion}_code
Unité canonique   = kg en base ; conversion t à l'export décla (÷ 1000)
Exclusions        = catégories hors REP du partenaire cible (ne pas compter dans l'agrégat)
```

### Formules cibles par flux

| Flux | Règle agrégation | Champs source Recyclique |
|------|------------------|--------------------------|
| **Gisement / entrée** | `SUM(poids_kg)` tickets **créés** dans le trimestre, `category` mappée, `destination` ∈ {magasin, stock} si pertinent | Export tickets / stats entrées LCQ-001 |
| **Réemploi / sortie vente** | `SUM(poids_kg)` lignes caisse **vente** trimestre, catégories mappées | Export sessions `Détails Tickets`, LCQ-003 type=vente |
| **Réemploi / don matière** | `SUM(poids_kg)` dons (y compris −18 ans **kg**) | LCQ-003 type=don — **gap actuel** |
| **Recyclage** | `SUM(poids_kg)` destination RECYCLAGE ou benne partenaire | Tickets `destination` ; benne Ecomaison **hors** Recyclique |
| **Ecologic LIV** | Tonnes **enlevées** / déposées filière (pas tout le magasin) | Entrées filtrées + enlèvements logistiques |
| **Ecologic DEC_REE** | Tonnes **réemployées** vendues/données | Sorties ventes filière |
| **Refashion collecte PAV** | `SUM(poids_kg)` collecte TLC par `pav_id` | Textile + linge + chaussures REP |

### Pseudo-export cible (patch 1.4.5)

```yaml
# Exemple structure — non implémenté
declaration:
  partner: ecomaison
  period: 2025-T4
  lines:
    - code: DEA_ENTREE_TOTAL
      flux: gisement
      unit: t
      value: 2.035
      source: stats/export?partner=ecomaison&filiere=EA&flux=entree
    - code: DEA_ASSISE_SORTIE
      flux: reemploi
      unit: t
      value: 0.330
      source: stats/export?partner=ecomaison&code=DEA_ASSISE&flux=sortie_vente+don
```

### Priorités patch 1.4.5

| Prio | Livrable | Partenaires |
|------|----------|-------------|
| **P0** | YAML mapping catégories + export pré-filtré par filière/code | Ecomaison |
| **P0** | Stats sous-catégories LCQ-001 / split sorties LCQ-002–003 | Ecomaison (+ Refashion) |
| **P1** | Flag multi-éco-organisme + export Ecologic `LIV`/`DEC_REE` | Ecologic |
| **P2** | Entité PAV + export textile trimestriel | Refashion |

**Références code / doc brownfield :**

- [`recyclique-1.4.4/docs/eco-organismes/01-fiche-eco-maison.md`](../../recyclique-1.4.4/docs/eco-organismes/01-fiche-eco-maison.md)  
- [`recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md`](../../recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md)  
- Analyses : [ecomaison](partenaires/ecomaison/2026-07-07_analyse-declarations-mapping.md) · [ecologic](partenaires/ecologic/2026-07-07_analyse-declarations-mapping.md) · [refashion](partenaires/refashion/2026-07-07_analyse-declarations-mapping.md)

---

## Annexe — comptage champs (retour parent)

| Partenaire | Nb champs obligatoires (volume) | Exemple champ critique |
|------------|--------------------------------|------------------------|
| **Ecomaison** | **14** | DEA entrée « Total éléments d'ameublement » = **2,035 t** (T4) |
| **Ecologic** | **18** | PAM `LIV` = **2,223 t** (T1 pro forma) |
| **Refashion** | **≥ 4 × nb PAV** (4 si 1 boutique) | Tonnage TLC Usagés collectés **par PAV** (non rempli au dépôt) |
