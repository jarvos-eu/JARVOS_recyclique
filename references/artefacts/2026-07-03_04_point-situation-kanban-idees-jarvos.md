# Point de situation — Kanban idées JARVOS Recyclique (post-triage lot A)

**Date de l'instantané :** 2026-07-03  
**Emplacement :** `references/artefacts/2026-07-03_04_point-situation-kanban-idees-jarvos.md`

---

## Relation avec l'instantané précédent

Analyse détaillée par carte (2026-04-18) et inventaire 23 cartes (2026-04-19) :

- [`2026-04-18_02_point-situation-kanban-idees-jarvos.md`](2026-04-18_02_point-situation-kanban-idees-jarvos.md)
- [`2026-04-19_02_point-situation-kanban-idees-jarvos.md`](2026-04-19_02_point-situation-kanban-idees-jarvos.md)

**Repère permanent :** [`references/idees-kanban/point-situation.md`](../idees-kanban/point-situation.md).

---

## Delta depuis 2026-04-19

| Élément | Détail |
|---------|--------|
| **Archivages lot A (7)** | Hygiène spirale 1 — cartes couvertes par décisions/epics, section « Intégrée — » + move `archive/` |
| **todo.md** | Spirale 1 clos ; doublons LLM/Peintre → `[x]` avec lien Kanban ; politique fichiers → fiche `chantier-fichiers` |
| **Inventaire actif** | **11** fiches hors `archive/` (5 conceptualiser + 1 rechercher + 5 creuser) ; **13** en archive |

### Cartes archivées (2026-07-03)

| Fichier | Motif archivage |
|---------|-----------------|
| `2026-02-24_integration-paheko-core.md` | Décisions max Paheko, cartographie, Epic 9, guide liaison compta |
| `2026-02-24_sync-financiere-caisse-paheko.md` | Décisions push, Redis Streams, story 9.10 |
| `2026-02-24_calendar-espace-fichiers-paheko.md` | Recherche capacités natives + décision agenda externe |
| `2026-02-24_plugin-framework-recyclic.md` | Design système modules (artefact 07) |
| `2026-02-24_module-correspondance-paheko.md` | Pattern plugin PHP + Epic 9 ; détail → todo post-v2 |
| `2026-02-24_nouvelles-ui-workflows-paheko.md` | Pattern UI modules ; workflows concrets = Epic 8 / gated |
| `2026-02-24_jarvos-le-fil-placeholder-github.md` | Hors scope explicite |

---

## Inventaire actif (11 cartes — 2026-07-03)

| # | Fichier | Stade |
|---|---------|-------|
| 1 | `2026-02-24_readme-international-ou-multipays.md` | a-conceptualiser |
| 2 | `2026-02-24_readme-contexte-projet-ancien-repo.md` | a-conceptualiser |
| 3 | `2026-02-24_module-store-recyclic.md` | a-conceptualiser |
| 4 | `2026-02-26_parcours-ouverture-caisse-postes-acces-pin.md` | a-conceptualiser |
| 5 | `2026-04-14_configuration-raccourcis-clavier-par-poste.md` | a-conceptualiser |
| 6 | `2026-03-31_peintre-workflows-raccourcis-navigation.md` | a-rechercher |
| 7 | `2026-02-25_chantier-fichiers-politique-documentaire.md` | a-creuser |
| 8 | `2026-02-24_jarvos-ports-nano-mini-peintre.md` | a-creuser |
| 9 | `2026-02-24_ia-llm-modules-intelligents.md` | a-creuser |
| 10 | `2026-02-24_ui-modulaire-configurable.md` | a-creuser |
| 11 | `2026-05-20_peintre-gardeien-seuil-conscience-affichage.md` | a-creuser |

**Couverture : 11/11** — aligné avec [`references/idees-kanban/index.md`](../idees-kanban/index.md) (stades actifs uniquement).

---

## Archive (13 cartes cumulées)

6 archivages antérieurs (2026-03-01 → 2026-04-23) + 7 archivages lot A (2026-07-03). Détail : colonne Stade = `archive` dans l'index Kanban.

---

## todo.md — état post-triage

| Item | Statut |
|------|--------|
| Spirale 1 découverte | `[x]` condensé (section dédiée) |
| Stratégie LLM/IA | `[x]` → Kanban `ia-llm-modules-intelligents` |
| Peintre gardien du seuil | `[x]` → Kanban `peintre-gardeien-seuil-conscience-affichage` |
| Politique fichiers | `[ ]` → Kanban `chantier-fichiers-politique-documentaire` |
| Front caisse, checklist v0.1, presets, correspondance | `[ ]` post-v2 / gated |

---

## Limites

Pas de re-scan repo code : tri documentaire Kanban + todo uniquement. Prochaine photo complète si déplacement massif de stades ou nouvel epic.
