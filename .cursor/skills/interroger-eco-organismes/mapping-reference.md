# Mapping reference — Recyclique → éco-organismes

> v1 — extrait mission Ecologic T2 2026 + cadrage patch 1.4.5. Enrichir au fil des déclarations.

---

## Ecologic — codes portail × catégories Recyclique

### DEC_REE / LIV (EEE)

| Code portail | Catégorie Recyclique (`categories.name`) | Unité DEC_REE | Confiance |
|--------------|------------------------------------------|---------------|-----------|
| PAM | `1- Petits appareils em melange(PAM)` | t | Forte (golden T1) |
| ECR | `2- Ecrans` | t | Forte |
| GHF | `3- Gros électroménager hors froid (GEMHF)` | t | Moyenne |
| GEF | `4- Gros électroménager froid (GEMF)` | t | Moyenne |
| ASL-CAT1 | `1- Cycles et engins de déplacement non motorisés` | t | Moyenne — **split photobook** |
| ASL-CAT2 | `2- Autres ASL` | t | Moyenne — **split photobook** |
| ABJ-TONA | `1- Tondeuses autoportées` | t ou pièces | Moyenne |
| ABJ-TONM | `2- Tondeuses à conducteur marchant` | t ou pièces | Moyenne |
| ABJ-AUT | `3- Autres ABJ thermique` | **pièces** | Forte |

Parent ASL : `Articles de sport et de loisir (ASL)` — **ne pas** sommer avec CAT1+CAT2 (doublon).

Parent ABJTH : `(ABJTH) Articles de bricolage et de jardin thermiques`

### Hors Ecologic (EXCLUDE)

| Catégorie / motif | Rediriger vers |
|-------------------|----------------|
| `A -Textile Divers`, Textiles | Refashion |
| `A - Livres Divers`, Livres | Recyclivre |
| Eléments d'ameublement (EA), `* Assises`… | Ecomaison DEA |
| `(ABJ) Articles de bricolage et de jardin` | Ecomaison BJ |
| `* Gros équipement de jardin sup80cm` | **Ecomaison BJ** (pas Ecologic) |
| `NE PLUS UTILISER…` | RECLASSER — exclure agrégats |

---

## Ecomaison — colonnes tableur K–T (session T2, brouillon)

Mapping utilisé pour agrégats caisse + entrées tickets (tableur combiné Germaine).  
Codes portail Ecomaison réels : voir analyse projet.

| Col. | Catégories Recyclique (`categories.name`) | Flux |
|------|-------------------------------------------|------|
| K | `Jardin`, `*Pots de fleurs`, `* Gros équipement de jardin sup80cm`, `NE PLUS UTILISER Materiel destinés à l'aménagement du jardin` | LIV + DEC_REE |
| L | `A - Outillage Divers`, `* Outillage à main`, `Outillage`, `NE PLUS UTILISER- Materiel de bricolage`, `* Gros Equipements de Bricolage (sup 80 cm)` | LIV + DEC_REE |
| M | `1- Jeux de plein air` | LIV + DEC_REE |
| N | `2- Jeux société et puzzle` | LIV + DEC_REE |
| O | `3- autres jeux d'intérieur`, `A - Jeux Divers` | LIV + DEC_REE |
| P | `* Assises`, `Chaises`, `Petit meuble/chaise en bois massif`, `Gros meuble en bois massif`, `Meuble moyen en bois massif`, `A - Meuble Divers` | LIV + DEC_REE |
| Q | `* Couchage` | LIV + DEC_REE |
| R | `* Rangement`, `NE PLUS UTILISER Rangement et plan de pose et de travail` | LIV + DEC_REE |
| S | `*Plan de pose , plan de travail` | LIV + DEC_REE |
| T | `* Décoration textile` | LIV + DEC_REE — attention double saisie si tableur déjà rempli |

Analyse : `references/eco-organismes/partenaires/ecomaison/2026-07-07_analyse-declarations-mapping.md`

---

## Formules (canon golden T1)

```text
DEC_REE (t)       = ROUND(SUM(sale_items.weight) / 1000, 3)   -- caisse, hors recyclage si filtre actif
LIV (t)           = ROUND(FLOOR(SUM(ligne_depot.poids_kg)) / 1000, 3)   -- is_exit=false
RECYCLAGE (kg)    = ROUND(SUM(poids_kg), 1)   -- is_exit=true AND destination='RECYCLAGE'
DEC_REE (pièces)  = SUM(sale_items.quantity)
```

Période SQL : `[date_debut 00:00 UTC, date_fin+1 jour)` — date_fin **inclusive**.

---

## Validations terrain (priorité humaine)

| Sujet | Règle agent | Override CLIC |
|-------|-------------|---------------|
| ASL CAT1 vs CAT2 split | Mapping auto ci-dessus | Photobook / retour équipe (ex. T2 : 0,055 + 0,081 t) |
| ABJ-TONM unité | pièces par défaut | tonnes OK si portail (ex. 0,010 t) |
| LIV entrées | tickets Recyclique | Pesées enlèvement tableur = source métier possible |
| Volume LIV aberrant | tickets Recyclique | Ex. PAM 246 t tableur vs ~1,1 t tickets → rejeter tableur, HITL |
