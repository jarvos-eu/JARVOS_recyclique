# Analyse déclarations & mapping — Ecomaison / La Clique

**Date :** 2026-07-07  
**Partenaire :** Ecomaison (marque **eco-maison**) — REP **DEA**, **Jouets**, **ABJ**  
**Sources :** `declarations-la-clique/2025-T4/` + `2026-T1/`, `referentiels-officiels/`, brownfield `recyclique-1.4.4/docs/eco-organismes/`  
**Extraction :** script Python / openpyxl → `log/cursor-agent/ecomaison-final.json`

---

## Résumé exécutif

La Clique déclare **3 filières REP** chez Ecomaison en **trimestriel** : **gisements (entrées)**, **réemploi (sorties vente + don)**, **recyclage benne** (souvent auto côté Ecomaison). Les xlsx **RECYCLIC T4 2025** montrent une **double nomenclature** : catégories **officielles** (`1- Assises`, `3- autres jeux d'intérieur`…) et catégories **boutique** (`Chaises`, `A - Meuble Divers`, emojis parent). **T4 validé** (PDF `0535813_*` + factures) ; **T1 2026 en cours** (exports Recyclique non filtrés → reclassement manuel, comme Ecologic). **Priorité patch 1.4.5** : agrégats sous-catégories eco-maison + séparation vente / don / recyclage (**LCQ-001…003**).

---

## Obligations — 3 filières × 3 flux

D’après le MO ESS (`-EA-JJ-ABJ- Mode Opératoire - Déclarations ESS - Février 2026.pdf`, juillet 2025) et la fiche brownfield [`01-fiche-eco-maison.md`](../../../../recyclique-1.4.4/docs/eco-organismes/01-fiche-eco-maison.md) :

| Filière | Code plateforme | Entrées (gisement) | Sorties réemploi | Recyclage |
|---------|-----------------|--------------------|------------------|-----------|
| **DEA** — Éléments d’ameublement | EA | 5 catégories officielles **ou** total mélangé | Par catégorie — **ventes et dons** sortants | Benne / Carte Pro (données souvent **chez Ecomaison**) |
| **Jouets** | JJ | 3 catégories JJ + paniers « Divers » | Idem (plein air / société / intérieur) | Idem |
| **ABJ** — Bricolage & jardin | BJ | Brico + jardin (2 axes) | Idem | Idem + sensibilisation filière BJ |

**Calendrier :** ouverture à partir du **15ᵉ jour** du mois suivant le trimestre, fenêtre **45 jours** (MO fév. 2026). Extranet : `extranet-reemploi-reutilisation.eco-mobilier.fr`.

**Unités terrain La Clique :**

- Entrées T4 RECYCLIC : colonne `poids_Tn` → **tonnes**
- Entrées / sorties T1 et sorties caisse : `poids_kg` ou `Poids (kg)` → **kilogrammes**

**Soutiens indicatifs** (fiche technique) : ~30 €/t gisement, ~130 €/t réemploi — à recouper avec factures T4/T1.

---

## Inventaire dépôt

### Référentiels (`referentiels-officiels/`)

| Fichier | Usage |
|---------|--------|
| MO déclarations ESS juillet 2025 / **février 2026** | Procédure, calendrier, catégories |
| Guides partenariat réemploi DEA / ABJ | Règles ESS, bennes |
| Consignes tri DEA Jouets ABJ (PNG + PDF Nov. 2024) | Acceptés / interdits, bennes |
| Schémas collecte, liste ABJ exclus | Tri terrain |

Doublon partiel dans `recyclique-1.4.4/docs/eco-organismes/eco-maison/` — **référencer**, ne pas recopier.

### T4 2025 — validé (`declarations-la-clique/2025-T4/`)

#### Entrées RECYCLIC (export tickets — matière mapping)

Format commun : `ticket_created_at` | `category_label` | `poids_Tn`

| Fichier | Lignes utiles | Total (t) | Total (kg) |
|---------|---------------|-----------|------------|
| `ECO MAISON ENTREES AMEUBLEMENT RECYCLIC.xlsx` | 83 | **2,035** | 2 035 |
| `ECO MAISON ENTREES JOUETS RECYCLIC.xlsx` | 82 | **0,227** | 227 |
| `ECO MAISON ENTREES JARDIN RECYCLIC.xlsx` | 1 | **0,005** | 5 |
| `ECO MAISON ENTREES MATERIEL BRICO RECYCLIC.xlsx` | 39 ⚠ | **0,125** | 125 |

⚠ Fichier brico : **~1 047 600 lignes Excel** mais seulement **39 lignes de données** (reste vide) — artefact d’export, pas 1 M de pesées.

**Détail catégories entrées T4 (tonnes) :**

| Filière | Catégorie `category_label` | Lignes | t |
|---------|---------------------------|--------|---|
| DEA | `3- Rangement et plan de pose et de travail` | 54 | 1,442 |
| DEA | `1- Assises` | 10 | 0,362 |
| DEA | `Chaises` | 4 | 0,073 |
| DEA | `Petit meuble/chaise en bois massif` | 5 | 0,044 |
| DEA | `A - Meuble Divers` | 2 | 0,036 |
| DEA | `Gros meuble en bois massif` | 1 | 0,034 |
| DEA | `2- Couchage` | 1 | 0,029 |
| DEA | `4- Eléments de décoration textile` | 5 | 0,016 |
| JJ | `3- autres jeux d'intérieur` | 26 | 0,089 |
| JJ | `A - Jeux Divers` | 33 | 0,087 |
| JJ | `2- Jeux société et puzzle` | 22 | 0,049 |
| JJ | `1- Jeux de plein air` | 1 | 0,002 |
| ABJ jardin | `2- Materiel destinés à l'aménagement du jardin` | 1 | 0,005 |
| ABJ brico | `A - Outillage Divers` | 37 | 0,124 |
| ABJ brico | `1- Materiel de bricolage` | 1 | 0,001 |

#### Sorties réemploi T4 (exports caisse + reclassement manuel)

| Fichier | Feuille clé | Total kg | Rôle observé |
|---------|-------------|----------|--------------|
| `SORTIES RECYCLIC Ameublement.xlsx` | `Détails Tickets` | **3 247** | Ventes ventilées **assise / couchage / rangement / plan de pose / déco textile** |
| `SORTIES RECYCLIC BRICO OUTIL.xlsx` | idem | **1 937** | Ventes ABJ (peu ventilées — surtout cat. parent) |
| `ECO MAISON SORTIES JOUETS.xlsx` | idem | **3 292** | JJ : libellés `autres jeux d'intérieur`, `jeux de société`, `jeux de plein air` |
| `ECO MAISON SORTIES ARTICLES ENTRETIEN AMENAGEMENT JARDIN.xlsx` | idem | **3 288** | Jardin / entretien |

**Extrait ventes DEA reclassees** (`SORTIES RECYCLIC Ameublement.xlsx`, kg) :

| Libellé reclassement | kg |
|----------------------|-----|
| assise | 330 |
| rangement | 175 |
| couchage | 124 |
| plan de pose | 44 |
| plan de travail | 15 |
| déco textile | 42 |

Les exports contiennent aussi **tout le magasin** (Textiles 834 kg, Cuisine 497 kg, Livres 368 kg, EEE 287 kg…) — **hors Ecomaison**, filtré manuellement pour la déclaration.

#### Pièces validées T4

- Synthèses PDF : `0535813_13251202431_EA.pdf`, `_JJ.pdf`, `_BJ.pdf`
- Factures : ameublement, jouets, brico-jardin (pdf/docx)

---

### T1 2026 — en cours (`declarations-la-clique/2026-T1/`)

#### Entrées (4 xlsx « Copie »)

Format **Résumé** (tickets) + **Détail** (lignes) :

| Fichier | Colonnes Détail | Lignes | Poids total export |
|---------|-----------------|--------|-------------------|
| `Entrée AMEUBLEMENT ecomaison T1 2026 - Copie.xlsx` | date, `category_secondaire`, `poids_kg`, notes | 2 276 | **17 136 kg** |
| `Entrée ecomaison JARDIN T1 2026 - Copie.xlsx` | + `category_principale` | 2 275 | **11 477 kg** |
| `Entrée ecomaison JOUETS T1 2026 - Copie.xlsx` | idem | 2 276 | **14 506 kg** |
| `Entrée ecomaison OUTILLAGE T1 2026 - Copie.xlsx` | date, secondaire, poids | 2 276 | **13 252 kg** |

**Constat :** chaque fichier « par filière » est un **dump complet** des tickets T1 (comme Ecologic) — **pas de pré-filtre** Recyclique. Seules des lignes `TOTAL JOUETS` (409 kg), `TOTAL JARDIN` (60 kg), `TOTAL OUTILLAGE` (142 kg) suggèrent l’agrégat **réellement déclarable**.

**Sous-catégories Ecomaison repérées dans les entrées T1** (tous fichiers confondus, à filtrer) :

| `category_secondaire` | kg (ordre de grandeur, fichier Ameublement) | Filière cible |
|-----------------------|---------------------------------------------|---------------|
| `* Assises` | ~583 | DEA |
| `* Couchage` | ~672 | DEA |
| `* Rangement` | ~550 | DEA |
| `* Décoration textile` | ~115 | DEA |
| `*Plan de pose , plan de travail` | (sorties) | DEA |
| `3- autres jeux d'intérieur` | ~261 | JJ |
| `2- Jeux société et puzzle` | ~91 | JJ |
| `1- Jeux de plein air` | faible | JJ |
| `A - Outillage Divers` | (Outillage) | ABJ |
| `NE PLUS UTILISER Materiel destinés à l'aménagement du jardin` | obsolète | ABJ |

Pollution **Ecologic / hors REP** : `1- Petits appareils em melange(PAM)` (~2 100 kg), `3- Gros électroménager…`, `2- Autres ASL`, etc.

#### Sorties T1 (5 xlsx par sous-catégorie officielle)

| Fichier | Colonnes | Total kg export | Commentaire |
|---------|----------|-----------------|-------------|
| `SORTIE … ELEMENT AMEUBLEMENT.xlsx` | Principale + Secondaire | **6 037** | Dump caisse complet |
| `SORTIE … JARDIN OUTIL.xlsx` | idem | **6 018** | Quasi identique au fichier EA |
| `SORTIE … AUTRES JEUX D INTERIEUR.xlsx` | Secondaire | **2 550** | Lignes détaillées ; JJ intérieur **277 kg** |
| `SORTIE … JEUX DE SOCIETE.xlsx` | Secondaire | **2 685** | **Même contenu** que « Plein air » (export non ventilé) |
| `SORTIE … JEUX DE PLEIN AIR.xlsx` | Secondaire | **2 685** | Idem — doublon |

PDF miroirs + factures T1 (ameublement, jouets, brico-jardin) + `Soutien filière REP T1 2026 brico jardin.pdf`. Pas encore de PDF synthèse type `0535813_*`.

---

## Workflow terrain observé

```text
Recyclique                              Ecomaison
──────────                              ─────────
Tickets entrée ──export RECYCLIC──►    Lignes ticket × category_label
  (T4: tonnes)                           Agrégation par catégorie officielle
                                         + reclassement paniers « Divers »
Ventes caisse  ──export sessions──►    Filtre manuel filière DEA/JJ/ABJ
                                         Reclassement sorties DEA (5 sous-cat.)
                                         (T4: assise/rangement/… en minuscules)
Bennes / Carte Pro ◄── Ecomaison        Rarement dans exports Recyclique
```

**Évolution T4 → T1 :** passage d’exports **entrées relativement propres** (une filière par fichier, catégories déjà partiellement officielles) à des exports **ticket/caisse bruts** multi-filières — **charge de tri accrue**, même schéma que le partenaire Ecologic.

---

## Matrice mapping brouillon — Recyclique → Ecomaison

### Niveau 1 — Catégories parentes boutique → filière

| Catégorie principale Recyclique (caisse / ticket) | Filière Ecomaison | Hors scope |
|---------------------------------------------------|-------------------|------------|
| `Eléments d'ameublement ménagers (EA)` / `🪑 Ameublement` | **DEA** | |
| `Jeux et jouets (JJ)` / `Jeux` | **Jouets** | |
| `(ABJ) Articles de bricolage et de jardin` / `Outillage` | **ABJ** | |
| `👕 Textiles`, `📖 Livres`, `🍽️ Cuisine`, `⚡ EEE`, `Articles de sport…` | | **Autre REP** (Refashion, Recyclivre, Ecologic…) |

### Niveau 2 — Sous-catégories entrées (T4 = vérité terrain)

| Catégorie secondaire Recyclique | Code Ecomaison cible | Confiance | Notes |
|--------------------------------|----------------------|-----------|-------|
| `1- Assises` | `DEA_ASSISE` | **Forte** | Libellé officiel |
| `Chaises`, `Petit meuble/chaise en bois massif`, `Gros meuble en bois massif` | `DEA_ASSISE` | Moyenne | Boutique → regrouper |
| `2- Couchage` | `DEA_COUCHAGE` | **Forte** | |
| `3- Rangement et plan de pose et de travail` | `DEA_RANGEMENT` + `DEA_PLAN_POSE` | Moyenne | **Fusionné en entrée** ; scinder en sortie |
| `4- Eléments de décoration textile` | `DEA_DECO_TEXTILE` | **Forte** | |
| `A - Meuble Divers` | *manuel* | Faible | Répartition opérateur |
| `1- Jeux de plein air` | `JOUETS_PLEIN_AIR` | **Forte** | |
| `2- Jeux société et puzzle` | `JOUETS_PRESCOLAIRE` | **Forte** | |
| `3- autres jeux d'intérieur` | `JOUETS_PRESCOLAIRE` | **Forte** | |
| `A - Jeux Divers` | `JOUETS_*` (à trancher) | Faible | |
| `1- Materiel de bricolage`, `A - Outillage Divers` | `ABJ_BRICO` | Moyenne | |
| `2- Materiel destinés à l'aménagement du jardin` | `ABJ_JARDIN` | **Forte** | |

### Niveau 2 — Sous-catégories sorties réemploi (T4 reclassement)

| Libellé export / saisie manuelle | Code Ecomaison | kg T4 |
|----------------------------------|----------------|-------|
| `assise` | `DEA_ASSISE` | 330 |
| `couchage` | `DEA_COUCHAGE` | 124 |
| `rangement` | `DEA_RANGEMENT` | 175 |
| `plan de pose` + `plan de travail` | `DEA_PLAN_POSE` | 59 |
| `déco textile` | `DEA_DECO_TEXTILE` | 42 |
| `autres jeux d'intérieur` | JJ intérieur | 87 |
| `jeux de société` | JJ société | 25 |
| `jeux de plein air` | JJ plein air | 2 |

### Niveau 2 — Préfixes T1 (`*` = sous-catégories caisse alignées décla)

| Recyclique T1 | Ecomaison |
|---------------|-----------|
| `* Assises` | Assises |
| `* Couchage` | Couchages |
| `* Rangement` | Rangement |
| `* Décoration textile` | Déco textile |
| `*Plan de pose , plan de travail` | Plan de pose / travail |

### Exclusions explicites

- **EEE** → Ecologic (PAM, écrans, GEMF…)
- **ASL** → Ecologic
- **Textiles habillement** → Refashion
- **Livres** → Recyclivre (cession, pas REP poids)
- **DEEE / jouets électroniques lourds** → Ecologic ou hors périmètre

---

## Cas particuliers

1. **Double nomenclature** : numérotée officielle (`1- Assises`) + boutique (`Chaises`, emojis) + préfixe `*` en T1 — le mapping doit accepter **alias multiples** vers un même code.
2. **Rangement + plan de pose fusionnés en entrée**, **scindés en sortie** (T4 : une colonne entrée, cinq libellés sortie).
3. **Exports caisse non filtrés** : ~3 200 kg « sorties ameublement » dont ~2 500 kg hors DEA — tri manuel systématique.
4. **Dons vs ventes** : le MO regroupe le réemploi ; les exports Recyclique = **ventes caisse** (+ parfois `Total Dons (€)` en session, pas en poids matière) → gap **LCQ-003**.
5. **Recyclage benne** : non présent dans les xlsx ; Ecomaison déduit via Carte Pro / bennes — pas de boucle Recyclique aujourd’hui.
6. **Catégories `NE PLUS UTILISER…`** encore présentes (~1 500 kg sur entrées T1) — dette technique Paheko / migration catégories.
7. **Chaises de jardin** : conflit DEA Assise vs ABJ Jardin (PNG `LISTE ABJ EXCLU` + guide tri) — règle à figer en config.
8. **Fichier brico T4** : dimension Excel gonflée (1 M lignes vides) — ne pas utiliser tel quel pour volumétrie Git / perfs.
9. **Sorties T1 JJ** : fichiers « Société » et « Plein air » **identiques** — l’équipe reclasse depuis un export unique.

---

## Gaps / questions La Clique

| # | Gap | Impact |
|---|-----|--------|
| 1 | **Aucun YAML / table mapping** Recyclique → codes Ecomaison | Agrégation manuelle chaque trimestre |
| 2 | Exports « par filière » = **dump complet** (T1 entrées & sorties) | Même problème qu’Ecologic |
| 3 | **LCQ-001…003** non livrés (sous-catégories dashboard, split vente/don/recyclage) | Préparation décla laborieuse |
| 4 | **Dons matière** non ventilés en poids | Sous-déclaration réemploi possible |
| 5 | Règle **`A - * Divers`** (Meuble, Jeux, Outillage) | Charge cognitive tri |
| 6 | **Unités** tonnes (T4 entrées) vs kg (T1 / caisse) | Risque erreur ×1000 |
| 7 | Catégories obsolètes dans les agrégats | Bruit stats |
| 8 | **Chaises / mobilier jardin** : DEA ou ABJ ? | Conformité tri |
| 9 | Mode **pesée vs comptage** sur plateforme | Non documenté dans le dépôt |

---

## Pistes patch 1.4.5

| Priorité | Action | Lien |
|----------|--------|------|
| **P0** | Config YAML `recyclique_category → ecomaison_code` (alias + filière) | Epic 9, matrice § ci-dessus |
| **P0** | Endpoints stats **sous-catégories** entrées/sorties | LCQ-001, LCQ-002 |
| **P0** | Split sorties **vente / don matière / recyclage** | LCQ-003 |
| **P1** | Export entrées **pré-filtré** par filière DEA/JJ/ABJ | Réduire tri manuel |
| **P1** | Export sorties ventilé par code officiel (5 DEA, 3 JJ, ABJ) | Aligner PDF `0535813_*` |
| **P1** | Normalisation unités (kg interne, conversion t à l’export décla) | Sécurité |
| **P2** | Exclure auto catégories hors périmètre (EEE, textile, livres…) | Conformité |
| **P2** | Page préparation décla trimestrielle (pré-agrégats + écarts) | Feedback 2026-07-05 |
| **P2** | Purger / migrer libellés `NE PLUS UTILISER` | Qualité données |

**Références projet :**

- [`references/artefacts/2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md`](../../../artefacts/2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md)
- [`references/vision-projet/vision-module-decla-eco-organismes.md`](../../../vision-projet/vision-module-decla-eco-organismes.md)
- [`recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md`](../../../../recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md)
- Analyse brute : `log/cursor-agent/ecomaison-final.json`

---

## Fichiers de référence

- Index éco-organismes : [`references/eco-organismes/index.md`](../../index.md)
- Inventaire dépôt : [`references/artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md`](../../../artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md)
- Parallèle multi-partenaire : [`partenaires/ecologic/2026-07-07_analyse-declarations-mapping.md`](../ecologic/2026-07-07_analyse-declarations-mapping.md)
