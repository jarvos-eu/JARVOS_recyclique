---
stepsCompleted: [consolidation, ventilation, courrier, menage-depot]
session_topic: 'Liaison Paheko — validation compta caisse (post-réunion terrain mai 2026)'
session_goals: 'Consolider recherches + terrain ; produire dossier de validation pour la comptable ; figer plan comptable et fermeture avant implémentation'
selected_approach: 'consolidation-documentaire'
session_mode: 'consolidation-validation-hitl'
facilitator: 'Strophe (+ agent Cursor)'
date: '2026-05-21'
module_scope: 'liaison-paheko-compta-v1'
validation_status: 'EN_ATTENTE_COMPTABLE'
validation_gate: 'Corinne (comptable) + Caro (terrain Paheko) — retour écrit ou réunion'
blocked_until: 'validation-comptable-2026-05-21'
inputDocuments:
  - 'references/artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md'
  - 'references/recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md'
  - 'references/recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md'
  - 'references/recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md'
  - 'references/migration-paheko/2026-05-21_courrier-validation-compta-paheko-corinne-caro.md'
  - 'references/migration-paheko/2026-05-21_guide-liaison-paheko-compta.md'
  - 'references/migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md'
  - 'references/migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md'
  - 'references/migration-paheko/2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md'
  - 'references/migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md'
context_file: 'references/migration-paheko/2026-05-21_guide-liaison-paheko-compta.md'
related_brainstorm: 'brainstorming-session-2026-05-21-180000.md'
---

# Session BMAD — Liaison Paheko × compta caisse (consolidation & validation)

**Date :** 2026-05-21  
**Type :** consolidation documentaire (pas une session d’idéation 100+ idées)  
**Facilitateur :** Strophe  

---

## Statut global — **EN ATTENTE DE VALIDATION COMPTABLE**

| Élément | État |
|---------|------|
| Recherche & consolidation interne | **Faite** (2026-05-21) |
| Dossier envoyable Corinne + Caro | **Prêt** — [courrier](../../references/migration-paheko/2026-05-21_courrier-validation-compta-paheko-corinne-caro.md) |
| Paramétrage Paheko / dev RecyClique (T1/T2/T3, API) | **Bloqué** jusqu’au retour de **Corinne (comptable)** |
| Brainstorm écran fermeture caisse (UX bénévole) | **Après** validation compta |
| Epic BMAD « Liaison Paheko v1 » | **Après** validation compta |

**Gate HITL :** Corinne et Caro doivent cocher / corriger le courrier (§6) — comptes **53x**, écritures **A/B/C** (récap / remboursements / écart), seuil **±2 €**, synchro Paheko off, etc.

---

## Ce qui a été fait dans cette session (travail agent + Strophe)

### 1. Recherches Perplexity (3 passes) — ventilées dans le dépôt

| Passe | Sujet | Fichier réponse |
|-------|--------|----------------|
| 1re | Caisse associative, comptage, 7070/7541, -18 ans | `references/recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md` |
| 2e | Validation plan comptable (11 questions, 53x, 5112…) | `references/recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md` |
| 3e | Trous restants (T1/T2/T3, 672, synchro, 754, banque) | `references/recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md` |

### 2. Documents canoniques produits / mis à jour

| Document | Rôle |
|----------|------|
| [guide-liaison-paheko-compta.md](../../references/migration-paheko/2026-05-21_guide-liaison-paheko-compta.md) | Point d’entrée unique |
| [decisions-compta-liaison-paheko-recherche-terrain.md](../../references/migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) | D1–D38, rejets, questions |
| [procedure-cloture-liaison-paheko-recyclique.md](../../references/migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) | Opérationnel T1/T2/T3 |
| [multi-caisse-lieux-vente-paheko-recyclique.md](../../references/migration-paheko/2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) | 1 caisse = 1 compte 53x |
| [repertoire-comptes-terrain-audio-recyclique.md](../../references/migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) | Tous les comptes + checklist |
| [PRD §8.4 / §9.2](../../references/migration-paheko/2026-04-15_prd-recyclique-caisse-compta-paheko.md) | Aligné T3 = écart, T2 = remb. |

### 3. Courrier de validation (livrab le humain)

- **[2026-05-21_courrier-validation-compta-paheko-corinne-caro.md](../../references/migration-paheko/2026-05-21_courrier-validation-compta-paheko-corinne-caro.md)**  
  - Langage simple pour **Caro** et Strophe  
  - §5 complément compta pour **Corinne (comptable)**  
  - Écritures expliquées **A / B / C** (récap jour, remboursement, écart) — pas seulement T1/T2/T3  

### 4. Corrections métier importantes

- **« −18 »** = dons **textile aux moins de 18 ans** (pas une remise 18 %).  
- **Corinne** = **comptable** (pas expert-comptable).  
- Clôture : **minimum 1 écriture** (récap) ; **+1 par remboursement** ; **+1 écart** si ≤ 2 €.

### 5. Ménage dépôt

- Synthèses et rapports QA intermédiaires → `references/artefacts/archive/2026-05-21-menage-paheko-compta-qa/`  
- Essentiels conservés : guide, décisions, courrier, recap terrain `02`, réponses Perplexity.

### 6. Amont terrain

- Réunion Paheko transcrite (mai 2026) ; matière dans [recap 02](../../references/artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md) (PKO liaison Paheko + réception).

---

## Décisions proposées (résumé — non figées)

**Fermeture :**

- **A — Récap du jour** (T1) : toujours — ventes **7070** + dons **7541**.  
- **B — Remboursement** (T2) : si besoin — **7070** (exercice courant) ou **672** (exercice clos), 1 pièce / remb.  
- **C — Écart caisse** (T3) : si comptage ≠ 0 et ≤ **2 €** — **658** / **758**.

**Comptes clés :** 53x (ou 530 mono), 5112 chèques, 511 CB, 512 banque, 58 virements.

**Bloquant validation :** grille **53x**, réimputation **672**, fusion **754.xx**, journaux Paheko, **754.900**, CVN / dons textile moins de 18 ans (hors clôture v1).

---

## Suite BMAD (après validation Corinne)

| Ordre | Action | Type session |
|-------|--------|--------------|
| 1 | Intégrer retours comptable dans `decisions-*` + guide | Consolidation |
| 2 | **Brainstorm** parcours fermeture caisse (écran bénévole) | Brainstorming BMAD classique |
| 3 | Stories epic liaison Paheko v1 (outbox, T1/T2/T3, param postes) | create-story / dev |
| 4 | Réunion terrain si besoin (tableau poste ↔ lieu ↔ 53x) | HITL |

**Ne pas démarrer** l’implémentation ni le brainstorm UX fermeture tant que le courrier n’est pas validé par **Corinne (comptable)**.

---

## Lien avec autre session BMAD du jour

- [brainstorming-session-2026-05-21-180000.md](brainstorming-session-2026-05-21-180000.md) = module **Réception** v1 (REC-001…).  
- **Cette session** = chantier **Liaison Paheko / compta** — périmètre distinct, même source terrain `02`.

---

*Session consolidation — 2026-05-21. Statut : **en attente validation comptable (Corinne + Caro)**.*
