# QA — ventilations compta Liaison Paheko (2026-05-21)

**Date :** 2026-05-21  
**Périmètre :** ventilation réponse validation 2e passe + doctrine multi-caisse + cohérence dépôt  
**Références :** [réponse validation](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md), [décisions](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md), [répertoire](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md), [multi-caisse](../migration-paheko/2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md), [synthèse 09](2026-05-21_09_synthese-validation-comptes-perplexity.md), [PRD §5.3](../migration-paheko/2026-04-15_prd-recyclique-caisse-compta-paheko.md)

**Voir aussi :** [QA prompt 3e passe](../recherche/2026-05-21_liaison-paheko-trous-recherche_prompt-qa.md) (GO 96 %, boucles 1–2 + re-vérif R8).

---

## Synthèse des verdicts

| Lot | Boucle 1 | Correctifs | Boucle 2 | Score |
|-----|----------|------------|----------|-------|
| **A — Ventilation 2e passe** | NO-GO | 6 correctifs | **GO** | **94 %** |
| **B — Multi-caisse** | NO-GO | 4 correctifs | **GO** | **97 %** |
| **C — Prompt 3e passe** | (déjà fait) | — | **GO** | **96 %** |

**Verdict global :** **GO** — lots A/B/C (2e passe + multi-caisse). **Lot D (3e passe)** : voir [QA 12](2026-05-21_12_qa-ventilation-3e-passe-perplexity.md) — **GO 96 %**.

---

## Lot A — Ventilation réponse validation 2e passe

### Boucle 1 — Issues

| ID | Gravité | Problème |
|----|---------|----------|
| V2-1 | P1 | **Synthèse 09** : « tout est 530 », tableau espèces 530 — **contredit** multi-caisse postérieure |
| V2-2 | P1 | **Répertoire §7** : pièce 2 écart en **530** au lieu de **53x du poste** |
| V2-3 | P2 | **Décisions** : D22/D23 **après** D24–D28 (ordre tableau) ; D23 encore « 530 → 6xx » |
| V2-4 | P2 | **Décisions sources** : pas de lien vers doc multi-caisse |
| V2-5 | P2 | **§7.1 EC** : pas de question **5112/511** multi-banques (pourtant §5) |
| V2-6 | info | Matrice 11 Q → D16–D23 : couverture **OK** (vérifiée ci-dessous) |

### Correctifs appliqués

- [x] Synthèse 09 réécrite (mono vs multi, liens, exemple annoté)
- [x] Répertoire workflow + checklist 53x
- [x] Décisions : ordre D22–D28, D23 en 53x, sources, §7.1
- [x] En-tête réponse validation : lien multi-caisse (ci-dessous)

### Matrice couverture réponse §1 (11 Q) → dépôt

| Q réponse | Intégré ? | Où |
|-----------|-----------|-----|
| Q1 trésorerie | OK | D16, D17, §4, répertoire §1 |
| Q2 530 vs 53 | OK | D21, multi-caisse §10 |
| Q3 1630 | OK | D21, rejeté, répertoire |
| Q4 531 fond | OK | D24–D26, multi-caisse, §5 (plus « 530 seul ») |
| Q5 658/758 | OK | D19, §4 |
| Q6 7541 / 754.x | OK | §5, répertoire §2 |
| Q7 58 | OK | D22, D28, multi-caisse §5 |
| Q8 471/472 | OK | D23, répertoire |
| Q9 7070 | OK | D7, §5 migration, répertoire |
| Q10 chèque mixte | OK | D10, D16 |
| Q11 672 | OK | §2, répertoire |

### Matrice plan comptable §2 → répertoire

| Lignes réponse D.1–D.3 | Répertoire |
|------------------------|------------|
| 530, 531, 511, 5112, 512, 58, 471, 472, 707/7070, 754.x, 678/778, 708/467/7073/7041 | §1–§3 — **OK** |
| 754.900 | **À clarifier** — conservé |

### Boucle 2 — Score **94 %** (0 P1, 0 P2)

---

## Lot B — Ventilation multi-caisse

### Boucle 1 — Issues

| ID | Gravité | Problème |
|----|---------|----------|
| MC-1 | P1 | **Synthèse 09** non alignée (voir V2-1) |
| MC-2 | P2 | **PRD §5.3** présent mais **synthèse** et **§4 décisions** divergeaient sur espèces globales |
| MC-3 | P2 | **Checklist répertoire §8** listait 530 en premier sans mention multi |
| MC-4 | info | **Prompt R8** : contexte multi ajouté après coup — **OK** dans prompt actuel |

### Correctifs appliqués

- [x] Doc pivot `2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md`
- [x] D24–D28, §4, §3 rejets, PRD §5.3, spec SuperAdmin encart
- [x] Répertoire 5311–5331, §1 bis, workflow
- [x] Index migration-paheko + config-modules-site-id

### Boucle 2 — Score **97 %**

| Critère | Statut |
|---------|--------|
| Entités sites / cash_registers / sessions | OK |
| 7 caisses exemple | OK |
| 58 virements | OK |
| Pas de contradiction D4 / §4 / PRD | OK (après correctifs) |
| Liens croisés bidirectionnels | OK |

---

## Lot C — Prompt 3e passe (re-vérification R8)

| Champ | Statut |
|-------|--------|
| R8 inline multi-caisse (mono + 7 postes) | OK |
| Questions restantes (ouverture, 5112/511 multi) | OK |
| Pas de « voir references/ » dans bloc | OK |
| Cohérence avec décisions D24–D28 | OK |

**Note :** la 3e passe Perplexity peut **raccourcir** R8 (points déjà figés en dépôt) — garder les 3 questions ouvertes R8.

---

## Écarts résiduels (non bloquants)

1. **PRD §6 exemples** et **§9.3** utilisent encore **530** en dur — cohérent comme **exemple mono-caisse** ; pas de refactor global du PRD demandé.
2. **Recyclique** vs **RecyClique** : mélange historique dans PRD / recap — hors périmètre QA compta.
3. **754.900** : toujours inconnu jusqu'à export plan Paheko.

---

## Suite recommandée

1. Coller le **prompt 3e passe** dans Perplexity.  
2. Réunion EC avec **checklist répertoire §8** + grille [multi-caisse §3](../migration-paheko/2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md).  
3. Brainstorm fermeture (2 pièces + comptage par poste).
