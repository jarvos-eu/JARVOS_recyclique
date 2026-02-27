# Story 7-2: Interface ou API d'administration du mapping

**Epic:** Epic 7 — Correspondance et mapping RecyClique ↔ Paheko  
**Story key:** 7-2-interface-ou-api-d-administration-du-mapping  
**Prérequis:** Story 7-1 (modèle et API CRUD mapping) livrée. HITL-7.1, 7.2, 7.3 franchis.

**Status:** done

---

## User story

En tant qu'admin ou responsable compta,  
je veux consulter et modifier le mapping entre RecyClique et Paheko via une interface ou une API RecyClique,  
afin de configurer à l'avance tout ce qui est nécessaire pour la sync caisse (moyens de paiement, catégories, sites/emplacements).

---

## Contexte

- **7-1 (done)** : modèle BDD et API CRUD du mapping (entités/tables de correspondance RecyClique → Paheko).
- **7-2** : ajoute l'**API d'administration** du mapping (v1 : API seule ; UI possible en story ultérieure).

**FR couvert :** FR13b.  
**Références :** `_bmad-output/planning-artifacts/epics.md` (Epic 7, Story 7.2), `references/migration-paeco/audits/matrice-correspondance-caisse-poids.md`, artefact 09 (périmètre API v1).

---

## Critères d'acceptation

**Étant donné** le modèle de mapping et l'API CRUD livrés en Story 7-1  
**Quand** j'accède à l'écran ou à l'API d'administration du mapping  
**Alors** je peux :
- lister les correspondances (RecyClique → Paheko) par type (moyens de paiement, catégories, sites/emplacements selon périmètre figé en 7.1) ;
- consulter le détail d'une entrée de mapping ;
- créer, modifier et supprimer (ou désactiver) des entrées de mapping dans les limites du modèle 7.1.

**Et** :
- les modifications sensibles sont tracées dans `audit_events` (création, modification, suppression d'entrées de mapping) ;
- l'accès est restreint aux rôles autorisés (admin / responsable compta, RBAC) ;
- le périmètre v1 est fixé ci-dessous (API seule par défaut).

---
## Décision de périmètre v1 (par défaut pour le dev)

**Livrable 7-2 en v1 : API seule (Option A).**

- La Story 7-1 fournit déjà le **modèle BDD et l'API CRUD** du mapping. La Story 7-2 ajoute une **API d'administration** dédiée : endpoints sous un préfixe type `/v1/admin/mapping/...` (ou aligné avec `api/routers/admin/`), **réutilisant** le modèle et les services 7-1 (pas de duplication de logique).
- Consommable par un client (Postman, script, ou future UI). Une **interface UI** (Option B ou C) pourra faire l'objet d'une story ultérieure ou d'une v2.

---

## Périmètre technique (détail)

- **Option A — API seule (v1 par défaut) :** Endpoints dédiés (ex. `GET/POST/PATCH/DELETE /v1/admin/mapping/...`) qui s'appuient sur le modèle et les services CRUD de la Story 7-1. Consommables par un client (Postman, script, ou future UI).
- **Option B — UI seule :** Écran(s) RecyClique (Mantine) qui appellent l'API CRUD du mapping (Story 7-1) — hors scope v1 de cette story.
- **Option C — Les deux :** API d'admin + écran(s) admin — prévu pour une story ultérieure ou v2.

**Livrable minimal 7-2 :** Option A (API d'administration du mapping). Réutilisation stricte du modèle et des services 7-1 ; pas de duplication.

---
## Implémentation (notes dev)

- **Emplacement :** Routes sous `api/routers/admin/` (ou module dédié `mapping` monté sous `/v1/admin/mapping/...`), aligné avec `architecture.md` (routers par domaine, `/api/*` ou `/v1/*`).
- **Réutilisation :** S'appuyer sur les modèles, schémas et services créés en 7-1 ; les endpoints admin exposent une API dédiée (liste par type, détail, CRUD) avec contrôle d'accès.
- **Sécurité :** Restriction aux rôles admin / responsable compta (RBAC existant).
- **Audit :** Enregistrer dans `audit_events` chaque création, modification et suppression d'entrée de mapping (resource_type / resource_id cohérents).
- **Tests :** Couvrir les nouveaux endpoints par des tests API (pytest, structure type `tests/routers/` ou `tests/api/`).

---

## Livrable implémenté (v1)

- **Routes :** Préfixe `/v1/admin/mapping` ; pour chaque sous-ressource (`payment_methods`, `categories`, `locations`) : `GET` (liste), `GET /{id}` (détail), `POST` (création), `PATCH /{id}` (modification), `DELETE /{id}` (suppression). Router monté dans `api/routers/v1/admin/` sous le préfixe `/mapping`.
- **RBAC :** `require_permissions("admin", "compta.responsable")` sur tous les endpoints (admin et responsable compta).
- **Audit :** Un enregistrement dans `audit_events` à chaque création, modification et suppression ; appel au service d'audit (ex. `write_audit_event`) après chaque opération ; actions `mapping.payment_method.created|updated|deleted`, `mapping.category.*`, `mapping.location.*` ; `resource_type` et `resource_id` cohérents.
- **Réutilisation 7-1 :** Modèles et schémas 7-1 inchangés ; logique CRUD dans `api/services/mapping_service` (create/update/delete) ; les routes admin appellent ce service puis enregistrent l'audit. Aucune duplication de logique CRUD par rapport à 7-1.
- **Tests :** `api/tests/routers/test_admin_mapping_payment_methods.py`, `test_admin_mapping_categories.py`, `test_admin_mapping_locations.py` (15 tests).

**Couverture AC :** liste par type (GET), détail (GET /{id}), créer/modifier/supprimer (POST, PATCH, DELETE), traçabilité audit sur chaque modification sensible, accès restreint RBAC (admin, compta.responsable), périmètre v1 API seule.

---

### Senior Developer Review

**bmad-qa (2026-02-27)** : Revue adversarial effectuée. Routes /v1/admin/mapping (GET list, GET /{id}, POST, PATCH /{id}, DELETE /{id}) pour payment_methods, categories, locations — conformes. RBAC `require_permissions("admin", "compta.responsable")` sur tous les endpoints. Audit `write_audit_event` à chaque create/update/delete avec actions et resource_type/resource_id cohérents. Réutilisation modèles/schémas/services 7-1. Tests test_admin_mapping_*.py (16 tests). **Résultat : approved.**

---

## Références

- Architecture / checklist : `_bmad-output/planning-artifacts/architecture.md`, `references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md`
- Traçabilité écrans/API : `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md`
- Matrice correspondance : `references/migration-paeco/audits/matrice-correspondance-caisse-poids.md`
