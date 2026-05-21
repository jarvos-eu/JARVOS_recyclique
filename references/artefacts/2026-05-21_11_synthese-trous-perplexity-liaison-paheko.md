# Synthèse — Perplexity 3e passe (trous Liaison Paheko)

**Date :** 2026-05-21  
**Source :** [réponse 3e passe](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md) · [prompt](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md)  
**Ventilé vers :** [décisions D29–D38](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) · [procédure T1/T2/T3](../migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) · [répertoire](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) · [PRD §8.4 / §9.2](../migration-paheko/2026-04-15_prd-recyclique-caisse-compta-paheko.md)  
**QA :** [12_qa-ventilation-3e-passe](2026-05-21_12_qa-ventilation-3e-passe-perplexity.md)

---

## 1. Verdict global

La 3e passe **ferme les trous opérationnels** restants après validation comptes (2e passe) et doctrine multi-caisse. Le modèle cible est **3 transactions API** par session (T1/T2/T3), avec **RecyClique seul producteur** d’écritures Paheko (synchro auto extension Caisse **désactivée**).

---

## 2. Décisions tranchées (R1–R8)

| Bloc | Décision | Codable v1 sans EC |
|------|----------|-------------------|
| **R1** Plugin 678/778 | Pas de comptes 678/778 documentés pour l’extension ; risque = **doublon** si synchro auto Paheko + API RecyClique → **désactiver** synchro (exercice vide) | Oui |
| **R2** Lots clôture | **T1** ventes+dons · **T2** remb. (7070 courant / 672 clos, **1 pièce/remb.**) · **T3** écart 658/758 ; **709 rejeté** | Oui (7070/672, label ≤200 car.) |
| **R3** 754 | **7541 seul** v1 ; **7542** si dons affectés projet ; fusion **754.xx → 7541** début N+1 | Partiel (7541) |
| **R4** 707→7070 | **Ne pas reclasser** N-1 ; créer **7070**, note annexe rapport | Oui |
| **R5** 672 | Débit **672** si vente sur exercice clos ; réimputation fin exercice (658/672) → **EC** | Oui (blocage si exercice clos mal paramétré) |
| **R6** Banque | Chèques **5112→512** (bordereau) ; CB **511→512** J+1/2 ; virements **58** | Hors clôture session (procédure) |
| **R7** API / écart | `id_year: current` ; seuil **±2 €** (blocage au-delà) ; libellé `Z SESSION …` | Oui |
| **R8** Fond / mono | **Pas d’écriture** à l’ouverture ; fond = solde permanent **53x** (mono **530**) | Oui |

---

## 3. Écarts documentaires résolus

| Avant | Après 3e passe |
|-------|----------------|
| PRD T3 = remb. exercice antérieur | **T3 = écart** ; **672** dans **T2** (exercice clos) |
| Plugin 678/778 « en attente » | **658/758** RecyClique ; synchro native **off** |
| « 2 pièces » ambigu | **T1 + T3** (+ **T2** si remb.) — voir [procédure](../migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) |
| 709 pour remboursements | **7070** débit (courant) — **709 rejeté** |

---

## 4. Reste pour expert-comptable

1. Réimputation **672** fin d’exercice (compte cible, date OD).  
2. OD fusion **754.xx → 7541** (N+1).  
3. Journaux Paheko exacts (Recettes / OD / Banque).  
4. Caisse native Paheko en parallèle (anti-doublon si cas réel).  
5. **7542** selon subventionneurs ; **754.900** à identifier (Carole).

---

## 5. Suite porteur produit

| Priorité | Action |
|----------|--------|
| 1 | Implémenter procédure T1/T2/T3 + outbox + seuil 2 € |
| 2 | Param SuperAdmin : désactiver synchro Paheko caisse sur sites RecyClique |
| 3 | Brainstorm **écran fermeture** + module comptage (déjà obligatoire) |
| 4 | Réunion EC / Carole — checklist [répertoire §8](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) |

---

*Dernière mise à jour : 2026-05-21 — ventilation + QA artefact 12.*
