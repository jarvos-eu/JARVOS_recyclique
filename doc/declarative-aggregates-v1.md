# Agrégats déclaratifs v1 — périmètre et traçabilité

**Story 9.1 — Modèle et persistance des données déclaratives.**  
Source de vérité : RecyClique (pas de sync bidirectionnelle avec Paheko pour ces données).

---

## Périmètre v1

- **Champs persistés** : `year`, `quarter` (T1–T4), `category_id` (FK `categories`), `flow_type` (`caisse` | `reception`), `weight_kg`, `quantity`, `created_at`, `updated_at`.
- **Périodes** : trimestres calendaires (T1 = janv.–mars, T2 = avr.–juin, T3 = juil.–sept., T4 = oct.–déc.). Pas de granulité mensuelle en v1.
- **Flux** :
  - **Caisse** : agrégats issus des lignes de vente (`sale_items`) dont la vente est dans la période.
  - **Réception** : agrégats issus des lignes de dépôt (`ligne_depot`) dont la date de création est dans la période.
- **Table** : `declarative_aggregates` (additive ; aucune modification des tables `sales`, `sale_items`, `ligne_depot`, `categories`).

---

## Traçabilité — source des agrégats

| Flux       | Table(s) source     | Colonnes utilisées pour les agrégats | Période dérivée de |
|-----------|---------------------|---------------------------------------|--------------------|
| Caisse    | `sale_items` + `sales` | `sale_items.weight` (kg), `sale_items.category_id`, `sale_items.quantity` | `COALESCE(sales.sale_date, sales.created_at)` |
| Réception | `ligne_depot`       | `ligne_depot.poids_kg`, `ligne_depot.category_id` ; quantité = nombre de lignes | `ligne_depot.created_at` |

- **Caisse** : une ligne par combinaison `(year, quarter, category_id, flow_type='caisse')` ; `weight_kg` = somme des `sale_items.weight`, `quantity` = somme des `sale_items.quantity` pour les ventes dont la date (sale_date ou created_at) tombe dans le trimestre.
- **Réception** : une ligne par combinaison `(year, quarter, category_id, flow_type='reception')` ; `weight_kg` = somme des `ligne_depot.poids_kg`, `quantity` = nombre de lignes (`COUNT(id)`).

---

## Règles de calcul

1. **Recalcul** : le service `compute_and_persist_aggregates(db, year, quarter)` supprime toutes les lignes existantes pour `(year, quarter)` puis recalcule à partir des tables source et réinsère. Réexécutable sans effet de bord (backfill, corrections).
2. **Lignes à 0** : les groupes avec `weight_kg = 0` et `quantity = 0` ne sont pas insérés.
3. **Catégorie nulle** : les lignes sans catégorie (`category_id` NULL) sont agrégées sous une même ligne avec `category_id = NULL`.

---

## Exposition des données

- **API** : `GET /v1/declarative/aggregates` (read-only), filtres optionnels : `year`, `quarter`, `flow_type`, `category_id`. Réponse JSON (snake_case, dates ISO 8601). Permission : `admin`.
- **Calcul** : `POST /v1/declarative/aggregates/compute` avec body `{ "year": 2026, "quarter": 1 }`. Appelable par un job planifié ou manuellement. Permission : `admin`.

---

## Évolutions prévues (hors v1)

- Story 9.2 (post-MVP) : module déclarations éco-organismes (exports, multi-éco-organismes, formats par éco-organisme). **Livré** : voir section ci-dessous.
- Granularité mensuelle éventuelle (HITL-9.0).

---

## Module décla post-MVP (Story 9.2)

**Périmètre :** post-MVP, non bloquant pour la mise en production MVP.

### Activation

- **Critère d'activation :** ajouter `"decla"` à la liste `enabled` dans `api/config/modules.toml` (section `[modules]`). Sans cela, l'endpoint d'export n'est pas exposé.
- **Entrée utilisateur :** lorsque le module est actif, l'API expose `GET /v1/declarative/export` (téléchargement CSV ou JSON des agrégats). Pas d'écran dédié en v1 ; usage via outil externe ou intégration ultérieure.

### Export

- **Endpoint :** `GET /v1/declarative/export?year=...&quarter=...&format=csv|json`
- **Paramètres obligatoires :** `year` (1900–2100), `quarter` (1–4).
- **Paramètres optionnels :** `format` (défaut `csv`), `flow_type` (caisse | reception), `category_id`, `eco_organism` (réservé multi-éco-organismes, ignoré en v1).
- **Permission :** admin (comme Story 9.1).
- **Données source :** table `declarative_aggregates` (lecture seule, pas de recalcul).

### Formats

- **CSV :** colonnes id, year, quarter, category_id, flow_type, weight_kg, quantity, created_at, updated_at. Encodage UTF-8 avec BOM pour Excel.
- **JSON :** tableau d'objets (snake_case, dates ISO 8601).

### Multi-éco-organismes

- Le paramètre `eco_organism` est accepté pour préparer des exports ciblés (ex. Ecologic, Ecomaison). En v1 il est ignoré ; le mapping catégories RecyClique → catégories officielles par éco-organisme sera documenté ou configurable en évolution ultérieure (référence : `references/vision-projet/vision-module-decla-eco-organismes.md`).
