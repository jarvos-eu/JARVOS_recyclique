# Runbook — miroir BDD La Clique (interrogations éco-organismes)

## Principe

- **SELECT only** — jamais INSERT/UPDATE/DELETE
- Dump = instantané pré-prod Recyclique 1.4.4 La Clique
- Miroir local = jetable, recréable à chaque session

---

## Dumps

| Emplacement | Convention |
|-------------|------------|
| `references/_depot/` | `recyclic_db_export_YYYYMMDD_HHMMSS.dump` |
| Gitignore | oui — ne pas committer |

**Choisir le dump :** le plus récent dont la date **≥** fin de période interrogée.

```bash
python .cursor/skills/interroger-eco-organismes/scripts/dump_manifest.py --dump-dir references/_depot
```

---

## Restauration Docker (Windows / Linux)

**Prérequis :** Docker Desktop · image `postgres:17` (dump format 1.16).

```powershell
$dump = "D:\Users\Strophe\Documents\1-IA\La Clique Qui Recycle\JARVOS_recyclique\references\_depot\recyclic_db_export_YYYYMMDD_HHMMSS.dump"
docker rm -f recyclic-mirror-t2 2>$null
docker run -d --name recyclic-mirror-t2 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=recyclic_la_clique_mirror postgres:17
Start-Sleep -Seconds 10
docker cp "$dump" recyclic-mirror-t2:/tmp/dump.dump
docker exec recyclic-mirror-t2 pg_restore -U postgres -d recyclic_la_clique_mirror --no-owner /tmp/dump.dump
docker exec recyclic-mirror-t2 psql -U postgres -d recyclic_la_clique_mirror -c "\dt"
```

| Paramètre | Valeur |
|-----------|--------|
| Conteneur | `recyclic-mirror-t2` |
| Base | `recyclic_la_clique_mirror` |
| User | `postgres` |

---

## Vérifier Docker avant d'interroger

Le script **ne restaure jamais** le dump tout seul. Il vérifie et explique en français si quelque chose manque :

```bash
python .cursor/skills/interroger-eco-organismes/scripts/docker_mirror.py
```

| Situation | Message utilisateur (résumé) |
|-----------|------------------------------|
| Docker absent / pas démarré | Ouvrir Docker Desktop, attendre le démarrage |
| Conteneur inexistant | Suivre runbook pg_restore — dump dans `_depot/` |
| Conteneur arrêté | `docker start recyclic-mirror-t2` |
| Base vide / tables manquantes | Refaire pg_restore |

`interroger_eco_org.py` appelle cette vérification automatiquement (sauf `--dry-run` ou `--skip-docker-check`). En cas d'échec : statut `docker_indisponible` sur toutes les lignes du CSV sortie.

---

## Exécuter des requêtes (UTF-8)

Sous Windows, préférer copier le fichier SQL dans le conteneur :

```powershell
docker cp ".cursor/skills/interroger-eco-organismes/references/exploration-requetes.sql" recyclic-mirror-t2:/tmp/explore.sql
docker exec recyclic-mirror-t2 psql -U postgres -d recyclic_la_clique_mirror -f /tmp/explore.sql
```

Pack requêtes mission : `references/eco-organismes/partenaires/.../queries-decla-tn.sql`

---

## Tables interrogées

| Table | Colonnes clés | Rôle décla |
|-------|---------------|------------|
| `categories` | `name`, `parent_id`, `id` | Mapping filière |
| `ticket_depot` | `created_at` | Date entrées LIV / recyclage |
| `ligne_depot` | `poids_kg`, `is_exit`, `destination`, `category_id` | Entrées + benne |
| `sales` | `sale_date`, `created_at` | Date ventes DEC_REE |
| `sale_items` | `category` (text UUID), `weight`, `quantity`, `notes` | Lignes caisse |

**Joins :** voir [references/bdd-metier.md](references/bdd-metier.md) §2.

Schéma complet : `references/dumps/schema-recyclic-dev.md`

---

## Début de session — reconnaissance

```text
1. pg_restore (ci-dessus)
2. Golden test T1 PAM DEC_REE ≈ 0,184 t
3. Agrégats période cible (exploration-requetes.sql)
4. SELECT destination WHERE is_exit=true — comprendre RECYCLAGE vs autres
5. Sanity checks (bdd-metier.md §5)
```

---

## Pièges métier (session T2)

| Piège | Action |
|-------|--------|
| LIV pesées tableur ≠ LIV tickets | Tracer les deux ; HITL si écart ×5 |
| Cumul lignes tableur (ex. PAM 246 t) | Croiser tickets ; sanity check |
| Recyclage benne dans DEC_REE | Exclure ; flux RECYCLAGE séparé (kg) |
| `preset_type:recyclage` notes caisse | Exclure DEC_REE |
| ASL CAT1/CAT2 | Split photobook → CLIC |
| ABJ > 80 cm | Ecomaison BJ |
| Dump antérieur à période | **Bloquer** |

---

## Livrables type session

```
partenaires/<partenaire>/declarations-la-clique/YYYY-Tn/
  queries-decla-tn.sql              ← prioritaire (audit)
  interrogation-*_rempli.csv
  Complément-*.csv / HITL-*.md      ← si portail
  <tableur-partenaire>                ← optionnel, format variable
```

---

## Sécurité

- Pas d'exposition réseau du conteneur
- Pas de credentials prod dans le repo
- `docker rm -f recyclic-mirror-t2` après session longue si machine partagée

---

## Formats tableur partenaire

**Non normatif** tant que le module déclaration Recyclique n'est pas livré.  
Si le fichier ressemble au Germaine T2 2026 : [references/archive-germaine-ods-t2-2026.md](references/archive-germaine-ods-t2-2026.md)
