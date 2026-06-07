# Révisions terrain — Caisse

**Périmètre :** Peintre v2 (`peintre-nano`), `/cash-register/*`, hub `/caisse/*`  
**Dernière passe HITL :** 2026-06-07 (revue live Strophe)

**Docs liés :** [checklist parité beta](../../artefacts/2026-05-30_01_checklist-chantier-parite-v2-beta-1.4.4.md) · [parité gestes](../../artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) · [Epic 6 terrain](../../artefacts/2026-04-08_07_caisse-v2-exploitabilite-terrain-epic6.md) · legacy `recyclique-1.4.4/frontend/src/pages/CashRegister/Sale.tsx`

---

## Synthèse (2026-06-07)

Reprise d'une **session déjà ouverte** avec **ticket en cours** → **encaissement impossible**, boucle reprise / fermeture, caisse virtuelle refusée.

---

## Tableau de bord

| ID | Titre | Type(s) | P | Investigé | Corrigé | HITL |
|----|-------|---------|---|-----------|---------|------|
| [01](#rev-caisse-01--session-orpheline-reprise-sans-date-claire) | Session orpheline reprise | métier · UI/UX | P1 | [x] | [x] | [ ] |
| [02](#rev-caisse-02--fermeture-caisse-sans-effet) | Fermeture sans effet | tech · métier | P0 | [x] | [x] | [ ] |
| [03](#rev-caisse-03--actualiser-ne-change-rien) | Actualiser inutile | UI/UX | P2 | [ ] | [ ] | [ ] |
| [04](#rev-caisse-04--ticket-trop-étroit-télescope) | Ticket trop étroit | UI/UX · parité-legacy | P1 | [ ] | [ ] | [ ] |
| [05](#rev-caisse-05--montant-visible-sans-action) | Montant OK, actions KO | UI/UX | P0 | [x] | [x] | [ ] |
| [06](#rev-caisse-06--finalisation-grisée) | Finalisation grisée | tech · métier | P0 | [x] | [x] | [ ] |
| [07](#rev-caisse-07--opérations-spéciales-grisé) | OP SP grisé | cadrage-produit | P2 | [ ] | [ ] | [ ] |
| [08](#rev-caisse-08--message-tickets-en-attente) | Message tickets en attente | tech · UI/UX | P1 | [ ] | [ ] | [ ] |
| [09](#rev-caisse-09--panneaux-session-et-tags) | Panneaux session / tags | UI/UX · cadrage-produit | P1 | [ ] | [ ] | [ ] |
| [10](#rev-caisse-10--held-sale-vs-encaissement) | Held sale vs encaissement | tech · métier | P0 | [x] | [x] | [ ] |
| [11](#rev-caisse-11--ux-remboursement) | UX remboursement | UI/UX · métier | P1 | [ ] | [ ] | [ ] |
| [12](#rev-caisse-12--virtuel-bloqué-par-réel) | Virtuel bloqué par réel | tech · métier | P0 | [x] | [x] | [ ] |
| [13](#rev-caisse-13--éloignement-legacy) | Écart legacy / v2 | parité-legacy · cadrage-produit | P2 | [ ] | [ ] | [ ] |
| [14](#rev-caisse-14--clavier-tab-vs-micro-phases) | Clavier Tab vs micro-phases | parité-legacy · UI/UX | P1 | [ ] | [ ] | [ ] |
| [15](#rev-caisse-15--multi-pesée-absente) | Multi-pesée `=` absente | parité-legacy · métier | P1 | [ ] | [ ] | [ ] |
| [16](#rev-caisse-16--flèches-select-paiement) | Flèches select paiement | parité-legacy · UI/UX | P1 | [ ] | [ ] | [ ] |
| [17](#rev-caisse-17--clavier-écarts-secondaires) | Clavier — écarts secondaires | parité-legacy · UI/UX | P2 | [ ] | [ ] | [ ] |
| [18](#rev-caisse-18--hub-caisse-écarts) | Hub caisse — intro / admin | parité-legacy · UI/UX | P2 | [ ] | [ ] | [ ] |
| [19](#rev-caisse-19--ouverture-date-cahier) | Ouverture — date cahier | parité-legacy · UI/UX | P2 | [ ] | [ ] | [ ] |
| [20](#rev-caisse-20--clôture-pin-step-up) | Clôture — PIN step-up | parité-legacy · cadrage-produit | P2 | [ ] | [ ] | [ ] |
| [21](#rev-caisse-21--deux-surfaces-clôture) | Deux parcours clôture | cadrage-produit · UI/UX | P2 | [ ] | [ ] | [ ] |
| [22](#rev-caisse-22--sync-paheko-invisible) | Sync Paheko invisible | UI/UX · métier | P2 | [ ] | [ ] | [ ] |
| [23](#rev-caisse-23--réf-checklist-clavier-audit-hors-live) | Réf. checklist clavier audit | cadrage-produit | P2 | [ ] | [ ] | [ ] |

---

## D1 — Session caisse (ouverture, reprise, fermeture)

### REV-CAISSE-01 — Session orpheline reprise sans date claire

| | |
|---|---|
| **Types** | métier · UI/UX |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Sur `/caisse`, poste « caisse principale » affiché **ouvert** ; « Reprendre » charge une session dont l'ancienneté est inconnue.

**Attendu / legacy**  
Reprise explicite avec contexte lisible (caissier, heure d'ouverture, fond de caisse).

**Impact**  
Impossible de savoir si la session est légitime ou résidu de test / crash.

**Piste technique**  
`useCaisseServerCurrentSession`, `attachCashflowDraftSessionPersistence`, table `cash_sessions`.

**Notes agent**  
Story 28.1 : hub affiche `opened_at` sur carte poste ouvert ; kiosque vente expose date d’ouverture dans le bandeau session ; reprise hub recolle `cashSessionIdInput` depuis GET courant.

**Gap résiduel (P1 suivi)**  
Caissier et fond de caisse **non affichés** — le fix 28.1 se limite à `opened_at` + recollage session ; contexte complet legacy (qui a ouvert, montant fond) reste à traiter hors story 28.1.

---

### REV-CAISSE-02 — Fermeture caisse sans effet

| | |
|---|---|
| **Types** | tech · métier |
| **Priorité** | P0 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
« Fermer la caisse » → retour hub `/caisse` ; poste toujours **ouvert** ; « Reprendre » recharge le même ticket.

**Attendu / legacy**  
Clôture effective ou message bloquant explicite (ticket non soldé, écart).

**Impact**  
Aucune sortie de secours ; boucle infinie.

**Piste technique**  
`CashflowCloseWizard`, `useCloseEntryBlock`, navigation `saleKioskCloseSessionPath()`, vente `held` non finalisée.

**Notes agent**  
Story 28.1 : après clôture réussie (`CaisseSessionCloseSurface`, `CashflowCloseWizard`), `resetCashflowDraft()` évite la reprise d’un ticket fantôme depuis sessionStorage. Blocage held non finalisé reste côté API (`CASH_SESSION_CLOSE_HELD_PENDING`). Distinct du gap parité **PIN step-up** (REV-CAISSE-20).

---

### REV-CAISSE-03 — Actualiser ne change rien

| | |
|---|---|
| **Types** | UI/UX |
| **Priorité** | P2 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
F5 / actualiser : état inchangé (session + ticket).

**Attendu / legacy**  
— (peut être cohérent si état serveur ; manque de feedback).

**Notes agent**  
—

---

## D2 — Écran vente / ticket

### REV-CAISSE-04 — Ticket trop étroit (« télescope »)

| | |
|---|---|
| **Types** | UI/UX · parité-legacy |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Colonne ticket **beaucoup trop étroite** ; contenu compressé ; KPI montant OK mais ticket illisible.

**Attendu / legacy**  
Colonne droite large (`Sale.tsx` — `RightColumn` + `Ticket`).

**Piste technique**  
`CashflowNominalWizard.module.css`, layout CREOS `/cash-register/sale`, `KioskFinalizeSaleDock`.

**Notes agent**  
—

---

### REV-CAISSE-05 — Montant visible sans action

| | |
|---|---|
| **Types** | UI/UX |
| **Priorité** | P0 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
KPI « Montant du ticket » visible ; aucune action utile sur le ticket (finalisation grisée).

**Lien**  
REV-CAISSE-06

**Notes agent**  
Story 28.1 : message explicite sous le bouton finalisation quand l’action reste bloquée (`cashflow-kiosk-finalize-blocked-reason`).

---

## D3 — Encaissement / finalisation

### REV-CAISSE-06 — Finalisation grisée

| | |
|---|---|
| **Types** | tech · métier · parité-legacy |
| **Priorité** | P0 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Ticket avec articles et montant ; bouton « **Ouvrir la finalisation** » **désactivé** — libellé peu parlant vs legacy (type **Encaisser**).

**Attendu / legacy**  
Encaisser dès lignes + total > 0 (modale `FinalizationScreen` legacy).

**Piste technique**  
`KioskFinalizeSaleDock` — `canOpenFinalize` = `!DATA_STALE` + `cashSessionIdInput` + lignes + total > 0 + moyens de paiement OK. Hypothèses : session ID vide, held sale, DATA_STALE, PM en erreur.

**Notes agent**  
Story 28.1 : prédicat partagé `evaluateCashflowFinalizeEligibility` — held sale débloqué sans `cashSessionIdInput` local ; sync session serveur au montage wizard. Écarts clavier **CLAV-04** → REV-CAISSE-16 (hors scope).

**Écart parité (hors scope 28.1)**  
Libellé legacy **« Encaisser »** non modifié (bouton reste « Ouvrir la finalisation ») — seul le prédicat d'éligibilité a été corrigé.

---

### REV-CAISSE-07 — Opérations spéciales grisé

| | |
|---|---|
| **Types** | cadrage-produit · UI/UX |
| **Priorité** | P2 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Bouton OP SP grisé avec ticket en cours.

**Attendu / legacy**  
Probablement **normal** (actif si ticket vide) — mais **non expliqué** à l'utilisateur.

**Piste technique**  
`specialOpsNavDepuisCaisseActif` dans `CashflowNominalWizard`.

**Notes agent**  
Décision PO : tooltip / masquer si confus.

---

## D4 — Panneaux session / tags (exposition caissier)

### REV-CAISSE-08 — Message tickets en attente

| | |
|---|---|
| **Types** | tech · UI/UX |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
« Session caisse requise pour les tickets en attente » alors qu'une session semble active.

**Piste technique**  
`HeldTicketsPanel` si `!sessionId` — décalage enveloppe / draft.

**Notes agent**  
—

---

### REV-CAISSE-09 — Panneaux session et tags permanents

| | |
|---|---|
| **Types** | UI/UX · cadrage-produit · parité-legacy |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Sous le ticket : encart Session caisse, moyen de paiement, tag métier (Gratiferia, etc.) **toujours visibles** — incompréhensible caissier, pas legacy.

**Attendu / legacy**  
Finalisation au moment d'encaisser uniquement ; pas d'UUID ni tags en permanence.

**Piste technique**  
`PaymentStep` mode `kioskSurface`, `.saleKioskFinalizeCard`.

**Notes agent**  
Décision PO : masquer kiosque beta vs admin.

---

## D5 — Tickets en attente (held)

### REV-CAISSE-10 — Held sale vs encaissement

| | |
|---|---|
| **Types** | tech · métier |
| **Priorité** | P0 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Reprise avec articles mais finalisation impossible — ticket = **held sale** ?

**Piste technique**  
`draft.activeHeldSaleId`, `finalizeHeldSale` vs `createSale`.

**Notes agent**  
Story 28.1 : reprise held recolle `cash_session_id` API dans le brouillon ; finalisation kiosque route `postFinalizeHeldSale` sans exiger UUID session saisi à la main.

---

## D6 — Remboursement

### REV-CAISSE-11 — UX remboursement

| | |
|---|---|
| **Types** | UI/UX · métier |
| **Priorité** | P1 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
- Sync OP / serveur = bruit dev  
- UUID ticket obligatoire — pas de recherche  
- UUID session 8-4-4-4-12 — impossible terrain  
- Pas de bouton retour (navigateur seulement)

**À développer**  
Recherche ticket, session préremplie, Annuler / Retour caisse.

**Piste technique**  
`CashflowRefundWizard.tsx`

**Notes agent**  
—

---

## D7 — Caisse virtuelle vs réel

### REV-CAISSE-12 — Virtuel bloqué par réel

| | |
|---|---|
| **Types** | tech · métier |
| **Priorité** | P0 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Caisse virtuelle → Simuler → **« Une session est déjà ouverte pour ce poste de travail »**.

**Attendu / legacy**  
Entraînement isolé du poste réel (`/cash-register/virtual` séparé).

**Piste technique**  
`cash_session_service.py` ConflictError ; `CaisseBrownfieldDashboardWidget.handleVirtualSimuler`.

**Notes agent**  
Story 28.1 : hub « Simuler » cible le poste `enable_virtual` (parité legacy 4445), pas le poste réel ouvert ; ouverture bloquée seulement si session déjà ouverte **sur le même register_id**.

---

## D8 — Cadrage produit

### REV-CAISSE-13 — Éloignement legacy

| | |
|---|---|
| **Types** | parité-legacy · cadrage-produit |
| **Priorité** | P2 |
| **Signalé** | 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Ajouts v2 (tags, champs session, sync) sans bénéfice terrain visible ; éloignement du geste 1.4.4.

**Notes agent**  
Décision PO globale kiosque beta. Hub + clavier P1 : REV-CAISSE-14…18 ; import rapport [`2026-05-26_03`](../../artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md).

---

## D9 — Parité clavier (import audit — pas revue live Strophe)

*Source : [`2026-05-26_03`](../../artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md) § **Workflows clavier** (CLAV-01…06). Écarts code/spec — à valider en terrain seulement si tu retestes le clavier caisse.*

### REV-CAISSE-14 — Clavier Tab vs micro-phases

| | |
|---|---|
| **Types** | parité-legacy · UI/UX |
| **Priorité** | P1 |
| **Signalé** | 2026-05-27 (rapport parité) · recoupé 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Legacy `SaleWizard` : **Tab** cycle focus dans l’onglet actif. Peintre : micro-rail browse → poids → prix — modèle différent (**CLAV-01**).

**Attendu / legacy**  
`SaleWizard.tsx` (Tab L757+) vs `CashflowNominalWizard` micro-phases.

**Piste**  
Dérogation PO documentée ou raccourcis équivalents ; valider en terrain si priorisé (voir REV-CAISSE-23).

**Notes agent**  
Non constaté explicitement en live 2026-06-07 — issu audit code.

---

### REV-CAISSE-15 — Multi-pesée `=` absente

| | |
|---|---|
| **Types** | parité-legacy · métier |
| **Priorité** | P1 |
| **Signalé** | 2026-05-27 (rapport parité) |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Legacy mode poids : touche **`=`** simule **+** multi-pesée (`MultipleWeightEntry`). **Absent** kiosk Peintre (**CLAV-02**).

**Piste**  
Confirmer usage terrain réel ; porter ou dérogation PO.

**Notes agent**  
—

---

### REV-CAISSE-16 — Flèches select paiement

| | |
|---|---|
| **Types** | parité-legacy · UI/UX |
| **Priorité** | P1 |
| **Signalé** | 2026-05-27 (rapport parité) |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Legacy `FinalizationScreen` : **flèches haut/bas** changent le moyen de paiement sans quitter le focus. Peintre : `<select>` natif uniquement (**CLAV-04**).

**Piste**  
Porter handlers legacy ou valider select natif en HITL (scénario C2b n°2).

**Notes agent**  
—

---

### REV-CAISSE-17 — Clavier — écarts secondaires

| | |
|---|---|
| **Types** | parité-legacy · UI/UX |
| **Priorité** | P2 |
| **Signalé** | 2026-05-27 (rapport parité) |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Regroupe **CLAV-03** (total éditable + Enter — legacy `no_item_pricing` seulement), **CLAV-05** (pavé global vs `KioskNumericPad` par phase), **CLAV-06** (libellés aide Enter B52 moins explicites).

**Piste**  
Dérogation PO si parcours kiosk nominal suffit ; cosmétique UX.

**Notes agent**  
—

---

## D10 — Hub, ouverture, clôture (écarts audit)

### REV-CAISSE-18 — Hub caisse — intro / admin

| | |
|---|---|
| **Types** | parité-legacy · UI/UX |
| **Priorité** | P2 |
| **Signalé** | 2026-05-27 (rapport parité) |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Hub `/caisse` : paragraphe intro CREOS sous titre ; menu admin postes legacy absent du widget brownfield.

**Piste**  
Stories 13.4 / 13.6 — dérogation PO documentée.

**Notes agent**  
—

---

### REV-CAISSE-19 — Ouverture — date cahier

| | |
|---|---|
| **Types** | parité-legacy · UI/UX |
| **Priorité** | P2 |
| **Signalé** | 2026-05-27 (rapport parité) |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Legacy ouverture différée : widgets **Date du cahier** (jour/mois/an). Peintre : `datetime-local` / modes widget — non recopié à l’identique.

**Piste**  
Story 13.2 si priorisée.

**Notes agent**  
—

---

### REV-CAISSE-20 — Clôture — PIN step-up

| | |
|---|---|
| **Types** | parité-legacy · cadrage-produit |
| **Priorité** | P2 |
| **Signalé** | 2026-05-27 (rapport parité) |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Brownfield clôture : **PIN obligatoire** + `X-Step-Up-Pin` (v2). Legacy `CloseSession.tsx` : clôture **sans PIN**. Dérogation PO story 13.3.

**Piste**  
Ne pas retirer step-up pour « parité » ; documenter pour caissiers.

**Notes agent**  
—

---

### REV-CAISSE-21 — Deux parcours clôture

| | |
|---|---|
| **Types** | cadrage-produit · UI/UX |
| **Priorité** | P2 |
| **Signalé** | 2026-05-27 (rapport parité) |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Coexistence **brownfield** (`…/session/close`) et **wizard CREOS** (`/caisse/cloture`, 3 onglets). Pas d’équivalence URL legacy stricte.

**Piste**  
Hors scope parité 1.4.4 stricte — slice CREOS v2 ; clarifier quel parcours pour beta.

**Notes agent**  
—

---

### REV-CAISSE-22 — Sync Paheko invisible

| | |
|---|---|
| **Types** | UI/UX · métier |
| **Priorité** | P2 |
| **Signalé** | 2026-05-27 (rapport parité) |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Après clôture : message texte relais Epic 8 ; **pas d’état** outbox / quarantaine / sync Paheko visible opérateur. Story **9.10** livrée côté batch (T1/T2/T3) — feedback UI v1 limité.

**Piste**  
Epic 22+ ; outbox admin si prévu.

**Notes agent**  
P0 métier D33/T3 **clos dev** (story 9-10, 2026-05-27) — ne pas rouvrir comme bug batch.

---

### REV-CAISSE-23 — Réf. checklist clavier audit (hors live)

| | |
|---|---|
| **Types** | cadrage-produit |
| **Priorité** | P2 |
| **Signalé** | 2026-05-27 (rapport parité § E) · recopié depuis collage autre agent 2026-06-07 |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
**Pas une remontée Strophe.** Checklist technique du rapport parité : 4 scénarios clavier caisse (30–60 min) pour comparer legacy vs Peintre. Le collage « C2b / tags v2.0.0 » venait d’un **autre chat** (coordination dev) — **pas une action pour toi** sauf si tu veux faire cette passe clavier un jour.

**Parcours suggérés (référence)**  
1. Vente rapide 3 catégories clavier → paiement espèces Enter.  
2. Paiement mixte 2 moyens sans souris (B52).  
3. Sous-catégorie drill + Escape.  
4. Comparaison perception legacy 4445 vs Peintre 4444.

**Notes agent**  
Ta revue live du 2026-06-07 couvre surtout session/ticket/UI, pas cette checklist clavier formelle.

---

## Pistes techniques transverses

1. Tracer reprise : `GET current session`, `envelope.cashSessionId`, `draft.cashSessionIdInput`, `activeHeldSaleId`, `widgetDataState`.
2. Held sale → branche `finalizeHeldSale` dans dock / PaymentStep.
3. Fermeture avec ticket non soldé → message vs navigation silencieuse.
4. Virtuel → `register_id` dédié entraînement.
5. Layout ticket : comparer largeur legacy 4445 vs Peintre 4444.
