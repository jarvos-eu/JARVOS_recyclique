# QA — prompt validation comptes (2e passe Perplexity) — boucle 2

**Date :** 2026-05-21  
**Livrable audité :** [2026-05-21_validation-comptes-liaison-paheko_perplexity_prompt.md](2026-05-21_validation-comptes-liaison-paheko_perplexity_prompt.md)  
**Références croisées :** [répertoire comptes](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md), [décisions](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md), [1re réponse Perplexity](2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md)

---

## Verdict

| Champ | Valeur |
|-------|--------|
| **Autonomie Perplexity** | **OK** — aucun « voir fichier X » dans le bloc copier-coller |
| **Couverture comptes** | **OK** — répertoire terrain + seeds RecyClique + obsolètes |
| **Couverture questions** | **OK** — 11 Q + livrables |
| **Bêtises / coquilles** | **Corrigées** (voir lot 2 ci-dessous) |
| **Verdict** | **GO** — prêt à coller |

---

## Checklist autonomie (bloc entre backticks)

| Critère | Statut |
|---------|--------|
| Contexte projet inline (A) | OK |
| Synthèse 1re recherche inline (B) | OK |
| Décisions produit (C) | OK |
| Liste comptes Paheko terrain (D.1) | OK |
| Param RecyClique (D.2) | OK |
| Comptes obsolètes 708/467/7073/7041 (D.3) | OK (ajout boucle 2) |
| Tableau écarts (D.4) | OK |
| 11 questions (E) | OK |
| Livrable structuré (F) | OK |
| Hors scope (G) | OK |
| Consignes (H) | OK |
| Meta dépôt **hors** bloc | OK (l.1–8 + l. fin) |

---

## Lot correctif — boucle QA 2 (2026-05-21)

| ID | Gravité | Problème | Correctif |
|----|---------|----------|-----------|
| Q2-1 | P2 | **5112** absent du tableau Paheko (écart majeur RecyClique vs terrain) | Ligne D.1 + rappel D.4 |
| Q2-2 | P2 | Comptes **708, 467, 7073, 7041** seulement mentionnés en passant dans D.2 | Section **D.3 obsolètes** |
| Q2-3 | P2 | Livrable plan cible ne mentionnait pas D.3 | F.2 → D.1 + D.2 + **D.3** |
| Q2-4 | P3 | Pas de rappel **batch** multi-écritures / prorata chèque dans B | Bullets B ajoutés |
| Q2-5 | P3 | Pas de **3 contrôles comptable** en sortie | Livrable F.5 |
| Q2-6 | P3 | **754.900** absent du répertoire prompt | Ligne D.1 |
| Q2-7 | info | Tableau D.1 brisé (3 colonnes) après ajout | Corrigé 2 colonnes |

**Boucle 1 (rapport précédent)** : Q9–Q11, écarts D.4, autonomie — déjà intégrés.

---

## Matrice couverture (répertoire → prompt)

| Élément répertoire / décisions | Dans prompt ? |
|-------------------------------|---------------|
| 530, 531, 511, 5112, 512, 205, 210 | D.1 / D.2 / Q1 |
| 707, 7070, 7073 | D.1 / D.3 / Q9 |
| 754.x, 7541 | D.1 / Q6 |
| 708, 467, 672, 772 | D.2 / D.3 / Q11 |
| 658/758 vs 678/778 | Q5 |
| 471, 472, 58, 53, 1630 | D.1 / Q2–Q8 |
| 7041, 754.900 | D.3 / D.1 |
| 771.3, 754.12, 756, 603 | D.1 ou G hors scope |
| Ticket mixte -18 | B + C |
| Module comptage | A + C + Q1 |
| Cerfa, CVN, bien revendu | G (hors scope) — **volontaire** |

---

## Ce que le prompt ne peut pas résoudre (normal)

1. Export **exact** du plan comptable Paheko à la date du jour (écran Comptabilité) — F.5 demande des **contrôles**, pas l’export.
2. Validation juridique définitive — reste EC.
3. Paramétrage journal `CA` et exercice Paheko (ID manuel) — hors numéros de comptes.

---

## Limites connues (non bloquantes GO)

- Liste Paheko D.1 = **terrain mai 2026** (oral + navigation), pas dump SQL — assumé jusqu’à export Carole.
- **RecyClique** vs ancienne orthographe « Recyclique » dans le code : prompt impose **RecyClique** (H).

---

## Suite

1. Copier le bloc intégral (l.12–~205) dans Perplexity Pro.  
2. Archiver la réponse dans `2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md`.  
3. Ventiler vers `decisions` + `repertoire-comptes` si des lignes passent de « à trancher » à « retenu ».
