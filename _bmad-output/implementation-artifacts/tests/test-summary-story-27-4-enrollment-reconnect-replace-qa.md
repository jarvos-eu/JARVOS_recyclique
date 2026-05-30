# Synthèse QA automatisée — Story 27.4 (`enrollment-reconnect-replace`)

**story_key :** `27-4-enrollment-reconnect-replace`  
**Date (run QA) :** 2026-05-30  
**Verdict :** **PASS** (post-CR1, retry QA)  
**qa_loop :** 0 (retry post-CR1)  
**Skill :** `bmad-qa-generate-e2e-tests` — périmètre backend enrollment/credential + Peintre (IndexedDB, widget terrain, panel admin) ; E2E Vitest jsdom (pas Playwright).

---

## Gates

| Gate | Commande | Résultat |
|------|----------|----------|
| Gate story backend | `cd recyclique/api && python -m pytest tests/ -k "story_27_4 or enrollment or device_credential" -q` | **8 passed**, exit 0 |
| Non-régression Epic 27 | `pytest tests/test_story_27_2_shared_workstation_context.py tests/test_story_27_3_superadmin_device_management.py tests/test_registered_device_epic27.py -q` | **37 passed**, exit 0 |
| Tests UI ciblés §13 | `vitest run tests/unit/device-identity-store.test.ts tests/unit/shared-workstation-enrollment-widget.test.tsx tests/unit/admin-registered-devices-enrollment.test.tsx` | **9 passed**, exit 0 |
| E2E Story 27.4 | `vitest run tests/e2e/shared-workstation-enrollment-27-4.e2e.test.tsx` | **8 passed**, exit 0 |
| Contrat CREOS enrôlement | `vitest run tests/contract/page-transverse-shared-workstation-enroll-27-4.test.ts` | **3 passed**, exit 0 |
| LiveAuthShell whitelist enroll | `vitest run tests/unit/live-auth-shell-11-2.test.tsx -t "27.4"` | **2 passed**, exit 0 |
| Playwright | N/A | **Hors scope** — stack projet = Vitest + jsdom |

---

## Correctifs CR1 — couverture QA

| Correctif CR1 | Preuve automatisée |
|---------------|-------------------|
| `replace_definitively` Option A (credential actif + code replace auto API) | `test_replace_definitively_poste_reste_utilisable` (pytest) |
| Modal admin code replace après resolve | Unit `replace_definitively affiche le code` + E2E `panel replace_definitively ouvre modal` |
| P2 bannière hint `hadPriorDeviceEnrollment` | `device-identity-store.test.ts` + unit widget hint + e2e `identité perdue réelle` |
| P2 catch `saveDeviceIdentity` | Unit widget `échec saveDeviceIdentity` |

---

## Tests automatisés (skill workflow)

### Tests API (DS + CR1)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `recyclique/api/tests/test_story_27_4_enrollment_reconnect_replace.py` | 8 | Enrôlement nominal, reconnect, replace/conflit, **replace_definitively Option A**, codes invalides, audit sanitize, device_id ≠ caisse |

### Tests UI unitaires (DS + compléments QA post-CR1)

| Fichier | Cas | Rôle |
|---------|-----|------|
| `peintre-nano/tests/unit/device-identity-store.test.ts` | 1 | save/load/clear ; `hadPriorDeviceEnrollment` hint ; **pas** `localStorage` |
| `peintre-nano/tests/unit/shared-workstation-enrollment-widget.test.tsx` | 4 | Happy path, code expiré, **bannière hint**, **catch IndexedDB** |
| `peintre-nano/tests/unit/admin-registered-devices-enrollment.test.tsx` | 4 | Code enrôlement, reconnect, resolve refuse, **replace_definitively + modal code** |
| `peintre-nano/tests/unit/live-auth-shell-11-2.test.tsx` | 2 | Route `/shared-workstation/enroll` publique sans JWT (DS) |

### Tests contrat CREOS (DS)

| Fichier | Rôle |
|---------|------|
| `peintre-nano/tests/contract/page-transverse-shared-workstation-enroll-27-4.test.ts` | Manifeste `shared-workstation-enroll`, widget enregistré, hors nav transverse |

### E2E Vitest — complément QA

| Fichier | Cas | Motif |
|---------|-----|-------|
| `peintre-nano/tests/e2e/shared-workstation-enrollment-27-4.e2e.test.tsx` | 8 | Compose RuntimeDemoApp : route publique, bannière identité perdue (hint), parcours nominal + erreur expiré, panel admin codes/reconnect/replace/conflit, **replace_definitively modal**, identité existante sans bannière |

---

## Grille critères d'acceptation ↔ preuves

Référence : `_bmad-output/implementation-artifacts/27-4-enrollment-reconnect-replace.md` §13.

| AC / gate | Preuve |
|-----------|--------|
| Enrôlement nominal (code → active + credential hashé) | `test_initial_enrollment_active_credential_hashed` |
| Identité perdue / reconnexion | `test_mark_identity_lost_then_reconnect` + bannière UI unit/e2e + `hadPriorDeviceEnrollment` |
| Remplacement + ancien secret refusé | `test_replace_old_secret_refused_and_conflict` |
| Conflit SuperAdmin (refuse, replace_definitively, create_distinct) | `test_resolve_conflict_actions` + `test_replace_definitively_poste_reste_utilisable` + modal admin unit/e2e |
| Codes expiré / consommé / invalide | `test_invalid_expired_consumed_codes` + widget/e2e erreur 410 |
| Garde credential `device-status` | Tests reconnect/replace (403 ancien secret) + replace_definitively poste utilisable |
| Audit sans secret en clair | `test_audit_never_contains_secret` |
| Non-régression 27.1–27.3 | 37 passed non-régression |
| IndexedDB, pas localStorage | `device-identity-store.test.ts` |
| Widget terrain code → save identity | Unit + e2e nominal ; catch IndexedDB unit |
| Panel admin codes / reconnect / conflit / replace_definitively | Unit 4 cas + e2e 8 cas |
| Route publique `/shared-workstation/enroll` | LiveAuthShell + e2e URL profonde |
| Manifeste CREOS hors nav | Contract test |
| Hors scope : QR, PIN, PWA, offline | Revue périmètre story |

---

## Endpoints / surfaces couverts

| Surface | Couverture |
|---------|------------|
| API enrollment-codes / enroll/complete / mark-identity-lost / resolve-conflict / device-status | 8/8 scénarios story (incl. replace_definitively Option A) |
| Client terrain `completeSharedWorkstationEnrollment` | Unit + e2e |
| Client admin enrollment + resolve-conflict (code auto replace) | 4/4 actions testées |
| Route `/shared-workstation/enroll` | E2E compose + LiveAuthShell |
| Route `/admin/registered-devices` extensions | E2E + unit |
| IndexedDB device identity + hint | Unit + e2e |

---

## Gaps restants

Aucun gap bloquant vs AC story 27.4 post-CR1.

| Sujet | Statut | Note |
|-------|--------|------|
| `create_distinct` UI (saisie nom + clic) | Accepté | Backend `test_resolve_conflict_actions` ; pattern identique refuse/replace |
| Playwright navigateur réel | Reporté | Projet n'utilise pas Playwright pour Peintre |
| Rate-limit endpoint semi-public | Accepté | Non testé e2e ; middleware documenté story |
| WebCrypto non exportable | Hors scope MVP | Tranchage Dev Notes |

---

## Checklist workflow (`bmad-qa-generate-e2e-tests` / `checklist.md`)

- [x] Tests API — exécutés avec succès (8/8 post-CR1)
- [x] Tests E2E UI — Vitest jsdom (enroll route, panel admin, replace_definitively modal)
- [x] Framework standard (pytest + Vitest + Testing Library)
- [x] Happy path + erreurs critiques (expiré, 403 credential, conflit, IndexedDB save fail)
- [x] Locators sémantiques / `data-testid` stables
- [x] Pas de sleep arbitraire (redirect post-succès = setTimeout produit, non asserté)
- [x] Résumé créé (ce fichier)
- [x] Métriques documentées

---

## Test Automation Summary (Step 5)

```markdown
# Test Automation Summary

## Generated Tests (post-CR1 retry)

### API Tests
- [x] recyclique/api/tests/test_story_27_4_enrollment_reconnect_replace.py — 8 cas (DS + CR1)

### E2E Tests (Vitest jsdom)
- [x] peintre-nano/tests/e2e/shared-workstation-enrollment-27-4.e2e.test.tsx — 8 cas (QA, +1 replace_definitively)

### Unit / contract
- [x] device-identity-store.test.ts — 1 (hint hadPrior)
- [x] shared-workstation-enrollment-widget.test.tsx — 4 (+2 CR1)
- [x] admin-registered-devices-enrollment.test.tsx — 4 (+1 replace_definitively)
- [x] live-auth-shell-11-2.test.tsx — 2 (DS, route 27.4)
- [x] page-transverse-shared-workstation-enroll-27-4.test.ts — 3 (DS)

## Coverage
- API scénarios §13 story 27.4 : 9/9 (incl. replace_definitively Option A)
- Surfaces UI enrollment + panel admin : 10/10
- Route publique + manifeste CREOS : 3/3

## Next Steps
- Story Runner parent : **CR** clôturé ou re-CR si nouveau delta
- Story 27.5 : PWA installable — nouveaux tests dédiés
```

---

## Fichiers créés / modifiés (worker QA retry post-CR1)

| Fichier | Action |
|---------|--------|
| `peintre-nano/tests/unit/admin-registered-devices-enrollment.test.tsx` | **Modifié** — cas replace_definitively + modal code |
| `peintre-nano/tests/unit/shared-workstation-enrollment-widget.test.tsx` | **Modifié** — bannière hint + catch saveDeviceIdentity |
| `peintre-nano/tests/e2e/shared-workstation-enrollment-27-4.e2e.test.tsx` | **Modifié** — e2e replace_definitively modal |
| `_bmad-output/implementation-artifacts/tests/test-summary-story-27-4-enrollment-reconnect-replace-qa.md` | **Mis à jour** — ce résumé |

`sprint-status.yaml` : **non modifié** (instruction worker).

---

## Prochaines étapes (pipeline Story Runner)

- Gate QA **PASS** post-CR1 — enchaînement parent : clôture story 27.4 ou CR final si requis.
