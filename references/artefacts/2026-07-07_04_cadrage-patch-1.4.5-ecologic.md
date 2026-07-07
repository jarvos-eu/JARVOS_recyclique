# Cadrage patch 1.4.5 — Ecologic (DEEE / ESS)

**Date :** 2026-07-07  
**Demandeur :** Strophe (via orchestration patch éco-organismes La Clique)  
**Statut :** cadrage · **P1** · **activation immédiate** (contrat point d'apport signé avril 2024)  
**Périmètre :** préparation déclaration trimestrielle Ecologic — **pas** saisie automatique portail SI Fusion

**Contexte :** 2ᵉ filière REP pour La Clique (après Ecomaison P0, avant Refashion P2). **T4 2025** saisi en grilles ODS manuelles ; **T1 2026** quasi bouclé (pro forma **218,87 € HT**, facture avril 2026). Patch code : stats, mapping double étape, export brouillon `LIV` / `DEC_REE`.

**Sources :** [grilles décla finale](../eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md) § Ecologic · [analyse mapping Ecologic](../eco-organismes/partenaires/ecologic/2026-07-07_analyse-declarations-mapping.md) · ODS T4 2025 · pro forma CSV T1 · [calendrier](../eco-organismes/2026-07-07_calendrier-declarations-partenaires.md) · [feedback LCQ](../artefacts/2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md) · [categories-decla](../migration-paheko/categories-decla-eco-organismes.md) · [vision module](../vision-projet/vision-module-decla-eco-organismes.md) · `stats_service.py` (agrégats parent uniquement).

---

## 1. Résumé — 18 volumes LIV / DEC_REE

| Élément | Valeur |
|---------|--------|
| **Partenaire** | Ecologic — **DEEE / ESS** (PAM, écrans, gros électro, ASL, ABJ thermique) |
| **Rôle La Clique** | **Point d'apport** ESS — contrat prévention signé avril 2024 |
| **Plateforme** | SI Fusion — `operation.ecologic-extranet.com` |
| **Périodicité** | Trimestre civil |
| **Délai calendaire** | **Non documenté** dans le dépôt — hypothèse **J+30** (T1 facturé avril 2026 pour activité janv.–mars) |
| **Granularité** | **Par code filière** × **type d'opération** (`LIV` ou `DEC_REE`) |
| **Champs volume minimum** | **18 cases** (9 codes × 2 opérations) |
| **Urgence patch Recyclique** | **P1** — T2 2026 à préparer (**~30/07/2026**) |
| **Exemple chiffré validé** | **PAM `LIV` = 2,223 t** (pro forma T1 2026) — champ le plus critique |
| **Facturation T1 2026** | **218,87 € HT** (PRFOPE-MO REE-007442) |

### Les 18 cases volume (9 codes × 2 opérations)

| Code | Filière | `LIV` (enlèvement / logistique) | `DEC_REE` (réemploi ESS) | Unité | Exemple T1 2026 |
|------|---------|--------------------------------|--------------------------|-------|-----------------|
| **PAM** | Petits appareils en mélange | ✓ | ✓ | **t** | LIV **2,223** · DEC_REE **0,184** |
| **ECR** | Écrans | ✓ | ✓ | **t** | LIV **0,081** · DEC_REE **0,012** |
| **GHF** | Gros électro hors froid | ✓ | ✓ | **t** | LIV **0,282** · DEC_REE **0,000** |
| **GEF** | Gros électro froid | ✓ | ✓ | **t** | LIV **0,214** · DEC_REE **0,018** |
| **ASL-CAT1** | Articles sport & loisirs cat. 1 | ✓ | ✓ | **t** | LIV **0,110** · DEC_REE **0,050** |
| **ASL-CAT2** | ASL cat. 2 | ✓ | ✓ | **t** | LIV **0,202** · DEC_REE **0,012** |
| **ABJ-TONA** | Tondeuses autoportées | ✓ | ✓ | **t** ou pièces | **0** |
| **ABJ-TONM** | Tondeuses marchantes | ✓ | ✓ | **t** ou pièces | **0** |
| **ABJ-AUT** | Autres outils jardin thermiques | ✓ | ✓ | **pièces** | LIV **3** · DEC_REE **2** |

> **Note nomenclature :** grille T4 ODS utilise `GF` (gros froid) et `ECRANS` ; pro forma T1 utilise `GEF` et `ECR`. Harmoniser dans le mapping YAML (`GF` → alias `GEF`).

### Priorité relative patch 1.4.5

```text
P0 Ecomaison  →  P1 Ecologic (ce document)  →  P2 Refashion
```

Le patch Ecologic **réutilise** les livrables transverses LCQ-001…003 (stats sous-catégories + split ventes/dons/recyclage) cadrés en P0 Ecomaison.

### Référence historique T4 2025 (ligne TOTAL sorties ODS, tonnes)

| PAM | ECR¹ | GHF | GF² | ASL-C1 | ASL-C2 | ABJ-A | ABJ-M | ABJ-aut |
|-----|------|-----|-----|--------|--------|-------|-------|---------|
| 136,63 | 4,94 | 74 | 32 | 44,56 | 9,18 | 0 | 0 | 5,41 |

> ¹ ODS T4 : colonne `ECRANS` → alias **`ECR`** (pro forma T1). ² ODS T4 : `GF` → alias **`GEF`** (cf. note §1).

T4 = saisie **manuelle par créneau d'enlèvement** — pas d'export Recyclique. T1 = rupture méthode (exports ticket/caisse bruts).

---

## 2. Déclaration finale — cases portail

D'après MO ESS 2025/2026, grilles ODS T4 et pro forma CSV T1 ([§ Ecologic](../eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md)).

### 2.1 Tableau opérationnel (1 trimestre = 18 lignes volume)

| Libellé officiel | Type ope | Flux métier | Unité | Source Recyclique cible | Exemple T1 |
|------------------|----------|-------------|-------|-------------------------|------------|
| **PAM** — `LIV` | Enlèvement / logistique filière | Gisement dépôt enlevé | **t** | Entrées tickets cat. PAM, période, hors exclusions autre REP | **2,223** |
| **PAM** — `DEC_REE` | Réemploi ESS | Ventes / dons PAM | **t** | Sorties caisse cat. PAM (LCQ-003 type=vente\|don) | **0,184** |
| **ECR** — `LIV` / `DEC_REE` | Idem | Écrans | **t** | Entrées / sorties mappées `ECR` | 0,081 / 0,012 |
| **GHF** — `LIV` / `DEC_REE` | Idem | Gros électro hors froid | **t** | `3- Gros électroménager hors froid (GEMHF)` | 0,282 / 0 |
| **GEF** — `LIV` / `DEC_REE` | Idem | Gros électro froid | **t** | `4- Gros électroménager froid (GEMF)` | 0,214 / 0,018 |
| **ASL-CAT1** — `LIV` / `DEC_REE` | Idem | Sport & loisirs cat. 1 | **t** | Photobook ASL + règles split CAT1 | 0,110 / 0,050 |
| **ASL-CAT2** — `LIV` / `DEC_REE` | Idem | ASL cat. 2 | **t** | Idem CAT2 | 0,202 / 0,012 |
| **ABJ-TONA/M** — `LIV` / `DEC_REE` | Idem | Tondeuses | **t** ou pièces | Entrées tondeuses (historique T4) | 0 |
| **ABJ-AUT** — `LIV` / `DEC_REE` | Idem | Autres ABJ thermique | **pièces** | Comptage pièces, pas tonnes | 3 / 2 |

### 2.2 Barèmes T1 2026 (pro forma — 18 lignes MO ESS)

| Code | Type | Volume | Coût unitaire | Coût total |
|------|------|--------|---------------|------------|
| PAM | LIV | 2,223 t | 20,40 €/t | 45,35 € |
| PAM | DEC_REE | 0,184 t | 561,00 €/t | 103,22 € |
| ECR | LIV | 0,081 t | 20,40 €/t | 1,65 € |
| ECR | DEC_REE | 0,012 t | 561,00 €/t | 6,73 € |
| GHF | LIV | 0,282 t | 20,40 €/t | 5,75 € |
| GHF | DEC_REE | 0,000 t | 561,00 €/t | 0,00 € |
| GEF | LIV | 0,214 t | 20,40 €/t | 4,37 € |
| GEF | DEC_REE | 0,018 t | 561,00 €/t | 10,10 € |
| ASL-CAT1 | LIV | 0,110 t | 0,00 €/t | 0,00 € |
| ASL-CAT1 | DEC_REE | 0,050 t | 550,00 €/t | 27,50 € |
| ASL-CAT2 | LIV | 0,202 t | 0,00 €/t | 0,00 € |
| ASL-CAT2 | DEC_REE | 0,012 t | 350,00 €/t | 4,20 € |
| ABJ-TONA | LIV | 0 | 30,00 €/u | 0,00 € |
| ABJ-TONA | DEC_REE | 0 | 30,00 €/u | 0,00 € |
| ABJ-TONM | LIV | 0 | 8,00 €/u | 0,00 € |
| ABJ-TONM | DEC_REE | 0 | 8,00 €/u | 0,00 € |
| ABJ-AUT | LIV | 3 pièces | 5,00 €/pièce | 0,00 € |
| ABJ-AUT | DEC_REE | 2 pièces | 5,00 €/pièce | 10,00 € |

**Total HT : 218,87 €** — source : `pro forma déclaration T1 2026.csv`. Config cible : `config/eco-organismes/ecologic-baremes.yaml` (story **9.ECO-06**).

### 2.3 Ce qui N'est PAS à remplir

| Élément | Raison |
|---------|--------|
| Textile, livres, cuisine, meubles Ecomaison dans exports « Entrée PAM » | Hors périmètre Ecologic — **double REP** |
| Lignes sorties caisse non ventilées (2 997 lignes identiques sur 5 fichiers T1) | Export Recyclique ≠ case portail |
| Totaux intermédiaires ODS T4 par enlèvement | Workflow amont ; seule la **ligne TOTAL** + pro forma fait foi |
| `DEC_REE` sans réemploi effectif | Peut rester à **0** (ex. GHF T1) |
| **DPRE** (prélèvement déchetterie) | La Clique : pratique non observée au dépôt — hors modèle T1/T4 |

---

## 3. Spec exports Recyclique

### 3.1 État actuel (T1 2026 observé)

```text
Recyclique                          Ecologic
──────────                          ────────
Tickets entrée  ──export xlsx──►   Fichier « Entrée PAM » = dump COMPLET magasin
Ventes caisse   ──export xlsx──►   Fichier « Sorties PAM » = quasi identique aux 5 autres filières
                                         │
                                         ▼
                                  Agrégation manuelle opérateur
                                  → codes PAM/ECR/GHF…
                                  → types LIV + DEC_REE
                                         │
                                         ▼
                                  Portail SI Fusion + pro forma CSV
```

| Fichier T1 (exemple) | Colonnes | Lignes | Poids total fichier | Poids déclaré filière |
|----------------------|----------|--------|---------------------|----------------------|
| `Entrée PAM T1 2026` | date, cat. secondaire, poids, destination | 2 276 | **14 205 kg** | PAM LIV **2 223 kg** |
| `Sorties PAM T1 2026` | Cat. principale, Quantité… | ~2 997 | **6 038,55 kg** | PAM DEC_REE **184 kg** |
| `SORTIES GHF T1 2026` | (schéma différent) | 2 910 | **5 872,74 kg** | GHF LIV **282 kg** |

**Pollution typique dans un export « Entrée PAM » :**

| Catégorie Recyclique | Masse brute T1 | Action |
|----------------------|----------------|--------|
| `1- Petits appareils em melange(PAM)` | **2 224 kg** | ✓ PAM |
| `A -Textile Divers` | ~2 867 kg | **Exclure** → Refashion / hors Ecologic |
| `A - Livres Divers` | variable | **Exclure** → Recyclivre |
| `NE PLUS UTILISER Rangement…` | 1 531 kg | **Reclasser** — dette technique |

### 3.2 Filtre cible (post-mapping)

```text
INCLUS  → eco_organisme = ecologic AND ecologic_code IN {PAM, ECR, GHF, GEF, ASL-CAT1, ASL-CAT2, ABJ-*}
EXCLU   → eco_organisme = ecomaison | refashion | EXCLUDE (autre REP)
RECLASSER → ecologic_code = RECLASSER (exclu des SUM, warning admin — reclassement obligatoire)
```

**Période :** `TicketDepot.created_at` (ou règle unifiée patch 1.4.5) ∈ trimestre civil `[T_start, T_end]`.

**Unité export :** kg en base → **tonnes** — `LIV` : `ROUND(FLOOR(SUM(poids_kg)) / 1000, 3)` ; `DEC_REE` : `ROUND(SUM(poids_kg) / 1000, 3)` (cf. §5.2–5.3). Exception **ABJ-AUT** : **pièces** (`COUNT` ou champ quantité).

### 3.3 Structure export cible

```yaml
# Structure cible — non implémenté
declaration:
  partner: ecologic
  period: 2026-T2
  lines:
    - code: PAM
      operation: LIV
      unit: t
      value: null  # calculé
    - code: PAM
      operation: DEC_REE
      unit: t
      value: null
    # … 16 autres lignes (18 total)
```

### 3.4 Endpoints cibles (brouillon)

Namespace unifié avec Ecomaison (`/v1/stats/eco-organismes/{partner}/…`) — cf. [cadrage Ecomaison §3.5](2026-07-07_03_cadrage-patch-1.4.5-ecomaison.md). Paramètre `period=YYYY-Tn` → résolution `start_date` / `end_date` (trimestre civil).

| Endpoint | Rôle | Story |
|----------|------|-------|
| `GET /v1/stats/eco-organismes/ecologic?period=2026-T2` | Agrégats 18 volumes (code × LIV/DEC_REE) | 9.ECO-04 |
| `GET /v1/stats/eco-organismes/ecologic/entries/by-code?period=&code=PAM` | Drill-down entrées par `ecologic_code` (LCQ-001) | 9.ECO-03 |
| `GET /v1/stats/eco-organismes/ecologic/exits/by-exit-type?period=&exit_type=vente\|don\|recyclage` | Split sorties (LCQ-003) | 9.ECO-03 |
| `GET /v1/admin/declarations/ecologic/export?period=2026-T2&format=csv` | Pro forma brouillon (colonnes alignées CSV T1) | 9.ECO-06 |
| `GET /v1/admin/declarations/ecologic/export?period=2026-T2&code=PAM&operation=LIV&detail=true` | Détail lignes tickets (audit PAM LIV) | 9.ECO-06 |

**Schémas sorties hétérogènes (gap) :** 4 à 6 colonnes selon filière dans les xlsx T1 — le générateur doit normaliser en interne avant export unifié.

---

## 4. Mapping double étape

Le chaînage Ecologic exige **deux résolutions successives** — contrairement à Ecomaison (1 code par case DEA/JJ/BJ).

### 4.1 Étape 1 — Catégorie boutique → code filière Ecologic

| Catégorie secondaire Recyclique (extrait T1) | Poids T1 (kg) brut | `ecologic_code` | Confiance |
|---------------------------------------------|-------------------|-----------------|-----------|
| `1- Petits appareils em melange(PAM)` | 2 224 | **PAM** | **Forte** |
| `2- Ecrans` (à confirmer libellé exact) | — | **ECR** | Moyenne |
| `3- Gros électroménager hors froid (GEMHF)` | — | **GHF** | Moyenne |
| `4- Gros électroménager froid (GEMF)` | — | **GEF** | Moyenne |
| *(photobook ASL — pas de préfixe unique)* | — | **ASL-CAT1** / **ASL-CAT2** | Faible — règles photobook |
| `3- Autres ABJ thermique` | — | **ABJ-AUT** | Moyenne |
| Tondeuses autoportées / marchantes | — | **ABJ-TONA** / **ABJ-TONM** | Historique T4 |
| `A -Textile Divers`, livres, cuisine… | > 5 500 | **EXCLUDE** | Autre REP |
| `NE PLUS UTILISER Rangement…` | 1 531 | **RECLASSER** | Dette technique — exclu des SUM agrégats, warning opérateur |

### 4.2 Étape 2 — Flux ticket → type opération `LIV` / `DEC_REE`

| Source données | Champ discriminant | Type ope Ecologic |
|----------------|------------------|-------------------|
| **Entrées** tickets réception | Ligne en entrée dépôt, enlèvement logistique¹ | **`LIV`** |
| **Entrées** avec destination `DECHETERIE` / prélèvement externe | Rare La Clique | **`DPRE`** (hors scope T1) |
| **Sorties** ventes caisse | Vente article réemployé | **`DEC_REE`** |
| **Sorties** dons matière (kg, y.c. −18 ans) | LCQ-003 type=don | **`DEC_REE`** |
| **Sorties** destination `RECYCLAGE` / benne | Matière sortante recyclage | **Hors DEC_REE** — ne compte pas en réemploi ESS |

> ¹ **Golden T1 (§5.3)** : LIV = somme entrées **catégorie mappée** uniquement — pas de filtre `destination` / stock magasin en v1.

```text
                    ┌─────────────────────┐
  Catégorie ticket  │  Étape 1 : code     │  PAM, ECR, GHF…
  ─────────────────►│  ecologic_code      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
  Entrée ou sortie  │  Étape 2 : type ope │  LIV | DEC_REE
  + destination     │  operation_type     │
                    └─────────────────────┘
```

### 4.3 Arbre de décision (agent / opérateur)

```text
Ligne ticket
  ├─ Catégorie textile / livre / ameublement ? ──► EXCLUDE (Ecomaison / Refashion)
  ├─ Catégorie « NE PLUS UTILISER » ? ───────────► RECLASSER avant décla
  ├─ is_exit = false (entrée) ?
  │     └─ Catégorie mappée ecologic_code=X ───────► LIV + code filière
  │         (golden T1 §5.3 : **filtre catégorie uniquement**, pas destination ;
  │          filtre enlèvement logistique / stock = évolution post-T1 si traçabilité SI Fusion)
  └─ is_exit = true (sortie) ?
        ├─ Vente caisse ou don structure ? ────────► DEC_REE + code filière
        └─ Recyclage / déchèterie ? ───────────────► Hors DEC_REE (LCQ-003 recyclage)
```

### 4.4 YAML cible (extrait)

```yaml
# config/eco-organismes/ecologic-mapping.yaml — à créer
partner: ecologic
version: 1
codes:
  PAM: { label: "Petits appareils en mélange", unit_liv: t, unit_dec_ree: t }
  ECR: { label: "Écrans", unit_liv: t, unit_dec_ree: t }
  GHF: { label: "Gros électro hors froid", unit_liv: t, unit_dec_ree: t }
  GEF: { label: "Gros électro froid", aliases: [GF], unit_liv: t, unit_dec_ree: t }
  ASL-CAT1: { label: "ASL catégorie 1", ref: photobook-asl }
  ASL-CAT2: { label: "ASL catégorie 2", ref: photobook-asl }
  ABJ-AUT: { label: "Autres ABJ thermique", unit_liv: pieces, unit_dec_ree: pieces }
mappings:
  - recyclique_category_pattern: "^1- Petits appareils em melange\\(PAM\\)$"
    ecologic_code: PAM
  - recyclique_category_pattern: "^A -Textile Divers$"
    ecologic_code: EXCLUDE
    redirect_partner: refashion
  - recyclique_category_pattern: ".*NE PLUS UTILISER.*"
    ecologic_code: RECLASSER
```

---

## 5. Règles calcul kg par trimestre

### 5.1 Paramètres

```text
Période décla     = trimestre civil (T1 jan–mar … T4 oct–déc)
Filtre partenaire = mapping YAML → ecologic_code ≠ EXCLUDE
Unité canonique   = kg en base ; conversion t à l'export (÷ 1000)
Exception         = ABJ-AUT : pièces (COUNT), pas ÷ 1000
```

### 5.2 Formules par type d'opération

| Type ope | Formule | Champs source |
|----------|---------|---------------|
| **`LIV`** (code X) | `ROUND(FLOOR(SUM(poids_kg)) / 1000, 3)` entrées mappées `ecologic_code=X`, période (cf. §5.3) | `LigneDepot` + `TicketDepot` ; filtre catégorie ; `RECLASSER` exclu |
| **`DEC_REE`** (code X) | `ROUND(SUM(poids_kg) / 1000, 3)` sorties vente + don, `ecologic_code=X` | Caisse / `is_exit=true` ; LCQ-003 |
| **`ABJ-AUT` LIV** | `COUNT(lignes)` ou `SUM(quantité)` | Pièces, pas poids |
| **`ABJ-AUT` DEC_REE** | Idem | Sorties ABJ |

### 5.3 Cas de référence PAM LIV T1 2026 (golden test)

```text
Export brut fichier « Entrée PAM »     = 14 205 kg (2 276 lignes, tout magasin)
Catégorie `1- Petits appareils…(PAM)` =  2 224 kg (arrondi affichage ; somme exacte tickets ≈ 2 223,88 kg)
Pro forma PAM LIV déclaré              =  2,223 t  (= 2 223 kg après FLOOR + arrondi export)
Écart résiduel                         =  1 kg — tolérance arrondi / ligne exclue
```

**Règle d'arrondi normative (golden test / CI) :** `value_t = ROUND(FLOOR(SUM(poids_kg)) / 1000, 3)` — reproduit 2 223,88 kg → **2,223 t** (arrondi kg entier avant conversion). Tolérance automatisée : **± 0,001 t**.

**Préséance golden :** le cas T1 utilise le filtre **catégorie PAM uniquement** (pas de filtre `destination` ni stock magasin) — aligne §4.3, §5.2 et tests **9.ECO-02** / **9.ECO-04**.

**Interprétation :** le patch doit reproduire **2,223 t** (± 0,001 t) à partir des tickets filtrés — **pas** 14,2 t.

### 5.4 Contrôles qualité (pré-soumission)

| Contrôle | Règle |
|----------|-------|
| **Ratio filtrage PAM** | `masse_PAM_LIV / masse_export_brut < 0,20` — alerte si dump non filtré soumis |
| Cohérence DEC_REE | `DEC_REE ≤ sorties_vente_don` pour le code (pas de recyclage dans DEC_REE) |
| Double REP | Aucun kg textile/livre/ameublement dans agrégat Ecologic |
| ASL doublon | CAT1 + CAT2 : vérifier que la même ligne n'est pas comptée deux fois (1 048 lignes différentes T1, même poids total) |
| Unité ABJ-AUT | Pas de conversion t sur pièces |
| Nomenclature | `GF` (T4) = `GEF` (T1) dans les rapports |

### 5.5 Calendrier 2026 (hypothèse J+30)

| Trimestre | Fin activité | Date limite indicative | Statut La Clique (07/07/2026) |
|-----------|--------------|------------------------|-------------------------------|
| T1 2026 | 31/03/2026 | ~30/04/2026 | **Quasi bouclé** |
| **T2 2026** | 30/06/2026 | **~30/07/2026** | **À faire — urgent** |
| T3 2026 | 30/09/2026 | ~30/10/2026 | — |
| T4 2026 | 31/12/2026 | ~30/01/2027 | — |

**Plan B T2 (si 9.ECO-04 non prêt ~30/07) :** exports filtrés manuels depuis drill-down **9.ECO-03** + agrégation tableur ; **interdiction** d'utiliser l'export legacy `export_service` EEE-1…8 (cf. **G12**).

---

## 6. Split ventes / dons / recyclage (LCQ-003)

Les cases **`DEC_REE`** ne doivent agréger que le **réemploi ESS** (ventes + dons). Les sorties **recyclage** restent hors DEC_REE mais utiles au contrôle de masse.

### 6.1 Matrice split × type Ecologic

| Nature sortie (LCQ-003) | Compte dans `DEC_REE` | Compte dans `LIV` | Exemple PAM T1 |
|-------------------------|----------------------|-------------------|----------------|
| **Vente caisse** | ✓ | — | DEC_REE **0,184 t** |
| **Don matière** (structure, −18 ans kg) | ✓ | — | Inclus si ventilé |
| **Recyclage / déchèterie** | ✗ | — | Hors pro forma DEC_REE |
| **Enlèvement logistique** (entrée) | — | ✓ | LIV **2,223 t** |

### 6.2 Écart `stats_service` actuel

| Méthode | Comportement | Impact décla Ecologic |
|---------|--------------|----------------------|
| `get_reception_by_category` | Agrège vers **catégorie parente** uniquement | LCQ-001 non satisfait — PAM noyé dans parent |
| `get_sales_by_category` | Ventes caisse, parent uniquement | LCQ-002 — pas de split DEC_REE par sous-catégorie |
| *(absent)* | Pas de `get_exits_by_type` vente/don/recyclage | LCQ-003 bloquant pour DEC_REE fiable |

**Story transverse (partagée Ecomaison / Ecologic / Refashion) :** endpoints drill-down sous-catégorie + `exit_type` avant export Ecologic.

### 6.3 Formule DEC_REE consolidée

```text
DEC_REE_t (code X, trimestre) =
    SUM_ventes(poids_kg | ecologic_code=X, exit_type=vente) / 1000
  + SUM_dons(poids_kg | ecologic_code=X, exit_type=don) / 1000
```

---

## 7. Gaps code et Paheko

### 7.1 Gaps Recyclique (code)

| # | Gap | Impact | Dépendance |
|---|-----|--------|------------|
| G1 | Pas de partenaire `ecologic` dans config éco-organismes | Aucun filtre export | YAML mapping §4.4 |
| G2 | **Aucun flag `eco_organisme` / `ecologic_code`** sur catégories | Tri manuel post-export | Admin catégories |
| G3 | Exports admin = dump magasin entier par filière | 14,2 t au lieu de 2,2 t PAM | G1 + G2 |
| G4 | Stats **parent uniquement** (`stats_service`) | LCQ-001/002 non satisfaits | Epic 5 + 9 |
| G5 | Pas de split **vente / don / recyclage** en stats | DEC_REE approximatif | LCQ-003 |
| G6 | ASL CAT1 vs CAT2 : pas de règle split ticket | Doublon potentiel (même poids total T1) | Photobook ASL en config |
| G7 | `destination` ticket non exploitée pour LIV/DEC_REE | Distribution auto avancée impossible | **Évolution post-T1** si traçabilité SI Fusion — **non bloquant** golden §5.3 |
| G8 | Schémas export sorties **hétérogènes** (4–6 col.) | Générateur unique difficile | Normalisation couche export |
| G9 | Catégories `NE PLUS UTILISER…` dans agrégats | Bruit + sur-déclaration risque | Nettoyage config boutique |
| G10 | `export_service.ECOLOGIC_CATEGORIES` (API v2) = codes **EEE-1…8** génériques | **Non aligné** codes portail PAM/ECR/GHF | Refonte mapping ou couche traduction |
| G11 | Nomenclature `GF` vs `GEF` / `GEHF` | Incohérence T4 ↔ T1 | Alias YAML |
| G12 | Export legacy `export_service.ECOLOGIC_CATEGORIES` (EEE-1…8) + CLI `generate-ecologic-export` encore actifs | Opérateur peut soumettre codes/masses invalides pour SI Fusion | Déprécier / garde-fou jusqu'à **9.ECO-06** ; bannière « non déclarable » |

### 7.2 Gaps Paheko (confrontation)

| Aspect | Paheko Saisie au poids | Recyclique (vision / décision 08) | Gap patch 1.4.5 |
|--------|------------------------|-----------------------------------|-----------------|
| Types opération | **LIV**, **PRE**, **DEC_REE** par provenance/motif | Mapping configurable multi-partenaire | Paheko = **1** référentiel Ecologic figé |
| Source de vérité | Optionnel (plugin lecture seule) | **Recyclique produit et conserve** | Pas de sync bidirectionnelle obligatoire |
| Export décla | Sous-onglet « Déclaration Ecologic » (`module_data_saisie_poids`) | Module décla agnostique | **Deux exports parallèles** si Paheko actif — risque divergence |
| Catégories | Provenances / motifs module | `ligne_depot` + `category_id` boutique | Correspondance **C** ([matrice Paheko](../migration-paheko/audits/matrice-correspondance-caisse-poids.md)) non implémentée |
| Codes filière | Pas de granularité PAM/ECR/GHF dans Paheko natif | 9 codes × LIV/DEC_REE | Paheko insuffisant seul pour les 18 cases |

**Décision maintenue :** le patch 1.4.5 implémente dans **Recyclique** ; Paheko reste optionnel (traçabilité compta). Ne pas bloquer le patch sur l'extension Saisie au poids.

### 7.3 Dette brownfield

- `recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md` — méthodologie générique, pas de YAML Ecologic La Clique.
- `categories-decla-eco-organismes.md` — aide classification REP (PAM vs luminaire DEEE vs EA) ; alimente les règles EXCLUDE §4.3, pas le calcul.

---

## 8. Backlog stories — focus PAM LIV 2,223 t

**Nombre de stories proposées : 6** (préfixe `9.ECO-` — Epic 9 extension Ecologic).

**Critère golden transverse :** sur jeu de données T1 2026 (ou seed équivalent), **`PAM` + `LIV` = 2,223 t** (± 0,001 t) avec **0 kg textile/livre** dans l'agrégat.

### 9.ECO-01 — Mapping YAML catégories → codes Ecologic

**Objectif :** Fichier `ecologic-mapping.yaml` + service résolution catégorie → `ecologic_code`.

**Critères d'acceptation :**

- [ ] Codes : `PAM`, `ECR`, `GHF`, `GEF` (+ alias `GF`), `ASL-CAT1`, `ASL-CAT2`, `ABJ-TONA`, `ABJ-TONM`, `ABJ-AUT`, `EXCLUDE`, `RECLASSER`
- [ ] Exclusion explicite textile / livres / ameublement → `redirect_partner` (refashion / recyclivre / ecomaison)
- [ ] Lignes `RECLASSER` : exclues des agrégats, warning admin
- [ ] Dépréciation / garde-fou export legacy EEE-1…8 (**G12**)
- [ ] Tests unitaires : libellés dépôt T1 (`1- Petits appareils em melange(PAM)`, `A -Textile Divers`, `NE PLUS UTILISER…`)
- [ ] Golden transverse : 0 kg textile/livre dans agrégat PAM (cf. §8 critère golden)
- [ ] Documentation opérateur : arbre §4.3

---

### 9.ECO-02 — Résolution double étape (code × LIV/DEC_REE)

**Objectif :** Service `resolve_ecologic_operation(ligne)` → `{ code, operation: LIV|DEC_REE }`.

**Critères d'acceptation :**

- [ ] Entrées ticket mappées → `LIV` (filtre catégorie ; golden §5.3 sans filtre destination)
- [ ] Sorties vente + don → `DEC_REE`
- [ ] Sorties recyclage → hors DEC_REE (tag `exit_type=recyclage`)
- [ ] Tests : 20 cas dont PAM entrée → LIV, PAM vente → DEC_REE ; golden PAM LIV = **2,223 t** (± 0,001 t)
- [ ] `RECLASSER` → exclu des SUM ; `destination` réservé évolution post-T1 (non bloquant golden)

---

### 9.ECO-03 — Stats LCQ sous-catégories + split sorties (transverse)

**Objectif :** Endpoints drill-down réutilisés par Ecomaison / Ecologic / Refashion — **même namespace** que [9.EM-02/03](2026-07-07_03_cadrage-patch-1.4.5-ecomaison.md).

**Prérequis :** infrastructure YAML **9.EM-01** (Ecomaison P0) ou **9.ECO-01** en parallèle.

**Critères d'acceptation :**

- [ ] `GET /v1/stats/eco-organismes/ecologic/entries/by-code?period=&code=PAM`
- [ ] `GET /v1/stats/eco-organismes/ecologic/exits/by-exit-type?period=&exit_type=vente|don|recyclage`
- [ ] Agrégation **sous-catégorie** (pas seulement parent — corrige `stats_service`)
- [ ] Inclusion dons −18 ans en **kg** dans `don`
- [ ] Test : catégorie PAM visible isolément (LCQ-001)

---

### 9.ECO-04 — Agrégats trimestriels 18 volumes

**Objectif :** Calcul des 18 cases `code × LIV|DEC_REE` pour un trimestre.

**Critères d'acceptation :**

- [ ] `GET /v1/stats/eco-organismes/ecologic?period=2026-T1`
- [ ] Réponse JSON : 18 lignes (codes à 0 inclus)
- [ ] **Golden test PAM LIV = 2,223 t** (± 0,001 t, règle §5.3) sur seed T1
- [ ] **Golden test PAM DEC_REE = 0,184 t**
- [ ] ABJ-AUT en **pièces**, autres en **tonnes**
- [ ] Volumes ASL : golden T1 uniquement si **9.ECO-05** livré ; sinon placeholder `0` + warning
- [ ] Bannière warning si `masse_filtree / masse_brute < 0,20` (équivalent §5.4 — dump non filtré)

---

### 9.ECO-05 — Règles ASL CAT1 / CAT2 (photobook)

**Objectif :** Split ASL à partir du photobook officiel + config admin.

**Critères d'acceptation :**

- [ ] Fichier référence `photobook-asl-rules.yaml` (extrait photobook PDF)
- [ ] Aucune double comptage CAT1+CAT2 sur même `ligne_depot.id`
- [ ] Tests : 10 libellés ASL typiques La Clique
- [ ] Documentation lien photobook `referentiels-officiels/Photobook-Articles-de-Sport-et-de-Loisirs.pdf`

---

### 9.ECO-06 — Export brouillon pro forma Ecologic

**Objectif :** CSV téléchargeable aligné colonnes `pro forma déclaration T1 2026.csv`.

**Critères d'acceptation :**

- [ ] `GET /v1/admin/declarations/ecologic/export?period=&format=csv`
- [ ] Fichier `config/eco-organismes/ecologic-baremes.yaml` (18 barèmes §2.2)
- [ ] Colonnes : `code`, `type_operation` (`LIV`/`DEC_REE`), `volume`, `unite`, `cout_unitaire`, `cout_total` (barèmes MO ESS en config)
- [ ] Export détail audit : `…&code=PAM&operation=LIV&detail=true` (lignes tickets)
- [ ] Bannière « brouillon — vérifier avant soumission SI Fusion »
- [ ] Test e2e : export T1 seed → PAM LIV = **2,223** ; total HT cohérent ± 1 €

### Ordre d'implémentation suggéré

```text
9.ECO-01 (mapping) → 9.ECO-02 (double étape) → 9.ECO-03 (stats LCQ) → 9.ECO-05 (ASL) → 9.ECO-04 (18 volumes) → 9.ECO-06 (export)
```

**Synergies P0 Ecomaison :** 9.ECO-01 partage l'infrastructure YAML ; 9.ECO-03 partage le **namespace** `/v1/stats/eco-organismes/{partner}/` avec 9.EM-02/03 (LCQ-001…003).

---

## 9. Hors scope

| Élément | Raison |
|---------|--------|
| Saisie automatique API portail SI Fusion | Pas d'API partenaire documentée |
| **DPRE** (prélèvement déchetterie conventionnée) | Non observé T1/T4 La Clique |
| Grilles ODS **manuelles par enlèvement** (modèle T4) | Workflow amont terrain — pas de reproduction code |
| Facturation / paiement Ecologic | Calcul barèmes en export brouillon seulement — pas de module compta |
| Photobook intégral en base | Règles extraites en YAML — PDF reste référence |
| **Ecosystem** (DEEE concurrent Ecologic) | La Clique conventionnée **Ecologic** uniquement |
| Luminaires / lampes isolées (filière Ecosystem) | Hors contrat La Clique — voir [categories-decla](../migration-paheko/categories-decla-eco-organismes.md) |
| Textile, livres, ameublement | **Ecomaison / Refashion / Recyclivre** — exclusion mapping |
| Sync bidirectionnelle Paheko Saisie au poids | Recyclique = source de vérité ; Epic 8 optionnel |
| Enlèvements SI Fusion (commande logistique) | Hors Recyclique — dates enlèvement = saisie manuelle opérateur |
| Codes **EEE-1…8** génériques `export_service` v2 | Couvert par **G12** / **9.ECO-01** (dépréciation) — pas d'usage opérateur avant **9.ECO-06** |

---

## 10. Liens

| Ressource | Chemin |
|-----------|--------|
| Grilles décla finale § Ecologic | [`references/eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md`](../eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md) |
| Analyse mapping Ecologic | [`references/eco-organismes/partenaires/ecologic/2026-07-07_analyse-declarations-mapping.md`](../eco-organismes/partenaires/ecologic/2026-07-07_analyse-declarations-mapping.md) |
| Calendrier partenaires | [`references/eco-organismes/2026-07-07_calendrier-declarations-partenaires.md`](../eco-organismes/2026-07-07_calendrier-declarations-partenaires.md) |
| ODS entrées T4 2025 | [`references/eco-organismes/partenaires/ecologic/declarations-la-clique/2025-T4/DeclarationEcologic-EntreesDepot-4T2025-1.ods`](../eco-organismes/partenaires/ecologic/declarations-la-clique/2025-T4/DeclarationEcologic-EntreesDepot-4T2025-1.ods) |
| ODS sorties T4 2025 | [`references/eco-organismes/partenaires/ecologic/declarations-la-clique/2025-T4/DeclarationEcologic-Sorties-4T2025-1.ods`](../eco-organismes/partenaires/ecologic/declarations-la-clique/2025-T4/DeclarationEcologic-Sorties-4T2025-1.ods) |
| Pro forma CSV T1 2026 | [`references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T1/pro forma déclaration T1 2026.csv`](../eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T1/pro%20forma%20d%C3%A9claration%20T1%202026.csv) |
| Contrat point d'apport avril 2024 | [`references/eco-organismes/partenaires/ecologic/referentiels-officiels/contrats-referencement/`](../eco-organismes/partenaires/ecologic/referentiels-officiels/contrats-referencement/) |
| Photobook ASL | [`references/eco-organismes/partenaires/ecologic/referentiels-officiels/Photobook-Articles-de-Sport-et-de-Loisirs.pdf`](../eco-organismes/partenaires/ecologic/referentiels-officiels/Photobook-Articles-de-Sport-et-de-Loisirs.pdf) |
| MO ESS 2025/2026 | [`references/eco-organismes/partenaires/ecologic/referentiels-officiels/`](../eco-organismes/partenaires/ecologic/referentiels-officiels/) |
| Feedback LCQ-001…003 | [`references/artefacts/2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md`](2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md) |
| Vision module décla | [`references/vision-projet/vision-module-decla-eco-organismes.md`](../vision-projet/vision-module-decla-eco-organismes.md) |
| Guide classification REP | [`references/migration-paheko/categories-decla-eco-organismes.md`](../migration-paheko/categories-decla-eco-organismes.md) |
| Matrice Paheko ↔ Recyclique | [`references/migration-paheko/audits/matrice-correspondance-caisse-poids.md`](../migration-paheko/audits/matrice-correspondance-caisse-poids.md) |
| Audit Saisie au poids Paheko | [`references/migration-paheko/audits/audit-saisie-au-poids-paheko.md`](../migration-paheko/audits/audit-saisie-au-poids-paheko.md) |
| `stats_service.py` (API v2) | [`recyclique/api/src/recyclic_api/services/stats_service.py`](../../recyclique/api/src/recyclic_api/services/stats_service.py) |
| Inventaire dépôt éco-organismes | [`references/artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md`](2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md) |
| Cadrage Refashion (P2) | [`references/artefacts/2026-07-07_05_cadrage-patch-1.4.5-refashion.md`](2026-07-07_05_cadrage-patch-1.4.5-refashion.md) |
| Guide mapping brownfield | [`recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md`](../../recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md) |
| Index éco-organismes | [`references/eco-organismes/index.md`](../eco-organismes/index.md) |
| Kanban LCQ stats | [`docs/ideas/kanban/IDEA-2026-07-05-001.md`](../../docs/ideas/kanban/IDEA-2026-07-05-001.md) |
| Analyse brute (script) | `log/cursor-agent/ecologic-analysis-full.txt` |

---

## Retour orchestrateur (synthèse)

| Champ | Valeur |
|-------|--------|
| **Chemin artefact** | `references/artefacts/2026-07-07_04_cadrage-patch-1.4.5-ecologic.md` |
| **Nb stories** | **6** (`9.ECO-01` … `9.ECO-06`) |
| **Golden test** | **PAM LIV = 2,223 t** (T1 2026) — filtré depuis 14,2 t brut |
| **Urgence** | **P1** — T2 2026 **~30/07/2026** |
| **Cases décla** | **18** (9 codes × `LIV` + `DEC_REE`) |
| **Prérequis** | Contrat signé ✓ · mapping YAML · LCQ-001…003 · photobook ASL pour split CAT1/CAT2 |
