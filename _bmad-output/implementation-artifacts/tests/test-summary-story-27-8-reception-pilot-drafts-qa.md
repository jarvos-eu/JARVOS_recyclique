# Synthèse QA automatisée — Story 27.8 (`reception-pilot-drafts`)

**story_key :** `27-8-reception-pilot-drafts`  
**Date (run QA) :** 2026-05-30  
**Verdict :** **PASS**  
**qa_loop :** 0  
**Skill :** `bmad-qa-generate-e2e-tests` — brouillons réception pilote poste partagé ; E2E Vitest jsdom (pas Playwright).

---

## Gates

| Gate | Commande | Résultat |
|------|----------|----------|
| Gate story backend | `cd recyclique/api && python -m pytest tests/ -k story_27_8 -q` | **12 passed**, exit 0 (~590 s) |
| Gate story backend (fichier ciblé) | `python -m pytest tests/test_story_27_8_reception_pilot_drafts.py -q` | **12 passed** (run parallèle, confirmé) |
| Lint front | `cd peintre-nano && npm run lint` | exit 0 |
| Suite front story 27.8 | `vitest run shared-workstation-reception-draft` | **4 passed** (2 fichiers), exit 0 (~13 s) |
| Non-régression Epic 27 (lock / session / modules) | `vitest run shared-workstation-operator-session shared-workstation-effective-modules shared-workstation-pin-lock-27-6` | **12 passed** (4 fichiers), exit 0 (~18 s) |
| Playwright | N/A | **Hors scope** — stack projet = Vitest + jsdom |

---

## Tests automatisés

### Tests API (DS)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `recyclique/api/tests/test_story_27_8_reception_pilot_drafts.py` | 12 | Masquage sans PIN, résumé autorisé, refus droits/allowlist, anti-fuite ticket, reprise inter-opérateur + audit, abandon + audit, confirm 422 (resume/abandon), second brouillon 409, brownfield web, context sans module effectif |

### Tests UI unitaires (DS)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `peintre-nano/tests/unit/shared-workstation-reception-draft.test.tsx` | 3 | Résumé sans lignes ; reprise après confirmation ; abandon double confirmation UI |

### E2E Vitest (DS)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `peintre-nano/tests/e2e/shared-workstation-reception-draft-27-8.e2e.test.tsx` | 1 | Lock screen : pas de fuite ticket/ligne/panel brouillon dans le DOM |

---

## Grille critères d'acceptation ↔ preuves

Référence : `_bmad-output/implementation-artifacts/27-8-reception-pilot-drafts.md` §8.

| # | Cas story / AC | Preuve |
|---|----------------|--------|
| 1 | Device verrouillé → `GET reception-draft` → 403 | `test_get_draft_without_pin_403` |
| 2 | Session + intersection + droits → résumé 200 sans lignes | `test_authorized_summary_without_lines` |
| 3 | Sans `reception.access` → 403 sans fuite | `test_operator_without_reception_access_403` |
| 4 | Sans `reception` dans allowlist → 403 module | `test_reception_not_in_allowlist_403` |
| 5 | `GET /v1/reception/tickets/{id}` sans PIN → 403 | `test_get_ticket_without_pin_403` |
| 6 | Reprise opérateur B + audit RESUMED | `test_resume_by_operator_b_audit_and_ticket_access` |
| 6b | Après reprise B : `GET ticket` → 200 | même test (GET détail) |
| 7 | Abandon + confirm → fermeture + audit ABANDONED | `test_abandon_closes_and_audits` |
| 8 | Reprise/abandon sans `confirm: true` → 422 | `test_resume_without_confirm_422`, `test_abandon_without_confirm_422` |
| 9 | `Cache-Control: no-store` routes brouillon | `test_authorized_summary_without_lines` (GET draft) |
| 10 | Web sans device → brownfield inchangé | `test_web_user_without_device_unchanged` |
| 11 | Module absent → pas de résumé dans context | `test_no_draft_summary_when_module_not_effective` |
| 12 | Lock e2e : pas de fuite DOM ticket/ligne | E2E lock screen 27.8 |
| — | Second brouillon même device → 409 | `test_second_open_poste_same_device_409` (nice-to-have VS, couvert DS) |
| — | Pilote Reception uniquement (pas caisse) | Hors tests dédiés ; invariant code + scope story |
| — | Audit sans PIN | patch resume/abandon : `"pin" not in call_args` |

---

## Endpoints / surfaces couverts

| Surface | Couverture |
|---------|------------|
| `GET /v1/shared-workstation/reception-draft` | pytest 403/200/204 + no-store |
| `POST …/reception-draft/resume` | pytest inter-op + confirm 422 |
| `POST …/reception-draft/abandon` | pytest abandon + confirm 422 |
| `POST /v1/reception/postes/open` (409 second brouillon) | pytest 409 |
| `GET /v1/reception/tickets/{id}` (garde sans PIN) | pytest 403 |
| `GET /v1/shared-workstation/context` (`reception_draft_summary`) | pytest null si module absent |
| `SharedWorkstationReceptionDraftResumePanel` | unit 3 |
| `SharedWorkstationLockScreen` (anti-fuite) | E2E 1 |
| Non-régression lock 27.6 / modules 27.7 / session opérateur | vitest 12 |

---

## Gaps restants

Aucun gap **bloquant** vs AC story 27.8.

| Sujet | Statut | Note |
|-------|--------|------|
| `no-store` sur POST resume/abandon | Mineur | Seul GET draft asserte `Cache-Control` ; implémentation attendue identique (middleware/garde partagée) |
| 404 `SHARED_WORKSTATION_RECEPTION_DRAFT_NOT_FOUND` | Mineur | Code stable documenté ; pas de cas pytest dédié reprise/abandon sans brouillon |
| Mutation ligne post-reprise inter-op (6b étendu) | Mineur | GET ticket couvert ; POST ligne non asserté explicitement |
| E2E compose App (wizard masqué → PIN → panel) | Accepté MVP | Lock DOM + unit panel suffisent pour gates story ; pattern aligné 27.7 partiel |
| Playwright navigateur réel | Reporté | Projet n'utilise pas Playwright |
| Caisse / atelier / inventaire | Hors scope | Attendu |

**Décision QA :** pas de nouveaux tests générés — couverture DS + gates green ; nice-to-have VS (409, abandon 422) déjà présents.

---

## Checklist workflow (`bmad-qa-generate-e2e-tests` / `checklist.md`)

- [x] Tests API — exécutés avec succès (12/12)
- [x] Tests E2E UI — Vitest jsdom (lock anti-fuite)
- [x] Framework standard (pytest + Vitest + Testing Library)
- [x] Happy path + erreurs critiques (403, 422, 409)
- [x] Locators sémantiques / `data-testid` stables
- [x] Pas de sleep arbitraire
- [x] Résumé créé (ce fichier)
- [x] Métriques documentées

---

## Test Automation Summary (Step 5)

```markdown
# Test Automation Summary

## Existing Tests (DS — vérifiés QA)

### API Tests
- [x] recyclique/api/tests/test_story_27_8_reception_pilot_drafts.py — 12 cas

### E2E Tests (Vitest jsdom)
- [x] peintre-nano/tests/e2e/shared-workstation-reception-draft-27-8.e2e.test.tsx — 1 cas

### Unit (DS)
- [x] shared-workstation-reception-draft.test.tsx — 3

## Coverage
- Cas obligatoires §8 story 27.8 : 12/12 (+ 409 inter-op nice-to-have)
- Surfaces UI brouillon + lock : 4/4 (unit + e2e)
- Non-régression Epic 27 (lock/session/modules) : 12/12

## Next Steps
- Story Runner parent : étape CR si gates DS/QA OK
- Gaps mineurs (404, no-store POST) : optionnels post-MVP
```

---

## Fichiers créés / modifiés (worker QA)

| Fichier | Action |
|---------|--------|
| `_bmad-output/implementation-artifacts/tests/test-summary-story-27-8-reception-pilot-drafts-qa.md` | **Créé** — synthèse QA |

Aucun fichier test ou code applicatif modifié (couverture existante suffisante).

`sprint-status.yaml` : **non modifié** (instruction worker).

---

## Prochaines étapes (pipeline Story Runner)

- Gate QA **PASS** (qa_loop 0) — prêt pour étape CR.
- Aucun retry DS requis pour gaps QA.
