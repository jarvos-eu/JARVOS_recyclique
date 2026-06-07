# Story 28.1 : Stabiliser la caisse terrain P0 sur session, finalisation et clôture

Status: done

**Story key :** `28-1-stabiliser-la-caisse-terrain-p0-session-finalisation-et-cloture`  
**Epic :** 28 — Stabiliser la beta terrain depuis le registre `references/revision/`  
**Implementation artifact :** `_bmad-output/implementation-artifacts/28-1-stabiliser-la-caisse-terrain-p0-session-finalisation-et-cloture.md`  
**Date CS :** 2026-06-07

## Contexte produit

La revue HITL du `2026-06-07` a confirmé que la chaîne caisse la plus critique reste bloquée sur le terrain : reprise de session douteuse, finalisation grisée, confusion ticket nominal / held sale, clôture sans effet, et conflit entre caisse réelle et virtuelle.

Cette story est la **première priorité de l’Epic 28**. Elle ne cherche pas à refaire la caisse v2 ni la compta ; elle doit **rendre à nouveau exploitable** le chemin terrain minimum :

`/caisse` -> reprise / ouverture -> vente -> finalisation -> clôture

## Scope `REV-*`

| ID | Titre | Priorité | Rôle dans 28.1 |
|----|-------|----------|----------------|
| `REV-CAISSE-01` | Session orpheline reprise | P1 | Clarifier la reprise et le contexte session |
| `REV-CAISSE-02` | Fermeture sans effet | P0 | Corriger ou expliciter la clôture |
| `REV-CAISSE-05` | Montant OK, actions KO | P0 | Rétablir l’action utile côté ticket |
| `REV-CAISSE-06` | Finalisation grisée | P0 | Débloquer l’accès à l’encaissement |
| `REV-CAISSE-10` | Held sale vs encaissement | P0 | Séparer held sale et vente nominale |
| `REV-CAISSE-12` | Virtuel bloqué par réel | P0 | Empêcher le conflit réel / virtuel retenu en beta |

**Hors scope direct :**

- `REV-CAISSE-11` remboursement UX ;
- `REV-CAISSE-14..17` parité clavier ;
- `REV-CAISSE-18..23` variantes / cadrage / Paheko UI ;
- toute extension comptable Epic 22/23.

## Story (BDD)

As a cashier or terrain tester,  
I want the real cash register path to resume, finalize and close sessions credibly,  
So that the v2 caisse is no longer blocked on the core sale-to-close workflow during beta.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 28.1**.

**Given** the revision register identifies blocking caisse items `REV-CAISSE-01`, `02`, `05`, `06`, `10` and `12`  
**When** this story is delivered  
**Then** the bounded real-cash path no longer traps the user in a resume / finalize / close loop  
**And** the system either closes the session effectively or returns an explicit blocking reason tied to the actual state  
**And** held-sale handling is not silently confused with nominal encaissement  
**And** the virtual-cash path does not fail because of the nominal workstation session when the retained beta behavior should keep them separated

**Given** Epic 6 remains the caisse business authority and Epic 13 the last UI parity baseline  
**When** the story is reviewed  
**Then** the fix stays anchored to backend authority, manifests and reviewable UI state  
**And** no new caisse business model is invented in frontend code  
**And** any residual deviation versus legacy is written as an explicit gap or defer decision in `references/revision/`

## Tasks / Subtasks

- [x] Tracer la reprise de session et les identifiants réellement utilisés (`current session`, `cashSessionIdInput`, `activeHeldSaleId`)
- [x] Corriger le prédicat qui grise la finalisation ou documenter le blocage explicite si le ticket est non finalisable
- [x] Séparer proprement la branche held sale de la branche encaissement nominal
- [x] Corriger la fermeture qui renvoie au hub sans effet utile
- [x] Vérifier le comportement retenu pour la caisse virtuelle sur poste réel
- [x] Ajouter au moins un test de non-régression backend ou front sur le cas le plus critique touché
- [x] Mettre à jour `references/revision/domaines/caisse.md` sur `Investigé` / `Corrigé` pour les items réellement couverts

## Dev Notes

### Pistes techniques issues du registre

- `useCaisseServerCurrentSession`
- `attachCashflowDraftSessionPersistence`
- `CashflowCloseWizard`
- `useCloseEntryBlock`
- `KioskFinalizeSaleDock`
- `draft.activeHeldSaleId`
- `finalizeHeldSale`
- `cash_session_service.py`
- `CaisseBrownfieldDashboardWidget.handleVirtualSimuler`

### Garde-fous

- Ne pas absorber remboursement, opérations spéciales ou clavier dans cette story sauf si un fix minimal est strictement requis pour fermer un P0 ci-dessus.
- Ne pas rouvrir Epic 22/23 : la story porte l’exploitabilité terrain, pas un nouveau chantier comptable.
- Ne pas transformer la caisse virtuelle en sujet de vision long terme ; traiter seulement le conflit bloquant retenu en beta.

### Références utiles

- `references/revision/domaines/caisse.md`
- `references/revision/index.md`
- `_bmad-output/planning-artifacts/epics.md` § Epic 28 / Story 28.1
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `references/artefacts/2026-05-26_03_rapport-parite-plancher-v2-gestes-terrain.md`

## Testing / gates recommandés

- pytest ciblé sur la clôture / sessions / held sale selon fichiers touchés ;
- tests front ciblés sur finalisation / fermeture si surface Peintre modifiée ;
- relecture de la régression réel vs virtuel ;
- QA2 ciblé sur le scope 28.1 avant CR ;
- retest HITL par Strophe ensuite.

## Alignement sprint / YAML

- `epic-28` : `in-progress`.
- `28-1-stabiliser-la-caisse-terrain-p0-session-finalisation-et-cloture` : `done` (DS + QA2 correcteur itération 1).
- Stories `28-2` à `28-5` : `backlog` / `ready-for-dev` selon `sprint-status.yaml`.

### Authz / PIN (story 28.1)

- **Hors scope** : pas de changement flux authz ni self-service PIN (story 28.2).
- **Clôture** : step-up PIN opérateur inchangé (`CaisseSessionCloseSurface` → `postCloseCashSession` avec `stepUpPin`) — pas de régression introduite.

## Dev Agent Record

### Completion Notes

- Prédicat partagé `evaluateCashflowFinalizeEligibility` : held sale encaissable sans `cashSessionIdInput` local ; message blocage explicite sous le bouton kiosque.
- Reprise session : sync `cashSessionIdInput` depuis GET courant ; hub affiche `opened_at` ; reprise « Reprendre » recolle l’ID session.
- Held : `applyServerHeldSaleToDraft` porte `cash_session_id` API ; branche `postFinalizeHeldSale` inchangée côté dock.
- Clôture : `resetCashflowDraft()` purge mémoire + `sessionStorage` après succès ; flush debounce au detach persistance (CR H1/M1).
- Virtuel : `handleVirtualSimuler` cible poste `enable_virtual` (parité legacy) ; ouverture bloquée seulement sur le même `register_id`.
- Tests : `cashflow-finalize-held-without-session-input-28-1`, `cashflow-register-variants-28-1`, `cashflow-finalize-eligibility-28-1`, `cashflow-kiosk-finalize-blocked-28-1`, `cashflow-draft-session-persistence` (REV-02).
- QA2 it.1 : session ouverte = `serverSession.status === 'open'` ; refresh enveloppe post-clôture ; blocage ajout lignes si held actif.
- QA2 it.2 : purge `openedSessionId` post-clôture ; en-tête kiosque sans ID fantôme ; sync brouillon vidé si GET fermé ; held list alignée GET courant ; TotalStep désactivé si held ; tests ghost envelope + held-line-add-blocked + pmLoading eligibility.
- `references/revision/domaines/caisse.md` : REV-01, 02, 05, 06, 10, 12 en Investigé/Corrigé — pas Validé HITL.

### File List

- `peintre-nano/src/domains/cashflow/cashflow-finalize-eligibility.ts`
- `peintre-nano/src/domains/cashflow/cashflow-register-variants.ts`
- `peintre-nano/src/domains/cashflow/cashflow-draft-store.ts`
- `peintre-nano/src/domains/cashflow/KioskFinalizeSaleDock.tsx`
- `peintre-nano/src/domains/cashflow/CashflowNominalWizard.tsx`
- `peintre-nano/src/domains/cashflow/CaisseBrownfieldDashboardWidget.tsx`
- `peintre-nano/src/domains/cashflow/CaisseSessionCloseSurface.tsx`
- `peintre-nano/src/domains/cashflow/CashflowCloseWizard.tsx`
- `peintre-nano/tests/unit/cashflow-finalize-held-without-session-input-28-1.test.tsx`
- `peintre-nano/tests/unit/cashflow-finalize-eligibility.test.ts`
- `peintre-nano/tests/unit/caisse-session-close-reset-draft-28-1.test.tsx`
- `peintre-nano/tests/unit/cashflow-kiosk-finalize-blocked-28-1.test.tsx`
- `peintre-nano/tests/unit/caisse-brownfield-ghost-session-28-1.test.tsx`
- `peintre-nano/tests/unit/cashflow-held-line-add-blocked-28-1.test.tsx`
- `peintre-nano/tests/unit/cashflow-register-variants-28-1.test.ts`
- `peintre-nano/tests/unit/cashflow-draft-session-persistence.test.ts`
- `recyclique/api/src/recyclic_api/services/admin_settings_service.py`
- `recyclique/api/src/recyclic_api/services/cash_denomination_service.py`
- `references/revision/domaines/caisse.md`

### Change Log

- 2026-06-07 — Story 28.1 DS : stabilisation P0 session / finalisation / clôture / virtuel (front Peintre).
- 2026-06-07 — CR retry : purge sessionStorage post-clôture, flush debounce, blockedReason non-kiosk ; fixes gate API (admin_settings, cash_denomination).
