# Cadrage patch 1.4.5 — Ecomaison (DEA / Jouets / ABJ)

**Date :** 2026-07-07  
**Demandeur :** Strophe (via orchestration patch éco-organismes La Clique)  
**Statut :** cadrage · **P0** · **activation immédiate** (T1 2026 en cours, T2 à préparer)  
**Périmètre :** préparation déclaration trimestrielle Ecomaison — **pas** saisie portail ni gestion bennes Carte Pro

**Contexte :** 1ʳᵉ filière REP prioritaire pour La Clique. T4 2025 **validé** (PDF `0535813_*` + factures) ; **T1 2026 en cours** (exports bruts, fenêtre soumission expirée 28/06). Patch code : mapping YAML, stats LCQ, agrégats 14 champs, export brouillon — réduction du tri manuel observé sur `declarations-la-clique/`.

**Sources :** [grilles décla finale](../eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md) § Ecomaison · [analyse mapping Ecomaison](../eco-organismes/partenaires/ecomaison/2026-07-07_analyse-declarations-mapping.md) · [calendrier](../eco-organismes/2026-07-07_calendrier-declarations-partenaires.md) · [feedback LCQ](2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md) · [vision module](../vision-projet/vision-module-decla-eco-organismes.md) · fiches brownfield [`01-fiche-eco-maison.md`](../../recyclique-1.4.4/docs/eco-organismes/01-fiche-eco-maison.md) · [`04-guide-mapping-categories.md`](../../recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md) · dépôt `partenaires/ecomaison/declarations-la-clique/` · `recyclique/api/.../stats_service.py`.

---

## 1. Résumé — 14 champs P0

| Élément | Valeur |
|---------|--------|
| **Partenaire** | Ecomaison (marque **eco-maison**) — REP **DEA**, **Jouets (JJ)**, **ABJ** |
| **Rôle La Clique** | Structure ESS — apports volontaires boutique (hors points Ecomaison permanents) |
| **Plateforme** | `extranet-reemploi-reutilisation.eco-mobilier.fr` |
| **Compte** | N° `0535813` — Association Eco de LA CLIQUE (SIRET `98905144600015`) |
| **Périodicité** | Trimestre civil — **3 déclarations** distinctes (EA, JJ, BJ) |
| **Calendrier soumission** | Ouverture **J+45** après fin trimestre · fenêtre **45 j** (MO ESS **février 2026**) |
| **Champs volume obligatoires** | **14** (6 DEA + 4 JJ + 4 BJ) |
| **Unité portail** | **Tonnes** (`t`) — conversion depuis kg interne (`÷ 1000`) |
| **Urgence patch Recyclique** | **P0** — T1 2026 à finaliser ; T2 ouvre soumission **15/08/2026** |
| **Exemple critique** | DEA entrée « Total éléments d'ameublement » = **2,035 t** (T4 2025 validé) |
| **Soutiens indicatifs** | ~30 €/t gisement · ~130 €/t réemploi (factures T4 : EA **155,95 € HT**) |
| **Recyclage benne** | **Hors exports Recyclique** — données côté Ecomaison (Carte Pro) |
| **Prérequis terrain** | Mapping catégories boutique → codes officiels ; split vente/don réemploi |

### Les 14 cases portail (récapitulatif)

| Filière | # | Libellé officiel (flux) | Exemple T4 2025 |
|---------|---|-------------------------|-----------------|
| **DEA** | 1 | Total éléments d'ameublement — **gisement** | **2,035 t** |
| DEA | 2 | Assises/Sièges — réemploi | 0,330 t |
| DEA | 3 | Couchages — réemploi | 0,124 t |
| DEA | 4 | Décoration textile — réemploi | 0,042 t |
| DEA | 5 | Rangements — réemploi | 0,175 t |
| DEA | 6 | Tables et plans de travail — réemploi | 0,059 t |
| **JJ** | 7 | Jouets en mélange — gisement | 0,227 t |
| JJ | 8 | Autres jeux d'intérieur — réemploi | 0,087 t |
| JJ | 9 | Jeux de plein air — réemploi | 0,002 t |
| JJ | 10 | Jeux de société et puzzles — réemploi | 0,025 t |
| **BJ** | 11 | Articles d'aménagement et d'entretien du jardin — gisement | 0,005 t |
| BJ | 12 | Matériel de bricolage dont l'outillage à main — gisement | 0,125 t |
| BJ | 13 | Articles d'aménagement et d'entretien du jardin — réemploi | 0,003 t |
| BJ | 14 | Matériel de bricolage dont l'outillage à main — réemploi | 0,009 t |

### Priorité relative patch 1.4.5

```text
P0 Ecomaison (ce document)  →  P1 Ecologic  →  P2 Refashion
```

---

## 2. Déclaration finale — cases par filière

D'après PDF synthèse T4 `0535813_13251202431_EA.pdf` / `_JJ.pdf` / `_BJ.pdf` et grille [§ Ecomaison](../eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md).

### 2.1 DEA — Éléments d'ameublement (6 champs)

| Libellé officiel (exact PDF) | Flux | Unité | Source Recyclique | T4 validé |
|------------------------------|------|-------|-------------------|-----------|
| **Total éléments d'ameublement** — « Apports volontaires et autres collectes hors points Ecomaison » | Gisement | **t** | `SUM(poids_kg)` tickets cat. DEA sur trimestre → `/1000` | **2,035 t** |
| **Assises/Sièges** — « Total des sorties (réemploi/ré-utilisation) » | Réemploi | **t** | Ventes + dons : alias `assise`, `* Assises`, `1- Assises`, `Chaises`… | **0,330 t** |
| **Couchages** | Réemploi | **t** | `couchage`, `* Couchage`, `2- Couchage` | **0,124 t** |
| **Décoration textile** | Réemploi | **t** | `déco textile`, `* Décoration textile`, `4- Eléments de décoration textile` | **0,042 t** |
| **Rangements** | Réemploi | **t** | `rangement`, `* Rangement` — **entrées** peuvent fusionner avec plan de pose | **0,175 t** |
| **Tables et plans de travail** | Réemploi | **t** | `plan de pose` + `plan de travail` + `*Plan de pose , plan de travail` | **0,059 t** |

**Soutien T4 EA :** entrées 61,05 € HT + sorties 94,90 € HT = **155,95 € HT**.

### 2.2 Jouets — JJ (4 champs)

| Libellé officiel | Flux | T4 validé |
|------------------|------|-----------|
| **Jouets en mélange** — apports volontaires | Gisement | **0,227 t** |
| **Autres jeux d'intérieur** | Réemploi | **0,087 t** |
| **Jeux de plein air** | Réemploi | **0,002 t** |
| **Jeux de société et puzzles** | Réemploi | **0,025 t** |

Facture T4 JJ : **58,11 € HT**.

### 2.3 Brico-Jardin — BJ (4 champs)

| Libellé officiel | Flux | T4 validé |
|------------------|------|-----------|
| **Articles d'aménagement et d'entretien du jardin** | Gisement | **0,005 t** |
| **Matériel de bricolage dont l'outillage à main** | Gisement | **0,125 t** |
| **Articles d'aménagement et d'entretien du jardin** | Réemploi | **0,003 t** |
| **Matériel de bricolage dont l'outillage à main** | Réemploi | **0,009 t** |

Facture T4 BJ : **7,50 € HT**.

### 2.4 Ce qui N'est PAS à remplir (La Clique)

| Élément | Raison |
|---------|--------|
| Colonnes « Points permanents Ecomaison », « Collecte détenteurs pro », « Porte à porte »… | Toujours **0** — apports volontaires boutique seuls |
| **Recyclage benne** / Carte Pro | Données **chez Ecomaison** — absent des exports Recyclique |
| Textiles, livres, cuisine, EEE, ASL dans exports caisse | **Autres REP** — filtrés manuellement avant saisie |
| Facture / appel de fonds | Émis **après** validation — pas une case de tonnage |

### 2.5 Situation calendaire au 07/07/2026

**Source canon (dates opérationnelles) :** ce cadrage + [`2026-07-07_calendrier-declarations-partenaires.md`](../eco-organismes/2026-07-07_calendrier-declarations-partenaires.md) — règle **J+45** après fin de trimestre, fenêtre **45 jours** (MO ESS fév. 2026). La formulation simplifiée des grilles (« 15ᵉ jour du mois suivant ») est **approximative** ; en cas d'écart, le calendrier projet fait foi pour Recyclique.

| Trimestre | Statut La Clique | Échéance soumission |
|-----------|------------------|---------------------|
| **T4 2025** | **Validé** — PDF + factures | Clôturé |
| **T1 2026** | **En cours** — exports + factures, pas de PDF `0535813_*` | Fenêtre **expirée** 28/06/2026 (retard possible) |
| **T2 2026** | À préparer (activité avr.–juin clos) | Ouverture **15/08/2026** · clôture **27/09/2026** |

---

## 3. Spec exports Recyclique

### 3.1 Problème actuel (terrain)

| Export observé | Symptôme | Risque |
|----------------|----------|--------|
| Entrées T4 `ECO MAISON ENTREES * RECYCLIC.xlsx` | Relativement propres — 1 filière/fichier, `poids_Tn` | Unité **tonnes** vs kg T1 |
| Entrées T1 `Entrée * ecomaison T1 2026 - Copie.xlsx` | **Dump complet** magasin (~17 t/fichier) | Sur-déclaration si pas de filtre |
| Sorties T4 `SORTIES RECYCLIC Ameublement.xlsx` | ~3 247 kg dont ~834 kg **Textiles** hors DEA | Tri manuel systématique |
| Sorties T1 JJ « Société » vs « Plein air » | **Fichiers identiques** (2 685 lignes) | Reclassement depuis export unique |

### 3.2 Filtre par filière REP

```text
INCLUS  → catégories mappées ecomaison_code ∈ {DEA_*, JOUETS_*, ABJ_*}
EXCLU   → ecomaison_code = EXCLUDE | NULL (autre REP : Ecologic, Refashion, Recyclivre…)
EXCLU   → catégories parentes hors filière (👕 Textiles, ⚡ EEE, 📖 Livres…)
```

**Période :** `TicketDepot.created_at` (ou règle unifiée patch) ∈ trimestre civil `[T_start, T_end]`.

**Unité export :** kg en base → **tonnes** à l'export (`value_t = round_half_up(SUM(poids_kg) / 1000, 3)` — arrondi **une fois** sur le total agrégé, pas par ligne).

**Détection colonne import legacy :**

| En-tête détecté | Interprétation | Conversion interne |
|-----------------|----------------|-------------------|
| `poids_Tn`, `poids_t`, suffixe `_Tn` | Valeurs déjà en **tonnes** | `kg = valeur × 1000` |
| `poids_kg`, `Poids (kg)` | **Kilogrammes** | `kg = valeur` |
| Ambigu / absent | Alerte + rejet export décla | — |

**Écart oracle T4 :** somme brute entrées DEA = **2 036 kg** → **2,036 t** arrondi ; portail affiche **2,035 t** (arrondi MO). Tolérance test : `|calc − 2,035| ≤ 0,001 t` sur agrégat final, pas ligne à ligne.

### 3.3 Types d'export cibles

| Export | Contenu | Format | Consommateur |
|--------|---------|--------|--------------|
| **Entrées pré-filtrées** | Tickets agrégés par `ecomaison_code` + filière | xlsx / csv | Opérateur décla |
| **Sorties ventilées** | Ventes + dons par code officiel (5 DEA, 3 JJ, 2 ABJ) | xlsx — feuille `Détails Tickets` compatible legacy | Reclassement minimal |
| **Brouillon portail** | 14 lignes prêtes à copier-coller extranet | csv / json | Saisie manuelle EA/JJ/BJ |
| **Contrôle qualité** | Écarts export brut vs agrégat filtré | json | Admin / dashboard |

### 3.4 Structure export brouillon (cible)

```yaml
# Exemple — non implémenté
declaration:
  partner: ecomaison
  account: "0535813"
  period: 2025-T4
  lines:
    - code: DEA_ENTREE_TOTAL
      filiere: EA
      flux: gisement
      unit: t
      value: 2.035
      source: stats/ecomaison?period=2025-T4&code=DEA_ENTREE_TOTAL
    - code: DEA_ASSISE_SORTIE
      filiere: EA
      flux: reemploi
      unit: t
      value: 0.330
      source: stats/ecomaison?period=2025-T4&code=DEA_ASSISE&flux=vente+don
```

### 3.5 Endpoints cibles (canon — alignés stories 9.EM-02…05)

Chemins alignés sur les stories §8 (`9.EM-02` … `9.EM-05`). Paramètre `period=YYYY-Tn` à résoudre en `start_date`/`end_date` (trimestre civil) — l’API stats actuelle n’expose que des bornes datetime.

| Endpoint | Rôle | Story |
|----------|------|-------|
| `GET /v1/stats/eco-organismes/ecomaison?period=2025-T4` | 14 lignes portail (agrégat unique) | 9.EM-04 |
| `GET /v1/stats/eco-organismes/ecomaison/entries/by-code?period=&filiere=EA` | Drill-down entrées par `ecomaison_code` (LCQ-001) | 9.EM-02 |
| `GET /v1/stats/eco-organismes/ecomaison/exits/by-exit-type?period=` | Split vente / don / recyclage (LCQ-003) | 9.EM-03 |
| `GET /v1/admin/declarations/ecomaison/export?period=&format=csv` | Fichier pré-rempli 14 champs | 9.EM-05 |
| `GET /v1/admin/declarations/ecomaison/export-entries?period=&filiere=EA` | Entrées tickets pré-filtrées | 9.EM-05 |
| `GET /v1/admin/declarations/ecomaison/export-exits?period=&filiere=EA` | Sorties caisse ventilées | 9.EM-05 |

**Hors périmètre patch :** aucune route `eco-organismes` ni `declarations/ecomaison` dans `contracts/openapi` ni `endpoints/stats.py` au 07/07/2026 — faisabilité via nouveau `EcoOrganismeStatsService` + routes dédiées (cf. §7).

---

## 4. Mapping — catégories boutique → codes Ecomaison

### 4.1 Principes (fiche 01 + guide 04)

- **Une catégorie boutique** → **un** `ecomaison_code` + `filiere` (EA | JJ | BJ) + `flux` (entree | sortie_vente | sortie_don | exclude).
- **Alias multiples** : libellés numérotés officiels (`1- Assises`), boutique (`Chaises`, emojis), préfixe T1 (`* Assises`) → **même code**.
- Chevauchements **autres REP** : EEE → Ecologic ; textiles habillement → Refashion ; livres → Recyclivre.

### 4.2 Niveau 1 — Catégorie parente → filière

| Catégorie principale Recyclique | Filière | Hors scope |
|--------------------------------|---------|------------|
| `Eléments d'ameublement ménagers (EA)` / `🪑 Ameublement` | **DEA** | |
| `Jeux et jouets (JJ)` / `Jeux` | **Jouets** | |
| `(ABJ) Articles de bricolage et de jardin` / `Outillage` | **ABJ** | |
| `👕 Textiles`, `📖 Livres`, `🍽️ Cuisine`, `⚡ EEE`, ASL… | | **Autre REP** |

### 4.3 Niveau 2 — Entrées (vérité T4)

| Catégorie secondaire Recyclique | `ecomaison_code` | Confiance | kg T4 (ordre) |
|--------------------------------|------------------|-----------|---------------|
| `1- Assises`, `Chaises`, `Petit meuble/chaise en bois massif`… | `DEA_ASSISE` | Forte / moyenne | ~478 (famille assises T4 : 361+73+44 kg) |
| `2- Couchage` | `DEA_COUCHAGE` | Forte | 29 |
| `3- Rangement et plan de pose et de travail` | `DEA_RANGEMENT_ENTREE` | Moyenne — **fusionné en entrée** ; sorties → `DEA_RANGEMENT` / `DEA_PLAN_POSE` | ~1 442 |
| `4- Eléments de décoration textile` | `DEA_DECO_TEXTILE` | Forte | 16 |
| `A - Meuble Divers` | `DEA_MEUBLE_DIVERS` | Faible — `requires_manual_split: true` | 36 |
| `1- Jeux de plein air` | `JOUETS_PLEIN_AIR` | Forte | 2 |
| `2- Jeux société et puzzle` | `JOUETS_SOCIETE` | Forte | ~49 (entrée → `JOUETS_ENTREE_TOTAL`) |
| `3- autres jeux d'intérieur` | `JOUETS_INTERIEUR` | Forte | ~89 (entrée → `JOUETS_ENTREE_TOTAL`) |
| `A - Jeux Divers` | `JOUETS_INTERIEUR` | Faible — **défaut PO §11.4** ; alerte si > 0 sans reclassement sortie | 87 |
| `1- Materiel de bricolage`, `A - Outillage Divers` | `ABJ_BRICO_ENTREE` | Moyenne | 125 |
| `2- Materiel destinés à l'aménagement du jardin` | `ABJ_JARDIN_ENTREE` | Forte | 5 |

### 4.4 Niveau 2 — Sorties réemploi (reclassement T4)

| Libellé export / saisie manuelle | `ecomaison_code` | kg T4 |
|----------------------------------|------------------|-------|
| `assise` | `DEA_ASSISE` | 330 |
| `couchage` | `DEA_COUCHAGE` | 124 |
| `rangement` | `DEA_RANGEMENT` | 175 |
| `plan de pose` + `plan de travail` | `DEA_PLAN_POSE` | 59 |
| `déco textile` | `DEA_DECO_TEXTILE` | 42 |
| `autres jeux d'intérieur` | `JOUETS_INTERIEUR` | 87 |
| `jeux de société` | `JOUETS_SOCIETE` | 25 |
| `jeux de plein air` | `JOUETS_PLEIN_AIR` | 2 |
| `articles jardin` (réemploi) | `ABJ_JARDIN_SORTIE` | 3 |
| `matériel bricolage` / outillage (réemploi) | `ABJ_BRICO_SORTIE` | 9 |

### 4.5 Cas particuliers à figer en config

| Cas | Règle proposée |
|-----|----------------|
| **Rangement + plan de pose fusionnés en entrée** | Entrée → `DEA_RANGEMENT_ENTREE` (agrégat) ; sorties → scinder `DEA_RANGEMENT` / `DEA_PLAN_POSE` |
| **`A - * Divers`** (Meuble, Jeux, Outillage) | **Jeux** → `JOUETS_INTERIEUR` (défaut). **Meuble** → `DEA_MEUBLE_DIVERS` inclus dans total entrée + alerte si > 0 sans reclassement. **Outillage** → `ABJ_BRICO_ENTREE` |
| **Chaises de jardin** | **Défaut : `ABJ_JARDIN_ENTREE`** (fiche 01 FAQ + guide 04). `Chaises` sans qualifiant → `DEA_ASSISE`. Patterns `chaise(s)? de jardin`, `mobilier jardin`, `transat` → `ABJ_JARDIN_ENTREE` |
| **`NE PLUS UTILISER…`** | `EXCLUDE` ou redirect vers code successeur |
| **Fichier brico T4** | 1 M lignes vides — ignorer lignes sans `poids_Tn` |

### 4.6 YAML cible (extrait)

**Codes canon complets (14 portail + intermédiaires)** : tableau oracles §8 (`DEA_*`, `JOUETS_*`, `ABJ_*`, `DEA_RANGEMENT_ENTREE`, `EXCLUDE`). L'extrait ci-dessous illustre DEA ; JJ/BJ suivent la même structure (`JOUETS_ENTREE_TOTAL`, `JOUETS_INTERIEUR`, `JOUETS_SOCIETE`, `JOUETS_PLEIN_AIR`, `ABJ_JARDIN_ENTREE`, `ABJ_BRICO_ENTREE`, `ABJ_JARDIN_SORTIE`, `ABJ_BRICO_SORTIE`).

```yaml
# config/eco-organismes/ecomaison-mapping.yaml — à créer
partner: ecomaison
version: 1
codes:
  DEA_ENTREE_TOTAL:
    filiere: EA
    flux: [entree]
    portail_label: "Total éléments d'ameublement"
    aggregate_of: [DEA_ASSISE, DEA_COUCHAGE, DEA_RANGEMENT_ENTREE, DEA_DECO_TEXTILE, DEA_MEUBLE_DIVERS]
  DEA_ASSISE:
    filiere: EA
    flux: [entree, sortie_vente, sortie_don]
    portail_label: "Assises/Sièges"
mappings:
  - recyclique_category_pattern: "^(1- Assises|\\* Assises|Chaises)$"
    ecomaison_code: DEA_ASSISE
  - recyclique_category_pattern: "^3- Rangement et plan de pose et de travail$"
    ecomaison_code: DEA_RANGEMENT_ENTREE
    note: "Fusion entrée — scinder en sortie"
  - recyclique_category_pattern: "^assise$"
    ecomaison_code: DEA_ASSISE
    flux: [sortie_vente, sortie_don]
  - recyclique_category_pattern: "^couchage$"
    ecomaison_code: DEA_COUCHAGE
    flux: [sortie_vente, sortie_don]
  - recyclique_category_pattern: "^👕 Textiles$"
    ecomaison_code: EXCLUDE
    redirect_partner: refashion
  - recyclique_category_pattern: "^1- Petits appareils em melange\\(PAM\\)$"
    ecomaison_code: EXCLUDE
    redirect_partner: ecologic
```

---

## 5. Règles calcul kg / t par trimestre

### 5.1 Paramètres

```text
Période décla     = trimestre civil (T1 jan–mar … T4 oct–déc)
Filtre partenaire = mapping YAML → ecomaison_code ≠ EXCLUDE
Unité canonique   = kg en base ; conversion t à l'export (÷ 1000, 3 décimales)
Date entrée       = TicketDepot.created_at ∈ période
Date sortie       = CashSession / SaleItem date ∈ période
```

### 5.2 Formules par flux

| Flux décla | Formule | Champs source |
|------------|---------|---------------|
| **Gisement DEA total** | `SUM(poids_kg)` tickets mappés filière EA, hors `is_exit=true` | `LigneDepot` + mapping |
| **Gisement JJ / BJ** | Idem filière JJ ou BJ | Idem |
| **Réemploi par sous-cat.** | `SUM(poids_kg)` sorties **vente + don** mappées code | `SaleItem` + dons matière (LCQ-003) |
| **Recyclage benne** | *Non calculé Recyclique* | Ecomaison Carte Pro |
| **DEA_ENTREE_TOTAL** | Somme codes enfants DEA entrée (incl. `A - Meuble Divers` si mappé) | Agrégat 14 champs |

### 5.3 Règle split entrée « Rangement + plan de pose »

```text
ENTRÉE (ticket) — code unique DEA_RANGEMENT_ENTREE :
  T4 : "3- Rangement et plan de pose et de travail" (fusion officielle)
  T1 : "* Rangement" OU "*Plan de pose , plan de travail" (séparés en caisse)
    → les deux mappent vers DEA_RANGEMENT_ENTREE (pas de scission entrée)
    → compte dans DEA_ENTREE_TOTAL
    → NE PAS double-compter en sortie

SORTIE (caisse) — scission obligatoire :
  libellé "rangement"      → DEA_RANGEMENT
  libellé "plan de pose"   → DEA_PLAN_POSE
  libellé "plan de travail"→ DEA_PLAN_POSE
```

**Défaut PO :** entrée = toujours agrégat `DEA_RANGEMENT_ENTREE` ; sortie = jamais fusionnée. Oracle T4 sorties : 175 kg rangement + 59 kg plan de pose (44+15).

### 5.4 Contrôles qualité (pré-soumission)

| Contrôle | Règle | Seuil T4 référence |
|----------|-------|-------------------|
| Cohérence DEA entrée | `|calc − portail| / portail` | **2,035 t** ± 0,001 t |
| Sorties DEA ≤ entrées DEA (ordre de grandeur) | Alerte si sorties > 50 % entrées sans justification | 0,730 t / 2,035 t |
| Pollution export brut | `masse_hors_REP / masse_totale` | Sorties ameublement T4 : ~78 % hors DEA (2 517 / 3 247 kg) |
| Unité | Rejet si colonne `poids_Tn` traitée comme kg | Leçon T4/T1 |
| Catégories obsolètes | Alerte si `NE PLUS UTILISER` > 0 kg | ~1 500 kg T1 entrées |

### 5.5 Calendrier 2026 (MO février 2026)

| Trimestre | Fin activité | Ouverture soumission | Clôture |
|-----------|--------------|----------------------|---------|
| T1 2026 | 31/03/2026 | 15/05/2026 | **28/06/2026** ← expiré |
| **T2 2026** | 30/06/2026 | **15/08/2026** | **27/09/2026** |
| T3 2026 | 30/09/2026 | 15/11/2026 | 28/12/2026 |

---

## 6. Split vente / don / recyclage (LCQ-003)

### 6.1 Besoin terrain

Le MO Ecomaison regroupe **ventes + dons** dans le réemploi. Recyclique doit néanmoins **distinguer** en amont pour :

- Dashboard La Clique (verbatim LCQ-003)
- Détection sous-déclaration réemploi (dons matière non ventilés en kg)
- Exclusion du recyclage benne des cases réemploi

### 6.2 Typologie sorties cible

| `exit_type` | Définition | Source données actuelle | Gap |
|-------------|------------|-------------------------|-----|
| **vente** | Ligne caisse payante (`SaleItem`, poids > 0) | `/stats/sales/by-category` | Pas de sous-catégorie |
| **don** | Don matière sortant (structure, −18 ans **kg**) | `LigneDepot.is_exit=true` partiel ; dons caisse `Total Dons (€)` sans kg | **Poids don non agrégé** |
| **recyclage** | Destination RECYCLAGE / benne / déchèterie | Champ `destination` en saisie réception | **Absent dashboard + stats décla** |

### 6.3 Règle agrégation portail

```text
CASE_PORTAIL_REEMPLOI(code, trimestre) =
    SUM_poids_kg(sorties, exit_type IN {vente, don}, ecomaison_code = code)
    ÷ 1000

CASE_PORTAIL_RECYCLAGE =
    NON RENSEIGNÉE dans les 14 champs — benne côté Ecomaison
```

### 6.4 Dons — périmètre (décisions PO figées)

| Type don | Comptage patch 1.4.5 | Note |
|----------|----------------------|------|
| Don matière sortie réception (`is_exit=true`, gratuit) | **Inclure** en `exit_type=don` | LCQ-003 cœur |
| Don caisse −18 ans (kg sans €) | **Inclure** en `exit_type=don` si catégorie mappée Ecomaison | Aligné Refashion |
| Ligne caisse `SaleItem` à 0 € | **`exit_type=vente`** par défaut | Sauf `is_exit=true` sur ticket lié **ou** note contenant `don` (insensible casse) → `don` |
| Don structure hors caisse (pas de `SaleItem`) | **`exit_type=don`** via `LigneDepot.is_exit=true` | Prioritaire sur règle caisse |

**Oracle T4 :** seed validé = ventes seules — tests 9.EM-03 vente+don à compléter quand seed enrichi.

**Non inclus patch 1.4.5 :** dons € session (`Total Dons (€)`) sans poids matière — exposés dashboard, hors agrégat portail.

### 6.5 Exposition dashboard + export

| Vue | Dimensions | Story liée |
|-----|------------|------------|
| Sorties DEA par sous-cat. × exit_type | `DEA_ASSISE` × {vente, don} | 9.EM-03 |
| Totaux trimestriels réemploi | Somme vente+don par code (→ portail) | 9.EM-04 |
| Lignes recyclage (hors décla 14 champs) | Info / contrôle interne | 9.EM-03 |

---

## 7. Gaps `stats_service` (canon v2)

Fichier : `recyclique/api/src/recyclic_api/services/stats_service.py` — consommé par `endpoints/stats.py`.

| # | Méthode actuelle | Comportement | Gap Ecomaison / LCQ |
|---|------------------|--------------|---------------------|
| G1 | `get_reception_by_category` | Agrège **enfants → parent** uniquement | **LCQ-001** : pas de drill-down sous-catégorie officielle |
| G2 | `get_reception_by_category` | Filtre `is_exit=false` | OK entrées — mais pas de filtre `ecomaison_code` |
| G3 | `get_sales_by_category` | Agrège ventes par **catégorie parente** | **LCQ-002** : pas de sous-catégorie sortie |
| G4 | `get_sales_by_category` | Ventes `SaleItem` ; fallback brownfield `LigneDepot.is_exit=true` si aucune ligne caisse, toujours rollup parent | **LCQ-003** : pas de split vente/don ; dons matière non ventilés par `ecomaison_code` |
| G5 | *(absent dans stats)* | Champ `LigneDepot.destination` (`MAGASIN`/`RECYCLAGE`/`DECHETERIE`) **existe en modèle** mais non agrégé ; pas de dimension `exit_type` | Recyclage invisible au dashboard / décla ; exploitable dans `EcoOrganismeStatsService` |
| G6 | *(absent)* | Pas de paramètre `partner=ecomaison` | Aucun filtre multi-éco-organisme |
| G7 | *(absent)* | Pas de conversion t à l'export | Risque ×1000 (T4 `poids_Tn` vs T1 `poids_kg`) |
| G8 | `get_reception_summary` | Totaux globaux | Insuffisant pour 14 cases |
| G9 | Catégories `deleted_at` | Conservées en stats (B48-P1) | OK décla historique — mapping doit inclure archivées |
| G10 | *(absent)* | Pas d'endpoint admin export décla | Workflow xlsx manuel |

**Piste implémentation :** nouveau service `EcoOrganismeStatsService` (ou extension `StatsService`) consommant le YAML mapping — **ne pas** surcharger les méthodes dashboard existantes sans versionner l'API (`/v1/stats/eco-organismes/...`).

**Note :** `get_sales_by_business_tag_and_category` (Story 24.9) ventile par tag métier × catégorie parente — **complément** possible pour LCQ-003 interne, mais ne remplace pas le mapping `ecomaison_code` ni les 14 cases portail.

---

## 8. Backlog stories chiffré — scénario T4 DEA 2,035 t

**Nombre de stories proposées : 6** (préfixe `9.EM-` — Epic 9 extension Ecomaison).

### Jeu de référence T4 2025 (oracles de test)

Source : PDF `0535813_*` + exports `declarations-la-clique/2025-T4/` — **vérité terrain validée**.

| Code | Flux | Oracle (t) | Oracle (kg) |
|------|------|------------|-------------|
| `DEA_ENTREE_TOTAL` | gisement | **2,035** | 2 035 |
| `DEA_ASSISE` | réemploi | 0,330 | 330 |
| `DEA_COUCHAGE` | réemploi | 0,124 | 124 |
| `DEA_DECO_TEXTILE` | réemploi | 0,042 | 42 |
| `DEA_RANGEMENT` | réemploi | 0,175 | 175 |
| `DEA_PLAN_POSE` | réemploi | 0,059 | 59 |
| `JOUETS_ENTREE_TOTAL` | gisement | 0,227 | 227 |
| `JOUETS_INTERIEUR` | réemploi | 0,087 | 87 |
| `JOUETS_PLEIN_AIR` | réemploi | 0,002 | 2 |
| `JOUETS_SOCIETE` | réemploi | 0,025 | 25 |
| `ABJ_JARDIN_ENTREE` | gisement | 0,005 | 5 |
| `ABJ_BRICO_ENTREE` | gisement | 0,125 | 125 |
| `ABJ_JARDIN_SORTIE` | réemploi | 0,003 | 3 |
| `ABJ_BRICO_SORTIE` | réemploi | 0,009 | 9 |

**Détail entrées DEA (composition 2 035 kg) :**

| `category_label` export T4 | kg |
|----------------------------|-----|
| `3- Rangement et plan de pose et de travail` | 1 442 |
| `1- Assises` | 361 |
| `Chaises` | 73 |
| `Petit meuble/chaise en bois massif` | 44 |
| `A - Meuble Divers` | 36 |
| `Gros meuble en bois massif` | 34 |
| `2- Couchage` | 29 |
| `4- Eléments de décoration textile` | 16 |
| **Total** | **2 035** = **2,035 t** (export `poids_Tn` T4 — somme catégories) |

### 9.EM-01 — Mapping YAML catégories → Ecomaison

**Objectif :** Fichier `ecomaison-mapping.yaml` + service résolution catégorie → `ecomaison_code` + alias.

**Critères d'acceptation :**

- [ ] 14 codes portail + codes intermédiaires (`DEA_RANGEMENT_ENTREE`, `EXCLUDE`)
- [ ] Alias T4 (`Chaises`, `1- Assises`) et T1 (`* Assises`) → même code
- [ ] Redirects : textile → `refashion`, PAM → `ecologic`
- [ ] Tests unitaires : **≥ 20** libellés dépôt dont composition DEA 2 035 kg
- [ ] Documentation : arbre décision §4.5

---

### 9.EM-02 — Stats entrées sous-catégories (LCQ-001)

**Objectif :** Drill-down réceptions par `ecomaison_code` sans rollup parent seul.

**Critères d'acceptation :**

- [ ] `GET /v1/stats/eco-organismes/ecomaison/entries/by-code?period=2025-T4&filiere=EA`
- [ ] Somme codes DEA entrée = **2,035 t** ± 0,001 sur seed T4
- [ ] Exclut catégories `EXCLUDE` (textile, EEE…)
- [ ] Widget ou JSON consommable dashboard

---

### 9.EM-03 — Split sorties vente / don / recyclage (LCQ-003)

**Objectif :** Dimension `exit_type` sur sorties mappées Ecomaison.

**Critères d'acceptation :**

- [ ] `GET /v1/stats/eco-organismes/ecomaison/exits/by-exit-type?period=2025-T4`
- [ ] Réemploi portail = `vente + don` par code
- [ ] Sur seed T4 : `DEA_ASSISE` vente+don = **330 kg** (vente seule si dons absents du seed)
- [ ] Lignes `recyclage` exposées mais **hors** export 14 champs

---

### 9.EM-04 — Agrégats trimestriels 14 champs

**Objectif :** Endpoint unique produisant les 14 lignes portail.

**Critères d'acceptation :**

- [ ] `GET /v1/stats/eco-organismes/ecomaison?period=2025-T4`
- [ ] Réponse JSON : 14 objets `{code, filiere, flux, unit, value_t, sources}`
- [ ] **DEA_ENTREE_TOTAL = 2.035** ; somme 5 sorties DEA = **0.730 t**
- [ ] Prérequis **9.EM-06** appliqué (split rangement/plan de pose, exclusions)
- [ ] Tests intégration pytest sur jeu seed T4 complet (table oracles §8)

---

### 9.EM-05 — Export brouillon décla portail

**Objectif :** CSV/xlsx téléchargeable aligné PDF `0535813_*`.

**Critères d'acceptation :**

- [ ] `GET /v1/admin/declarations/ecomaison/export?period=2025-T4&format=csv`
- [ ] Colonnes : `filiere`, `code`, `portail_label`, `flux`, `tonnes`, `period`, `account`
- [ ] Bannière « brouillon — vérifier avant soumission extranet »
- [ ] Export entrées pré-filtrées DEA : total **2,035 t** (pas 17 t dump T1)
- [ ] Test e2e : export T4 seed → 14 lignes cohérentes avec 9.EM-04

---

### 9.EM-06 — Règles métier & exclusions

**Objectif :** Split rangement/plan de pose, `A - Divers`, chaises jardin, catégories obsolètes.

**Critères d'acceptation :**

- [ ] Entrée fusionnée `3- Rangement…` → un seul compteur entrée ; sorties scindées
- [ ] Alerte export si `A - Meuble Divers` > 0 sans `manual_split_done`
- [ ] `NE PLUS UTILISER…` → `EXCLUDE` + rapport lignes affectées
- [ ] Règle configurable `chaises_jardin.default: ABJ_JARDIN_ENTREE` + patterns override (§4.5)
- [ ] Tests : 5 cas particuliers §4.5

### Ordre d'implémentation suggéré

```text
9.EM-01 (mapping) → 9.EM-06 (règles métier) → 9.EM-02 (entrées LCQ-001) → 9.EM-03 (split LCQ-003) → 9.EM-04 (14 champs) → 9.EM-05 (export)
```

> **Dépendance** : 9.EM-04 consomme les règles rangement/plan de pose et `A - Divers` de 9.EM-06 — ne pas valider les oracles T4 avant 9.EM-06.

**Synergies :** infrastructure YAML partagée avec Ecologic (P1) et Refashion (P2) ; 9.EM-02/03 alimentent le dashboard LCQ transversal.

---

## 9. Hors scope

| Élément | Raison |
|---------|--------|
| Saisie automatique API extranet Ecomaison | Pas d'API partenaire documentée |
| **Recyclage benne** / Carte Pro / sensibilisation BJ | Données et workflow **côté Ecomaison** |
| Colonnes portail « Points permanents », « Porte à porte »… | Toujours **0** La Clique — pas de calcul |
| Facturation / appel de fonds (30 €/t, 130 €/t) | Émis par Ecomaison post-validation — hors moteur décla v1 |
| **Ecologic, Refashion, Valdelia, Recyclivre** | Patches séparés (P1/P2) — seuls les `redirect` mapping sont touchés |
| Mode **comptage + abaques** (alternative MO pesée) | La Clique en **pesée** — non documenté comptage |
| Nettoyage migration catégories Paheko (`NE PLUS UTILISER`) | Chantier config boutique — alerte seulement en 9.EM-06 |
| Intégration Paheko Saisie au poids | Module Paheko distinct — post patch 1.4.5 |
| Fichier brico T4 1 M lignes vides | Export legacy — filtre lignes vides côté export, pas correction source |
| T1 2026 **soumission portail** | Opération terrain — le patch fournit les chiffres, pas le dépôt |

---

## 10. Liens

| Ressource | Chemin |
|-----------|--------|
| Grilles décla finale § Ecomaison | [`references/eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md`](../eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md) |
| Analyse mapping Ecomaison | [`references/eco-organismes/partenaires/ecomaison/2026-07-07_analyse-declarations-mapping.md`](../eco-organismes/partenaires/ecomaison/2026-07-07_analyse-declarations-mapping.md) |
| Déclarations La Clique T4/T1 | [`references/eco-organismes/partenaires/ecomaison/declarations-la-clique/`](../eco-organismes/partenaires/ecomaison/declarations-la-clique/) |
| Calendrier partenaires | [`references/eco-organismes/2026-07-07_calendrier-declarations-partenaires.md`](../eco-organismes/2026-07-07_calendrier-declarations-partenaires.md) |
| Fiche technique eco-maison (01) | [`recyclique-1.4.4/docs/eco-organismes/01-fiche-eco-maison.md`](../../recyclique-1.4.4/docs/eco-organismes/01-fiche-eco-maison.md) |
| Guide mapping catégories (04) | [`recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md`](../../recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md) |
| Feedback LCQ-001…003 | [`references/artefacts/2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md`](2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md) |
| Vision module décla | [`references/vision-projet/vision-module-decla-eco-organismes.md`](../vision-projet/vision-module-decla-eco-organismes.md) |
| Inventaire dépôt éco-organismes | [`references/artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md`](2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md) |
| Cadrage Refashion (P2) | [`references/artefacts/2026-07-07_05_cadrage-patch-1.4.5-refashion.md`](2026-07-07_05_cadrage-patch-1.4.5-refashion.md) |
| Index éco-organismes | [`references/eco-organismes/index.md`](../eco-organismes/index.md) |
| Extraction JSON T4 | `log/cursor-agent/ecomaison-final.json` |
| `stats_service` canon v2 | [`recyclique/api/src/recyclic_api/services/stats_service.py`](../../recyclique/api/src/recyclic_api/services/stats_service.py) |
| Kanban LCQ stats | [`docs/ideas/kanban/IDEA-2026-07-05-001.md`](../../docs/ideas/kanban/IDEA-2026-07-05-001.md) |

---

## 11. Décisions PO — levée ambiguïtés (audit QA 2026-07-07)

**Passe :** `pass-assumption-audit` · **Statut :** défauts figés pour implémentation patch 1.4.5 · révision PO post-T2 si écarts terrain.

### 11.1 Dons (§6.4)

| Hypothèse implicite | Décision PO | Impact si faux |
|---------------------|-------------|----------------|
| Les dons matière passent par `is_exit=true` | **Confirmé** — source primaire don | Sous-déclaration réemploi |
| Lignes caisse à 0 € = dons | **Rejeté** — défaut `vente` ; override via ticket lié ou note `don` | Sur-déclaration réemploi |
| Dons −18 ans kg comptent en réemploi Ecomaison | **Confirmé** — même règle que Refashion | Écart JJ/DEA si filière mal mappée |

### 11.2 Chaises de jardin (DEA vs ABJ)

| Contexte | Code | Référence |
|----------|------|-----------|
| Libellé explicite jardin (`chaise de jardin`, `mobilier jardin`, `transat`, `salon de jardin`) | **`ABJ_JARDIN_ENTREE`** | Fiche 01 FAQ L606-607 · guide 04 cas 3 |
| `Chaises` / `1- Assises` sans qualifiant extérieur | **`DEA_ASSISE`** | Précédent T4 (73 + 362 kg) |
| Chaises de plage pliantes | **`ABJ_JARDIN_ENTREE`** | Fiche 01 exclusions Assise |

**Config YAML :** `chaises_jardin.default: ABJ_JARDIN_ENTREE` + liste `patterns_assise_interieur` pour éviter faux positifs.

### 11.3 Fusion rangement / plan de pose

| Flux | Règle | Oracle T4 |
|------|-------|-----------|
| **Entrée** | Un seul code `DEA_RANGEMENT_ENTREE` — fusion T4 **et** alias T1 `* Rangement` / `*Plan de pose…` | 1 442 kg entrée |
| **Sortie réemploi** | Scission `DEA_RANGEMENT` (175 kg) + `DEA_PLAN_POSE` (59 kg) | Jamais fusionner en sortie |
| **Portail** | Cases distinctes « Rangements » et « Tables et plans de travail » | 5 sorties DEA |

### 11.4 Paniers `A - * Divers`

| Panier | Entrée (défaut) | Sortie | Alerte export |
|--------|-----------------|--------|---------------|
| `A - Meuble Divers` | `DEA_MEUBLE_DIVERS` → inclus dans `DEA_ENTREE_TOTAL` | Reclassement manuel opérateur | Si > 0 kg et `manual_split_done=false` |
| `A - Jeux Divers` | `JOUETS_INTERIEUR` (proximité T4 « autres jeux d'intérieur ») | Ventiler société / plein air / intérieur si possible | Idem |
| `A - Outillage Divers` | `ABJ_BRICO_ENTREE` | — | Non bloquant |

**Export brouillon :** warning, pas blocage — l'opérateur valide avant soumission extranet.

### 11.5 Unités kg / tonnes

| Règle | Détail |
|-------|--------|
| Stockage canon | **kg** (`poids_kg` float) |
| Export portail | `round_half_up(sum_kg / 1000, 3)` **une fois** par case |
| Import legacy | Détection par en-tête colonne (§3.2) — jamais par magnitude seule |
| Tolérance test | `|calc − oracle_portail| ≤ 0,001 t` sur agrégat ; écart 2 036 → 2,035 t documenté |

---

## 12. FMEA — modes d'échec déclaration Ecomaison

Analyse FMEA (passe QA `pass-fmea-declaration`, 2026-07-07) sur les cinq modes d'échec observés en terrain T4/T1 et les gaps `stats_service` §7. Échelle **S/O/D** : 1 (faible) → 10 (critique). **RPN** = S × O × D.

| # | Mode d'échec | Effet sur décla | S | O | D | RPN | Preuve terrain (source) | Mitigation documentée | Stories |
|---|--------------|-----------------|---|---|---|-----|-------------------------|----------------------|---------|
| **F1** | **Dump entrées T1 non filtré** | Sur-déclaration gisement (~**8×** sur DEA : 17,1 t export brut vs **2,035 t** portail T4) | 9 | 8 | 3 | **216** | `Entrée AMEUBLEMENT T1 2026` : **17 135,91 kg**, 2 276 lignes — textiles, PAM, livres inclus (`ecomaison-final.json`) | Filtre `ecomaison_code ∉ {EXCLUDE,NULL}` + filière ; export entrées pré-filtrées ; contrôle QC `masse_hors_REP / masse_totale` §5.4 | 9.EM-01, 9.EM-02, 9.EM-05 |
| **F2** | **Pollution textiles / hors-REP en sorties** | Réemploi DEA gonflé ou rejet portail ; tri manuel systématique | 7 | 7 | 4 | **196** | T4 `SORTIES RECYCLIC Ameublement.xlsx` : **834 kg textiles** / **3 247 kg** total (~26 %) ; ~78 % masse hors codes DEA réemploi | `EXCLUDE` + `redirect_partner: refashion` ; export sorties ventilé par code officiel (5 DEA / 3 JJ / 2 ABJ) ; seuil pollution §5.4 | 9.EM-01, 9.EM-03, 9.EM-05 |
| **F3** | **Erreur unité ×1000** (kg traité comme t ou inverse) | Déclaration hors échelle (milliers de tonnes ou quasi-nul) | 10 | 5 | 4 | **200** | T4 entrées colonne `poids_Tn` ; T1 entrées `poids_kg` ; `stats_service` sans conversion t (G7) | Canon kg base → `÷ 1000` à l'export (`value_t`, 3 déc.) ; métadonnée `unit: t` ; contrôle §5.4 « rejet si `poids_Tn` traité comme kg » ; test oracle **2,035 t** | 9.EM-04, 9.EM-05, §5.1 |
| **F4** | **Export JJ dupliqué** (même dump, reclassement manuel) | Triple saisie ou mauvais code JJ (société / plein air / intérieur) | 6 | 8 | 4 | **192** | T1 `JEUX DE PLEIN AIR` vs `JEUX DE SOCIETE` : **2 684,9 kg** identiques, ~3 096 lignes quasi-identiques (14 lignes diff.) | **Un seul** export sorties ventilé (`export-exits`) ; colonne `ecomaison_code` ; **interdiction** workflow « 3 fichiers copiés » ; test pytest sommes par code ≠ doublon global | 9.EM-03, 9.EM-05 |
| **F5** | **Catégories obsolètes `NE PLUS UTILISER…`** | Pollution entrées ; code mapping invalide | 6 | 7 | 4 | **168** | T1 dump ameublement : **1 516,54 kg** sur `NE PLUS UTILISER Rangement…` (+ DVD-CD, brico…) | `EXCLUDE` mapping ; rapport lignes affectées à l'export ; alerte si > 0 kg (chantier config boutique hors scope) | 9.EM-06 |
| **F6** | **Dons matière kg non agrégés** (LCQ-003) | Sous-déclaration réemploi portail | 7 | 6 | 6 | **252** | `get_sales_by_category` ignore dons (G4) ; dons caisse −18 ans sans kg | Dimension `exit_type` {vente, don} ; réemploi = vente + don ; exposition dashboard | 9.EM-03 |

**Contrôles de détection transverses (pré-soumission)** :

| Contrôle | Déclencheur | Action |
|----------|-------------|--------|
| Oracle T4 DEA entrée | `|calc − 2,035 t| > 0,001 t` | Bloquer export brouillon |
| Ratio pollution | `masse_hors_REP / masse_totale > 0,15` sur export sorties | Alerte + liste catégories exclues |
| Unité | Colonne source `poids_Tn` sans conversion OU total > 50 t sur trimestre La Clique | Rejet export + message unité |
| Doublon JJ | Somme codes JJ réemploi > somme ventes JJ mappées × 1,05 | Alerte reclassement |
| Obsolètes | Lignes `NE PLUS UTILISER` > 0 kg post-filtre | Rapport admin obligatoire |

### 12.1 Règle chaises de jardin (mitigation F1/F2)

| Contexte | `ecomaison_code` | Filière |
|----------|------------------|---------|
| `Chaises` / `1- Assises` sans qualifiant jardin | `DEA_ASSISE` | EA |
| Patterns `chaise(s)? de jardin`, `mobilier jardin`, `transat`, `bain de soleil` | `ABJ_JARDIN_ENTREE` (entrée) / `ABJ_JARDIN_SORTIE` (sortie) | BJ |
| **Défaut PO** (fiche 01 + guide 04) | `chaises_jardin.default: ABJ_JARDIN_ENTREE` pour patterns explicites ; `DEA_ASSISE` sinon | — |

Configurable dans `ecomaison-mapping.yaml` § `rules.chaises_jardin`.

### 12.2 Règle `A - * Divers` (mitigation F1/F5)

| Catégorie | Code entrée | Sortie réemploi | Alerte |
|-----------|-------------|-----------------|--------|
| `A - Meuble Divers` | `DEA_MEUBLE_DIVERS` (inclus `DEA_ENTREE_TOTAL`) | Reclassement manuel vers sous-codes DEA | `requires_manual_split: true` si > 0 kg |
| `A - Jeux Divers` | `JOUETS_INTERIEUR` (défaut PO) | Ventiler société / intérieur / plein air | Alerte si sortie sans reclassement |
| `A - Outillage Divers` | `ABJ_BRICO_ENTREE` | `ABJ_BRICO_SORTIE` | — |

---

## Retour orchestrateur (synthèse)

| Champ | Valeur |
|-------|--------|
| **Chemin artefact** | `references/artefacts/2026-07-07_03_cadrage-patch-1.4.5-ecomaison.md` |
| **Nb stories** | **6** (`9.EM-01` … `9.EM-06`) |
| **Champs portail** | **14** (6 DEA + 4 JJ + 4 BJ) |
| **Oracle critique** | DEA entrée **2,035 t** (T4 2025 validé) |
| **Urgence** | **P0** — T1 à boucler ; T2 soumission dès **15/08/2026** |
| **Gaps bloquants** | Mapping YAML · sous-catégories stats · split vente/don · exports non filtrés |
