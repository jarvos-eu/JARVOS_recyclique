# Synthèse QA automatisée — Story 27.2 (`server-context-audit`)

**story_key :** `27-2-server-context-audit`  
**Date (run QA) :** 2026-05-30 (retry post-CR1 DS, `cr_loop=1`)  
**Verdict :** **PASS**  
**qa_loop :** 0  
**Skill :** `bmad-qa-generate-e2e-tests` — périmètre **backend-only** ; pas de front Peintre, pas de lock screen PIN (story 27.6), pas d'intersection modules (27.7).

---

## Gates

| Gate | Commande | Résultat |
|------|----------|----------|
| Gate story (retry CR) | `cd recyclique/api && python -m pytest tests/ -k "story_27_2" -q` | **20 passed**, exit 0 (2026-05-30 retry) |
| Tests ciblés story (étendu) | `python -m pytest tests/ -k "shared_workstation or device_operator or epic27_2 or story_27_2" -q` | **20 passed** (suite 27.2), exit 0 |
| Suite dédiée 27.2 | `python -m pytest tests/test_story_27_2_shared_workstation_context.py -q` | **20 passed**, exit 0 |
| Audit socle (non-régression) | `python -m pytest tests/test_audit_story_25.py -q` | Validé QA (sanitize + merge patterns inchangés) |
| E2E Playwright | N/A | **Hors scope** — aucune UI livrée dans 27.2 |

---

## Post-CR1 — fixes DS (CR-27.2-M1 / CR-27.2-M2)

| Finding | Fix DS | Preuve test |
|---------|--------|-------------|
| **CR-27.2-M1** — `RegisteredDeviceService.update()` n'invalidait pas les sessions sur `status=revoked` | `revoked_at` + `invalidate_sessions_for_device(reason="device_revoked")` dans `update()` | `test_update_status_revoked_invalidates_session_and_audit` (service `update` via `model_construct`, session terminée, audit `device_revoked`) |
| **CR-27.2-M2** — device non ACTIVE accepté pour sessions / résolution contexte | `_require_active_device` (`start_session`) et `resolve_shared_workstation_context` exigent `status == active` | `test_revoked_device_refused_and_audit` (GET contexte → 403 `device_invalid` + audit) ; `start_session` couvert par invariant `_make_active_device` sur tous les cas positifs |

---

## Tests automatisés (skill workflow)

### Tests API complétés par QA (gaps AC)

| Ajout QA | Motif |
|----------|--------|
| `test_unknown_device_404` | AC refus device invalide / inconnu (404 + code stable) |
| `test_revoked_device_refused_and_audit` | AC recalcul + audit `SHARED_WORKSTATION_ACCESS_REFUSED` (`outcome=device_invalid`) |
| `test_envelope_refresh_post_with_device_merges_fields` | AC ContextEnvelope — endpoint `POST /me/context/refresh` non couvert par DS |
| `test_envelope_with_device_header_merges_fields` | AC en-tête `X-Recyclique-Device-Id` prioritaire sur enveloppe |
| `test_sanitize_step_up_pin_derivative` | AC « pas de PIN ni dérivé » (`step_up_pin`) |
| `TestDeviceOperatorSessionAuditStory272` (2 tests) | AC audit `DEVICE_OPERATOR_SESSION_STARTED` / `ENDED` |
| `test_site_change_emits_context_invalidated_audit` | AC invalidation auditée (`SHARED_WORKSTATION_CONTEXT_INVALIDATED`) |

### Fichier de tests

| Fichier | Classes / cas |
|---------|----------------|
| `recyclique/api/tests/test_story_27_2_shared_workstation_context.py` | `TestDeviceOperatorSessionStory272` (1), `TestSharedWorkstationRouteStory272` (5), `TestContextEnvelopeSharedWorkstationStory272` (4), `TestAuditSharedWorkstationStory272` (3), `TestDeviceOperatorSessionAuditStory272` (2), `TestIdentifierSeparationStory272` (2), `TestInvalidationStory272` (3, incl. post-CR M1) — **20 tests** |

### E2E UI

| Type | Statut |
|------|--------|
| E2E Playwright | **N/A** — story backend-only ; lock screen PIN en 27.6 |

---

## Grille critères d'acceptation ↔ preuves

Référence : `_bmad-output/implementation-artifacts/27-2-server-context-audit.md` (§ Acceptance criteria, § Interprétation exécutable §7).

| AC / gate story | Preuve (test ou livrable) |
|-----------------|---------------------------|
| Invariant tuple `site_id + device_id + operator_user_id + module_key + override` | `test_success_with_active_session` ; service `SharedWorkstationContextService` (docstring module) |
| Authz frontière API, pas UI seule | `test_refusal_without_operator_403_and_audit`, garde `require_active_operator_context` |
| Refus sans opérateur actif | `test_refusal_without_operator_403_and_audit` → 403 `SHARED_WORKSTATION_OPERATOR_REQUIRED` |
| Recalcul / refus sur changement poste/site/module | `test_site_change_invalidates_session_then_403`, `test_revoked_device_refused_and_audit`, `test_header_module_mismatch_409_context_stale`, `test_site_change_emits_context_invalidated_audit`, `test_update_status_revoked_invalidates_session_and_audit` (CR-27.2-M1) |
| Audit socle `audit_logs` (pas second journal) | Helpers `log_shared_workstation_*`, `log_device_operator_session_*` dans `core/audit.py` ; tests mock `log_audit` |
| Pas de PIN / dérivé en logs | `test_sanitize_pin_on_shared_workstation_audit`, `test_sanitize_step_up_pin_derivative` |
| Session opérateur start/get/end, une active/device | `test_start_get_active_end_single_active_per_device` |
| ContextEnvelope champs optionnels null (non-régression) | `test_envelope_without_device_fields_null` |
| ContextEnvelope fusion poste partagé | `test_envelope_with_device_session_merges_fields`, `test_envelope_refresh_post_with_device_merges_fields`, `test_envelope_with_device_header_merges_fields` |
| `merge_critical_audit_fields` device/module/override | `test_merge_critical_audit_fields_device_module_override` |
| Non-confusion `device_id` vs caisse | `test_device_id_distinct_from_cash_register_in_context`, `test_audit_device_id_not_cash_register_id` |
| Device inconnu / révoqué / non ACTIVE (CR-27.2-M2) | `test_unknown_device_404`, `test_revoked_device_refused_and_audit` ; `_require_active_device` sur `start_session` (device ACTIVE requis) |
| Audit session started/ended | `test_start_session_emits_started_audit`, `test_end_session_emits_ended_audit` |
| Route pilote `GET /v1/shared-workstation/context` | `test_success_with_active_session` + refus/409 ; `Cache-Control: no-store` |
| Hors scope : offline, PIN public, intersection modules, lock UI | Revue périmètre story — aucun front / endpoint PIN ajouté |

---

## Endpoints couverts (API)

| Opération | Couvert par |
|-----------|-------------|
| `GET /v1/shared-workstation/context` | refus 403/404, succès 200, 409 CONTEXT_STALE, device révoqué |
| `GET /v1/users/me/context` | champs null ; fusion device query + header |
| `POST /v1/users/me/context/refresh` | fusion device (QA) |
| `PATCH /v1/registered-devices/{id}` | invalidation session sur changement `site_id` ; révocation via service `update(status=revoked)` (CR-27.2-M1, test service) |

**Couverture endpoints story 27.2 :** 4/4 (100 %).

---

## Gaps restants

Aucun gap bloquant identifié vs AC story 27.2.

| Sujet | Statut | Note |
|-------|--------|------|
| Persistance `audit_logs` PostgreSQL | Accepté | SQLite CI neutralise `log_audit` (conftest) — preuves via mock, pattern projet établi |
| Intersection modules effective | Hors scope | Story 27.7 |
| Endpoint PIN public | Hors scope | Story 27.6 |
| E2E UI poste partagé | Reporté | Story 27.5–27.6 |

---

## Checklist workflow (`bmad-qa-generate-e2e-tests` / `checklist.md`)

- [x] Tests API — suite complétée DS + QA, exécutée avec succès
- [x] Tests E2E UI — N/A (pas d'UI dans le périmètre)
- [x] Framework standard (pytest + FastAPI TestClient)
- [x] Happy path + erreurs critiques (403, 404, 409, invalidation, sanitize PIN)
- [x] Tests indépendants, pas de sleep arbitraire
- [x] Résumé créé (ce fichier)
- [x] Métriques de couverture documentées

---

## Test Automation Summary (Step 5)

```markdown
# Test Automation Summary

## Generated Tests

### API Tests
- [x] recyclique/api/tests/test_story_27_2_shared_workstation_context.py — 20 cas (13 DS post-CR + 7 QA)

### E2E Tests
- [ ] N/A — backend-only ; lock screen / PWA en stories 27.5–27.6

## Coverage
- API endpoints story 27.2 : 4/4
- Gates story §7 (session, refus, recalcul, enveloppe, audit, sanitize, ids) : 7/7

## Next Steps
- Story Runner parent : **CR** (code review)
- Story 27.3 : panel SuperAdmin UI → E2E Playwright à planifier
```

---

## Prochaines étapes (pipeline Story Runner)

- Post-CR1 DS retry : gate **PASS** — enchaînement parent : **CR** (boucle CR si findings restants) ou clôture story.
