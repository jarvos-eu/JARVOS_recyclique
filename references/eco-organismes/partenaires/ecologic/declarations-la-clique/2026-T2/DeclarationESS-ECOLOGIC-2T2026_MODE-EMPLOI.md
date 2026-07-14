# Mode d'emploi — Déclaration ESS Ecologic T2 2026

**Date d'extraction :** 2026-07-07  
**Fichier source :** [`DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods`](DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods) · template vierge : [`../../../_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods`](../../../_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods)  
**Période :** **T2 2026** — 1er avril au 30 juin 2026 inclus  
**Statut fichier :** en cours de remplissage (entrées Ecologic quasi complètes au niveau TOTAL ; sorties Ecologic quasi vides)

> **Pour les agents :** ne pas re-parser l'ODS. Ce document est la source de vérité structurelle. Extraction brute : [`log/cursor-agent/ecologic-t2-2026-ods-extract.json`](../../../../../../log/cursor-agent/ecologic-t2-2026-ods-extract.json).

---

## 1. Résumé

| Élément | Détail |
|---------|--------|
| **Objet** | Grille de travail trimestrielle La Clique — **entrées dépôt** (enlèvements logistiques) et **sorties réemploi** (ventes/dons), ventilées par filière REP Ecologic |
| **Période T2** | Avril–juin 2026 (trimestre civil clos le 30/06/2026) |
| **Portail final** | SI Fusion — `operation.ecologic-extranet.com` (MO ESS 2025/2026) |
| **Pro forma** | CSV généré après saisie portail (modèle T1 : `pro forma déclaration T1 2026.csv`) |
| **Échéance indicative** | **~30/07/2026** (hypothèse J+30, cf. [calendrier](../../../../2026-07-07_calendrier-declarations-partenaires.md)) |
| **Cases portail obligatoires** | **18 volumes** = 9 codes filière × 2 opérations (`LIV` + `DEC_REE`) |
| **Particularité T2** | Fichier **combiné Ecologic + Ecomaison** (colonnes K–T) — hors périmètre portail Ecologic mais utile au workflow terrain |

**Lecture clé :** l'ODS est un **tableur amont** (pesées par enlèvement / période). La **déclaration finale** portail reprend les **totaux par filière** convertis en `LIV` (entrées) et `DEC_REE` (sorties ventes/dons). Ne pas confondre les colonnes Ecomaison (ABJ, jouets, ameublement) avec les cases Ecologic.

---

## 2. Inventaire des feuilles

| Onglet | Lignes non vides | Rôle | Zone Ecologic | Zone Ecomaison (hors portail Ecologic) |
|--------|------------------|------|---------------|----------------------------------------|
| **Entrees-Reception** | 84 | Entrées dépôt par créneau d'enlèvement + section **RECYCLAGE** | Col. **B–J** (l. 2), données l. **5–51** | Col. **K–T** (l. 2–4), données l. **5–6** + recyclage l. **55–84** |
| **Sortie-VenteDonsReemploi** | 125 | Sorties ventes/dons/réemploi par période | Col. **B–J** (l. 2), données l. **4–125** | Col. **K–T** (l. 2–3), données l. **5–125** |
| **Feuille3** | 0 | Vide (réservée) | — | — |

**Repères visuels (ligne 1) :**

- `Entrees-Reception` : **F1** = libellé zone **ECOLOGIC** · **M1** = libellé zone **ECOMAISON**
- `Sortie-VenteDonsReemploi` : **F1** = **ECOLOGIC** · colonnes K–T = ABJ / jouets / ameublement

---

## 3. Tableau maître — cases à remplir

### 3.1 Déclaration finale portail (18 cases volume)

Ces **18 cases** sont les seules obligatoires sur le portail Ecologic / pro forma. L'ODS alimente le calcul amont ; les valeurs ci-dessous indiquent l'état **au 07/07/2026** dans le fichier T2.

| # | Libellé officiel | Code pro forma | Opération | Flux métier | Unité | Source calcul Recyclique (cible patch 1.4.5) | Repère ODS (contrôle) | État actuel T2 |
|---|------------------|---------------|-----------|-------------|-------|-----------------------------------------------|----------------------|----------------|
| 1 | **PAM** | PAM | `LIV` | Enlèvement / gisement dépôt | **t** | `ROUND(FLOOR(SUM(poids_kg)) / 1000, 3)` entrées tickets cat. `1- Petits appareils em melange(PAM)`, période T2, hors EXCLUDE | `Entrees-Reception` **B51** (somme B5:B50) | **246,5 t** — rempli (ligne TOTAL) |
| 2 | **PAM** | PAM | `DEC_REE` | Réemploi ESS (ventes + dons) | **t** | `ROUND(SUM(poids_kg) / 1000, 3)` sorties caisse + dons cat. PAM (LCQ-003 vente\|don) | `Sortie-VenteDonsReemploi` **B4** (partiel) | **0,25 t** — partiel (1 période sur ~120) |
| 3 | **ECRANS** | ECR | `LIV` | Enlèvement écrans | **t** | Entrées tickets cat. `2- Ecrans` (libellé à confirmer) | **C51** | **25,1 t** — rempli |
| 4 | **ECRANS** | ECR | `DEC_REE` | Réemploi écrans | **t** | Sorties ventes/dons écrans | Col. C (sorties) | **vide** |
| 5 | **GHF** | GHF | `LIV` | Enlèvement gros électro hors froid | **t** | Entrées `3- Gros électroménager hors froid (GEMHF)` | **D51** | **40 t** — rempli |
| 6 | **GHF** | GHF | `DEC_REE` | Réemploi GHF | **t** | Sorties ventes/dons GHF | Col. D (sorties) | **vide** |
| 7 | **GF** | GEF | `LIV` | Enlèvement gros électro froid | **t** | Entrées `4- Gros électroménager froid (GEMF)` | **E51** | **0 t** — rempli (zéro explicite) |
| 8 | **GF** | GEF | `DEC_REE` | Réemploi gros froid | **t** | Sorties ventes/dons GEMF | Col. E (sorties) | **vide** |
| 9 | **ASL-CAT1 o-o** | ASL-CAT1 | `LIV` | Enlèvement ASL cat. 1 | **t** | Entrées mappées photobook ASL CAT1 | **F51** | **69 t** — rempli |
| 10 | **ASL-CAT1 o-o** | ASL-CAT1 | `DEC_REE` | Réemploi ASL CAT1 | **t** | Sorties ventes/dons ASL CAT1 | Col. F (sorties) | **vide** |
| 11 | **ASL-CAT2** | ASL-CAT2 | `LIV` | Enlèvement ASL cat. 2 | **t** | Entrées mappées photobook ASL CAT2 | **G51** | **32,7 t** — rempli |
| 12 | **ASL-CAT2** | ASL-CAT2 | `DEC_REE` | Réemploi ASL CAT2 | **t** | Sorties ventes/dons ASL CAT2 | Col. G (sorties) | **vide** |
| 13 | **ABJ-TON Auto** | ABJ-TONA | `LIV` | Enlèvement tondeuses autoportées | **t** ou pièces | Entrées tondeuses autoportées (historique T4) | **H51** | **0** — rempli (zéro) |
| 14 | **ABJ-TON Auto** | ABJ-TONA | `DEC_REE` | Réemploi tondeuses auto | **t** ou pièces | Sorties tondeuses autoportées | Col. H (sorties) | **vide** |
| 15 | **ABJ-TON Marchant** | ABJ-TONM | `LIV` | Enlèvement tondeuses marchantes | **t** ou pièces | Entrées tondeuses marchantes | **I51** | **0** — rempli (zéro) |
| 16 | **ABJ-TON Marchant** | ABJ-TONM | `DEC_REE` | Réemploi tondeuses marchantes | **t** ou pièces | Sorties tondeuses marchantes | Col. I (sorties) | **vide** |
| 17 | **ABJ-AUTres** | ABJ-AUT | `LIV` | Enlèvement autres ABJ thermiques | **pièces** | `COUNT` entrées `3- Autres ABJ thermique` | **J51** | **0** — rempli (zéro) |
| 18 | **ABJ-AUTres** | ABJ-AUT | `DEC_REE` | Réemploi ABJ thermique | **pièces** | `COUNT` sorties ABJ thermique (ventes/dons) | Col. J (sorties) | **vide** |

**Synthèse état portail (dérivé ODS au 07/07/2026) :**

| Métrique | Valeur |
|----------|--------|
| Cases documentées | **18** |
| `LIV` renseignées (valeur présente, y.c. zéro) | **9 / 9** (via ligne TOTAL entrées) |
| `DEC_REE` renseignées | **1 / 9** (PAM partiel 0,25 t) |
| `DEC_REE` vides | **8 / 9** |
| Cases portail prêtes à soumettre | **0 / 18** (sorties Ecologic non consolidées ; libellé TOTAL entrées erroné — cf. §5) |

> **Alias nomenclature :** colonne ODS `GF` = code portail **`GEF`** · `ECRANS` = **`ECR`**.

### 3.2 Grille ODS — colonnes Ecologic (référence coordonnées)

En-têtes officiels — **ligne 2** des deux feuilles actives :

| Colonne | Libellé exact (ODS) | Code pro forma | Unité ODS |
|---------|---------------------|---------------|-----------|
| **B** | PAM | PAM | t |
| **C** | ECRANS | ECR | t |
| **D** | GHF | GHF | t |
| **E** | GF | GEF | t |
| **F** | ASL-CAT1 o-o | ASL-CAT1 | t |
| **G** | ASL-CAT2 | ASL-CAT2 | t |
| **H** | ABJ-TON Auto | ABJ-TONA | t (ou pièces) |
| **I** | ABJ-TON Marchant | ABJ-TONM | t (ou pièces) |
| **J** | ABJ-AUTres | ABJ-AUT | **pièces** |

### 3.3 Grille ODS — cellules de saisie par période (workflow amont)

#### Feuille `Entrees-Reception` — zone Ecologic (l. 5–50)

| Repère | Libellé colonne A (période) | Cellules Ecologic renseignées | État |
|--------|----------------------------|------------------------------|------|
| **L5** | Du 1er avril 2026 | B:0,25 · C:2,8 · D:40 · F:10 · G:0,8 | partiel (E, H–J vides) |
| **L6** | Au 30 juin 2026 inclus | B:108 · C:18,5 · F:21 · G:0,2 | partiel (D, E, H–J vides) |
| **L7** | *(sans libellé A)* | B:1,8 · C:3,8 · F:3 · G:1 | orpheline |
| **L8** | L 3673 inclus | B:5 · F:15 · G:2 | partiel |
| **L9–L46** | *(majoritairement sans libellé A)* | **B uniquement** (PAM) sur 38 lignes ; quelques F/G éparses | en cours |
| **L51** | TOTAL 4T 2025 *(libellé erroné — valeurs = somme T2)* | B:246,5 · C:25,1 · D:40 · E:0 · F:69 · G:32,7 · H:0 · I:0 · J:0 | **TOTAL entrées Ecologic T2** |

**Statistiques zone Ecologic entrées (l. 5–50, col. B–J) :**

| Métrique | Valeur |
|----------|--------|
| Cellules potentielles | 414 (46 lignes × 9 colonnes) |
| Cellules remplies | **64** |
| Cellules vides | **350** |

**Sommes calculées (l. 5–50, avant ligne TOTAL) — cohérentes avec B51:C51:D51:F51:G51 :**

| PAM | ECRANS | GHF | GF | ASL-CAT1 | ASL-CAT2 |
|-----|--------|-----|----|---------|---------| 
| 246,5 t | 25,1 t | 40 t | 0 | 69 t | 32,7 t |

#### Feuille `Sortie-VenteDonsReemploi` — zone Ecologic (l. 4–124)

| Repère | Libellé colonne A | Cellules Ecologic renseignées | État |
|--------|-------------------|------------------------------|------|
| **L4** | Du 1er avril 2026 | B:0,25 (PAM seul) | partiel |
| **L5–L124** | Périodes diverses (surtout col. K–T Ecomaison) | **aucune** cellule Ecologic | vide |
| **L125** | TOTAL 4T 2025 *(reliquat modèle)* | B:0,25 · C–J:0 | **non à jour pour T2** |

**Statistiques zone Ecologic sorties (l. 4–124, col. B–J) :**

| Métrique | Valeur |
|----------|--------|
| Cellules potentielles | 1 089 (121 lignes × 9 colonnes) |
| Cellules remplies | **1** |
| Cellules vides | **1 088** |

#### Section RECYCLAGE — `Entrees-Reception` (l. 55–84, hors Ecologic portail)

| Repère | Rôle | État T2 |
|--------|------|---------|
| **L55** | Marqueur `RECYCLAGE` | — |
| **L56–L83** | Pesées recyclage (colonnes Ecomaison L–T) | partiellement rempli |
| **L84** | **TOTAL 2T 2026** (Ecomaison/recyclage) | L:2,5 · M:13,5 · N:14,7 · O:8,1 · P:971,6 · Q:560 · R:1321,1 · S:132 · T:0 |

> La ligne **TOTAL 2T 2026** (l. 84) concerne **uniquement** la zone Ecomaison/recyclage. **Il n'existe pas encore de ligne TOTAL 2T 2026 pour les colonnes Ecologic B–J** — à créer ou à reporter depuis la ligne 51 une fois le libellé corrigé.

---

## 4. Mode opératoire humain

### 4.1 Ordre de remplissage recommandé

```text
1. Exports Recyclique T2 (entrées par filière + sorties caisse ventes/dons)
2. Feuille Entrees-Reception — colonnes B–J : saisir tonnes par enlèvement / période
3. Vérifier somme l. 5–50 = ligne TOTAL (corriger libellé « TOTAL 2T 2026 »)
4. Feuille Sortie-VenteDonsReemploi — colonnes B–J : ventiler sorties réemploi par filière
5. Consolider les 18 volumes portail (LIV = totaux entrées ; DEC_REE = totaux sorties)
6. Saisie SI Fusion + export pro forma CSV
7. Facturation (barèmes MO ESS — story 9.ECO-06)
```

### 4.2 Pièges identifiés

| Piège | Détail | Action |
|-------|--------|--------|
| **Libellé TOTAL erroné** | L51 et L125 indiquent « TOTAL 4T 2025 » | Renommer en **TOTAL 2T 2026** ; les valeurs L51 sont déjà la somme T2 entrées |
| **Lignes sans libellé A** | L7–L46 : pesées PAM isolées (col. B) | Compléter colonne A (date enlèvement / n° ligne) ou fusionner dans les périodes L5–L6 |
| **Double REP dans exports** | Exports « Entrée PAM » T1 = 14,2 t tout magasin vs ~2,2 t PAM | Filtrer catégories Ecologic ; exclure textile, livres, ameublement |
| **Colonnes Ecomaison** | K–T remplies en parallèle | Ne pas reporter sur portail Ecologic |
| **ABJ-AUT en pièces** | Unité ≠ tonnes | Compter pièces, pas de ÷ 1000 |
| **DEC_REE sans réemploi** | Peut rester à 0 (ex. GHF T1) | Confirmer sur portail |
| **Arrondi LIV** | Golden T1 : `FLOOR(kg)/1000` arrondi 3 déc. | Ne pas arrondir avant somme si possible |

### 4.3 Règles d'arrondi

| Opération | Formule |
|-----------|---------|
| `LIV` (tonnes) | `ROUND(FLOOR(SUM(poids_kg)) / 1000, 3)` |
| `DEC_REE` (tonnes) | `ROUND(SUM(poids_kg) / 1000, 3)` |
| `ABJ-AUT` | Comptage **pièces** (pas de conversion t) |

Tolérance golden test PAM LIV : **± 0,001 t**.

---

## 5. Différences vs T4 2025

| Aspect | T4 2025 (`DeclarationEcologic-EntreesDepot-4T2025-1.ods`) | T2 2026 (ce fichier) |
|--------|-----------------------------------------------------------|----------------------|
| **Nom des onglets** | `Feuille1` / `Feuille2` / `Feuille3` | `Entrees-Reception` / `Sortie-VenteDonsReemploi` / `Feuille3` |
| **Colonnes Ecologic** | B–J uniquement (9 filières) | B–J identiques + **colonnes Ecomaison K–T** |
| **Structure** | 1 fichier entrées + 1 fichier sorties séparés | **Fichier unique** entrées + sorties + recyclage |
| **Lignes de données** | ~20 lignes entrées T4 | **46+ lignes** entrées T2 (granularité accrue PAM) |
| **Section recyclage** | Absente | Présente (l. 55–84) |
| **Ligne TOTAL** | `TOTAL 4T 2025` cohérent | L51 valeurs T2 mais **libellé T4** ; L84 = TOTAL 2T Ecomaison seulement |
| **Méthode** | Saisie manuelle pesées enlèvements | Entrées saisies + exports Recyclique prévus pour sorties |
| **Portail** | Non documenté T4 | Pro forma CSV (modèle T1 2026) |

**Colonnes Ecologic inchangées** entre T4 et T2 (mêmes libellés B–J).

---

## 6. Lien cadrage — stories et golden tests

| Référence | Contenu |
|-----------|---------|
| [Cadrage patch 1.4.5 Ecologic](../../../../../../artefacts/2026-07-07_04_cadrage-patch-1.4.5-ecologic.md) | 18 cases, mapping double étape, formules, plan B T2 |
| [Grilles décla finale § Ecologic](../../../../2026-07-07_grilles-declaration-finale-champs-a-remplir.md) | Tableau portail + exemples T1 |
| [Analyse mapping Ecologic](../../2026-07-07_analyse-declarations-mapping.md) | Workflow hybride, gaps Recyclique |
| [Calendrier partenaires](../../../../2026-07-07_calendrier-declarations-partenaires.md) | Échéance T2 ~30/07/2026 |

### Stories BMAD Epic 9 (patch Ecologic)

| Story | Rôle |
|-------|------|
| **9.ECO-02** | Mapping YAML `recyclique_category → ecologic_code` |
| **9.ECO-03** | Drill-down entrées/sorties par code (LCQ-001, LCQ-003) |
| **9.ECO-04** | Endpoint agrégats 18 volumes `GET …/ecologic?period=2026-T2` |
| **9.ECO-06** | Export pro forma CSV + barèmes `ecologic-baremes.yaml` |

### Golden tests

| Cas | Attendu |
|-----|---------|
| PAM LIV T1 2026 | **2,223 t** depuis 2 224 kg cat. PAM (± 0,001 t) |
| PAM LIV T2 2026 (ODS) | **246,5 t** — à valider contre tickets filtrés avant soumission |
| Ratio filtrage | `masse_PAM_LIV / masse_export_brut < 0,20` |

---

## 7. Pour les agents

### Chemins

```text
ODS T2 (rempli)     : references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods
Template Germaine   : references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods
Mode d'emploi (SoT) : …/2026-T2/DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md
JSON extraction     : log/cursor-agent/ecologic-t2-2026-ods-extract.json
ODS référence T4    : …/2025-T4/DeclarationEcologic-EntreesDepot-4T2025-1.ods
```

### Regénérer l'extraction JSON (si ODS mis à jour)

```bash
python "_tmp_extract_ecologic_t2_ods.py"
```

*(Script temporaire racine — régénère `log/cursor-agent/ecologic-t2-2026-ods-extract.json`.)*

### Ce qui n'est PAS à remplir (Ecologic)

| Élément | Raison |
|---------|--------|
| Colonnes K–T (ABJ, jouets, ameublement) | **Ecomaison** — autre déclaration |
| `Feuille3` | Vide |
| Lignes TOTAL 4T 2025 (reliquats) | Libellés obsolètes — remplacer par TOTAL 2T 2026 |
| Textile, livres, cuisine dans exports bruts | Hors périmètre Ecologic |
| Sorties recyclage / benne | Hors `DEC_REE` |

### Compteurs (extraction 2026-07-07)

| Périmètre | Documentées | Remplies | Vides |
|-----------|-------------|----------|-------|
| **Cases portail** (18) | 18 | 10 *(9 LIV + 1 DEC_REE partiel)* | 8 *(DEC_REE)* |
| **Cellules ODS Ecologic entrées** (l. 5–50) | 414 | 64 | 350 |
| **Cellules ODS Ecologic sorties** (l. 4–124) | 1 089 | 1 | 1 088 |

---

*Document généré par analyse ODS — ne pas re-parser le fichier source si ce mode d'emploi est à jour.*
