# MISSION — Assistance décla Ecologic T2 2026 (urgence terrain)

**Type :** mission **exceptionnelle** d'assistance — **hors** livraison patch 1.4.5 complet.  
**Statut :** `en cours` — dump BDD **reçu** 2026-07-07 · miroir read-only à restaurer.  
**Date cadrage :** 2026-07-07  
**Échéance indicative :** ~**30/07/2026** (T2 Ecologic, hypothèse J+30)

> **Entrée unique session suivante :** lire ce fichier puis le spec détaillé  
> [`references/artefacts/2026-07-07_06_mission-assistance-decla-ecologic-t2-recyclic-144.md`](../../../../../artefacts/2026-07-07_06_mission-assistance-decla-ecologic-t2-recyclic-144.md)

---

## En une phrase

Restaurer le **dump PostgreSQL** La Clique en **miroir read-only**, croiser avec l'**ODS T2** et son **mode d'emploi**, produire un **CSV de complément** pour les **cases manquantes** (surtout **8 × `DEC_REE`**) — **sans rien inventer** ; tout trou en **HITL**.

---

## Dump BDD (canon)

| Fichier | Rôle |
|---------|------|
| **`references/_depot/recyclic_db_export_20260707_152448.dump`** | **Canon** — export 2026-07-07 15:24, pré-prod live 1.4.4 |
| `references/_depot/recyclic_db_export_20260411_172643.dump` | Archive avril 2026 |

*(gitignore — non versionné)*

---

## Fichiers clés (ne pas re-parser l'ODS)

| Rôle | Chemin |
|------|--------|
| ODS en cours | [`DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods`](DeclarationESS-ECOLOGIC-ECOMAISON-EntreesSorties-REMPLI.ods) |
| Mode d'emploi | [`DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md`](DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md) |
| Spec mission | [`references/artefacts/2026-07-07_06_…`](../../../../../artefacts/2026-07-07_06_mission-assistance-decla-ecologic-t2-recyclic-144.md) |
| Schéma BDD (ref.) | [`references/dumps/schema-recyclic-dev.md`](../../../../../dumps/schema-recyclic-dev.md) |
| Kanban | [`IDEA-2026-07-07-001`](../../../../../../docs/ideas/kanban/IDEA-2026-07-07-001.md) |
| Miroir + bot (futur) | [`IDEA-2026-07-05-002`](../../../../../../docs/ideas/kanban/IDEA-2026-07-05-002.md) § miroir BDD |
| Fil reprise | [`REPRISE.md`](../../../../../../REPRISE.md) § mission urgence Ecologic T2 |
| Index éco-org | [`references/eco-organismes/index.md`](../../../../index.md) |

---

## Prompt reprise (coller en tête de chat)

```
Mission urgence — assistance décla Ecologic T2 2026 La Clique.
Charger : references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/2026-07-07_mission-assistance-decla-ecologic-t2-2026.md
         + references/artefacts/2026-07-07_06_mission-assistance-decla-ecologic-t2-recyclic-144.md
         + DeclarationESS-ECOLOGIC-2T2026_MODE-EMPLOI.md (même dossier)
Dump canon : references/_depot/recyclic_db_export_20260707_152448.dump
→ pg_restore miroir local read-only → requêtes T2 → CSV complément DEC_REE.
Règle absolue : rien inventer — relever chaque inconnue en HITL pour Strophe.
Livrable : Complément-DEC_REE-T2-2026.csv + HITL-questions-decla-ecologic-t2-2026.md (ce dossier 2026-T2/)
```

---

## Trio BMAD

| Rôle | Action faite / attendue |
|------|-------------------------|
| **Mentor** | Cadrage mission + kanban + fil REPRISE |
| **Clio** | Section REPRISE + prompt reprise |
| **Ariane** | Item P0 `references/todo.md` — pas de story BMAD tant que mission assistance |
