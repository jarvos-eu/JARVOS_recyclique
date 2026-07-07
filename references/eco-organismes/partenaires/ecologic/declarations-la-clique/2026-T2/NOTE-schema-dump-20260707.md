# NOTE — Schéma dump Recyclique 1.4.4 La Clique (2026-07-07)

**Dump :** `references/_depot/recyclic_db_export_20260707_152448.dump`  
**Format :** PostgreSQL custom (pg_dump 17.8 → DB source 15.14)  
**Base source :** `recyclic`  
**Restauration session :** Docker `postgres:17`, conteneur `recyclic-mirror-t2`, DB `recyclic_la_clique_mirror`

---

## Tables utiles mission T2

| Table | Rôle mission |
|-------|--------------|
| `categories` | Libellés boutique (`name`), hiérarchie (`parent_id`) |
| `ticket_depot` | Horodatage entrées/sorties ticket (`created_at`) |
| `ligne_depot` | Poids (`poids_kg`), `is_exit`, `destination`, `category_id` |
| `sales` | Ventes caisse (`sale_date`, `created_at`, `donation` en €) |
| `sale_items` | Lignes vente : `category` (UUID texte), `weight`, `quantity` |
| `poste_reception` | Session réception (non utilisée seule pour filtres T2) |

**Énumération `destinationenum` :** `MAGASIN`, `RECYCLAGE`, `DECHETERIE`

---

## Volumes dump (instantané 2026-07-07)

| Métrique | Valeur |
|----------|--------|
| `ligne_depot` total | 5 131 (4 649 entrées · 482 sorties) |
| Période tickets | 2025-09-20 → 2026-07-04 |
| Période ventes | 2025-09-17 → 2026-07-04 |

---

## Écarts vs `references/dumps/schema-recyclic-dev.md`

Schéma dev **aligné** sur les tables mission (28 tables restaurées). Pas d’écart bloquant constaté sur les colonnes `ligne_depot`, `sale_items`, `categories`.

---

## Décisions requête (documentées)

| Flux | Table | Filtre date | Filtre métier |
|------|-------|-------------|---------------|
| **DEC_REE** | `sale_items` → `sales` | `COALESCE(sale_date, created_at)` ∈ T2 | Jointure `categories` ; mapping § HITL |
| **LIV** (contrôle) | `ligne_depot` → `ticket_depot` | `ticket_depot.created_at` ∈ T2 | `is_exit = false` ; formule `FLOOR(kg)/1000` |
| **Recyclage** (hors DEC_REE) | `ligne_depot` | idem | `is_exit = true` AND `destination = RECYCLAGE` |

---

## Reproductibilité miroir

```powershell
# Docker (PostgreSQL 17 requis pour ce dump)
docker rm -f recyclic-mirror-t2 2>$null
docker run -d --name recyclic-mirror-t2 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=recyclic_la_clique_mirror postgres:17
docker cp "D:\Users\Strophe\Documents\1-IA\La Clique Qui Recycle\JARVOS_recyclique\references\_depot\recyclic_db_export_20260707_152448.dump" recyclic-mirror-t2:/tmp/dump.dump
docker exec recyclic-mirror-t2 pg_restore -U postgres -d recyclic_la_clique_mirror --no-owner /tmp/dump.dump
docker exec -it recyclic-mirror-t2 psql -U postgres -d recyclic_la_clique_mirror
```

Requêtes : [`queries-decla-t2.sql`](queries-decla-t2.sql)
