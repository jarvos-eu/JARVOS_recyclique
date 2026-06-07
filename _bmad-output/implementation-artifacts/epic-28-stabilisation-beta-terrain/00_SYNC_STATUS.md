| Vague | Statut | Fin | Note |
|-------|--------|-----|------|
| A_PREP | done | 2026-06-07 | Epic 28 branché ; story `28-1` prête (`ready-for-dev`) ; stories `28-2` à `28-5` jalonnées ; brief Epic Runner ajouté |
| B_28_1 | done | 2026-06-07 | Story 28.1 — caisse P0 — Story Runner PASS ; QA2 95/100 (3 it.) ; 6 REV-CAISSE Investigé/Corrigé ; HITL terrain restant |
| B_28_2 | done | 2026-06-07 | Story 28.2 — profil/PIN/PWA — Story Runner PASS ; QA2 96/100 (2 it.) ; REV-TRANSVERSE-01, ADMIN-01, RECEPTION-02 Investigé/Corrigé |
| B_28_3 | done | 2026-06-07 | Story 28.3 — réception hub/poste — Story Runner PASS ; QA2 95/100 (3 it.) ; REV-RECEPTION-01/03/05/06 Investigé/Corrigé |
| B_28_4 | done | 2026-06-07 | Story 28.4 — admin pilotes — Story Runner PASS ; QA2 95/100 (2 it.) ; REV-ADMIN-02/03/05 + TRANSVERSE-04/05 Investigé/Corrigé |
| B_28_5 | done | 2026-06-07 | Story 28.5 — sites/postes — Story Runner PASS ; QA2 95/100 (2 it.) ; REV-ADMIN-06/07/08 Investigé/Corrigé |
| B_EPIC28 | done | 2026-06-07 | Stories 28.1–28.5 done + QA2/CR passés ; **0 P0 ouvert** dans revision/index ; retests HITL listés ci-dessous — `epic-28` reste `in-progress` jusqu'à rétro/HITL |
| C_GATES_READY | pending | | Gate Epic 10.7/10.8 — prérequis : retests HITL prioritaires Strophe + `B_EPIC28 = done` |

---

## Retests HITL prioritaires (Strophe — avant Validé HITL / Epic 10.7)

| Priorité | Parcours | REV concernés |
|----------|----------|---------------|
| P0 | `/caisse` → reprise → vente → finalisation → clôture (+ virtuel) | REV-CAISSE-02, 05, 06, 10, 12 |
| P0 | Menu → Mon profil → PIN self-service ; reset admin → nouveau PIN | REV-TRANSVERSE-01, ADMIN-01 |
| P0 | Réception hub inactif → Retour menu (PWA installée si possible) | REV-RECEPTION-02 |
| P1 | Réception hub historique, resize cockpit, clôture ticket, hint sortie stock | REV-RECEPTION-01, 03, 05, 06 |
| P1 | Admin modules (F5), santé signaux, noms sites vs UUID | REV-ADMIN-02, 03, 05 ; TRANSVERSE-04, 05 |
| P1 | Admin sites/postes : hub → édition site → retour → édition poste | REV-ADMIN-06, 07, 08 |
| P1 | Session orpheline : contexte reprise (date ; caissier/fond si visible) | REV-CAISSE-01 |

**Différés hors Epic 28** : REV-TRANSVERSE-02/03 (barre PWA), REV-ADMIN-04 (dashboard polish), REV-ADMIN-09/10 (archiver/zones), REV-CAISSE-14…23 (parité audit).
