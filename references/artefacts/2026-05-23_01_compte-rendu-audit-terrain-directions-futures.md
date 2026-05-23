# Compte rendu canonique — audit terrain ressourcerie et directions produit

**Date du document :** 2026-05-23  
**Statut :** synthèse **exhaustive de second niveau** — agrège et cadrre le corpus déjà traité ; ne remplace pas les sources normatives ligne par ligne.  
**Périmètre terrain couvert par le corpus indexé :** 18–21 mai 2026 (**six** enregistrements), pipeline **transcription-pipeline-v1.1**, template **brainstorming-organique**, révision éditoriale et régénération des finaux (2026-05-21).

---

## 1. Objet et périmètre

Ce document constitue le **compte rendu structurant** de l’audit terrain oral : il relie les idées captées à la **vision projet**, aux **modules** cibles (Réception, Liaison Paheko / caisse, paramétrage), au **pilotage BMAD** et aux **dépendances** entre idées. Il sert de **porte d’entrée unique** pour toute personne (humain ou agent) qui doit comprendre **où va le produit** après le terrain, sans relire immédiatement les six transcripts complets.

**Sources primaires (ordre de vérité décroissant pour le détail idée par idée) :**

1. Fichiers sous **`.transcription/meetings/<MEETING_ID>/`** (`working/draft/*.md`, `final/<MEETING_ID>.md`) — **non versionnés** ; présents sur la machine locale où le pipeline a tourné.
2. [2026-05-21_02_recap-idees-paheko-reception-terrain.md](2026-05-21_02_recap-idees-paheko-reception-terrain.md) — recap **REC-*** / **PKO-*** avec statuts, dépendances, questions ouvertes, graphe mermaid, mapping IDEA → meetings.
3. [2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) — **D1–D38** et rejets explicites (orientation métier post-recherche).
4. Documents satellite : [guide liaison Paheko](../migration-paheko/2026-05-21_guide-liaison-paheko-compta.md), [procédure de clôture](../migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md), brainstorm BMAD Réception ([`_bmad-output/brainstorming/brainstorming-session-2026-05-21-180000.md`](../../_bmad-output/brainstorming/brainstorming-session-2026-05-21-180000.md)), consolidation Paheko ([`brainstorming-session-2026-05-21-paheko-compta-validation.md`](../../_bmad-output/brainstorming/brainstorming-session-2026-05-21-paheko-compta-validation.md)).

**Hors périmètre de ce compte rendu :** détail d’implémentation API, code `recyclique/`, et idées **Peintre agentique seul** (explicitement hors recap terrain sauf mentions transverses).

---

## 2. Synthèse exécutive — directions futures

| Axes | Direction | Justification courte |
|------|-----------|----------------------|
| **Priorité chantier (D1)** | **Liaison Paheko** (fermeture caisse → écritures) **avant** de « finir » la réception au sens large | Décision porteur ; alignée [décisions compta](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) |
| **Double vérité métier (PKO-000)** | **Matière / traçabilité objet** côté RecyClique ; **€ réels** côté Paheko | Cadre toutes les règles tickets, dons -18, mixité |
| **Réception v1 (brainstorm BMAD)** | Parcours **REC-001, 002, 004, 008, 012** en atelier prioritaire ; **REC-016** omnicanal → **parking v2** | Session 2026-05-21 clôturée ; omnicanal = intuition à trancher |
| **Validation externe** | Points **EC** (expert-comptable) avant figement BMAD sur **PKO-016b**, **PKO-013**, structure **754.x**, traces sorties -18 | Plusieurs lignes du recap + décisions D12–D14 |
| **Gate produit liaison** | Brainstorm **UX fermeture caisse** **après** validation comptable (Corinne + Caro) | [`ou-on-en-est.md`](../ou-on-en-est.md) — éviter dev sur sable |
| **Modules / ADR** | Protocole **modules v2** déjà bouclé côté doc (P0) ; la suite exécution = stories **Epic 9** etc., pas reprise du débat modularité ici | [protocole-modules-recyclique/index.md](../protocole-modules-recyclique/index.md) |
| **Vision flux objets** | Document **2026-05-22** + QA2 gate 95 % : langage métier **PKO-000**, chaîne réception → caisse, rôle super admin | [vision-projet/2026-05-22_vision-flux-objets-reception-etiquettes-webcam-superadmin.md](../vision-projet/2026-05-22_vision-flux-objets-reception-etiquettes-webcam-superadmin.md), [2026-05-22_01_qa2-loop-vision-flux-objets-gate95.md](2026-05-22_01_qa2-loop-vision-flux-objets-gate95.md) |

---

## 3. Cartographie idées → modules → documents projet

### 3.1 Module Réception (granularité REC-*)

Le recap liste **REC-001 à REC-016** (et dépendances). Rôles diarisés **A/B/C/D** restent **hypothèses** jusqu’à renommage dans `transcription-profile.json` (voir recap §1).

**Idées structurantes :**

- **REC-001** — Poste idéal pesée → étiquette → caisse : **épine dorsale** ; conditionne matériel, webcams, bascule, impression codes-barres / QR.
- **REC-002** — Workflow objet générique entrée → vente/recyclage : **priorité narrative terrain** (« flux d’entrée d’abord »).
- **REC-008** — Moteur de workflows par famille : **cœur configurateur** ; maturité **intuition à affiner** (réserve QA, ton « idéal cible »).
- **REC-004** — Étiquette tôt vs tard : **ouvert** ; arbitrage par famille (lien REC-008).
- **REC-012** — Pas de vente par lot : **specification** (impact ticket = lignes unitaires).
- **REC-009** — Besoins / alertes / SMS / file : **fil rouge** multi-sources (1246, 1401, Paheko IDEA-020) ; questions RGPD et unification parcours.
- **REC-016** — Omnicanal : ajout **post-QA2** ; **parking v2** pour ne pas diluer v1.

**Alignement vision / BMAD :** la vision **flux objets / étiquettes / webcam** (2026-05-22) **s’appuie** sur PKO-000 et sur la chaîne **REC-001 → caisse** ; le brainstorm Réception v1 a **borné** le périmètre v1 (omnicanal exclu du scope immédiat).

### 3.2 Module Liaison Paheko / caisse (granularité PKO-*)

**Chaîne cible** : PKO-001 fermeture → ventilation Paheko, s’appuyant sur PKO-003 (530/511/512), PKO-004 (comptage), PKO-002 (dons chèque vs espèces), PKO-011 (754.x), PKO-025 (paramétrage plan par asso).

**Points de tension documentés (non résolus sans EC) :**

- **PKO-016 / PKO-016b** — Ligne ticket don -18 vs **trace comptable** kg / don (séparation IDEA-004 / 005 après révision).
- **PKO-013** — 471 vs 53 vs 58 : **piste séance**, validation EC requise.
- **PKO-015** — UX défaut « don » : friction confirmée ; **hors priorité** brainstorm explicite (D15) mais reste dette UX.

**Décisions D1–D38** du fichier migration **surclassent** les intuitions orales **lorsqu’elles sont en conflit** : ce fichier est la **couche décision** après recherche Perplexity + terrain.

### 3.3 Chantiers adjacents (hors module central mais liés)

- **PKO-023** — Notes de frais bénévoles (chantier **adjacent** liaison Paheko).
- **REC-011** — Déclarations éco-organismes : recherche / long terme ; lien gravats REC-010.
- **PKO-018** — Cockpit import banque, alertes prélèvements.

---

## 4. Graphe de dépendances (lecture opérationnelle)

Le **graphe mermaid** et la liste des arêtes **PKO-000 → REC/PKO** figurent dans le recap §5. En résumé conceptuel :

1. **Fondation** : PKO-000 (double compta) + REC-012 (pas de lot commercial) + PKO-025 (param plan).
2. **Réception** : REC-008 alimente REC-002 ; REC-004 conditionne REC-001 ; REC-001 active la majorité des patterns UX (005, 006, 007, 009, 016) et alimente la **caisse** (scan, poids).
3. **Caisse / tickets** : PKO-014 mixte → PKO-006/007 (chèque) ; PKO-016/016b raccrochent PKO-000.
4. **Paheko** : PKO-025 → PKO-003 / PKO-011 ; PKO-004 et PKO-002 convergent vers PKO-001 ; PKO-001 ouvre PKO-018 et la **vision cockpit** (PKO-005).

Toute **story BMAD** future sur la réception ou la caisse doit **declarer** quels nœuds du graphe elle touche, pour éviter les régressions (ex. changer REC-001 sans retoucher PKO-014).

---

## 5. Questions encore ouvertes (registre unique)

Les **sections 6.1 à 6.8** du recap constituent le **backlog de clarification** exhaustif (étiquetage, besoins/SMS, caisse, Paheko, clôture, fiscalité bénévoles, éco-organismes, omnicanal). **Ne pas dupliquer** ici le tableau complet : ce document **pointe** vers [recap §6](2026-05-21_02_recap-idees-paheko-reception-terrain.md#6-questions-à-trancher-et-recherches--par-sujet) comme registre **normatif des questions**.

**Règle de travail :** toute nouvelle réponse terrain (audio, atelier, mail EC) doit **mettre à jour** soit le recap (si nouvelle idée REC/PKO), soit le fichier décisions (si nouvelle règle comptable), soit les deux — puis une **ligne** dans la section 10 (journal) du recap ou équivalent daté.

---

## 6. Intégration d’un nouvel enregistrement (post–mai 2026)

Sur le dépôt, le dossier **`.transcription/`** est **gitignoré** sauf README, profil et script de file (voir [`.transcription/README.md`](../../.transcription/README.md)).

**Étapes obligatoires :**

1. Placer l’audio dans **`.transcription/inbox/`** (ou `_queue/` puis exécuter `_queue_run_pipeline.py`).
2. Définir un **`meeting_id`** stable (`YYYY-MM-DD-recyclique-terrain-…`).
3. Lancer le skill **transcription-pipeline-v1.1** (`run_pipeline.py`) avec la clé AssemblyAI.
4. Après génération des drafts : **révision éditoriale** (STT, tags, maturité) comme pour le lot mai 2026.
5. **Fusion** dans le recap : ajouter colonnes IDEA / meeting ; mettre à jour graphe §5 et questions §6 si besoin.
6. Si l’enregistrement **clôt** ou **infirme** une décision D* : mettre à jour [décisions compta](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) avec une **entrée datée** ou un nouveau fichier `YYYY-MM-DD_…`.

**Constat agent cloud (2026-05-23) :** aucun fichier audio n’était présent dans le workspace distant ; le pipeline **n’a pas pu être exécuté** ici (skill et clés sur poste local Strophe). La structure **`inbox/`** et le script **`_queue_run_pipeline.py`** ont été **alignés** pour un usage portable (variable **`TRANSCRIPTION_SKILL_ROOT`**).

---

## 7. Traçabilité vers epics BMAD et pilotage

- **État des epics** : voir [`ou-on-en-est.md`](../ou-on-en-est.md) et [`_bmad-output/planning-artifacts/guide-pilotage-v2.md`](../../_bmad-output/planning-artifacts/guide-pilotage-v2.md) pour le **grain fin** (jalons, emplacement livrables).
- **Epics 6–10** : pack de lecture [2026-04-08_02](2026-04-08_02_pack-lecture-epics-6-10-et-corpus-captures.md) et tableau [2026-04-08_03](2026-04-08_03_tableau-ultra-operationnel-epics-6-10.md) — utile pour relier **exploitabilité terrain** des modules caisse/réception déjà « done » au **nouveau** cahier des charges oral.
- **Epic 9 / modules** : seed config admin ; croiser [protocole-modules-recyclique/index.md](../protocole-modules-recyclique/index.md) pour ne pas **reinventer** les invariants CREOS / `module_key`.
- **Backlog epics** (9, 10, 12, 20, 21 au dernier état noté dans `ou-on-en-est`) : les directions terrain **priorisent** le travail **sous** ces epics (liaison Paheko, réception paramétrable) plutôt que de créer de nouveaux epics sans besoin.

---

## 8. Cohérence avec la vision long terme

| Source vision | Lien avec le terrain |
|---------------|---------------------|
| [2026-03-31_decision-directrice-v2.md](../vision-projet/2026-03-31_decision-directrice-v2.md) | Ligne brownfield : le terrain **confirme** l’incrémental (pas de big bang) ; Paheko reste **référentiel comptable**. |
| [2026-05-22_vision-flux-objets-…](../vision-projet/2026-05-22_vision-flux-objets-reception-etiquettes-webcam-superadmin.md) | Formalise en langage métier ce que REC-001/004/008 explorent oralement. |
| [2026-04-19_prd-architecture-permissions-…](../vision-projet/2026-04-19_prd-recyclique-architecture-permissions-multisite-kiosques-bmad.md) | Multisite / kiosques : **REC-016** omnicanal et **postes** multiples recoupent ce chantier (parking / v2). |
| [PRD caisse-compta Paheko](../migration-paheko/2026-04-15_prd-recyclique-caisse-compta-paheko.md) | Substrat technique des décisions D* ; terrain = **contraintes réelles** (ex. multi-caisse D24–D28). |

---

## 9. Liste de contrôle « audit clos »

- [x] Six meetings transcrits, révisés, finaux régénérés (état 2026-05-21).
- [x] Recap REC/PKO exhaustif + graphe + questions + mapping IDEA (recap 02).
- [x] Décisions compta D1–D38 + rejets explicites.
- [x] Brainstorm BMAD Réception v1 clôturé ; Paheko compta en attente validation externe.
- [x] Vision flux objets publiée + QA2 gate ≥ 95 %.
- [ ] QA2 draft/fusion **optionnel** pour meetings **1401** et **Paheko** si besoin de gate documentaire (cf. recap §9).
- [ ] Renommage **speakers** dans `transcription-profile.json` (validation terrain).
- [ ] **Nouvel** audio post-mai : suivre §6 du présent document.

---

## 10. Références croisées minimales (navigation)

| Besoin | Fichier |
|--------|---------|
| Détail chaque idée REC/PKO | [2026-05-21_02_recap…](2026-05-21_02_recap-idees-paheko-reception-terrain.md) |
| Décisions comptables après recherche | [2026-05-21_decisions-compta…](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) |
| Guide opératoire liaison | [2026-05-21_guide-liaison-paheko-compta.md](../migration-paheko/2026-05-21_guide-liaison-paheko-compta.md) |
| Procédure clôture | [2026-05-21_procedure-cloture…](../migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) |
| Brainstorm Réception | [`brainstorming-session-2026-05-21-180000.md`](../../_bmad-output/brainstorming/brainstorming-session-2026-05-21-180000.md) |
| Brainstorm / validation Paheko | [`brainstorming-session-2026-05-21-paheko-compta-validation.md`](../../_bmad-output/brainstorming/brainstorming-session-2026-05-21-paheko-compta-validation.md) |
| Inbox / pipeline | [`.transcription/README.md`](../../.transcription/README.md) · [inbox/README.md](../../.transcription/inbox/README.md) |
| Vision flux objets | [2026-05-22_vision-flux-objets…](../vision-projet/2026-05-22_vision-flux-objets-reception-etiquettes-webcam-superadmin.md) |

---

*Document produit pour clore la phase « vrac d’idées » du terrain mai 2026 dans le référentiel Git : il **oriente** et **indexe** ; le détail exhaustif des idées reste dans le recap 02 et les transcripts locaux.*
