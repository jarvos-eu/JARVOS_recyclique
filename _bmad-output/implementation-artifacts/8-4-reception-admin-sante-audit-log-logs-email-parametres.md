# Story 8.4 — Réception admin, santé, audit log, logs email, paramètres

- **Epic:** epic-8 (Administration, compta v1 et vie associative)
- **Story_key:** 8-4-reception-admin-sante-audit-log-logs-email-parametres
- **Livrable:** 1.4.4 — migration/copie 1.4.4 (artefact 10 §7.8, §7.9)

---

## User story

En tant qu'admin,
je veux les écrans d'administration de la réception (stats, rapports, tickets), la santé de l'instance, l'audit log, les logs email et les paramètres opérationnels,
afin de surveiller l'instance et de configurer les seuils (alertes, session, email, activité).

---

## Critères d'acceptation

- **Étant donné** les APIs réception, santé, audit, logs et paramètres existantes ou à compléter,
- **Quand** j'accède aux sections admin réception (§7.8), santé, audit, logs email et paramètres (§7.9),
- **Alors** tous les écrans listés dans l'artefact 10 §7.8 et §7.9 sont opérationnels.
- **Et** livrable = migration/copie 1.4.4.

### Section Admin réception (artefact 10 §7.8)

- **Routes :** `/admin/reception-stats`, `/admin/reception-reports`, `/admin/reception-sessions`, `/admin/reception-tickets/:id`
- **Permissions :** admin.
- **Données / appels au chargement :**
  - Dashboard réception : stats (GET /v1/stats/reception/summary, GET /v1/stats/reception/by-category).
  - Liste tickets/sessions : GET /v1/reception/tickets avec filtres admin (période, poste, etc.).
  - Détail ticket : GET /v1/reception/tickets/{id} (lignes incluses).
- **Actions :** Export bulk tickets réception → POST /v1/admin/reports/reception-tickets/export-bulk (body : filtres).

### Section Santé (artefact 10 §7.9)

- **Route :** `/admin/health`
- **Permissions :** admin (ou super-admin selon politique).
- **Données / appels :** GET /v1/admin/health, GET /v1/admin/health/database, GET /v1/admin/health/scheduler, GET /v1/admin/health/anomalies.
- **Actions :** Test notifications → POST /v1/admin/health/test-notifications.

### Section Audit log (artefact 10 §7.9)

- **Route :** `/admin/audit-log`
- **Permissions :** admin.
- **Données / appels :** GET /v1/admin/audit-log — query : pagination, filtres (date, type, user_id, etc.).
- **Actions :** Filtres / pagination → rechargement avec nouveaux paramètres.

### Section Logs email (artefact 10 §7.9)

- **Route :** `/admin/email-logs`
- **Permissions :** admin.
- **Données / appels :** GET /v1/admin/email-logs (pagination/filtres si prévus).
- **Actions :** Consultation uniquement (pas de modification).

### Section Paramètres opérationnels (artefact 10 §7.9)

- **Route :** `/admin/settings`
- **Permissions :** admin (ou super-admin pour certains paramètres).
- **Données / appels au chargement :**
  - GET /v1/admin/settings/alert-thresholds
  - GET /v1/admin/settings/session
  - GET /v1/admin/settings/email
  - GET /v1/admin/settings/activity-threshold
- **Actions :**
  - Modifier seuil d'activité → PUT /v1/admin/settings/activity-threshold — body : valeur.
  - Modifier alertes → PUT /v1/admin/settings/alert-thresholds.
  - Modifier session → PUT /v1/admin/settings/session.
  - Modifier email → PUT /v1/admin/settings/email ; test → POST /v1/admin/settings/email/test.

---

## Tasks

### Frontend

1. **Admin réception (stats, rapports, sessions, tickets)**
   - Implémenter les routes `/admin/reception-stats`, `/admin/reception-reports`, `/admin/reception-sessions`, `/admin/reception-tickets/:id`.
   - Écran stats : appels GET /v1/stats/reception/summary et GET /v1/stats/reception/by-category ; affichage dashboard réception.
   - Écran liste tickets/sessions : GET /v1/reception/tickets avec filtres (période, poste, etc.) et pagination.
   - Écran détail ticket : GET /v1/reception/tickets/{id} avec lignes.
   - Bouton Export bulk : POST /v1/admin/reports/reception-tickets/export-bulk avec filtres ; téléchargement du fichier.

2. **Admin santé**
   - Implémenter la route `/admin/health`.
   - Affichage des métriques (système, DB, scheduler, anomalies) via GET /v1/admin/health, /database, /scheduler, /anomalies.
   - Bouton Test notifications → POST /v1/admin/health/test-notifications.

3. **Admin audit log**
   - Implémenter la route `/admin/audit-log`.
   - Liste paginée et filtrable (GET /v1/admin/audit-log) ; colonnes pertinentes (date, type, user, ressource, détail).

4. **Admin logs email**
   - Implémenter la route `/admin/email-logs`.
   - Liste des logs email (GET /v1/admin/email-logs) ; lecture seule.

5. **Admin paramètres**
   - Implémenter la route `/admin/settings`.
   - Sous-sections ou onglets : alertes, session, email, seuil d'activité.
   - Chargement des paramètres (GET …/alert-thresholds, /session, /email, /activity-threshold).
   - Formulaires d'édition et envoi PUT pour chaque catégorie ; bouton Test email → POST …/email/test.

### APIs (backend)

6. **Réception admin**
   - Exposer ou compléter : GET /v1/stats/reception/summary, GET /v1/stats/reception/by-category (si absents).
   - GET /v1/reception/tickets avec filtres admin (période, poste_id, etc.) et pagination.
   - POST /v1/admin/reports/reception-tickets/export-bulk (filtres, génération CSV/ZIP).

7. **Santé**
   - GET /v1/admin/health (agrégé), /v1/admin/health/database, /scheduler, /anomalies (selon spec existante health check).
   - POST /v1/admin/health/test-notifications (envoi test selon config).

8. **Audit log**
   - GET /v1/admin/audit-log — query : pagination (page, limit), filtres (date_from, date_to, event_type, user_id). Données depuis table `audit_events`.

9. **Logs email**
   - GET /v1/admin/email-logs — pagination/filtres si applicable (table ou log externe selon implémentation 1.4.4).

10. **Paramètres opérationnels**
    - GET/PUT /v1/admin/settings/alert-thresholds, /session, /email, /activity-threshold (lecture/écriture config selon artefact 10 §7.9).
    - POST /v1/admin/settings/email/test — envoi d'un email de test.

---

## Références

- **Epic 8, Story 8.4 :** `_bmad-output/planning-artifacts/epics.md`
- **Epic 8, Story 8.4 :** `_bmad-output/planning-artifacts/epics.md`
- **Traçabilité écran → API :** `references/artefacts/2026-02-26_10_tracabilite-ecran-donnees-appels-api.md` (§7.8 Réception admin, §7.9 Santé / audit / logs email / paramètres)
- **Checklist import 1.4.4 :** `references/ancien-repo/checklist-import-1.4.4.md`
- **Architecture et conventions :** `_bmad-output/planning-artifacts/architecture.md` ; `references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md`
- **Sprint status :** `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Conventions d'implémentation

- **UI / styling :** Mantine (alignement 1.4.4).
- **Layout admin :** écrans intégrés au layout admin (navigation / sidebar) dans `frontend/src/admin/`.
- **Tests frontend :** Vitest + React Testing Library + jsdom ; tests co-locés `*.test.tsx`.
- **Backend :** respect des conventions API (snake_case, pluriel, erreur `{ "detail": "..." }`, dates ISO 8601).

---

## Review (adversarial, pass 2 — 2026-02-27)

- **Résultat :** `changes-requested`
- **Fichier :** `_bmad-output/implementation-artifacts/8-4-reception-admin-sante-audit-log-logs-email-parametres.review.json`

**Vérifié :** Routes /admin/reception, /admin/health, /admin/audit-log, /admin/email-logs, /admin/settings ; backends correspondants ; permission admin ; Mantine.

**Manques demandés en correction :**
- POST /v1/admin/health/test-notifications + bouton « Test notifications » sur la page Santé.
- POST /v1/admin/reports/reception-tickets/export-bulk + bouton Export bulk tickets réception.
- (Optionnel) POST /v1/admin/settings/email/test + bouton Test email dans Paramètres.

Consolidation des routes réception (/admin/reception avec onglets Stats + Tickets) et usage de GET /v1/reception/stats/live acceptés comme équivalent fonctionnel.

---

## Review (pass 3 — corrections appliquées 2026-02-27)

- **Résultat :** `approved`
- **Fichier :** `_bmad-output/implementation-artifacts/8-4-reception-admin-sante-audit-log-logs-email-parametres.review.json`
- **Corrections vérifiées présentes :**
  1. **Backend** : POST /v1/admin/health/test-notifications (stub v1) dans `api/routers/v1/admin/health.py`.
  2. **Frontend** : Bouton « Test notifications » sur la page Santé (`AdminHealthPage.tsx`) + `postAdminHealthTestNotifications` dans `adminHealthAudit.ts`.
  3. **Backend** : POST /v1/admin/reports/reception-tickets/export-bulk dans `api/routers/v1/admin/reports_reception.py` (export CSV avec filtres date_from, date_to, poste_id, status).
  4. **Frontend** : Bouton « Export bulk tickets réception » sur `/admin/reception` (onglet Tickets) + `postAdminReceptionTicketsExportBulk` dans `adminHealthAudit.ts`.
  5. **Backend (optionnel)** : POST /v1/admin/settings/email/test (stub v1) dans `api/routers/v1/admin/settings.py`.
  6. **Frontend (optionnel)** : Bouton « Test email » dans l'onglet Email de Paramètres (`AdminSettingsPage.tsx`) + `postAdminSettingsEmailTest` dans `adminHealthAudit.ts`.
