# BDD Recyclique — règles métier déclarations éco-organismes

> Durci session T2 2026 · indépendant du format tableur (Germaine ou autre).  
> Schéma complet : `references/dumps/schema-recyclic-dev.md`

---

## 1. Trois flux distincts (ne pas mélanger)

| Flux | Question métier | Tables | Filtre clé | Unité sortie | Colonne template `flux` |
|------|-----------------|--------|------------|--------------|---------------------------|
| **DEC_REE** | Réemploi vendu/donné en **caisse** | `sale_items` → `sales` → `categories` | ventes période | **t** ou **pièces** | `DEC_REE` |
| **LIV** | Matière **entrée** au dépôt (tickets) | `ligne_depot` → `ticket_depot` → `categories` | `is_exit = false` | **t** | `LIV` |
| **RECYCLAGE** | Matière partie en **benne interne** | idem LIV | `is_exit = true` + `destination` (défaut `RECYCLAGE`) | **kg** | `RECYCLAGE` |
| **SORTIES_DEPOT_KG** | Exploration — toutes sorties dépôt | idem | `is_exit = true` (toute destination) | **kg** | `SORTIES_DEPOT_KG` |

**Erreurs vues en session :**

- Compter le recyclage benne dans DEC_REE → faux (caisse ≠ benne)
- Recopier des pesées tableur cumulées comme LIV sans croiser tickets → faux (ex. PAM 246 t vs ~1,1 t tickets)
- Utiliser `sale_items.created_at` seul → faux ; privilégier `COALESCE(sales.sale_date, sales.created_at)`

---

## 2. Joins et types (pièges SQL)

```sql
-- Caisse : category sur sale_items est du TEXT (UUID stringifié)
JOIN categories c ON c.id::text = si.category

-- Dépôt : category_id est un UUID natif
JOIN categories c ON c.id = ld.category_id

-- Horodatage ventes DEC_REE
WHERE COALESCE(s.sale_date, s.created_at) >= :t_start
  AND COALESCE(s.sale_date, s.created_at) < :t_end   -- date_fin inclusive

-- Horodatage entrées LIV / recyclage
WHERE t.created_at >= :t_start
  AND t.created_at < :t_end
```

**Exclure preset recyclage en caisse** (DEC_REE) :

```sql
AND (si.notes IS NULL OR si.notes NOT ILIKE '%recyclage%')
```

---

## 3. Formules canon (golden T1 validé)

| Opération | SQL | Notes |
|-----------|-----|-------|
| DEC_REE (t) | `ROUND(SUM(COALESCE(si.weight,0)) / 1000, 3)` | Arrondi **après** somme |
| LIV (t) | `ROUND(FLOOR(SUM(ld.poids_kg)) / 1000, 3)` | **FLOOR** avant conversion t |
| DEC_REE (pièces) | `SUM(si.quantity)` | ABJ-AUT, tondeuses si portail en pièces |
| RECYCLAGE (kg) | `ROUND(SUM(ld.poids_kg), 1)` | Pas de conversion tonnes |

**Golden test** (doit matcher pro forma T1) :

- PAM DEC_REE T1 → **0,184 t** (avec `COALESCE(sale_date, created_at)`)
- PAM LIV T1 → **2,223 t** (2 224 kg → FLOOR → /1000)

Requête complète : [exploration-requetes.sql](exploration-requetes.sql) § golden T1.

---

## 4. Reconnaissance schéma (début de session)

Ordre recommandé avant d'agréger une période inconnue :

```text
1. pg_restore miroir (runbook.md)
2. \dt — vérifier tables présentes
3. Lister catégories du partenaire (mapping-reference.md)
4. Golden test T1 sur 1 code connu (PAM DEC_REE)
5. Agrégats période cible
6. Sanity checks (§5)
```

**Explorer les sorties dépôt** (comprendre `destination`) :

```sql
SELECT ld.destination, COUNT(*), ROUND(SUM(ld.poids_kg)::numeric, 2) AS kg
FROM ligne_depot ld
JOIN ticket_depot t ON t.id = ld.ticket_id
WHERE ld.is_exit = true
  AND t.created_at >= :t_start AND t.created_at < :t_end
GROUP BY ld.destination ORDER BY kg DESC;
```

Session T2 : quasi tout `is_exit=true` → `RECYCLAGE` (hors DEC_REE portail).

**Lister catégories sous un parent** (ex. ASL, ABJTH) :

```sql
SELECT c.name, c.id
FROM categories c
WHERE c.parent_id = :parent_uuid   -- ou name ILIKE '%ASL%'
ORDER BY c.name;
```

Parent ABJTH connu T2 : `192b6d5b-aabe-40ac-bace-68aabcdf3a4e` — **re-vérifier** sur dump si doute.

---

## 5. Sanity checks (bloquants ou HITL)

| Signal | Seuil indicatif | Action |
|--------|-----------------|--------|
| LIV filière >> volume trimestre plausible | ex. PAM > 10 t / trimestre La Clique | STOP — requête ou mapping à revoir |
| Écart tableur vs tickets | ratio > ×5 | Ne pas recopier tableur ; documenter HITL |
| `NE PLUS UTILISER` dans `categories.name` | toute ligne | Exclure ou reclasser avant agrégat |
| Dump antérieur à `date_fin` | date dump < fin période | STOP — export frais `_depot/` |
| ASL CAT1 + CAT2 vs parent ASL | somme enfants ≈ parent | Split photobook = override humain |
| ABJ > 80 cm | cat. jardin gros format | **Ecomaison**, pas Ecologic |

**Ratio filtrage export** (cadrage 1.4.5) : masse filière cible / masse export brut < 0,20 → normal si export « tout magasin ».

---

## 6. LIV tickets vs pesées tableur

Deux sources métier **légitimes** :

| Source | Usage | Agent |
|--------|-------|-------|
| Tickets Recyclique (`ligne_depot`) | Contrôle, complément DEC_REE, module futur | Calcule et trace |
| Pesées enlèvement (tableur partenaire) | Souvent source **officielle LIV** portail | Ne pas écraser sans validation CLIC |

Si les deux divergent : produire les deux chiffres + note HITL, pas de fusion silencieuse.

---

## 7. Partenaires — périmètre requêtes

### Ecologic (EEE)

9 codes × 2 opérations = **18 cases portail** (`LIV` + `DEC_REE`).  
Mapping : `mapping-reference.md` § Ecologic.

### Ecomaison (DEA, JJ, BJ…)

Mapping **partiel** — colonnes K–T si tableur combiné.  
Analyse projet : `references/eco-organismes/partenaires/ecomaison/2026-07-07_analyse-declarations-mapping.md`

### Hors périmètre Recyclique caisse/dépôt

Textile → Refashion · Livres → Recyclivre · etc. (cf. mapping EXCLUDE)

---

## 8. Exécution SQL via Docker

**Accents / UTF-8** : préférer `docker cp fichier.sql container:/tmp/q.sql` puis `psql -f` plutôt qu'une longue `-c` inline sous Windows.

```powershell
docker cp "chemin/requete.sql" recyclic-mirror-t2:/tmp/q.sql
docker exec recyclic-mirror-t2 psql -U postgres -d recyclic_la_clique_mirror -f /tmp/q.sql
```

Script skill : `interroger_eco_org.py` (template CSV) · audit : `--save-sql`.

Requêtes session T2 archivées projet :  
`references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/queries-decla-t2.sql`

---

## 9. Scripts d'exploration (one-shot session T2)

Patterns réutilisables — **pas** dans le skill canon ; inspiration si nouveau format fichier :

| Script racine repo | Usage |
|--------------------|-------|
| `_tmp_inspect_ods.py` | Lire structure ODS (feuilles, formules, lignes) via zip+XML |
| `_tmp_extract_ecologic_t2_ods.py` | Extraire cellules → JSON audit |
| `_tmp_fill_germaine_ods_v2.py` | Remplissage ODS **spécifique Germaine** — voir archive |

Si le prochain partenaire envoie un XLSX/CSV différent : repartir de `interroger_eco_org.py` + ce doc, pas du script Germaine.

---

## 10. Livrables agent (indépendants du tableur)

```
references/eco-organismes/partenaires/<partenaire>/declarations-la-clique/YYYY-Tn/
  queries-decla-tn.sql              ← audit SQL (prioritaire)
  interrogation-*_rempli.csv        ← sortie script
  Complément-*.csv                  ← cases portail manquantes
  HITL-questions-*.md               ← écarts / inconnues
```

Le tableur partenaire (ODS/XLSX) est **optionnel** et **non normatif** tant que le module déclaration Recyclique n'est pas livré.
