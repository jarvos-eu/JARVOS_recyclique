# Checklist chantier — parite v2 vs 1.4.4 (beta test v2.0)

**Date :** 2026-05-30  
**Statut :** document de reference actif — chantier a reprendre avant beta terrain  
**Objectif :** tracer tout ce qui doit etre **verifie**, **complete** ou **decide** pour une **premiere v2.0 en beta test** exploitable par les benevoles (equivalence robuste avec prod **1.4.4**, autre depot `recyclique-1.4.4/`).

**Contexte session :** synthese conversation Cursor (recherche repo + audit code v2 mai 2026). Renommer la session Cursor avec un titre explicite (voir fin de document).

---

## 1. Role du document

| Question | Reponse |
|----------|---------|
| Remplace le PRD ? | **Non** — cadrage produit = `_bmad-output/planning-artifacts/prd.md` |
| Remplace le rapport parite Agent A ? | **Non** — il **operationalise** et **etend** [`2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md`](2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) avec statut **code + UI** |
| Correct course BMAD ? | **Probable** apres C2b + ce tableau coche — candidat `bmad-correct-course` ou epic dedie « parite beta » |
| Qui coche ? | **Strophe** (HITL) + agents dev ; colonnes `HITL` / `Dev` |

**Sources croisees (ne pas reparcourir tout le repo a chaque reprise) :**

- Remontees Discord : [`references/besoins-terrains.md`](../besoins-terrains.md)
- Inventaire 1.4.4 : [`references/ancien-repo/fonctionnalites-actuelles.md`](../ancien-repo/fonctionnalites-actuelles.md)
- Rapport parite + clavier : [`2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md`](2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) · QA2 [`2026-05-27_02_qa2-loop-rapport-parite-plancher-v2-gestes-terrain.md`](2026-05-27_02_qa2-loop-rapport-parite-plancher-v2-gestes-terrain.md)
- Matrice normative UI : [`2026-04-10_03_matrice-parite-ui-pilotes-peintre.md`](2026-04-10_03_matrice-parite-ui-pilotes-peintre.md)
- Mapping caisse Epic 6 : [`2026-04-08_05_mapping-brownfield-v2-caisse-epic6.md`](2026-04-08_05_mapping-brownfield-v2-caisse-epic6.md)
- Registre reception Epic 7 : [`2026-04-09_01_reception-v2-exploitabilite-terrain-epic7-squelette.md`](2026-04-09_01_reception-v2-exploitabilite-terrain-epic7-squelette.md)
- Ops speciales (Epic 24) : [`references/operations-speciales-recyclique/`](../operations-speciales-recyclique/index.md)
- Corrections 6.8 : [`2026-04-19_correction-lignes-vente-annulation-stats.md`](2026-04-19_correction-lignes-vente-annulation-stats.md)
- Plan coordinateur : [`.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md`](../../.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md) § **C2b**
- Etat projet : [`references/ou-on-en-est.md`](../ou-on-en-est.md)

---

## 2. Legende et colonnes de suivi

### Statut audit code (2026-05-30)

| Symbole | Signification |
|--------|----------------|
| **UI-OK** | Visible sur Peintre (`localhost:4444`) dans le parcours indique |
| **UI-partiel** | Implemente mais autre route, modal, permission, ou UX incomplete vs 1.4.4 |
| **API-seul** | Backend / client API OK ; pas d'equivalent visible caissier |
| **Absent** | Non porte v2 (ou legacy seulement) |
| **HITL** | A valider humainement (C2b ou session beta) |

### Priorite beta v2.0

| Priorite | Regle |
|----------|--------|
| **P0-beta** | Bloquant beta benevole (caisse ou reception quotidienne) |
| **P1-beta** | Fortement attendu ; contournement penible |
| **P2-post-beta** | Dette acceptee documentee ; apres tag beta |

### Colonnes a remplir en reprise

`[ ] HITL` · `[ ] Dev` · notes libres

---

## 3. Synthese executive (pour reprise rapide)

**Pourquoi l'impression « il manque tout » en testant v2 :**

1. Beaucoup de flux ne sont **pas sur le kiosque** `/cash-register/sale` mais sur **hub ops** `/caisse/operations-speciales` ou **admin**.
2. Des **widgets existent sans etre montes** sur la page CREOS (ex. historique reception).
3. Des **ecarts UX reels** vs 1.4.4 (presets kiosk, multi-pesee, boutons sociaux dedies).
4. **C2b HITL** (validation clavier / parcours) **pas encore faite** — voir `ou-on-en-est.md`.

**Ratio indicatif (~45 items operationnels) :** ~15 UI-OK · ~20 UI-partiel/API-seul · ~10 Absent — **beaucoup de « manques » = chercher au mauvais endroit**.

### Backlog candidat correct course / stories (triage initial)

| ID | Sujet | Priorite | Statut code | Piste story / epic |
|----|--------|----------|-------------|-------------------|
| BC-01 | Presets kiosk Don / Recyclage / Decheterie | P0-beta | Absent UI | Extension 13.8 ou story dediee |
| BC-02 | Multi-pesee touche `=` / `+` | P1-beta | Absent | 13.8 + validation usage terrain |
| BC-03 | Historique + export CSV sur `/reception` | P1-beta | Widget non monte | CREOS manifest + 7.4 |
| BC-04 | Dashboard terrain `/reception/dashboard` | P1-beta | Absent | Epic 19 / decision PO substitut admin |
| BC-05 | Saisie differee reception (`opened_at` UI) | P1-beta | API-seul | Aligner `ReceptionNominalWizard` |
| BC-06 | Boutons actions sociales dedies (vs liste) | P1-beta | UI-partiel | 6.6 + besoins-terrains |
| BC-07 | Annuler = parcours clair depuis ticket (pas seulement admin) | P1-beta | UI-partiel | Epic 24 + UX |
| BC-08 | Edition admin poids vente inline | P2-post-beta | API-seul | Admin cash-session detail |
| BC-09 | Bandeau live heures ouverture caisses | P2-post-beta | Absent | besoins-terrains §3 |
| BC-10 | Clavier Tab / fleches paiement (CLAV-01, CLAV-04) | P1-beta | UI-partiel | 13.8 + C2b |
| BC-11 | Seuil ecart D33 ±2 € vs 0,05 € terrain | P0-beta compta | Tension doc | Coordinateur / 9.10 suite |
| BC-12 | Lot comptable T3 (658/758) | P0-beta compta | API-partiel | Agent B / fil E |

---

## 4. Checklist A — Caisse kiosque (vente)

| ID | Fonctionnalite | Prio | Statut code | Ou tester v2 | Legacy 4445 | HITL | Dev |
|----|----------------|------|-------------|--------------|-------------|------|-----|
| A1 | Grille 26 touches AZERTY categories | P0 | UI-OK | `/cash-register/sale` | `/cash-register/sale` | | |
| A2 | Saisie poids / prix (pave) | P0 | UI-partiel | micro-phases browse→poids→prix | Tab + Numpad colonne | | |
| A3 | Multi-pesee `=` / `+` | P1 | Absent | — | `MultipleWeightEntry` | | |
| A4 | Finaliser + modale paiement | P0 | UI-OK | `cashflow-kiosk-finalize-modal` | `FinalizationScreen` | | |
| A5 | Paiements multiples clavier (B52) | P0 | UI-OK | Enter chaine dans modale | spec B52-P1 | | |
| A6 | Fleches haut/bas moyen paiement | P1 | Absent | select natif | custom legacy | | |
| A7 | Presets Don / Recyclage / Decheterie | **P0** | **Absent UI** | — | `GET /v1/presets` | | |
| A8 | Ticket lateral (lignes, total) | P0 | UI-OK | aside / kiosque | `Ticket.tsx` | | |
| A9 | Bandeau KPI sous header vente | P2 | UI-partiel | hub `/caisse` | `CashKPIBanner` | | |
| A10 | Notes sur vente | P1 | UI-partiel | correction / finalisation | B40-P4 | | |
| A11 | Ticket en attente | P1 | UI-partiel | hub `cashflow-held-tickets-panel` ; kiosque bas | panneau legacy | | |
| A12 | Total editable (mode no_item_pricing) | P2 | UI-partiel | total lecture seule kiosk | legacy mode | | |

**Fichiers cles :** `peintre-nano/src/domains/cashflow/CashflowNominalWizard.tsx`, `KioskFinalizeSaleDock.tsx`, `CategoryHierarchyPicker.tsx` · API `recyclique/api/.../endpoints/sales.py`

---

## 5. Checklist B — Hub caisse, ouverture, cloture

| ID | Fonctionnalite | Prio | Statut code | Ou tester v2 | Legacy | HITL | Dev |
|----|----------------|------|-------------|--------------|--------|------|-----|
| B1 | Hub postes Ouvrir / Reprendre | P0 | UI-OK | `/caisse` | `/caisse` | | |
| B2 | Caisse virtuelle | P0 | UI-OK | `/cash-register/virtual/*` | idem | | |
| B3 | Saisie differee + date cahier | P1 | UI-partiel | champ `date` (pas spinbuttons) | `OpenCashSession` differe | | |
| B4 | Cloture brownfield comptage + ecart 0,05 € | P0 | UI-OK | `.../session/close` | `CloseSession.tsx` | | |
| B5 | PIN step-up cloture | P0 | UI-partiel | obligatoire v2 | absent legacy | | |
| B6 | Wizard cloture `/caisse/cloture` | P2 | UI-OK | 2e surface CREOS | N/A URL legacy | | |
| B7 | Menu admin postes (super-admin) | P2 | Absent | — | menu legacy | | |

**Fichiers :** `CaisseBrownfieldDashboardWidget.tsx`, `CaisseSessionCloseSurface.tsx`, `CashflowCloseWizard.tsx`

---

## 6. Checklist C — Operations speciales et encaissements

| ID | Fonctionnalite | Prio | Statut code | Ou tester v2 | HITL | Dev |
|----|----------------|------|-------------|--------------|------|-----|
| C1 | Hub Annuler / Rembourser / Decaisser / Mouvement / Echanger | P0 | UI-OK | `/caisse/operations-speciales` | | |
| C2 | Rembourser (ticket source) | P0 | UI-OK | `/caisse/remboursement` | | |
| C3 | Annuler (vs remboursement) | P1 | UI-partiel | hub → souvent admin / corrections | | |
| C4 | Remb. N-1 / exceptionnel sans ticket | P1 | UI-OK | routes hub dediees + PIN | | |
| C5 | Decaissement / mouvement interne / echange | P1 | UI-OK | `/caisse/decaissement`, etc. | | |
| C6 | Don sans articles | P0 | UI-OK | `cashflow-open-special-don` | | |
| C7 | Adhesion asso | P0 | UI-OK | `cashflow-open-special-adhesion` | | |
| C8 | Actions sociales (Maraude, …) | **P1** | **UI-partiel** | liste `cashflow-social-don-wizard-kind` | | |
| C9 | Acces hub depuis dashboard caisse | P0 | UI-OK | boutons brownfield | | |

**Epic 24** : stories `24-1` … `24-10` **done** (`sprint-status.yaml`). PRD : `operations-speciales-recyclique/2026-04-18_prd-..._v1-1.md`

---

## 7. Checklist D — Corrections et admin caisse

| ID | Fonctionnalite | Prio | Statut code | Ou tester v2 | HITL | Dev |
|----|----------------|------|-------------|--------------|------|-----|
| D1 | Corriger lignes (cat, poids, qte, PU) | **P0** | UI-partiel | `/admin/cash-sessions/:id` → modal correction | | |
| D2 | Corriger date vente (`sale_date`) | **P0** | UI-partiel | meme wizard `sale_date` | | |
| D3 | Route `/caisse/correction-ticket` | P2 | Absent (volontaire) | retirée nav | | |
| D4 | PATCH poids inline admin | P2 | API-seul | API oui ; pas champ Peintre | | |
| D5 | Gestionnaire sessions admin | P1 | UI-partiel | `/admin/session-manager` | | |
| D6 | Detail session + journal ventes | P1 | UI-partiel | `/admin/cash-sessions/:id` | | |

**Story 6.8** · artefact [`2026-04-19_correction-lignes-vente-annulation-stats.md`](2026-04-19_correction-lignes-vente-annulation-stats.md)

---

## 8. Checklist E — Reception terrain

| ID | Fonctionnalite | Prio | Statut code | Ou tester v2 | Legacy | HITL | Dev |
|----|----------------|------|-------------|--------------|--------|------|-----|
| E1 | Poste + ticket + lignes CRUD | P0 | UI-OK | `/reception` | `TicketForm` | | |
| E2 | Clavier poids / categories | P0 | UI-OK | wizard | shortcuts legacy | | |
| E3 | Modifier / supprimer ligne (ouvert) | P0 | UI-OK | wizard | | | |
| E4 | PATCH poids (ferme, admin) | P0 | UI-OK | wizard + admin detail | | | |
| E5 | Dashboard terrain multi-tickets | P1 | **Absent** | — | `/reception/dashboard` | | |
| E6 | Saisie differee `opened_at` | P1 | **API-seul** | API OK ; UI n'envoie pas | modal admin | | |
| E7 | Historique + export sur meme page | P1 | **UI-partiel** | widget **non** dans `page-reception-nominal.json` | integre legacy | | |
| E8 | Export CSV ticket | P1 | UI-partiel | `/admin/reception-tickets/:id` | | | |
| E9 | Un ticket actif / poste | P1 | UI-partiel | comportement v2 | multi-tickets legacy | | |
| E10 | Poste partage + brouillon (Epic 27) | P1 | UI-OK | headers device + draft | | | |

**Action CREOS evidente :** ajouter slot `reception-history-panel` dans [`contracts/creos/manifests/page-reception-nominal.json`](../../contracts/creos/manifests/page-reception-nominal.json) (aujourd'hui seul slot `reception-nominal-wizard`).

---

## 9. Checklist F — Reception et pilotage admin

| ID | Fonctionnalite | Prio | Statut code | Ou tester v2 | HITL | Dev |
|----|----------------|------|-------------|--------------|------|-----|
| F1 | Stats reception (graphiques) | P2 | UI-partiel | `/admin/reception-stats` sans Recharts | | |
| F2 | Liste tickets | P0 | UI-OK | `/admin/reception-sessions` | | |
| F3 | Detail ticket admin | P0 | UI-OK | `/admin/reception-tickets/:id` | | |
| F4 | `/admin/reception-reports` | P2 | Absent | backlog Epic 16 | | |
| F5 | Export bulk groupe | P1 | UI-OK | liste admin | | |

---

## 10. Checklist G — Transverse

| ID | Fonctionnalite | Prio | Statut | Source | HITL | Dev |
|----|----------------|------|--------|--------|------|-----|
| G1 | Bandeau live KPI | P0 | UI-partiel | affiche ; heures ouverture caisses **non** | besoins-terrains §3 | | |
| G2 | ACL centralisees super-admin | P2 | UI-partiel | permissions + groupes | besoins-terrains §4 | | |
| G3 | Hub admin 6+3 | P1 | UI-partiel | `/admin` | stories 18.x | | |
| G4 | Parametrage comptable SuperAdmin | P1 | UI-partiel | `/admin/compta` | spec QA 2026-04-18 | | |

---

## 11. Checklist H — Compta Paheko (peu visible caissier, gate beta)

| ID | Sujet | Prio | Statut | Note |
|----|--------|------|--------|------|
| H1 | Feedback sync / outbox apres cloture | P1 | UI-partiel | relais Epic 8 |
| H2 | D33 ±2 € vs 0,05 € UI terrain | P0 | Tension | trancher PO — rapport 03 |
| H3 | Lot T3 ecart 658/758 | P0 | API-partiel | `paheko_close_batch_builder` |

Story **9.10** **done** (2026-05-27) — ne pas confondre « liaison livree » et « parite gestes + compta terrain valides ».

---

## 12. Protocole de test beta (30–60 min)

**Prerequis :** Peintre `http://localhost:4444` · Legacy `http://localhost:4445` · compte admin recette · poste caisse ouvert.

| Etape | Parcours | Sections checklist |
|-------|----------|-------------------|
| 1 | Vente kiosque 3 lignes + paiement | A1–A5 |
| 2 | Ticket en attente depuis hub | A11, B1 |
| 3 | Hub operations speciales → remboursement | C1–C2 |
| 4 | Don / adhesion / social | C6–C8 |
| 5 | Cloture + PIN | B4–B5 |
| 6 | Correction admin session | D1–D2 |
| 7 | Reception complete + export admin | E1–E4, F3 |
| 8 | Comparer intentions legacy 4445 | notes ecarts |

**C2b officiel :** plan [post-9.6](../../.cursor/plans/post-9.6_plancher_et_compta_3341de2e.plan.md) § C2b · 4 scenarios clavier du rapport 03 § *Workflows clavier caisse*.

---

## 13. Remontees Discord (`besoins-terrains.md`) — mapping

| Besoin terrain | Section checklist | Statut resume |
|----------------|-----------------|---------------|
| Ticket en attente | A11 | UI-partiel |
| Remboursement | C2 | UI-OK |
| Don sans articles | C6 | UI-OK |
| Adhesion | C7 | UI-OK |
| Boutons actions sociales | C8 | UI-partiel |
| Modifier date/contenu vente super-admin | D1–D2 | UI-partiel (admin) |
| Bandeau live heures ouverture | G1 | Absent |
| ACL centralisees | G2 | UI-partiel |

---

## 14. Prochaines etapes chantier (ordre suggere)

1. **Session C2b** — cocher colonne HITL sur A, B, C (kiosque + ops + cloture).
2. **Triage P0-beta** — BC-01 (presets), BC-03 (history manifest), BC-07 (annuler UX), D1–D2 visibilite corrections.
3. **Decision PO** — BC-04 dashboard reception vs admin ; BC-06 boutons sociaux ; BC-11/12 compta.
4. **Lancer correct course BMAD** si ecarts > capacite stories 13.8 / 6.8 / 7.4 — brief : ce document + rapport 03 + matrice 04-10-03.
5. **Mettre a jour** `sprint-status.yaml` / epics apres arbitrage — pas avant HITL P0.

---

## 15. Journal des mises a jour

| Date | Auteur | Changement |
|------|--------|------------|
| 2026-05-30 | Cursor (session Strophe) | Creation initiale : checklist + audit code peintre-nano / recyclique/api + synthese BC-01..12 |

---

## 16. Titre de session Cursor suggere

**Parite v2 beta — checklist chantier 1.4.4 (caisse reception admin)**

Variante courte : **`v2.0 beta — parite terrain 1.4.4`**
