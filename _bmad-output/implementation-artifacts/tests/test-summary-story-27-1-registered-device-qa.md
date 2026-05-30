# Synthèse QA automatisée — Story 27.1 (`RegisteredDevice`)

**story_key :** `27-1-registered-device`  
**Date (run QA) :** 2026-05-30  
**Verdict :** **PASS**  
**Skill :** `bmad-qa-generate-e2e-tests` — périmètre **backend-only** ; pas de front Peintre ni panel SuperAdmin (story 27.3).

---

## Gates

| Gate | Commande | Résultat |
|------|----------|----------|
| Tests ciblés story | `cd recyclique/api && python -m pytest tests/ -k "registered_device" -q` | **12 passed**, exit 0 (~199 s) |
| E2E Playwright | N/A | **Hors scope** — aucune UI livrée dans 27.1 |

---

## Tests automatisés (skill workflow)

### Tests API générés / complétés par QA

| Type | Statut | Motif |
|------|--------|--------|
| API pytest | **Couverture suffisante (DS)** | La suite `test_registered_device_epic27.py` couvre l’intégralité des gates story (modèle, CRUD, authz, allowlist, type MVP, non-confusion ids, révocation). Aucun complément QA requis. |
| E2E UI | **N/A** | Story explicitement backend-only ; panel « Gestion des postes » reporté en 27.3. |

### Fichier de tests existant (DS)

| Fichier | Classes / cas |
|---------|----------------|
| `recyclique/api/tests/test_registered_device_epic27.py` | `TestRegisteredDeviceModel` (2), `TestRegisteredDeviceCrudSuperAdmin` (4), `TestRegisteredDeviceValidation` (4), `TestRegisteredDeviceIdentifierSeparation` (2) — **12 tests** |

---

## Grille critères d’acceptation ↔ preuves

Référence : `_bmad-output/implementation-artifacts/27-1-registered-device.md` (§ Acceptance criteria, § Interprétation exécutable).

| AC / gate story | Preuve (test ou livrable) |
|-----------------|---------------------------|
| Modèle MVP `shared_workstation` + champs contractuels | `TestRegisteredDeviceModel` ; assertions create dans `test_crud_lifecycle_super_admin` (`device_type`, `status`, `allowed_module_keys`, `inactivity_timeout_seconds`, `device_id`) |
| Table dédiée `registered_devices`, FK `site_id` | `test_registered_device_table_in_metadata`, `test_registered_device_fk_site_id` |
| CRUD SuperAdmin : create → get → list → patch → revoke | `test_crud_lifecycle_super_admin`, `test_list_excludes_revoked_by_default` |
| 403 rôles non SuperAdmin | `test_non_super_admin_forbidden` |
| Site inconnu → 404 | `test_create_unknown_site_404` |
| Allowlist : rejet clé inconnue / doublons → 422 | `test_allowlist_unknown_module_key_422`, `test_allowlist_duplicate_module_key_422` |
| Type ≠ `shared_workstation` → 422 | `test_device_type_not_shared_workstation_422` |
| `device_id` ≠ `cash_registers.id` | `test_device_id_not_accepted_as_cash_register_id` (404 route caisse + absence ligne table) |
| `device_id` ≠ `poste_reception.id` | `test_device_id_distinct_from_poste_reception_id` |
| Révocation : `status=revoked`, `revoked_at` non null, idempotent | `test_crud_lifecycle_super_admin`, `test_revoke_idempotent` |
| `Cache-Control: no-store` | Assertion headers dans `test_crud_lifecycle_super_admin` |
| Contrat OpenAPI aligné | `contracts/openapi/recyclique-api.yaml` — schémas `RegisteredDeviceV1*` + 5 paths `/v1/registered-devices/` |
| Hors scope : pas de front, PIN, enrôlement, SW offline | Revue périmètre story / grep — aucun fichier `peintre-nano/` ajouté |

---

## Endpoints couverts (API)

| Opération | Couvert par |
|-----------|-------------|
| `GET /v1/registered-devices/` | list lifecycle + filtres `site_id`, `include_revoked` |
| `POST /v1/registered-devices/` | create lifecycle + validations 422/404 |
| `GET /v1/registered-devices/{device_id}` | get lifecycle + post-revoke |
| `PATCH /v1/registered-devices/{device_id}` | patch lifecycle |
| `POST /v1/registered-devices/{device_id}/revoke` | revoke lifecycle + idempotence |

**Couverture endpoints story :** 5/5 (100 %).

---

## Checklist workflow (`bmad-qa-generate-e2e-tests` / `checklist.md`)

- [x] Tests API — suite DS complète, exécutée avec succès
- [x] Tests E2E UI — N/A (pas d’UI dans le périmètre)
- [x] Framework standard (pytest + FastAPI TestClient)
- [x] Happy path + erreurs critiques (403, 404, 422, révocation)
- [x] Tests indépendants, pas de sleep arbitraire
- [x] Résumé créé (ce fichier)
- [x] Métriques de couverture documentées

---

## Test Automation Summary (Step 5)

```markdown
# Test Automation Summary

## Generated Tests

### API Tests
- [x] recyclique/api/tests/test_registered_device_epic27.py — 12 cas (DS, validés QA)

### E2E Tests
- [ ] N/A — backend-only ; UI SuperAdmin en story 27.3

## Coverage
- API endpoints story 27.1 : 5/5
- Gates story (modèle, CRUD, allowlist, type, non-confusion, révocation) : 6/6

## Next Steps
- Story 27.2 : ContextEnvelope + audit
- Story 27.3 : panel SuperAdmin UI → E2E Playwright à planifier alors
```

---

## Prochaines étapes (pipeline Story Runner)

- Enchaînement parent : **CR** (code review).
