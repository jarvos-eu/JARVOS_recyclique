# Révisions terrain — Réception

**Périmètre :** Peintre v2 — hub `/reception`, `ReceptionNominalWizard`, poste + ticket  
**Dernière passe HITL :** 2026-06-07

**Docs liés :** [checklist parité BC-03](../../artefacts/2026-05-30_01_checklist-chantier-parite-v2-beta-1.4.4.md) (historique widget non monté) · [registre Epic 7](../../artefacts/2026-04-09_01_reception-v2-exploitabilite-terrain-epic7-squelette.md)

**Legacy référence :** `recyclique-1.4.4/frontend/src/pages/Reception.tsx` (hub + liste tickets) · `TicketForm.tsx` (`react-resizable-panels`, raccourcis poids)

---

## Synthèse (2026-06-07, post-28.3)

**Hub** : liste paginée tickets via `ReceptionHistoryPanel` monté sur hub inactif (story **28.3**, [REV-RECEPTION-01](#rev-reception-01--hub-sans-historique-tickets)). **Sortie PWA hub (28-2)** : CTA « Retour au menu » sans poste ouvert ([REV-RECEPTION-02](#rev-reception-02--pwa-sans-retour-menu)). **Cockpit** : grille 3 colonnes redimensionnable + persistance `reception-cockpit-layout-v1` ([REV-RECEPTION-03](#rev-reception-03--layout-non-redimensionnable)) ; hint sortie de stock au-dessus des catégories ([REV-RECEPTION-06](#rev-reception-06--raccourcis-sortie-de-stock)). **Clôture ticket** : cockpit démonté, bandeau résumé + CTA « Créer le ticket » ([REV-RECEPTION-05](#rev-reception-05--clôture-ticket-état-confus)). **HITL restant** : retest terrain hub liste après fermeture poste, confort resize ~1280px, découverte sortie stock, enchaînement nouveau ticket post-clôture ; badges clavier ([REV-RECEPTION-04](#rev-reception-04--badges-clavier-trop-lourds)) non traités.

---

## Tableau de bord


| ID                                                   | Titre                            | Type(s)               | P   | Investigé | Corrigé | HITL |
| ---------------------------------------------------- | -------------------------------- | --------------------- | --- | --------- | ------- | ---- |
| [01](#rev-reception-01--hub-sans-historique-tickets) | Hub sans historique tickets      | parité-legacy · UI/UX | P1  | [x]       | [x]     | [ ]  |
| [02](#rev-reception-02--pwa-sans-retour-menu)        | PWA sans retour menu             | UI/UX · métier        | P0  | [x]       | [x]     | [ ]  |
| [03](#rev-reception-03--layout-non-redimensionnable) | Layout non redimensionnable      | UI/UX · parité-legacy | P1  | [x]       | [x]     | [ ]  |
| [04](#rev-reception-04--badges-clavier-trop-lourds)  | Badges « Clavier : » trop lourds | UI/UX                 | P2  | [ ]       | [ ]     | [ ]  |
| [05](#rev-reception-05--clôture-ticket-état-confus)  | Clôture ticket — état confus     | UI/UX · métier        | P1  | [x]       | [x]     | [ ]  |
| [06](#rev-reception-06--raccourcis-sortie-de-stock)  | Raccourcis sortie de stock       | parité-legacy · UI/UX | P2  | [x]       | [x]     | [ ]  |
| [07](#rev-reception-07--dashboard-terrain-absent)    | Dashboard terrain absent         | parité-legacy · cadrage-produit | P2  | [ ]       | [ ]     | [ ]  |
| [08](#rev-reception-08--saisie-différée-absente)   | Saisie différée absente          | parité-legacy · métier | P2  | [ ]       | [ ]     | [ ]  |


---

## D1 — Hub réception (avant ouverture poste)

### REV-RECEPTION-01 — Hub sans historique tickets


|              |                       |
| ------------ | --------------------- |
| **Types**    | parité-legacy · UI/UX |
| **Priorité** | P1                    |
| **Signalé**  | 2026-06-07            |


**Suivi**

- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Page `/reception` : bandeau vert « Ouvrir le poste », bandeau live KPI (OK), puis encart **« Ouvrez poste puis ticket »** et **page blanche** en dessous. Après **Fermer le poste** : même écran (ouvrir le poste + rien d'autre).

**Attendu / legacy**  
`Reception.tsx` : **liste paginée** des tickets récents (colonnes : ID, ouvert le, fermé le, bénévole, articles, poids, statut) — `ReceptionTicketList.tsx`.

**État v2 (post-28.3)**  
Slot CREOS `history` (widget `reception-history-panel`) monté sur `/reception` ; liste paginée API visible **hub inactif uniquement** (`posteOpened === false`). Masquée en cockpit ; réapparaît après fermeture poste (pagination réinitialisée page 1).

**Piste technique**  
~~Manifest CREOS : ajouter slot `history` → `reception-history-panel`~~ **livré 28.3**.

**Notes agent**  
Story **28.3** (2026-06-07) : slot CREOS `history` + garde `posteOpened` dans `ReceptionHistoryPanel` — liste visible hub inactif uniquement ; reset page/selection au retour hub. HITL restant : retest terrain liste après fermeture poste.

---

### REV-RECEPTION-02 — PWA sans retour menu


|              |                |
| ------------ | -------------- |
| **Types**    | UI/UX · métier |
| **Priorité** | P0             |
| **Signalé**  | 2026-06-07     |


**Suivi**

- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Dans la **web app installée** (barre Windows, hors navigateur) : **aucun bouton retour** ; si on n'ouvre pas le poste, **coincé** sur la page réception — impossible d'aller au tableau de bord ou ailleurs.

**Attendu / legacy**  
Barre de navigation globale toujours visible (Header : Tableau de bord, Caisse, Réception…).

**État v2**  
`RuntimeDemoApp` : `hideShellNav` sur `/reception` (`isReceptionNominalCertificationPathRoute`) — bandeau nav **masqué** en mode certification kiosque.

**Correction story 28-2**  
- `ReceptionNominalWizard.tsx` : CTA **Retour au menu** (`data-testid="reception-return-to-menu"`) visible sur hub **sans poste ouvert** (`posteId === null`) ; navigation `spaNavigateTo('/dashboard')`.
- CTA **masqué** dès qu'un poste est ouvert — mode certification kiosque inchangé (`hideShellNav` global conservé).

**État post-28-2**  
- Hub `/reception` sans poste ouvert : sortie vers `/dashboard` sans fermer la PWA.
- Poste ouvert : pas de CTA retour (kiosque certification inchangé).
- **HITL restant** : retest PWA installée Windows — hub inactif → menu ; poste ouvert → pas de régression.

**Impact**  
Était bloquant en PWA terrain sans chrome navigateur (contournement : fermer / rouvrir l'app). **Corrigé code 28-2** ; validation terrain en attente.

**Piste technique**  
~~Bouton Retour au menu sur hub inactif~~ **livré 28-2**. Reste : polish chrome PWA ([REV-TRANSVERSE-02](transverse.md#rev-transverse-02--barre-de-titre-pwa-bleue), [REV-TRANSVERSE-03](transverse.md#rev-transverse-03--plier-barre-de-titre-pwa)).

**Notes agent**  
Story 28.2 (done 2026-06-07) — `ReceptionNominalWizard.tsx` (CTA `reception-return-to-menu`). Tests `*28-2*` : `reception-return-to-menu-28-2`, `reception-pwa-exit-28-2.e2e`.

---

## D2 — Cockpit poste ouvert (layout & clavier)

### REV-RECEPTION-03 — Layout non redimensionnable


|              |                       |
| ------------ | --------------------- |
| **Types**    | UI/UX · parité-legacy |
| **Priorité** | P1                    |
| **Signalé**  | 2026-06-07            |


**Suivi**

- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Catégories à **gauche écrasées** ; impossible de **redimensionner** les colonnes ; rendu global « horrible ».

**Attendu / legacy**  
`TicketForm.tsx` : **3 colonnes** avec `react-resizable-panels` (`PanelResizeHandle`), préférences layout persistées (`LAYOUT_STORAGE_KEY`).

**État v2 (post-28.3)**  
Grille CSS 3 colonnes + poignées drag (`reception-cockpit-resize-left` / `-right`) ; ratios persistés `reception-cockpit-layout-v1` (localStorage). **Sans** `react-resizable-panels`.

**Piste technique**  
~~Réintroduire panneaux redimensionnables~~ **livré 28.3** (grille CSS + drag). Polish confort desktop reste HITL.

**Notes agent**  
Story **28.3** : grille CSS 3 colonnes + poignées drag (`reception-cockpit-layout-v1` localStorage) — **sans** `react-resizable-panels`. HITL : confort resize desktop ~1280px.

---

### REV-RECEPTION-04 — Badges « Clavier : » trop lourds


|              |            |
| ------------ | ---------- |
| **Types**    | UI/UX      |
| **Priorité** | P2         |
| **Signalé**  | 2026-06-07 |


**Suivi**

- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Sur chaque tuile catégorie : libellé vert **« Clavier : X »** — trop gros, trop long, gêne la lisibilité.

**Attendu / legacy**  
Raccourcis présents (aria / touche seule) mais affichage plus **discret** sur les tuiles.

**État v2**  
`CategoryHierarchyPicker.tsx` — `.kioskCategoryShortcutBadge` / `.categoryTileShortcutBadge` (« Clavier : » / « Touche »).

**Piste technique**  
Réduire badge à une lettre en coin de tuile ; garder raccourcis clavier fonctionnels.

**Notes agent**  
—

---

### REV-RECEPTION-06 — Raccourcis sortie de stock


|              |                       |
| ------------ | --------------------- |
| **Types**    | parité-legacy · UI/UX |
| **Priorité** | P2                    |
| **Signalé**  | 2026-06-07            |


**Suivi**

- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
En saisie poids : **Flèche bas** change destination (recyclage / déchetterie / magasin) — OK. En remontant au début du parcours, **manque** la visibilité / raccourcis pour **sortie de stock** comme au legacy.

**Attendu / legacy**  
Toggle « Sortie de boutique » + raccourci `**=`** dans le champ poids (`TicketForm.tsx` B48-P3).

**État v2 (post-28.3)**  
Raccourci `=` inchangé ; switch `reception-switch-is-exit` au centre ; hint `reception-exit-stock-hint` au-dessus de la grille catégories. Écart résiduel : **découverte terrain** début de parcours (HITL).

**Notes agent**  
Story **28.3** : hint `reception-exit-stock-hint` au-dessus grille catégories ; raccourci `=` inchangé (test 7.5 / 28-3). HITL : découverte terrain début de parcours.

---

## D3 — Cycle ticket / poste

### REV-RECEPTION-05 — Clôture ticket — état confus


|              |                |
| ------------ | -------------- |
| **Types**    | UI/UX · métier |
| **Priorité** | P1             |
| **Signalé**  | 2026-06-07     |


**Suivi**

- [x] Investigé
- [x] Corrigé
- [ ] Validé HITL

**Observation**  
Clic **« Clôturer le ticket »** : le ticket **reste visible** à l'écran (lignes affichées) ; le header propose alors **« Fermer le poste »**. Pas clair si le ticket est vraiment clôturé ; pas de proposition **nouveau ticket** comme sur le hub legacy.

**Attendu / legacy**  
Après clôture : retour hub ou vue lecture seule `/reception/ticket/{id}/view` ; hub permet **nouveau ticket** + **liste** des sessions.

**État v2 (post-28.3)**  
Après close API OK : `ticketId` null, cockpit démonté, bandeau `reception-ticket-closed-summary`, CTA « Créer le ticket » ; poste reste ouvert.

**Piste technique**  
~~Après clôture : vider cockpit, proposer « Nouveau ticket »~~ **livré 28.3**. Reste HITL : enchaînement nouveau ticket terrain.

**Notes agent**  
Story **28.3** : après close API OK → `ticketId` null, cockpit démonté, bandeau `reception-ticket-closed-summary`, CTA « Créer le ticket » ; poste reste ouvert. HITL : enchaînement nouveau ticket terrain.

---

## D4 — Import audit (pas revue live Strophe)

*Source rapport parité — écarts non testés le 2026-06-07.*

### REV-RECEPTION-07 — Dashboard terrain absent

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
Legacy : `/reception/dashboard` (terrain). Peintre : supervision admin CREOS — **pas même URL / rôle**.

**Piste**  
Epic 19.x ; hors scope parité nominal si pilotage = admin. Distinct de REV-RECEPTION-01 (liste tickets hub).

**Notes agent**  
—

---

### REV-RECEPTION-08 — Saisie différée absente

| | |
|---|---|
| **Types** | parité-legacy · métier |
| **Priorité** | P2 |
| **Signalé** | 2026-05-27 (rapport parité) |

**Suivi**
- [ ] Investigé
- [ ] Corrigé
- [ ] Validé HITL

**Observation**  
Legacy : modal **date admin** pour saisie différée (`Reception.tsx`). Peintre : **non trouvé** dans `domains/reception/`.

**Piste**  
Décision PO — hors scope v2.0 plancher sauf besoin stats Paheko.

**Notes agent**  
—

---

## Pistes techniques transverses

1. ~~Monter `ReceptionHistoryPanel` sur hub (BC-03)~~ **fait 28.3** ([REV-RECEPTION-01](#rev-reception-01--hub-sans-historique-tickets)).
2. ~~Nav PWA : bouton retour sur hub inactif~~ **fait 28-2** ([REV-RECEPTION-02](#rev-reception-02--pwa-sans-retour-menu)).
3. ~~Layout : `react-resizable-panels` ou équivalent Peintre~~ **fait 28.3** (grille CSS + drag, sans `react-resizable-panels`).
4. Parité clavier : audit complet vs `TicketForm.tsx` + rapport parité § clavier B52/CLAV.

