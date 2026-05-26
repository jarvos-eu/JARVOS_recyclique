# QA2 — Plan post-9.6 plancher & compta

**Date** : 2026-05-26  
**Livrable audité** : `.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md`  
**Méthode** : QA2 délégué (`@qa2-orchestrator`) — planner + 3 workers (it. 1) → correctifs plan → re-QA2 → it. 2 correctifs → validation finale.  
**Gate** : score ≥ 95 %, P0 plan = 0 (`workflow-loop.md`).

---

## Verdict final (itération 2)

| Métrique | Valeur |
|----------|--------|
| **Score fusionné** | **97 / 100** |
| **P0 ouverts (plan)** | **0** |
| **Gate 95 %** | **Atteint** (contenu plan) |
| **Itérations boucle** | **2 / 3** |
| **P1 restants** | **2** (non bloquants) |

**Méta-gate C0bis (exécution)** : ce rapport satisfait la condition « artefact 04 publié avec P0 plan = 0 et score ≥ 95 % ». Le Coordinateur peut lancer **C1** après lecture de ce fichier. **C1 reste interdit** tant que ce rapport n’était pas publié (corrigé en it. 2 dans le plan, L35).

---

## Historique des scores

| Phase | Passes | Score moyen | P0 | Verdict |
|-------|--------|-------------|-----|---------|
| QA2 initial | validation doc 90, concept 78, adversarial 62 | **77** | 8+ (fusion) | Non |
| Re-QA2 it. 1 | validation 91, adversarial 84 | **88** | 3 résiduels | Non |
| Re-QA2 it. 2 | validation finale | **97** | 0 | **Oui** |

---

## Synthèse exécutive

Le plan post-9.6 est **exécutable** pour orchestrer **Agent A** (parité plancher), **Agent B** (liaison Paheko 2.0.1) et **Coordinateur** en parallèle contrôlé. Les correctifs it. 1–2 ont comblé les trous majeurs : **protocole C-sync** (fermeture caisse), **conditionnement DS B**, **gates C0bis→C2a→C2b→C3**, **dérogation EC** documentée, **MVP D5 dégradée**, **QA2 sur livrables** (rapport 03 seul pour A), **pont D33/D29**, **interdiction tags v2.0.0 / v2.0.1** avant C2b.

**Points forts** : un chat = un rôle ; délégation Task systématique ; owners fichiers ; hors scope répété ; gate pytest explicite ; chemins qa2-agent.

**Risques résiduels (P1)** : alignement **brief 02 fil E** avec dérogation EC du plan (sync en C3 ou patch brief avant C1) ; critères **tag v2.0.1** vs **Fin B** (story done + QA2 B) à harmoniser en une ligne.

---

## Issues fusionnées (état final)

### P0 — tous fermés

| Thème | Statut | Correctif appliqué |
|-------|--------|-------------------|
| Sync fermeture caisse | Fermé | Tableau C-sync + pause DS + GO Coordinateur |
| Parallélisme A/B / DS B | Fermé | DS après § fermeture caisse A ou GO |
| C2a / C2b / C3 / HITL | Fermé | Checklist, C3 après C2b |
| Gate EC vs brief 02 | Fermé | Tableau `EN_ATTENTE_VALIDATION_COMPTABLE` + dérogation fil E |
| MVP sans module D5 | Fermé | v1 dégradée + écart manuel admin |
| C0bis / méta-QA | Fermé | Formulation « cible » + ce rapport 04 |
| QA2 scope A | Fermé | `scope_paths` = rapport 03 uniquement |
| Pont D33/D29 | Fermé | Encarts Agent A + Agent B |
| Tag v2.0.1 avant C2b | Fermé | Interdiction explicite L219 / ordre global |

### P1 — restants (non bloquants gate)

- **[Brief 02 vs plan EC]** — Le plan renvoie à la dérogation fil E ; le brief 02 dit encore « après gate EC fil C ». → En **C3**, patch brief 02 ou note explicite « lire § Agent B dérogation ».
- **[Tag v2.0.1 vs Fin B]** — Gates tag listent C2b + QA2 A ; **Fin B** exige story done + CR. → Ajouter à § Hors scope : tag v2.0.1 aussi après QA2 B ≥ 95 % et CR APPROVE.

### Info

- Tolérance legacy 0,05 € vs D33 ±2 € : documentée ; à recoller en AC story B.
- `sprint-status.yaml` : préférer chemin complet `_bmad-output/implementation-artifacts/` dans prompts agents.

---

## Revue adversarial — findings actionnables (≥10)

*Ton cynique ; la plupart ont été mitigés en it. 1–2 — conservés pour traçabilité.*

| # | [LOC] | Sévérité initiale | Finding | Mitigation (plan) |
|---|-------|-------------------|---------|-------------------|
| 1 | EC / brief 02 | P0 | Dev B sous gate EC non figée | Tableau waived/blocking + dérogation Strophe 2026-05-26 |
| 2 | Sync caisse | P0 | Pause B sans GO ni délai | C-sync L114–124 + escalade J+1 |
| 3 | D5 / D33 | P0 | Liaison Paheko sans comptage physique | MVP v1 dégradée + encart D33/D29 |
| 4 | C2 / HITL | P0 | Sync doc avant sign-off parité | C2a vs C2b, tag interdit avant C2b |
| 5 | Artefact 04 | P0 | Gate plan circulaire | C0bis = cible ; ce rapport |
| 6 | QA2 triple | P1 | Coût 3× QA2 @95 % | QA2 sur livrables seuls ; plan hors scope A/B |
| 7 | Owners | P1 | Collision protocole-modules | Owners + lecture seule A |
| 8 | 1.4.4 | P1 | Dépôt legacy non cloné | Prérequis Agent A |
| 9 | pytest 300 s | P1 | Seuil ambigu | timeout_sec ≥ 330 |
| 10 | Mermaid | P1 | Schéma incomplet | C0bis, pause B, HITL, C2a/b |
| 11 | Parallélisme | P0 | B merge avant parité | DS B conditionné |
| 12 | VS retries | P1 | Impasse après 2 échecs | Escalade Coordinateur |
| 13 | P0 double sens | P1 | P0 parité vs P0 QA2 | Rappel workflow-loop L79 |
| 14 | v2.0.1 tag | P0 | Ship module avant HITL | Interdit avant C2b + QA2 A |

---

## Axes utilisateur — couverture

| Axe | Couverture |
|-----|------------|
| Orchestration multi-agents | OK (Coordinateur routeur, A∥B) |
| Parallélisme A/B | OK (explore parallèle, DS B gated) |
| Délégation Task | OK (explore, DS, pas d’ingestion parent) |
| QA2 sur livrables | OK (03 pour A ; story pour B) |
| Owners fichiers | OK (+ brief 02 en tableau) |
| Sync fermeture caisse | OK (C-sync) |
| Gate EC Paheko | OK (dérogation documentée) |
| Hors scope | OK (9.7, 9.1, HelloAsso, D5 phase 2) |
| Adversarial ≥10 | OK (tableau ci-dessus) |

---

## Lots correctifs appliqués (plan seul)

**Itération 1** : C-sync, parallélisme DS B, C2a/C2b/C3, EC, MVP D5, C0bis, QA2 scope A, pytest, owners, mermaid, chemins qa2.  
**Itération 2** : C0bis formulation, D33/D29, tag v2.0.1, C3↔C2b, escalade C-sync, QA2 B scope_paths, note brief 02.

**Fichiers non modifiés** (volontairement) : `references/ou-on-en-est.md`, `sprint-status.yaml`, `epics.md`, `2026-05-26_02_brief-bmad-remise-a-flot-modules-9-6.md`.

---

## Recommandations pour Strophe

1. **Lancer C0bis** : lire ce rapport → valider GO plan → puis **C0** (commit 9.6 si souhaité) → **C1** (chats A + B).
2. **Avant C1** : noter la dérogation EC dans le brief 02 ou s’en tenir au § Agent B du plan.
3. **Surveiller** : premier écart fermeture caisse → déclencher C-sync (pas de DS B sans GO).
4. **P1 optionnel** : une ligne sur tag v2.0.1 + Fin B dans le plan (correctif mineur ultérieur).

---

*Rapport généré par fusion parent QA2 — détail des passes workers disponible sur demande. Ne pas dupliquer cette grille dans le fichier `.plan.md`.*
