# Rapport parité plancher v2 — gestes terrain (caisse & réception)

**Agent :** A (parité plancher 2.0)  
**Date :** 2026-05-27 (complément clavier caisse : 2026-05-27)  
**Référence prod :** legacy `recyclique-1.4.4/` (autre dépôt Git, prod 1.4.4)  
**Cible v2 :** `peintre-nano/` + API `recyclique/api/`  
**Matrice normative :** [`2026-04-10_03_matrice-parite-ui-pilotes-peintre.md`](2026-04-10_03_matrice-parite-ui-pilotes-peintre.md)  
**Proposition sprint :** [`sprint-change-proposal-2026-04-12-parite-caisse-legacy-stricte.md`](../../_bmad-output/planning-artifacts/sprint-change-proposal-2026-04-12-parite-caisse-legacy-stricte.md)  
**Guide pilotage :** [`guide-pilotage-v2.md`](../../_bmad-output/planning-artifacts/guide-pilotage-v2.md) (caisse)

---

## Synthèse exécutive (5 lignes)

1. **Prérequis legacy** : clone `recyclique-1.4.4/` accessible — exploration OK.  
2. **Caisse brownfield** : parité URL et libellés hub / ouverture / clôture largement couverte (stories 13.1–13.6) ; **clavier saisie** : grille catégories AZERTY **OK** ; **écarts P1** = modèle micro-phases (browse/poids/prix) vs wizard+tablist legacy, pas de multi-pesée `=` ; **paiement** : workflow B52 **largement porté** (`KioskFinalizeSaleDock`) mais **sans** champ « Total à payer » éditable ni flèches haut/bas custom sur le select — détail **§ Workflows clavier caisse** (2 lignes P1 tableau principal + **CLAV-01**, **CLAV-02**, **CLAV-04** P1 ; **CLAV-03** P2).  
3. **Fermeture caisse** : UI terrain alignée à **±0,05 €** (legacy + API + Peintre) ; décision produit **D33 ±2 €** (Paheko) **non portée** en UI/API terrain — **arbitrage PO requis** avant story liaison Paheko (Agent B).  
4. **Lots comptables T1/T2** : builder batch présent (`sales_donations`, remboursements) ; **T3 (écart 658/758) absent** du code batch — gap **P0 métier (fil E)**.  
5. **Réception** : parcours nominal + raccourcis AZERTY alignés ; **dashboard terrain** `/reception/dashboard` non cloné en Peintre (P2, ligne tableau) ; **saisie différée réception** legacy sans équivalent Peintre — gap plancher (hors compta immédiate).

**Écarts P0 métier (tableau)** : 2 lignes (D33 terrain, T3 batch). **C-sync** : voir § Impact Agent B — écart D33 + T3 = **bloquants** pour figer les AC « fermeture → Paheko » sans décision Coordinateur.

---

## Méthode

| Étape | Action |
|-------|--------|
| 1 | `Task` explore — cartographie fichiers legacy / Peintre / API / CREOS |
| 2 | Croisement matrice pilotes `ui-pilote-03*` … `03f`, extension admin `ui-pilote-14*`, `ui-admin-15-4-reception-*` |
| 3 | Lecture ciblée : `CloseSession.tsx`, `CaisseSessionCloseSurface.tsx`, `CashflowCloseWizard.tsx`, `cash_session_service.py`, `paheko_close_batch_builder.py`, décisions D29/D33 |
| 4 | Complément clavier : `Sale.tsx`, `SaleWizard.tsx`, `FinalizationScreen.tsx`, `cashKeyboardShortcuts.ts`, `CashflowNominalWizard.tsx`, `KioskFinalizeSaleDock.tsx`, `CategoryHierarchyPicker.tsx`, spec B52-P1, blueprint 13.7 § workflows clavier |
| 5 | Pas de preuve navigateur MCP dans cette session (reprise **C2b** recommandée sur 3–5 parcours **clavier** caisse) |

**Hors scope Agent A :** code métier, module 9.7, HelloAsso, implémentation liaison Paheko (Agent B).

---

## Tableau principal — parcours | legacy | Peintre | écart | sévérité | owner | dérogation PO

| Parcours | Legacy 1.4.4 | Peintre v2 | Écart | Sévérité | Owner | Dérogation PO |
|----------|--------------|------------|-------|----------|-------|----------------|
| Hub caisse `/caisse` | `CashRegisterDashboard.tsx` — postes, virtuel, différé | `CaisseBrownfieldDashboardWidget` + `page-cashflow-nominal.json` | Paragraphe intro CREOS sous titre ; menu admin postes legacy absent widget | P2 | A / stories 13.4 | **Dérogation PO** stories 13.4 / 13.6 (`ui-pilote-03e-rcn-01`) |
| Ouverture session | `OpenCashSession.tsx` — fond initial ; différé : **Date du cahier** (widgets jour/mois/an) | Même widget brownfield ; date via `datetime-local` / modes widget | Widget date cahier legacy non recopié à l’identique | P2 | B (13.2) si priorisé | **Dérogation PO** story 13.2 (`ui-pilote-03c`) |
| Vente kiosque `/cash-register/sale` | `Sale.tsx` + `SaleWizard.tsx` plein écran | `CashflowNominalWizard` + alias runtime ; grille catégories 13.8 | Voir § **Workflows clavier caisse** — saisie P1, paiement P1 partiel | **P1** | stories 13.7–13.8 | **Dérogation PO** (`ui-pilote-03-caisse-vente-kiosk`) — **à resserrer** si PO exige parité clavier stricte |
| **Clavier — grille catégories** | `cashKeyboardShortcuts.ts` — 26 touches positionnelles AZERTY | `CategoryHierarchyPicker` — `KIOSK_CATEGORY_POSITION_KEYS` identique | Priorité `shortcut_key` BDD si renseigné | — | — | **OK** |
| **Clavier — écran paiement** | `FinalizationScreen.tsx` — spec **B52-P1** | `KioskFinalizeSaleDock.tsx` — tests `kiosk-finalize-sale-enter-shortcut` | Total non éditable ; pas de flèches custom sur select ; pas d’indicateurs 💡 legacy | **P1** | 13.8 / PO | **Dérogation PO** si accepté ; sinon backlog parité clavier |
| **Fermeture brownfield** `…/session/close` | `CloseSession.tsx` — résumé, comptage, commentaire si \|écart\|>0,05 €, **sans PIN** | `CaisseSessionCloseSurface.tsx` — mêmes blocs + **PIN step-up obligatoire** | PIN absent legacy ; OpenAPI exige `X-Step-Up-Pin` | P2 | API / 2.4 / 6.7 | **Dérogation PO** story 13.3 (`ui-pilote-03d`) |
| **Fermeture wizard** `/caisse/cloture` | *N/A* (route legacy = brownfield ci-dessus) | `CashflowCloseWizard.tsx` — 3 onglets (récap / comptage / confirmer), totaux 6.4, relais Epic 8 | Deux surfaces clôture coexistants ; pas d’équivalence URL legacy | P2 | Epic 6 / PO | **Hors scope** parité 1.4.4 stricte — slice CREOS v2 |
| Tolérance écart espèces | 0,05 € (`CloseSession.tsx`) | 0,05 € (`CLOSE_VARIANCE_TOLERANCE_EUR`, `cash_session_service.py`) | Décision **D33 ±2 €** non implémentée terrain | **P0** | **Coordinateur / PO** | **Aucune** — trancher avant AC Agent B D33 |
| Lots Paheko T1/T2/T3 | N/A UI (post-clôture API) | Idem ; batch `paheko_close_batch_builder.py` : T1/T2 kinds seulement | **T3 (variance 658/758) absent** du builder | **P0** | **Agent B** | **Aucune** — procédure D29 exige T3 |
| Retour état sync Paheko | N/A | Message texte relais Epic 8 après close | Pas d’état outbox/quarantaine visible opérateur | P2 | Epic 22+ | Attendu v1 liaison (Agent B) |
| Réception nominale `/reception` | `Reception.tsx` + `TicketForm.tsx` | `ReceptionNominalWizard` + `page-reception-nominal.json` | Bandeau KPI live Peintre (unifié) | P2 | stories réception | Alignement intention OK |
| Raccourcis catégories réception | `receptionKeyboardShortcuts.ts` | `CategoryHierarchyPicker` (grille AZERTY 26 touches) | — | — | — | **OK** |
| Raccourcis poids / destination | `TicketForm.tsx` (`=`, flèches, Tab, Enter) | `reception-poids-keyboard.ts` + wizard | — | — | — | **OK** |
| Dashboard réception terrain | `/reception/dashboard` | Supervision admin CREOS (pas même URL terrain) | Pas de clone `/reception/dashboard` | P2 | Epic 19.x | **Hors scope** parité nominal si pilotage = admin |
| **Saisie différée réception** | Modal date admin `Reception.tsx` | *Absent* `peintre-nano/src/domains/reception/` | Fonction admin legacy non portée | P2 | Coordinateur | **Hors scope** v2.0 plancher sauf décision PO |
| Admin réception stats | `/admin/reception-stats` | `AdminReceptionStatsSupervisionWidget` | Graphiques Recharts legacy non revendiqués | P2 | 19.1 / 19.3 | **OK** (`ui-admin-15-4-reception-stats`) |
| Exports réception | `/admin/reception-reports` | Gap CREOS | Backlog | P3 | Epic 16 | **Hors scope** parité 19.x |

---

## Section dédiée — Fermeture caisse

### Pont D33 / D29 (lecture Agent A, implémentation Agent B)

| Identifiant | Règle documentée | Implémentation observée (2026-05-27) |
|-------------|------------------|--------------------------------------|
| **D29** | Ventiler clôture Paheko en **T1** (ventes+dons), **T2** (remboursements), **T3** (écart 658/758) | T1/T2 : kinds `sales_donations*`, `refunds_*` dans `paheko_close_batch_builder.py` ; **T3 : absent** |
| **D33** | Écart espèces/fonds **±2 €** — au-delà **blocage clôture compta Paheko** (procédure / story Agent B), pas blocage UI brownfield ; en deçà → T3 auto | Terrain brownfield : **0,05 €** — commentaire obligatoire au-delà (`CLOSE_VARIANCE_TOLERANCE = 0.05`) ; **pas de seuil ±2 € en UI** terrain |
| **Legacy arrondi** | Tolérance **0,05 €** sur écart physique vs théorique | Aligné legacy ↔ Peintre ↔ API |
| **Tension** | Ne pas calquer D33 sur 0,05 € sans décision PO | **Non résolu** — voir § Impact Agent B |

> **Note :** le libellé « T1 » dans `FinalizationScreen.tsx` (legacy) = ordre d’affichage paiement, **pas** le lot comptable Paheko.

### Parcours UI — legacy (`CloseSession.tsx`)

1. `refreshSession` au montage ; redirection si pas de session `open` → `/caisse`.  
2. **Session vide** : alerte + « Continuer quand même » → `actual_amount = initial_amount`.  
3. **Résumé** : fond initial, ventes, dons (si > 0), montant théorique, articles vendus.  
4. **Contrôle** : saisie montant physique compté.  
5. Écart = physique − théorique ; théorique = fond + ventes + dons.  
6. Si \|écart\| > **0,05 €** → commentaire obligatoire.  
7. Submit `closeSession(id, { actual_amount, variance_comment })` — **sans PIN**.  
8. Routes : `/cash-register/session/close`, `virtual/…`, `deferred/…` (`App.jsx`).

**Raccourcis clavier :** aucun dédié (formulaire standard).

### Parcours UI — Peintre

#### Surface A — parité brownfield (`CaisseSessionCloseSurface.tsx`)

- Déclenchée via `presentation_surface: session_close` sur manifest `cashflow-nominal` ; alias runtime `…/session/close` (`RuntimeDemoApp.tsx`).  
- Même enchaînement résumé / session vide / comptage que legacy.  
- **Écart** : champ **PIN** + `postCloseCashSession` avec `X-Step-Up-Pin` et `Idempotency-Key`.  
- Tolérance commentaire : `needsVarianceComment()` → seuil **0,05 €** (`cash-session-client.ts`).

#### Surface B — wizard CREOS (`CashflowCloseWizard.tsx`)

- Route **`/caisse/cloture`** (`page-cashflow-close.json`).  
- Onglets : (1) Récap serveur (initial, ventes, dons, poids, totals 6.4, théorique) ; (2) Comptage ; (3) Confirmer + PIN.  
- Garde-fous : permission `caisse.access`, enveloppe, `DATA_STALE`.  
- Succès : relais Epic 8 — **pas** de feedback sync Paheko.

### Formules et champs (alignement)

| Champ | Legacy | Peintre | Backend |
|-------|--------|---------|---------|
| Fond initial | `initial_amount` | idem | `CashSession.initial_amount` |
| Ventes | `total_sales` | + `totals.sales_completed` (wizard) | Preview clôture / service |
| Dons | `total_donations` | idem | Agrégat session |
| Montant théorique | fond + ventes + dons | `theoreticalCloseAmount()` (preview API prioritaire) | `cash_session_service.py` |
| Montant physique | saisie | idem | `actual_amount` |
| Commentaire écart | \|écart\| > 0,05 € | idem | L835 `cash_session_service.py` |

### Matrice pilote liée

- `ui-pilote-03d-caisse-session-close-legacy-urls` — statut matrice : **Écart accepté** (PIN documenté).  
- Preuves DevTools 2026-04-12 référencées dans la matrice ; **validation humaine C2b** : à faire par Strophe (30–60 min, 3–5 parcours).

---

## Workflows clavier caisse — saisie article & écran paiement

**Périmètre :** kiosque vente `/cash-register/sale` (alias Peintre `cashflow-nominal`). Références normatives : blueprint [`2026-04-12_06_blueprint-portage-kiosque-13-7.md`](2026-04-12_06_blueprint-portage-kiosque-13-7.md) § *Workflows clavier* ; spec legacy [`spec-b52-p1-keyboard-workflow-paiements-multiples.md`](../../recyclique-1.4.4/docs/front-end-specs/spec-b52-p1-keyboard-workflow-paiements-multiples.md).

**Objectif utilisateur :** enchaîner **catégorie → quantité/poids/prix → finaliser → paiement(s)** sans souris, comme en prod 1.4.4.

### Synthèse conformité clavier

| Zone | Conformité globale | Commentaire |
|------|-------------------|-------------|
| Sélection catégories (26 touches) | **Conforme** | Même carte position → touche AZERTY legacy/réception/caisse |
| Saisie numérique (chiffres, décimale, effacer) | **Partielle** | Même **mapping AZERTY chiffres** (`&`→1 … `à`→0) ; **contexte** différent (micro-phases vs pavé global legacy) |
| Navigation entre étapes saisie | **Écart P1** | Legacy : **Tab** custom entre onglets wizard ; Peintre : micro-rail browse → poids → prix |
| Finaliser depuis la grille | **Conforme (intention)** | Legacy : **Enter** sur étape catégorie si lignes ; Peintre : **Enter** ouvre modale finalisation (hors champs texte) |
| Écran paiement — chaîne Enter | **Partielle** | Boucle paiements multiples **sans souris** portée ; **Total → Enter** : legacy **conditionné** au mode `no_item_pricing` ; parcours kiosk standard = total lecture seule + focus moyen (**aligné Peintre**) |
| Écran paiement — moyens de paiement | **Écart P1** | Legacy : **Flèches haut/bas** + Enter sur `<select>` ; Peintre : `<select>` natif, pas de handler flèches custom |

### A — Sélection catégories / sous-catégories

| Touche / geste | Legacy 1.4.4 | Peintre v2 | Conforme ? |
|---------------|--------------|------------|------------|
| **A–P, Q–M, W–N** (26 positions) | `cashKeyboardShortcutHandler` — ordre d’affichage des catégories | `CategoryHierarchyPicker` — `KIOSK_CATEGORY_POSITION_KEYS` (commentaire code : *« Même ordre position → touche que le legacy caisse »*) | **Oui** |
| Touche si `shortcut_key` en BDD | Non prioritaire (position seule) | **Priorité** `category.shortcut_key` puis position | **Oui** (extension) |
| Désactivation si focus input | `shouldPreventShortcut` | Grille + listener document : ignore INPUT/TEXTAREA/SELECT | **Oui** |
| Drill sous-catégories | Onglet / étape `subcategory` dans `SaleWizard` | Drill `kiosk_drill` (`setParentId`) ; **Escape/Backspace** remonte d’un niveau | **Partiel** (même intention, touches différentes de Tab legacy) |
| Badges raccourci visibles | `ShortcutBadge` sur boutons | `kioskCategoryShortcut` / badge clé | **Oui** |

**Fichiers :** `recyclique-1.4.4/frontend/src/utils/cashKeyboardShortcuts.ts` · `peintre-nano/src/widgets/category-hierarchy-picker/CategoryHierarchyPicker.tsx`

### B — Saisie quantité / poids / prix (gestes répétés)

| Touche / geste | Legacy 1.4.4 (`Sale.tsx` + `Numpad`) | Peintre v2 (`CashflowNominalWizard` + `KioskNumericPad`) | Conforme ? |
|---------------|--------------------------------------|----------------------------------------------------------|------------|
| **0–9** (ligne chiffres + pavé num.) | Handler document global si hors input ; alimente `numpadMode` quantity/price/weight | `decodeKioskNumericKeyboardKey` — phases **weight** / **price** uniquement | **Partiel** |
| **& é " ' ( - è _ ç à** → 1–0 | `AZERTY_NUMERIC_MAP` (identique réception) | `KIOSK_AZERTY_TOP_ROW_DIGIT_BY_KEY` | **Oui** (dans les phases actives) |
| **.** ou **,** décimale | `handleNumpadDecimal` | `isKioskDecimalSeparatorKey` / append `.` | **Oui** (poids/prix) |
| **Backspace** | Efface un caractère | Efface ; si vide → **étape précédente** (`onStepBack`) | **Partiel** (comportement enrichi Peintre) |
| **Escape** | Efface tout (`handleNumpadClear`) | Retour étape ou clear selon contexte | **Partiel** |
| **Enter** | Valide l’étape courante via pavé / wizard | Valide micro-phase (`onValidate`) | **Oui** (intention) |
| **Tab** | `SaleWizard.tsx` — cycle focus **dans l’onglet** actif (category → subcategory → …) | **Tab** : recule/avance micro-phase ; en **browse** avec lignes → focus finalisation | **Non** — modèle navigation différent |
| **Enter** (grille, lignes présentes) | Finalise vente depuis étape **category** | Ouvre modale finalisation (`KioskFinalizeSaleDock`) | **Oui** (intention) |
| **=** en mode poids | Simule **+** multi-pesée (`MultipleWeightEntry`) | **Absent** (pas d’équivalent kiosk) | **Non** — **P1** si multi-pesée métier encore utilisée |
| Pavé visuel colonne gauche | `Numpad.tsx` toujours (sauf `numpadMode=idle`) | `KioskNumericPad` intégré (boutons à l’écran) | **Partiel** (layout 3 colonnes legacy vs rail Peintre) |

**Fichiers :** `recyclique-1.4.4/frontend/src/pages/CashRegister/Sale.tsx` (L470–574) · `SaleWizard.tsx` (Tab L757+) · `peintre-nano/src/domains/cashflow/CashflowNominalWizard.tsx` (`KioskNumericPad`, L1120–1147, `LinesStep`)

### C — Écran paiement / finalisation (`FinalizationScreen` legacy → `KioskFinalizeSaleDock`)

Spec cible legacy : **B49-P5** (chaîne simple) + **B52-P1** (paiements multiples **sans souris**).

| Étape / touche | Legacy `FinalizationScreen.tsx` | Peintre `KioskFinalizeSaleDock.tsx` | Conforme ? |
|----------------|------------------------------|-------------------------------------|------------|
| Ouverture | Modale depuis ticket | Modale `cashflow-kiosk-finalize-modal` ; **Enter** hors champs sur layout kiosque | **Oui** |
| **Total à payer** + **Enter** | Champ **éditable** → focus moyen paiement *(mode legacy `no_item_pricing` uniquement)* | Total **lecture seule** (`cashflow-finalize-amount-due`) ; focus auto **moyen paiement** à l’ouverture *(parcours kiosk standard)* | **Partiel** — écart **P1** seulement si PO exige parité mode `no_item_pricing` ; kiosk standard **aligné Peintre** |
| **Moyen paiement** + **Enter** | → focus montant reçu | → montant reçu (ou don si gratuit) | **Oui** |
| **Flèches haut/bas** sur select | Change sélection **sans** quitter le focus (pending) | Comportement **natif** navigateur uniquement | **Non** — **P1** si caissiers utilisaient le cycle custom |
| **Montant reçu** + **Enter** | → focus **Don** | → focus **Don** | **Oui** |
| **Don** + **Enter** (paiement unique) | Valide vente | Valide si `canConfirmPayment` | **Oui** |
| **Don** + **Enter** (reste dû, 1er paiement) | Ajoute 1er paiement puis boucle | `addPaymentLine()` puis focus boucle | **Oui** (spec B52) |
| Boucle : moyen → Enter → montant → Enter | Ajoute paiement ; **sans** clic « + Ajouter » | Idem ; `loopPaymentSelectRef` / `loopPaymentInputRef` | **Oui** |
| **Escape** | Annule modale | `closeFinalizeModal` | **Oui** |
| Indicateurs visuels (💡 « Appuyez sur Enter… ») | Présents (B52) | Textes statut / balance ; **pas** les mêmes libellés indicatifs | **Partiel** (P2 UX) |
| Saisie chiffres dans champs montant | Clavier standard | `decodeFinalizeNumericKeyboardKey` + backspace dans champs | **Oui** (extension) |

**Preuve automatisée Peintre :** `peintre-nano/tests/unit/kiosk-finalize-sale-enter-shortcut.test.tsx` (chaîne Enter, paiements multiples, gratuit).

**Fichiers :** `recyclique-1.4.4/frontend/src/components/business/FinalizationScreen.tsx` · `recyclique-1.4.4/docs/front-end-specs/spec-b52-p1-keyboard-workflow-paiements-multiples.md` · `peintre-nano/src/domains/cashflow/KioskFinalizeSaleDock.tsx`

### D — Tableau écarts clavier (priorisation terrain)

| ID | Écart | Sévérité | Owner | Recommandation |
|----|-------|----------|-------|----------------|
| **CLAV-01** | Navigation **Tab** wizard legacy vs micro-phases Peintre | **P1** | Story 13.8 / PO | C2b : valider avec 2–3 caissiers ; **Dérogation PO** ou raccourcis documentés |
| **CLAV-02** | **Multi-pesée** (`=` → `+`) absente en kiosk Peintre | **P1** | PO métier | Confirmer usage réel ; reporter ou porter si encore critique |
| **CLAV-03** | Paiement : **Total éditable + Enter** en tête de chaîne *(legacy `no_item_pricing` seulement ; kiosk standard = lecture seule + focus moyen, aligné Peintre)* | **P2** | 13.8 / PO | **Dérogation PO** si parcours kiosk nominal suffit ; sinon documenter mode legacy hors scope v2 |
| **CLAV-04** | Paiement : pas de **flèches haut/bas** custom sur moyen | **P1** | 13.8 | Porter handlers legacy ou valider select natif en HITL |
| **CLAV-05** | Pavé global legacy vs `KioskNumericPad` par phase | **P2** | 13.8 | Écart structurel accepté si CLAV-01 tranché |
| **CLAV-06** | Libellés d’aide Enter (B52) moins explicites | **P2** | UX | Cosmétique — non bloquant exploitation |

**Impact Agent B :** aucun — écarts clavier = **plancher UX caisse** (stories 13.7–13.8), pas liaison Paheko.

### E — Parcours C2b suggérés (validation clavier Strophe)

1. **Vente rapide** : 3 catégories au clavier (touches A/Z/E…) → poids/prix au pavé → **Enter** finaliser → paiement espèces unique **Enter** jusqu’à validation.  
2. **Paiement mixte** : total couvert en 2 moyens (spec B52) **sans souris**.  
3. **Sous-catégorie** : drill + **Escape** retour + nouvelle sélection touche.  
4. **Régression** : comparer temps/perception vs `localhost:4445` (legacy) et `localhost:4444` (Peintre) sur les 4 scénarios.

---

## Section — Réception (synthèse)

| Élément | Legacy | Peintre | Statut |
|---------|--------|---------|--------|
| Ticket nominal | `TicketForm.tsx` | `ReceptionNominalWizard.tsx` | Parité intention + clavier |
| Grille AZERTY 26 catégories | `receptionKeyboardShortcuts.ts` | `CategoryHierarchyPicker` | **OK** |
| Poids / destination | Handlers TicketForm | `reception-poids-keyboard.ts` | **OK** |
| Dashboard terrain | `/reception/dashboard` | Admin supervision CREOS | Écart URL / rôle |
| Saisie différée | Admin modal date | Non trouvé domaine reception | Gap P2 |

---

## Impact Agent B (liaison Paheko clôture v1)

**Contexte plan :** Agent B avance sous **dérogation EC** (brief 02 fil E) ; DS conditionné à section fermeture caisse présente ou GO Coordinateur.

| # | Écart | Bloquant pour B ? | Action attendue |
|---|-------|-------------------|-----------------|
| 1 | **D33 (±2 €) vs terrain (0,05 €)** | **Oui** — AC « alerte si dépassement ±2 € » ne peut pas être codés sans décision PO | Coordinateur tranche : (a) implémenter D33 terrain + compta, (b) garder 0,05 € terrain et D33 seulement côté Paheko post-validation, (c) dérogation PO documentée en story B |
| 2 | **T3 absent du batch** | **Oui** — procédure D29 incomplète | Agent B : kind T3 + mapping 658/758 dans story ; dépend snapshot 22.6 |
| 3 | **MVP sans module D5** | Non (plan tranché) | Saisie manuelle écart admin — documenter dans AC |
| 4 | **PIN legacy vs API** | Non pour story B (déjà dérogation 13.3) | Ne pas retirer step-up v2 pour « parité » legacy |
| 5 | **Pas d’UI sync Paheko** | Non v1 | Hors AC opérateur ; outbox côté admin si prévu epic 22 |
| 6 | **Réception différée absente Peintre** | Non liaison caisse v1 | Signaler Coordinateur si stats Paheko croisent réception différée |

**Alerte C-sync (plan post-9.6) :** les écarts **#1** et **#2** sont classés **bloquants** pour figer les critères d’acceptation « fermeture → écritures Paheko ». Agent B peut poursuivre **explore + create-story** ; **DS** (`bmad-dev-story`) doit attendre GO Coordinateur ou section fermeture validée C2b, avec copie explicite de la tranche PO sur D33 dans la story.

**Horodatage alerte :** 2026-05-27 — émetteur Agent A.

---

## Références fichiers (index rapide)

**Legacy**  
- `recyclique-1.4.4/frontend/src/pages/CashRegister/CloseSession.tsx`  
- `recyclique-1.4.4/frontend/src/pages/CashRegister/Sale.tsx`  
- `recyclique-1.4.4/frontend/src/components/business/SaleWizard.tsx`  
- `recyclique-1.4.4/frontend/src/components/business/FinalizationScreen.tsx`  
- `recyclique-1.4.4/frontend/src/utils/cashKeyboardShortcuts.ts`  
- `recyclique-1.4.4/docs/front-end-specs/spec-b52-p1-keyboard-workflow-paiements-multiples.md`  
- `recyclique-1.4.4/frontend/src/pages/Reception/TicketForm.tsx`  
- `recyclique-1.4.4/frontend/src/utils/receptionKeyboardShortcuts.ts`

**Peintre**  
- `peintre-nano/src/domains/cashflow/CaisseSessionCloseSurface.tsx`  
- `peintre-nano/src/domains/cashflow/CashflowCloseWizard.tsx`  
- `peintre-nano/src/domains/cashflow/CashflowNominalWizard.tsx`  
- `peintre-nano/src/domains/cashflow/KioskFinalizeSaleDock.tsx`  
- `peintre-nano/src/widgets/category-hierarchy-picker/CategoryHierarchyPicker.tsx`  
- `peintre-nano/tests/unit/kiosk-finalize-sale-enter-shortcut.test.tsx`  
- `peintre-nano/src/domains/cashflow/CaisseBrownfieldDashboardWidget.tsx`  
- `peintre-nano/src/domains/reception/ReceptionNominalWizard.tsx`  
- `peintre-nano/src/api/cash-session-client.ts`

**API / compta**  
- `recyclique/api/src/recyclic_api/services/cash_session_service.py` (L25, L835)  
- `recyclique/api/src/recyclic_api/services/paheko_close_batch_builder.py`  
- `references/migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md` (D29, D33)  
- `references/migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md`

**CREOS**  
- `contracts/creos/manifests/page-cashflow-nominal.json`  
- `contracts/creos/manifests/page-cashflow-close.json`  
- `contracts/creos/manifests/page-reception-nominal.json`

---

## Prochaines étapes (hors Agent A)

| Étape | Responsable |
|-------|-------------|
| Gate QA2 itération 1 | Atteinte — [`2026-05-27_01_qa2-rapport-parite-plancher-v2-gestes-terrain.md`](2026-05-27_01_qa2-rapport-parite-plancher-v2-gestes-terrain.md) (gate ≥ 95 %, P0 qualité document = 0) |
| Re-QA2 boucle itération 2 | Si correctifs post-…01 sur périmètre élargi |
| C2b HITL Strophe — validation matrice gestes + **4 scénarios clavier** § Workflows clavier | Coordinateur + Strophe |
| Tranche D33 + T3 pour Agent B | Coordinateur (C-sync) |
| C3 sync `ou-on-en-est.md`, brief 02 | Coordinateur après C2b |

---

## Validation humaine (C2b)

| Champ | Valeur |
|-------|--------|
| Statut | **En attente** — hors chat Agent A |
| Signataire | Strophe |
| Date | — |
| Parcours validés | — |
| Commentaire | Section réservée au sign-off HITL (3–5 parcours critiques, 30–60 min). |
