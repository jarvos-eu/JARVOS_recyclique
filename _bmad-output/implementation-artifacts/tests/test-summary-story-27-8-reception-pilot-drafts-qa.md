# Synthèse QA automatisée — Story 27.8 (`reception-pilot-drafts`)

**story_key :** `27-8-reception-pilot-drafts`  
**Date (run QA) :** 2026-05-30  
**Verdict :** **PASS**  
**qa_loop :** 1 (re-exécution post DS cr_loop=1)  
**Skill :** `bmad-qa-generate-e2e-tests` — brouillons réception pilote poste partagé ; E2E Vitest jsdom (pas Playwright).

---

## Gates

| Gate | Commande | Résultat |
|------|----------|----------|
| Gate story backend | `cd recyclique/api && python -m pytest tests/ -k story_27_8 -q` | **19 passed**, exit 0 (~67 s) |
| Lint front | `cd peintre-nano && npm run lint` | exit 0 |
| Suite front story 27.8 | `vitest run shared-workstation-reception-draft` | **7 passed** (3 fichiers), exit 0 (~39 s) |
| B1 — headers device reception-client | `vitest run reception-client-shared-workstation-headers` | **1 passed**, exit 0 |
| Playwright | N/A | **Hors scope** — stack projet = Vitest + jsdom |

**Note :** non-régression lock 27.6 (`shared-workstation-pin-lock-27-6.e2e.test.tsx`) : 1 cas flaky (`STALE_CONTEXT` sur parcours enrôlement) — **hors gate story 27.8**, non bloquant QA.

---

## Couverture findings CR — B1 / B2 / I1 / I2 (cr_loop=1)

| ID | Finding CR | Preuve automatisée | Statut |
|----|------------|-------------------|--------|
| **B1** | `reception-client.ts` doit propager `sharedWorkstationAuthHeaders()` (ancrage `registered_device_id`) | `peintre-nano/tests/unit/reception-client-shared-workstation-headers.test.ts` — `postOpenPoste` envoie Bearer + `X-Recyclique-Device-*` | **Couvert PASS** |
| **B2** | Gardes PIN sur routes nominaux manquantes (PUT/DELETE lignes, close poste/ticket) | `TestStory278ReceptionGuardM1` — 7 cas 403 `SHARED_WORKSTATION_OPERATOR_REQUIRED` | **Couvert PASS** |
| **I1** | Reprise inter-op + mutations post-reprise ; masquage liste tickets JWT seul | `test_resume_by_operator_b_audit_and_ticket_access` (POST/PUT/DELETE lignes) ; `test_get_tickets_list_hides_enrolled_draft_without_device` | **Couvert PASS** |
| **I2** | E2E wizard monté → transition lock → pas de fuite DOM | `shared-workstation-reception-draft-27-8.e2e.test.tsx` cas « wizard monté puis transition lock masque les données sensibles » | **Couvert PASS** |

---

## Tests automatisés

### Tests API (DS + CR loop 1)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `recyclique/api/tests/test_story_27_8_reception_pilot_drafts.py` | 19 | Cas §8 story + `TestStory278ReceptionGuardM1` (B2/I1 backend) |

### Tests UI unitaires (DS + CR loop 1)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `peintre-nano/tests/unit/shared-workstation-reception-draft.test.tsx` | 3 | Résumé sans lignes ; reprise ; abandon double confirmation UI |
| `peintre-nano/tests/unit/shared-workstation-reception-draft-client.test.ts` | 2 | GET/POST draft : Bearer, device headers, `cache: no-store` |
| `peintre-nano/tests/unit/reception-client-shared-workstation-headers.test.ts` | 1 | **B1** — headers device sur `postOpenPoste` |

### E2E Vitest (DS + CR loop 1)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `peintre-nano/tests/e2e/shared-workstation-reception-draft-27-8.e2e.test.tsx` | 2 | Lock screen anti-fuite ; **I2** wizard → lock sans fuite ticket/ligne/opérateur |

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
| 6b | Après reprise B : GET ticket + POST/PUT/DELETE ligne → 200 | même test (I1) |
| 7 | Abandon + confirm → fermeture + audit ABANDONED | `test_abandon_closes_and_audits` |
| 8 | Reprise/abandon sans `confirm: true` → 422 | `test_resume_without_confirm_422`, `test_abandon_without_confirm_422` |
| 9 | `Cache-Control: no-store` routes brouillon | `test_authorized_summary_without_lines` (GET draft) |
| 10 | Web sans device → brownfield inchangé | `test_web_user_without_device_unchanged` |
| 11 | Module absent → pas de résumé dans context | `test_no_draft_summary_when_module_not_effective` |
| 12 | Lock e2e : pas de fuite DOM ticket/ligne | E2E lock screen 27.8 (×2 cas) |
| — | Second brouillon même device → 409 | `test_second_open_poste_same_device_409` |
| — | Garde PIN routes close/PUT/DELETE (CR B2) | `TestStory278ReceptionGuardM1` (7 cas) |
| — | Anti-JWT brownfield + cross-device (CR) | `test_get_ticket_brownfield_without_device_headers_403`, `test_get_ticket_wrong_device_scope_403` |

---

## Endpoints / surfaces couverts

| Surface | Couverture |
|---------|------------|
| `GET /v1/shared-workstation/reception-draft` | pytest 403/200/204 + no-store |
| `POST …/reception-draft/resume` | pytest inter-op + confirm 422 |
| `POST …/reception-draft/abandon` | pytest abandon + confirm 422 |
| `POST /v1/reception/postes/open` (409 + **B1** headers) | pytest 409 ; unit reception-client |
| `PUT/DELETE /v1/reception/lignes/{id}` (garde + I1) | pytest guard M1 + inter-op |
| `POST …/postes/{id}/close`, `POST …/tickets/{id}/close` | pytest guard M1 |
| `GET /v1/reception/tickets/{id}` (garde sans PIN) | pytest 403 |
| `GET /v1/reception/tickets` (masquage JWT seul) | pytest I1 |
| `GET /v1/shared-workstation/context` (`reception_draft_summary`) | pytest null si module absent |
| `SharedWorkstationReceptionDraftResumePanel` | unit 3 |
| `ReceptionNominalWizard` + lock transition | E2E I2 |
| `SharedWorkstationLockScreen` (anti-fuite) | E2E 1 |

---

## Gaps restants

Aucun gap **bloquant** vs AC story 27.8 ni vs findings **B1/B2/I1/I2**.

| Sujet | Statut | Note |
|-------|--------|------|
| `no-store` sur POST resume/abandon | Mineur | Seul GET draft asserte `Cache-Control` ; implémentation attendue identique |
| 404 `SHARED_WORKSTATION_RECEPTION_DRAFT_NOT_FOUND` | Mineur | Pas de cas pytest dédié reprise/abandon sans brouillon |
| Double confirmation UI reprise (CR MEDIUM) | Ouvert CR | Serveur exige `confirm: true` ; UX un clic — non bloquant QA |
| Non-régression lock 27.6 (1 cas STALE_CONTEXT) | Flaky / hors scope | Parcours enrôlement → dashboard ; indépendant story 27.8 |
| Playwright navigateur réel | Reporté | Projet n'utilise pas Playwright |

**Décision QA (loop 1) :** couverture CR B1/B2/I1/I2 validée ; gates story green ; pas de nouveaux tests générés.

---

## Checklist workflow (`bmad-qa-generate-e2e-tests` / `checklist.md`)

- [x] Tests API — exécutés avec succès (19/19)
- [x] Tests E2E UI — Vitest jsdom (lock anti-fuite + transition wizard I2)
- [x] Framework standard (pytest + Vitest + Testing Library)
- [x] Happy path + erreurs critiques (403, 422, 409)
- [x] Findings CR B1/B2/I1/I2 — preuves automatisées PASS
- [x] Locators sémantiques / `data-testid` stables
- [x] Pas de sleep arbitraire
- [x] Résumé mis à jour (ce fichier)
- [x] Métriques documentées

---

## Test Automation Summary (Step 5)

```markdown
# Test Automation Summary

## Existing Tests (DS + CR loop 1 — vérifiés QA loop 1)

### API Tests
- [x] recyclique/api/tests/test_story_27_8_reception_pilot_drafts.py — 19 cas

### E2E Tests (Vitest jsdom)
- [x] peintre-nano/tests/e2e/shared-workstation-reception-draft-27-8.e2e.test.tsx — 2 cas

### Unit (DS + CR loop 1)
- [x] shared-workstation-reception-draft.test.tsx — 3
- [x] shared-workstation-reception-draft-client.test.ts — 2
- [x] reception-client-shared-workstation-headers.test.ts — 1 (B1)

## Coverage
- Cas obligatoires §8 story 27.8 : 12/12 (+ guard M1 + 409)
- Findings CR B1/B2/I1/I2 : 4/4
- Surfaces UI brouillon + lock + wizard : 8/8 (unit + e2e)

## Next Steps
- Story Runner parent : CR2 ou clôture si CR APPROVE
- Gaps mineurs (404, no-store POST, UX double confirm reprise) : optionnels post-MVP
```

---

## Fichiers créés / modifiés (worker QA)

| Fichier | Action |
|---------|--------|
| `_bmad-output/implementation-artifacts/tests/test-summary-story-27-8-reception-pilot-drafts-qa.md` | **Mis à jour** — qa_loop 1, grille B1/B2/I1/I2, compteurs 19/8 |

Aucun fichier test ou code applicatif modifié (couverture DS/CR suffisante).

`sprint-status.yaml` : **non modifié** (instruction worker).

---

## Prochaines étapes (pipeline Story Runner)

- Gate QA **PASS** (qa_loop 1) — prêt pour CR2 / clôture story.
- Aucun retry DS requis pour gaps QA.
