# Guide — Liaison caisse RecyClique × Paheko (compta)

**Date :** 2026-05-21  
**Statut :** doctrine produit + compta **figée** (3 passes Perplexity + terrain mai 2026) — détails techniques dans le PRD avril.

**Point d’entrée unique** — charger ce fichier en priorité ; les réponses Perplexity brutes restent dans `references/recherche/` pour audit.

---

## Lecture rapide (10 lignes)

1. Clôture **par session** : **T1** ventes+dons · **T2** remboursements (7070 ou 672) · **T3** écart 658/758 si \|écart\| ≤ **2 €**.
2. **RecyClique seul** produit les écritures API — **désactiver** la synchro auto de l’extension Caisse Paheko sur ces postes.
3. Comptes v1 : **7070**, **7541**, **5112**, **511**, **512**, **658/758**, **672** ; espèces **53x** (ou **530** mono-caisse).
4. **511 205 / 511 210** = module comptage UI seulement — **pas** dans le plan Paheko.
5. **Pas d’écriture** à l’ouverture de session ; fond de caisse = solde permanent sur le **53x** du poste.
6. Chèques → **5112** ; dépôt banque **5112 → 512** ; CB **511 → 512** (J+1/J+2).
7. Remb. courant → débit **7070** (pas **709**) ; exercice clos → débit **672** (une pièce API par remboursement).
8. Multi-caisse : **1 poste = 1 compte 53x** = **Lieu de vente** Paheko — voir doc multi-caisse.
9. **EC** : grille 53x, réimputation 672, fusion 754.xx, journaux, **754.900** (Carole).
10. Suite : implémentation procédure + brainstorm écran fermeture ; idées terrain → [recap 02](../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md).

---

## Documents canoniques (ne pas dupliquer ailleurs)

| Besoin | Fichier |
|--------|---------|
| Décisions D1–D38, rejets, questions EC | [decisions-compta-liaison-paheko-recherche-terrain.md](2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) |
| Tous les comptes + statuts + checklist EC | [repertoire-comptes-terrain-audio-recyclique.md](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) |
| Procédure opérationnelle T1/T2/T3 | [procedure-cloture-liaison-paheko-recyclique.md](2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) |
| Multi-caisse / lieux de vente | [multi-caisse-lieux-vente-paheko-recyclique.md](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) |
| Spec produit dev | [prd-recyclique-caisse-compta-paheko.md](2026-04-15_prd-recyclique-caisse-compta-paheko.md) |
| Idées terrain Réception + Paheko | [recap 02](../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md) |

---

## Paramétrage comptes (référence rapide)

| Rôle | Compte |
|------|--------|
| Ventes réemploi | **7070** |
| Dons caisse | **7541** |
| Espèces | **53x** ou **530** |
| Chèques | **5112** |
| Carte | **511** |
| Banque | **512** |
| Écart manque / trop-perçu | **658** / **758** |
| Remb. exercice clos | **672** |

**À ne plus utiliser :** 708, 467, 707, 7073, 709, 678/778 (RecyClique), 1630, 7041.

---

## Exemple clôture — mono-caisse (530)

**T1 — ventes + dons** : Débit 530 122 € + 5112 30 € + 511 50 € · Crédit 7070 200 € + 7541 2 €.  
**T3 — écart** (si besoin) : 658 ou 758 ↔ 530.  
**T2 — remb.** : 7070 ou 672 débit · trésorerie crédit.

Multi-postes : remplacer **530** par le **53x** du `cash_register`.

---

## Recherches Perplexity (sources)

| Passe | Réponse |
|-------|---------|
| 1re | [liaison-paheko-caisse-compta-terrain_perplexity_reponse.md](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md) |
| 2e validation | [validation-comptes-liaison-paheko_perplexity_reponse.md](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md) |
| 3e trous | [liaison-paheko-trous-recherche_perplexity_reponse.md](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md) |

*Ventilations intégrées 2026-05-21 ; rapports QA intermédiaires archivés sous `artefacts/archive/2026-05-21-menage-paheko-compta-qa/`.*

---

## Ateliers brainstorm (quand tu veux)

| Atelier | Sujet |
|---------|--------|
| **Fermeture** | Récap → comptage → écart → envoi Paheko → preuve |
| **Ticket** | Ligne payante / don textile −18 ans / gratuité ; entrée dans le Z de clôture |

---

*Dernière mise à jour : 2026-05-21 — fusion synthèses 06/09/11 ; ménage artefacts QA.*
