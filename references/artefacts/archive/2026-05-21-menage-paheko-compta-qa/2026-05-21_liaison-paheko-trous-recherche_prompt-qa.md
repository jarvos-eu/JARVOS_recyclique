# QA — prompt trous Liaison Paheko (3e passe Perplexity)

**Date :** 2026-05-21  
**Livrable audité :** [2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md](2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md)  
**Références croisées :** [décisions](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) §5–6, [répertoire](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md), [validation 2e passe](2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md), [PRD §9](2026-04-15_prd-recyclique-caisse-compta-paheko.md), [remboursements 04-02](2026-04-02_remboursements-compta-associations-loi-1901_perplexity_reponse.md), [audit caisse](../migration-paheko/audits/audit-caisse-paheko.md)

**Type / mode :** prd · medium · validation + adversarial ciblé  
**Pipeline :** Standard (boucle 1 → correctifs → boucle 2)

---

## Verdict

| Champ | Boucle 1 | Boucle 2 (après correctifs) |
|-------|----------|-----------------------------|
| **Autonomie Perplexity** | OK | OK |
| **Couverture trous §5 décisions** | Partiel (P1) | **OK** |
| **Cohérence PRD vs validation** | P1 manquant | **OK** (R2) |
| **Score** | **88 %** | **96 %** |
| **Verdict** | NO-GO | **GO** — prêt à coller |

---

## Boucle 1 — Issues

### Critical / P1

| ID | Problème | Correctif appliqué |
|----|----------|-------------------|
| T1-1 | **Nom fichier** : `…-perplexity_prompt.md` vs convention `…_perplexity_prompt.md` + liens dépôt cassés | Fichier renommé `_perplexity_` |
| T1-2 | **531 fond de caisse** : en attente EC (décisions §5) mais **aucun bloc R** | **R8** ajouté |
| T1-3 | **R1** : « audit existant » sans contexte inline → Perplexity aveugle | Contexte plugin 678/778 + constantes POS inline |
| T1-4 | **R2** : PRD stratégie B + **pièce écart** + tension **709 vs 7070** absentes | § R2 enrichi (6 questions + modèles PRD/validation/remboursements) |

### Warning / P2

| ID | Problème | Correctif |
|----|----------|-----------|
| T1-5 | **3 contrôles plan Paheko** (validation §5) non demandés en sortie | Livrable **C.6** ajouté |
| T1-6 | Module comptage obligatoire peu visible | Rappel en **§ A** |
| T1-7 | Livrable 5 : pas d’écriture **écart** ni **531** | Liste livrable 5 complétée |

### Info / P3

| ID | Problème | Statut |
|----|----------|--------|
| T1-8 | **511 220** virements tampon (décisions §6) | Non bloquant — couvert indirectement R6 (58/512) |
| T1-9 | **771.3** libéralités exceptionnelles | Hors scope D — volontaire |
| T1-10 | Copier-coller : indiquer lignes ~13–175 | Meta dépôt (non dans bloc) — OK |

---

## Checklist autonomie (bloc entre backticks)

| Critère | Boucle 2 |
|---------|----------|
| Aucun « voir fichier / references/… » dans le bloc | OK |
| Comptes figés 2e passe inline (§ A) | OK |
| Clôture 2 pièces + post-clôture banque | OK |
| Trous EC §5 décisions : plugin, lots, 754, 707, 672, 531 | OK (R1–R8) |
| PRD stratégie B 3 transactions inline | OK (R2) |
| Remboursements 709/7070 + même jour / J+N | OK (R2) |
| Livrables structurés C.1–C.7 | OK |
| Hors scope explicite | OK |
| Meta dépôt hors bloc | OK |

---

## Matrice couverture (décisions §5 → prompt)

| Thème décisions / répertoire | Bloc prompt |
|-----------------------------|-------------|
| Plugin 678/778 vs 658/758 | R1 |
| Lots PRD vs 2 pièces + écart | R2 |
| 754.1 / 754.x / 754.900 | R3 + C.6 |
| Migration 707 → 7070 | R4 |
| 672 fin d’exercice | R5 |
| Dépôt chèques, CB, multi-512, journal | R6 |
| API libellé, exercice ID, seuil écart, checklist prod | R7 |
| 530 vs 531 fond de caisse | **R8** |
| 5112 alignement terrain | R6 + C.6 |
| Cerfa, CVN, bien revendu | D hors scope — volontaire |

---

## Boucle 2 — Re-vérification

- [x] T1-1 à T1-7 corrigés dans le fichier prompt
- [x] Pas de régression autonomie
- [x] R2 ne contredit pas § A (511 CB, pas 512)
- [x] 8 blocs = 8 lignes attendues tableau C.1

**Score boucle 2 :** 96 % (0 P0, 0 P1, 1 P3 résiduel T1-8 acceptable)

---

## Ce que le prompt ne résout pas (normal)

1. Export **live** du plan Paheko — C.6 demande des contrôles, pas l’export SQL.
2. Décisions **531 / 754.x / migration 707** — recommandations Perplexity, signature **EC** obligatoire.
3. Paramétrage exact API Paheko (champs JSON) — R7 niveau métier seulement.

---

## Boucle 3 — Re-vérification R8 (post multi-caisse, 2026-05-21)

| Critère | Statut |
|---------|--------|
| R8 contexte mono + multi inline | OK |
| Aligné D24–D28 | OK |
| Score maintenu | **96 %** — **GO** |

---

## Suite

1. Copier le bloc intégral (l.13–~188) dans Perplexity Pro.  
2. Archiver la réponse dans `2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md`.  
3. Ventilation 2e passe + multi-caisse : [QA artefact 10](../artefacts/2026-05-21_10_qa-ventilation-compta-paheko-2026-05-21.md) (**GO**).
