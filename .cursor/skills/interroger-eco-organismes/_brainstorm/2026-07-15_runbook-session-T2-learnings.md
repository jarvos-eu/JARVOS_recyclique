# Mémo runbook — session Ecologic + Ecomaison T2 2026

**Date rédaction :** 2026-07-15  
**Contexte :** mission assistance décla trimestre 01/04–30/06/2026 · dump `recyclic_db_export_20260707_152448.dump`  
**Statut :** brouillon agent → à fusionner dans `runbook.md` / évolution skill v2

---

## 1. Ce que cette mission a réellement couvert

Le skill v1 décrit surtout **CSV template → SQL → CSV rempli**. La session T2 a en plus exigé :

| Couche | Livrable | Outil |
|--------|----------|-------|
| **Agrégats auditables** | `queries-decla-t2.sql`, `interrogation-*_rempli.csv`, `Complément-DEC_REE-T2-2026.csv` | `interroger_eco_org.py` + psql |
| **Tableur Germaine** | `DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods` | `_tmp_fill_germaine_ods_v2.py` (lxml) |
| **Doc structure** | `DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md` | extraction JSON one-shot |

**Leçon :** une décla terrain La Clique = **deux sorties** (chiffres SQL + ODS avec formules Germaine intactes). Ne pas confondre « remplir le portail » et « remplir le tableur amont ».

---

## 2. Workflow agent recommandé (étendu, post-T2)

```text
0. Charger MODE-EMPLOI trimestre + mission (ne pas re-parser l'ODS à la main)
1. dump_manifest.py → fraîcheur dump vs date_fin
2. runbook → miroir Docker postgres:17 (recyclic-mirror-t2)
3. interroger_eco_org.py sur template CSV → *_rempli.csv + --save-sql
4. Sanity checks métier (voir §4) — STOP si ordre de grandeur absurde
5. Copier template Germaine depuis references/_depot/ (JAMAIS éditer l'original)
6. Remplir UNIQUEMENT lignes de détail (R13, R38, R19) — script lxml
7. Vérifier table:formula count ≥ 70 dans content.xml
8. Sidecar JSON (.json) + note agent en bas de feuille
9. Ménage : 1 seul ODS validé dans declarations-la-clique/YYYY-Tn/
```

---

## 3. Tableur Germaine — anatomie (SoT structurelle)

**Template vierge (intouché) :** `references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods`

### Feuilles

| Onglet | Rôle |
|--------|------|
| `Entrees-Reception` | 3 blocs : (1) LIV matière, (2) recyclage benne kg, (3) autres |
| `Sortie-VenteDonsReemploi` | DEC_REE ventes/dons caisse |

### Colonnes

| Zone | Colonnes | Unité |
|------|----------|-------|
| Ecologic | **B–J** | t (sauf **J** ABJ-AUT = **pièces**) |
| Ecomaison | **K–T** | t (recyclage bloc 2 = **kg**) |

### Lignes agent vs lignes Germaine (CRITIQUE)

Les lignes **TOTAL** portent des `table:formula` (`of:=SUM(...)`). Les plages SOMME du modèle :

| Feuille | Bloc | Ligne détail agent | Plage SOMME TOTAL | Ligne TOTAL |
|---------|------|-------------------|-------------------|-------------|
| Entrees | 1 LIV | **R13** | B13:B23 … S13:S23 | R17 |
| Entrees | 2 recyclage | **R38** | B38:B48 … | R33 |
| Entrees | 3 autres | *(vide)* | B63:B73 … | R49 |
| Sorties | DEC_REE | **R19** | B9:B19 … **S9:S19** | R21 |

**Interdits vus en session :**

- Écrire dans R17/R33/R49/R21 (TOTAL) → formules écrasées ou affichées en texte `of:=SUM(...)`
- Remplir R15, R20, R31 (hors plages SOMME) → chiffres ignorés par Germaine
- Toucher colonne **T** sorties si Germaine l'a déjà saisie (R9–R18) → double comptage

**Libellés période :** renommer cellule A des TOTAL « TOTAL 4T 2025 » → **TOTAL 2T 2026** (valeurs inchangées).

---

## 4. Pièges métier (ordre de gravité)

### 4.1 PAM LIV 246,5 t — rejeté

L'ancien ODS `DeclarationESS-ECOLOGIC-2T2026.ods` cumulait des pesées enlèvement sur des dizaines de lignes B sans filtrage → **246,5 t PAM**.

Tickets Recyclique T2 (cat. PAM, `is_exit=false`) : **~1,136 t**.

| Source | PAM LIV T2 | Verdict |
|--------|------------|---------|
| Pesées tableur cumulées | 246,5 t | **Faux** (double comptage / mélange périodes) |
| Tickets Recyclique | 1,136 t | **Retenu** (avec HITL bordereaux Ecologic) |

**Règle agent :** si écart > ×10 entre tickets et tableur → **ne pas recopier le tableur** ; documenter en note + HITL.

### 4.2 LIV tableur ≠ LIV tickets

- **LIV portail / pro forma** peut venir des **pesées enlèvement** (workflow Germaine).
- **LIV Recyclique** = somme `ligne_depot` entrées (`is_exit=false`) par catégorie.

Les deux sont légitimes métier ; l'agent **ne fusionne pas** sans validation CLIC.

### 4.3 DEC_REE = caisse uniquement

```sql
COALESCE(sales.sale_date, sales.created_at)  -- pas created_at sale_items seul
```

Exclure lignes caisse `notes ILIKE '%recyclage%'` si preset benne.

### 4.4 Recyclage bloc 2 ≠ DEC_REE

```sql
ligne_depot.is_exit = true AND destination = 'RECYCLAGE'
```

Unité **kg** (entiers ou 1 décimale), pas tonnes. Ne pas mettre en sorties réemploi.

### 4.5 Ecomaison colonne T (déco textile)

Sorties caisse : inclure en SQL mais **ne pas écrire col. T** sur R19 si Germaine a déjà des lignes T9–T18 — risque double total.

### 4.6 ASL CAT1/CAT2

Mapping auto OK pour total ASL ; **split photobook** = override humain (ex. T2 retour CLIC 0,055 + 0,081 t vs auto 0,100 + 0,036).

### 4.7 ABJ > 80 cm

**Ecomaison BJ**, pas Ecologic — voir `mapping-reference.md`.

---

## 5. Pièges techniques ODS (XML)

### 5.1 Utiliser lxml, pas ElementTree stdlib

`xml.etree.ElementTree.tostring()` **casse les namespaces** OpenDocument :

- `table:formula` → `formula` ou `ns0:formula`
- LibreOffice affiche les formules en **texte brut** au lieu de les calculer

**Gate qualité :**

```python
assert content_xml.count("table:formula") >= 70
```

### 5.2 Règles édition cellules

1. Si `cell.get("{urn:...table:1.0}formula")` → **skip** (ne jamais écraser)
2. Déplier `table:number-columns-repeated` sur lignes de détail seulement
3. Format FR : virgule décimale, `office:value-type="float"`, `office:value`
4. Copier ZIP ODS : remplacer **seulement** `content.xml`, garder le reste du zip tel quel

### 5.3 Script de référence (à promouvoir)

Racine repo : `_tmp_fill_germaine_ods_v2.py`

- Source : `_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods`
- Sortie : `…/2026-T2/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods`
- Sidecar : `.json` avec agrégats bruts
- Requiert Docker miroir actif

**Évolution skill :** déplacer vers `.cursor/skills/interroger-eco-organismes/scripts/fill_germaine_ods.py` + tests formula count.

---

## 6. Chiffres T2 retenus (dump 2026-07-07)

### Ecologic DEC_REE (t) — sorties caisse

| Code | t |
|------|---|
| PAM | 0,270 |
| ECR | 0,032 |
| GHF | 0,060 |
| GEF | 0,063 |
| ASL-CAT1 | 0,100 |
| ASL-CAT2 | 0,036 |
| ABJ-TONM | 1 **pièce** |

### Ecologic LIV (t) — entrées tickets

| Code | t |
|------|---|
| PAM | **1,136** |
| ECR | 0,032 |
| GHF | 0,040 |
| GEF | 0,037 |
| ASL-CAT1 | 0,209 |
| ASL-CAT2 | 0,155 |

### Ecomaison sorties caisse (K–S, t)

K 0,022 · L 0,012 · M 0,014 · N 0,011 · O 0,164 · P 0,169 · Q 0,069 · R 0,106 · S 0,313

*(T = 0,039 t en SQL mais non injecté sur R19 — voir §4.5)*

---

## 7. Hygiène fichiers / ménage post-session

**Conserver :**

- Template : `references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods`
- Validé : `declarations-la-clique/2026-T2/DeclarationESS-…-REMPLI.ods` (+ `.json`)

**Supprimer après validation :**

- `REMPLI-v2/v3/v4.ods`, ancien `2T2026.ods`, ODS avec formules cassées

**Docs à pointer vers REMPLI + template** (pas l'ancien 2T2026) : mission, README, MODE-EMPLOI, REPRISE.

---

## 8. HITL — quand solliciter (ou pas)

| Sujet | Agent seul | HITL CLIC |
|-------|------------|-----------|
| Dump antérieur à période | STOP | export frais |
| PAM LIV tickets vs bordereaux | note + chiffre tickets | validation enlèvements |
| ASL split CAT1/CAT2 | brouillon auto | photobook |
| Col. T Germaine vs SQL | ne pas écraser T | Germaine tranche |
| Surcharge cognitive équipe | **documenter dans HITL.md** | pas de ping Discord systématique |

---

## 9. Propositions d'évolution skill v2

| Priorité | Item | Détail |
|----------|------|--------|
| P0 | Runbook ODS Germaine | Intégrer §3–§5 dans `runbook.md` |
| P0 | Script `fill_germaine_ods.py` | Promouvoir `_tmp_fill_germaine_ods_v2.py` |
| P1 | Flux `RECYCLAGE` dans template CSV | Nouveau flux `RECYCLAGE` (kg) + mapping Ecomaison K–T |
| P1 | Gate sanity | Alerte si LIV > 50 t sur filière ou ratio PAM/export > 0,5 |
| P2 | Parser ODS → template CSV | Éviter double saisie des périodes Germaine |
| P2 | YAML mapping Ecomaison | Compléter `mapping-reference.md` depuis analyse 07/07 |
| P3 | Endpoint 9.ECO-04 | Remplacer Docker ad hoc par API agrégats |

---

## 10. Prompt reprise (mis à jour post-ménage)

```text
Mission décla Ecologic+Ecomaison T2 2026.
Charger :
  - references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/2026-07-07_mission-assistance-decla-ecologic-t2-2026.md
  - …/DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md
  - .cursor/skills/interroger-eco-organismes/_brainstorm/2026-07-15_runbook-session-T2-learnings.md
Skill : interroger-eco-organismes (CSV + ODS Germaine).
Template ODS : references/_depot/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties.ods
Validé : …/DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods
Dump : references/_depot/recyclic_db_export_YYYYMMDD_HHMMSS.dump
Règle : lignes détail R13/R38/R19 seulement — jamais écraser TOTAL/formules.
```

---

## 11. Références croisées

| Chemin | Rôle |
|--------|------|
| `references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/queries-decla-t2.sql` | Requêtes canon T2 |
| `references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md` | Structure ODS (SoT) |
| `.cursor/skills/interroger-eco-organismes/mapping-reference.md` | Codes ↔ catégories |
| `_tmp_fill_germaine_ods_v2.py` | Script remplissage ODS (temporaire racine) |
