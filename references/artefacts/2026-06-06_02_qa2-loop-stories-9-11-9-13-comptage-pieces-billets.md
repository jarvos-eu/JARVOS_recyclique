# QA2 boucle — stories 9.11–9.13 comptage pièces/billets (documentation)

**Date :** 2026-06-06  
**Itération :** 1/3 (pass-1) + correctifs P0/P1 → re-score it. 2  
**Périmètre :** artefact HITL, stories 9.11/9.12/9.13, entrées `epics.md` 9.10–9.13, `sprint-status.yaml`

---

## Pass-1 — score initial : **82/100** — **NO-GO**

| ID | Sévérité | Sujet |
|----|----------|--------|
| P0-01 | P0 | Collision D-CPT-10 (poids vs Paheko) dans story 9.11 |
| P1-01 | P1 | Champs `float_target_cents` / `withdraw_cents` manquants en AC 9.11 |
| P1-02 | P1 | Contrat PDF anomalie absent en 9.11 |
| P1-03 | P1 | Cas tiroir vide (`theoretical = 0`) non précisé |
| P1-04 | P1 | Lien 9.12 obsolète dans 9.13 |

---

## Correctifs appliqués (itération 2)

- **9.11** : D-CPT-10 = poids ; **D-CPT-11** = Paheko ; AC3/4/5/13 étendus ; task PDF
- **9.13** : lien 9.12 corrigé
- **HITL artefact** : D-CPT-11 ajouté

---

## Pass-2 — score estimé : **96/100** — **GO**

| Règle | Résultat |
|-------|----------|
| Seuil 95 % | **Oui** |
| P0 = 0 | **Oui** |

**P2 résiduels (non bloquants)** : harmonisation `COMPTAGE_DENOMINATION_REQUIRED` → `COMPTAGE_REQUIRED` dans 08-MOD §9.3 ; note `show_images` dans schéma 08-MOD §4.2 ; mention explicite v2.0.2 dans blocs Pilotage `epics.md` (optionnel).

---

## Gate

**GO** pour lancer **`bmad-dev-story`** sur **9.11** (`ready-for-dev`), puis **9.12** → **9.13**.
