# Handoff — interroger Paheko pour déclarations éco-organismes

**Date :** 2026-08-18  
**Type :** handoff nouveau fil Cursor  
**Statut :** **corrigé 2026-08-18** — Paheko = compta € seulement ; volumes / éco-org = Recyclique. Ne plus suivre le plan `--source paheko` de ce handoff.

---

## Correction Strophe (2026-08-18, après session 1)

Paheko n'est **pas** une 2e source de volumes. Dump SQLite = **écritures, exercices, bilans**.  
Saisie au poids + Caisse Paheko : **désinstaller**. Recyclique reste le seul backend du skill.

Le plan ci-dessous ( `--source paheko`, mapping objets, compare deux colonnes) est **obsolète**.  
Skill à jour : `SKILL.md` + `references/bdd-metier-paheko.md` (frontière).

---

## En une phrase (obsolète — ne plus exécuter)

Étendre le skill **interroger-eco-organismes** pour interroger un dump Paheko SQLite en parallèle de Recyclique. **Annulé :** mauvais périmètre.

---

## Décision recommandée : enrichir, pas dupliquer

| Option | Verdict |
|--------|---------|
| **Nouveau skill `interroger-paheko`** | Risque de divergence (mapping, sanity checks, template CSV) |
| **Enrichir `interroger-eco-organismes`** | **Recommandé** — un workflow, deux backends (`--source recyclique` \| `paheko`) |

Le skill reste centré **déclarations éco-organismes** ; Paheko est une **source de données** supplémentaire, pas un sujet différent.

**Évolution cible du script :**

```bash
python .../interroger_eco_org.py \
  --source paheko \
  --template mon-template.csv \
  --output mon-template_paheko_rempli.csv
```

Recyclique garde Docker + PostgreSQL ; Paheko = **SQLite** (fichier dump, pas pg_restore).

---

## Ce qui existe déjà (ne pas réinventer)

| Ressource | Rôle |
|-----------|------|
| `.cursor/skills/interroger-eco-organismes/` | Skill canon Recyclique (DEC_REE, LIV, RECYCLAGE, Ecomaison K–T, docker_mirror.py) |
| `references/bdd-metier.md` (dans le skill) | Règles métier Recyclique |
| `references/migration-paheko/audits/audit-saisie-au-poids-paheko.md` | **LIV / DEC_REE Paheko** — `module_data_saisie_poids`, flags Ecologic |
| `references/migration-paheko/audits/audit-caisse-paheko.md` | Caisse — `plugin_pos_*`, poids lignes |
| `references/migration-paheko/categories-decla-eco-organismes.md` | Filières REP, vocabulaire |
| `references/dumps/schema-paheko-dev.md` | Schéma BDD Paheko (gitignore — régénérer si besoin) |
| Session Ecologic T2 | Golden tests, sanity PAM 246 t vs 1,1 t, skill durci |

---

## Dump Paheko — ce que Strophe doit fournir

1. **Fichier** dans `references/_depot/` (gitignore), convention proposée :
   - `paheko_association_YYYYMMDD.sqlite` ou copie de `association.sqlite`
2. **Date de l'export** (pour fraîcheur, comme Recyclique)
3. **Contexte** : prod La Clique ? pré-prod ? après clôtures caisse du trimestre visé ?

**Chemin canon Paheko dans un conteneur :** `/var/www/paheko/data/association.sqlite`

**Dump reçu (2026-08-18) :** `references/_depot/L'Eco de la Clique - Sauvegarde données - PAHEKO - 2026-08-18.sqlite` (~54 Mo, Paheko 1.3.22.1). Dump **compta** (attendu). Saisie au poids encore listée mais désactivée : **désinstaller**, ne pas activer. Caisse absente : ne pas installer.

---

## Tables Paheko à explorer (priorité décla)

### 1. Extension Saisie au poids (source décla Ecologic native Paheko)

| Table / stockage | Contenu | Flux métier |
|------------------|---------|-------------|
| `module_data_saisie_poids` | Documents JSON (entrées / sorties / config) | **LIV**, **PRE**, **DEC_REE** via flag type opération Ecologic |

→ Aligner avec les **18 cases** Ecologic et exports « Déclaration Ecologic » de l'extension.

### 2. Plugin Caisse (DEC_REE alternatif / complément)

| Table | Colonnes clés | Flux |
|-------|---------------|------|
| `plugin_pos_sessions` | `closed` (session clôturée) | Filtre période |
| `plugin_pos_tabs` / `plugin_pos_tabs_items` | `weight`, catégorie, produit | **DEC_REE** (ventes au poids) |
| `plugin_pos_categories` | nom catégorie | Mapping → codes filière |

→ Import manuel vers Saisie au poids dans Paheko ; vérifier si le dump contient déjà les deux ou seulement caisse.

### 3. Croisement Recyclique ↔ Paheko

- Recyclique = **source de vérité opérationnelle** (artefacts 2026-02-25)
- Paheko peut être **miroir compta + décla legacy** ou **source officielle** selon filière / période
- **Ne pas fusionner** sans règle explicite — produire **deux colonnes** (recyclique \| paheko) + HITL si écart

---

## Plan de travail session 1 (nouveau fil)

```text
Phase A — Dump & schéma
  1. Strophe dépose le dump dans references/_depot/
  2. Vérifier format (sqlite3 .tables)
  3. Charger / régénérer schema-paheko-dev.md si absent
  4. Lister module_data_saisie_poids (structure JSON, champs Ecologic)

Phase B — Mapping
  5. Lier catégories Paheko ↔ codes Ecologic/Ecomaison (étendre mapping-reference.md)
  6. Repérer équivalents DEC_REE / LIV / RECYCLAGE côté Paheko

Phase C — Script
  7. Étendre dump_manifest.py (paheko sqlite + date)
  8. Ajouter check_paheko_mirror.py (fichier existe, sqlite lisible, tables clés)
  9. Étendre interroger_eco_org.py --source paheko (sqlite3 local, pas Docker)
  10. Réutiliser le même template CSV + colonne resultat

Phase D — Validation
  11. Golden / sanity : comparer un trimestre connu (ex. T2 2026 Ecologic) Recyclique vs Paheko
  12. Documenter écarts dans references/bdd-metier-paheko.md (skill)
  13. Mettre à jour SKILL.md (section Paheko intégrée)

Phase E — Livrables
  14. queries-decla-paheko.sql (ou .md avec requêtes SQLite)
  15. CSV rempli + HITL si divergence majeure
```

---

## Pièges anticipés

| Piège | Action |
|-------|--------|
| Double comptage caisse + saisie au poids | Paheko doc : une seule source pour sorties ; filtrer `pos_session_id` |
| JSON dans `module_data_saisie_poids` | Parser en Python ; pas SQL naïf |
| Dates | Identifier champ date sur documents (created_at, session closed, etc.) |
| Catégories Paheko ≠ Recyclique | Mapping explicite ; pas d'alias silencieux |
| Dump sans sessions clôturées | DEC_REE caisse incomplet — message clair utilisateur |

---

## Fichiers à créer / modifier (session cible)

| Fichier | Action |
|---------|--------|
| `.cursor/skills/interroger-eco-organismes/scripts/interroger_eco_org.py` | `--source paheko` |
| `.cursor/skills/interroger-eco-organismes/scripts/dump_manifest.py` | Détecter dumps Paheko |
| `.cursor/skills/interroger-eco-organismes/scripts/check_paheko_dump.py` | Vérif SQLite (équivalent docker_mirror) |
| `.cursor/skills/interroger-eco-organismes/references/bdd-metier-paheko.md` | Règles métier Paheko |
| `.cursor/skills/interroger-eco-organismes/references/exploration-requetes-paheko.sql` | Requêtes SQLite |
| `.cursor/skills/interroger-eco-organismes/mapping-reference.md` | Section Paheko |
| `.cursor/skills/interroger-eco-organismes/SKILL.md` | Workflow multi-source |

---

## Prompt reprise (coller en tête du nouveau fil)

```text
Handoff — Paheko + déclarations éco-organismes (enrichissement skill existant).

Charger en priorité :
  1. references/artefacts/2026-08-18_01_handoff-interroger-paheko-eco-organismes.md
  2. .cursor/skills/interroger-eco-organismes/SKILL.md
  3. .cursor/skills/interroger-eco-organismes/references/bdd-metier.md (Recyclique — référence)
  4. references/migration-paheko/audits/audit-saisie-au-poids-paheko.md
  5. references/migration-paheko/audits/audit-caisse-paheko.md

Objectif : étendre le skill interroger-eco-organismes pour interroger un dump Paheko (SQLite)
avec le même template CSV (DEC_REE, LIV, RECYCLAGE…) — pas un nouveau skill.

Dump Paheko à utiliser : references/_depot/<fichier fourni par Strophe>

Plan :
  - Explorer schéma (module_data_saisie_poids, plugin_pos_*)
  - Mapping Paheko → codes Ecologic/Ecomaison
  - Script --source paheko + vérif dump (messages clairs si fichier absent / tables manquantes)
  - Comparer avec agrégats Recyclique sur une période test si miroir Docker encore dispo
  - Documenter dans skill/references/bdd-metier-paheko.md

Règles :
  - SELECT only sur dumps
  - Ne pas fusionner Recyclique et Paheko sans validation — deux colonnes + HITL
  - Messages utilisateur en français clair (comme docker_mirror.py)
  - Germaine / tableurs partenaires = non prioritaire (cf. skill references/archive-germaine)

Commencer par : confirmer le dump fourni, sqlite3 .tables, puis exploration module_data_saisie_poids.
```

---

## Liens

- Skill Recyclique : `.cursor/skills/interroger-eco-organismes/`
- Éco-org La Clique : `references/eco-organismes/index.md`
- Migration Paheko : `references/migration-paheko/index.md`
- Cadrage Ecologic 1.4.5 : `references/artefacts/2026-07-07_04_cadrage-patch-1.4.5-ecologic.md` (gaps Paheko/LCQ)
