---
name: interroger-eco-organismes
description: >-
  Interroge le dump PostgreSQL Recyclique La Clique (miroir read-only) pour
  calculer volumes déclaration éco-organismes (Ecologic, Ecomaison, etc.).
  Agrégats DEC_REE, LIV, RECYCLAGE depuis sale_items, ligne_depot, sales.
  Vérifie fraîcheur dump, exécute template CSV, produit CSV rempli + SQL audit.
  Use when the user asks to query eco-organismes declarations, run DEC_REE/LIV
  aggregates, explore Recyclique DB for declaration volumes, or refresh from dump.
  Do not use Paheko for weights or eco-organism volumes — Paheko is euros/accounting only.
---

# Interroger éco-organismes (dump Recyclique)

Skill **projet** — La Clique / Recyclique 1.4.4 · miroir BDD read-only.

**Périmètre canon :** extraire des **chiffres fiables depuis Recyclique** (caisse + dépôt). Le format tableur partenaire (ODS Germaine, XLSX, etc.) change à chaque mission — **non prioritaire** ; voir [references/](references/) si besoin.

## Frontière Paheko (2026-08-18)

**Paheko = compta en euros** (écritures, exercices, bilans, questions comptables).  
**Recyclique = poids, caisse métier, dépôts, déclarations éco-organismes.**

Ne pas interroger Paheko pour DEC_REE / LIV / RECYCLAGE / PRE. Les extensions Paheko **Saisie au poids** et **Caisse** (`plugin_pos_*`) sont **hors périmètre** et vont être **désinstallées**. `--source paheko` / `--compare` sont **refusés** par le script.

Détail : [references/bdd-metier-paheko.md](references/bdd-metier-paheko.md)

## Quand l'utiliser

- Calculer **DEC_REE** (sorties réemploi caisse), **LIV** (entrées tickets), **RECYCLAGE** (benne kg)
- Remplir un **template CSV** de volumes par filière et période
- Vérifier la **fraîcheur du dump Recyclique** avant une période
- Reconnaître le schéma BDD / rejouer golden tests (cf. [references/bdd-metier.md](references/bdd-metier.md))

**Hors périmètre v1 :** saisie portail, module déclaration Recyclique (story 9.ECO-04), **tout volume poids depuis Paheko**.

---

## Workflow agent (7 étapes)

```
1. mapping-reference.md + references/bdd-metier.md (règles métier Recyclique)
2. dump_manifest.py → dernier dump Recyclique + date couverture
3. Si date_fin > date dump → STOP : demander dump frais
4. docker_mirror.py → Docker démarré ? conteneur miroir prêt ? (sinon message clair, pas de force)
5. runbook.md → restaurer le miroir si étape 4 échoue
6. interroger_eco_org.py → template CSV → *_rempli.csv (+ --save-sql)
7. Sanity checks + HITL
```

**Vérifier le miroir seul :**

```bash
python .cursor/skills/interroger-eco-organismes/scripts/docker_mirror.py
```

**Si tableur partenaire à remplir :** charger [references/README.md](references/README.md) — choisir la fiche adaptée au format reçu (pas de supposition Germaine).

---

## Format template (CSV)

Fichier modèle : [templates/interrogation-template.csv](templates/interrogation-template.csv)

| Colonne | Obligatoire | Description |
|---------|-------------|-------------|
| `id` | oui | Identifiant ligne (Q1, Q2…) |
| `partenaire` | oui | `ecologic` · `ecomaison` (v1) |
| `flux` | oui | `DEC_REE` · `LIV` · `RECYCLAGE` · `COUNT` · `SORTIES_DEPOT_KG` |
| `code` | oui* | Code portail Ecologic (PAM, ECR…) ou colonne Ecomaison (K–T) |
| `categorie_recyclique` | non | Libellé exact catégorie (prioritaire sur `code`) |
| `date_debut` / `date_fin` | oui | ISO `YYYY-MM-DD` · fin **inclusive** |
| `unite` | oui | `t` · `kg` · `pieces` |
| `destination` | non | Pour `RECYCLAGE` : défaut `RECYCLAGE` (benne interne) |
| `exclure_recyclage` | non | défaut `oui` pour DEC_REE |
| `resultat` / `statut` / `commentaire` | sortie | Remplis par le script |

```bash
python .cursor/skills/interroger-eco-organismes/scripts/interroger_eco_org.py \
  --template chemin/mon-template.csv \
  --output chemin/mon-template_rempli.csv \
  --save-sql log/cursor-agent/eco-org-queries.sql
```

---

## Règles métier (ne pas inventer)

| Flux | Source BDD | Date | Formule |
|------|------------|------|---------|
| **DEC_REE** | `sale_items` + `sales` + `categories` | `COALESCE(sale_date, created_at)` | `ROUND(SUM(weight)/1000,3)` t |
| **LIV** | `ligne_depot` + `ticket_depot` + `categories` | `ticket_depot.created_at` | `ROUND(FLOOR(SUM(poids_kg))/1000,3)` t |
| **RECYCLAGE** | idem LIV | `ticket_depot.created_at` | `is_exit=true` + `destination` (défaut RECYCLAGE) → **kg** |
| **SORTIES_DEPOT_KG** | idem LIV | idem | `is_exit=true` toutes destinations → **kg** (exploration) |
| **COUNT** | idem DEC_REE | idem | `COUNT(*)` lignes caisse |

Détail joins, pièges, sanity checks : [references/bdd-metier.md](references/bdd-metier.md)

- **Exclure recyclage caisse** : `notes NOT ILIKE '%recyclage%'` si `exclure_recyclage=oui`
- **LIV tableur ≠ LIV tickets** : deux sources ; ne pas fusionner sans CLIC
- **ASL cat.1/2** : split photobook → HITL
- **ABJ > 80 cm** : Ecomaison, pas Ecologic

---

## Fraîcheur dump (bloquant)

```bash
python .cursor/skills/interroger-eco-organismes/scripts/dump_manifest.py
```

Convention : `references/_depot/recyclic_db_export_YYYYMMDD_HHMMSS.dump`

---

## Ressources

| Priorité | Fichier | Contenu |
|----------|---------|---------|
| 1 | [runbook.md](runbook.md) | Docker, restore, sécurité |
| 2 | [mapping-reference.md](mapping-reference.md) | Codes ↔ catégories Recyclique |
| 3 | [references/bdd-metier.md](references/bdd-metier.md) | SQL, flux, sanity, exploration |
| 4 | [references/exploration-requetes.sql](references/exploration-requetes.sql) | Requêtes copiables |
| 5 | [examples.md](examples.md) | Cas T2 chiffré |
| — | [templates/interrogation-template-complet.csv](templates/interrogation-template-complet.csv) | Exemple DEC_REE + LIV + RECYCLAGE + Ecomaison |
| — | [scripts/docker_mirror.py](scripts/docker_mirror.py) | Vérif Docker / miroir (messages clair) |
| — | [references/bdd-metier-paheko.md](references/bdd-metier-paheko.md) | Frontière : Paheko = €, pas les volumes |
| — | [references/](references/) | Archives situational (ex. Germaine ODS) |

**Projet :** `references/eco-organismes/index.md` · `references/dumps/schema-recyclic-dev.md`

---

## Limites v1

- Partenaires : Ecologic + Ecomaison (colonnes K–T) dans le script
- Pas d'écriture dump / prod · pas de restauration Docker automatique
- Tableur partenaire : ad hoc — voir `references/`
- Paheko n'est **pas** une source de volumes

## Évolutions prévues

- YAML mapping officiel (story 9.ECO-01)
- Endpoint agrégats API (story 9.ECO-04)
