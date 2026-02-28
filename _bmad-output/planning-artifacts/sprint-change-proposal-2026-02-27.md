# Proposition de changement de sprint — Correct Course

**Date :** 2026-02-27  
**Workflow :** correct-course (4-implementation)  
**Projet :** JARVOS_recyclique

---

## 1. Résumé du problème

**Déclencheur :** La règle « mêmes écrans, réécriture depuis le code 1.4.4, même visuel » figurait dans le PRD, la spécification UX et la section générale des epics, mais **pas dans les critères d’acceptation (AC) des stories**. Le front a donc été livré en « Mantine générique » au lieu d’une réécriture fidèle au rendu 1.4.4.

**Précision portée par le product owner :**
- En fin de refactor, **les écrans doivent être exactement les mêmes** que en 1.4.4 (même rendu, mêmes parcours).
- Le refactor ne doit **pas** être un simple copier-coller : il doit inclure une **analyse de cohérence du code** et une **analyse de sécurité** (checklist import 1.4.4 : copy + consolidate + security). Donc : même résultat visuel, mais code passé au crible cohérence/sécurité.

**Type de problème (checklist) :** Mauvaise traçabilité des exigences — règle UX v1 et méthode d’import non contractuelles au niveau des stories.

---

## 2. Analyse d’impact

### 2.1 Epics concernées

| Epic | Impact |
|------|--------|
| **Epic 1** (Socle) | Déjà livré ; les stories front (1.2–1.4) n’avaient pas l’AC « même rendu 1.4.4 ». Pas de revert demandé ; la règle s’applique aux prochaines livraisons et aux corrections éventuelles. |
| **Epic 2** | Référentiels (API/BDD) ; peu d’UI. Règle brownfield déjà dans l’epic ; ajouter l’AC standard pour toute story qui livre un écran (ex. écran caisse presets). |
| **Epic 3** | Auth, PIN, postes — beaucoup d’écrans (login, profil, démarrage poste, mode verrouillé). **Impact fort** : AC à renforcer sur « même rendu » + « analyse cohérence/sécurité ». |
| **Epic 4** | Canal push — pas d’écrans utilisateur. Impact limité à la règle générale en tête d’epic si besoin. |
| **Epic 5** | Caisse — **impact majeur** : sessions, ventes, clôture. AC explicites « même rendu 1.4.4 » + méthode d’import. |
| **Epic 6** | Réception — **impact majeur** : postes, tickets, lignes. Idem. |
| **Epic 7** | Correspondance — écrans/API admin mapping. AC à aligner. |
| **Epic 8** | Admin — **impact majeur** : tous les écrans admin (users, sites, postes, sessions, rapports, catégories, réception, santé, audit, paramètres, BDD, vie asso). |
| **Epic 9** | Données déclaratives — peu d’UI en v1. |
| **Epic 10** | Extension points — stubs ; pas de reproduction d’écrans 1.4.4. |

### 2.2 Conflits avec les artefacts

- **PRD :** Pas de conflit. À **préciser** que le refactor inclut analyse de cohérence et de sécurité (pas simple copier-coller), tout en gardant les mêmes écrans.
- **Architecture :** Pas de conflit. Déjà « Mantine (alignement 1.4.4) » ; on renforce la traçabilité vers les AC.
- **UX (ux-design-specification.md) :** Clarifier que « copy + consolidate + security » implique analyse cohérence + sécurité, pas reprise brute du code ; résultat = mêmes écrans.
- **Epics/Stories :** C’est l’artefact principal à modifier : ajout d’AC explicites dans toutes les stories qui livrent du front/UI.

### 2.3 Impact technique

- **Code existant :** Pas de rollback demandé. Les écrans déjà livrés (socle, auth, etc.) pourront faire l’objet d’un passage de conformité « même rendu 1.4.4 » + revue cohérence/sécurité lors de stories dédiées ou de la continuité des epics.
- **Backlog :** Toute nouvelle story qui livre un écran doit avoir les AC proposés ci-dessous ; les stories déjà en cours ou à venir (caisse, réception, admin) sont concernées en priorité.

---

## 3. Option retenue : Ajustement direct

- **Option 1 — Ajustement direct :** Modifier les artefacts (PRD, UX, epics/stories) pour inscrire la règle et la méthode dans les AC et les sections de référence. Aucun rollback, pas de réduction de scope MVP.
- **Effort :** Faible (rédaction + mise à jour des documents).
- **Risque :** Faible.
- **Justification :** Le besoin est clair (mêmes écrans + analyse cohérence/sécurité) ; l’équipe peut appliquer la règle dès les prochaines stories et, si besoin, traiter les écrans déjà livrés par des tâches de conformité ciblées.

---

## 4. Propositions de modifications détaillées

### 4.1 PRD (`_bmad-output/planning-artifacts/prd.md`)

**Section à modifier :** Product Scope → MVP – Minimum Viable Product (v1.0.0), phrase sur « UX v1 ».

**AVANT :**
```markdown
- **UX v1** : mêmes écrans que 1.4.4 (copy + consolidate + security), pas de refonte UX pour la v1. Référence : `_bmad-output/planning-artifacts/ux-design-specification.md`.
```

**APRÈS :**
```markdown
- **UX v1** : mêmes écrans que 1.4.4, pas de refonte UX pour la v1. Le refactor du code 1.4.4 suit la checklist d’import (copy + consolidate + security) : analyse de cohérence du code et de sécurité à chaque import, pas de simple copier-coller ; le rendu final des écrans doit être identique à 1.4.4. Référence : `_bmad-output/planning-artifacts/ux-design-specification.md`.
```

**Rationale :** Rendre explicite que « même écran » = même rendu, et que la méthode = analyse cohérence + sécurité (checklist), pas copier-coller brut.

---

### 4.2 Spécification UX (`_bmad-output/planning-artifacts/ux-design-specification.md`)

**Section à modifier :** § 1. Décision de stratégie UX (v1), paragraphe sur la méthode d’import.

**Ajout après** « Méthode d’import : à chaque pioche… copy + consolidate + security » :

```markdown
L’import n’est pas un simple copier-coller : chaque pioche fait l’objet d’une **analyse de cohérence** (alignement architecture, pas de doublon, dépendances maîtrisées) et d’une **analyse de sécurité** (pas de secret en dur, audit des fichiers, CVE des dépendances). Le **résultat** visuel reste identique aux écrans 1.4.4.
```

**Rationale :** Aligner la spec UX sur la demande produit (même rendu, méthode exigeante).

---

### 4.3 Epics (`_bmad-output/planning-artifacts/epics.md`)

#### 4.3.1 Section « Règle refactor brownfield » (décisions architecturales)

**AVANT :**
```markdown
> **Pour toute story qui touche au métier caisse, réception, auth, admin, catégories :**
> le livrable est une **migration/copie** depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md` (copy + consolidate + security).
> Ce n'est **pas** une conception from scratch.
```

**APRÈS :**
```markdown
> **Pour toute story qui touche au métier caisse, réception, auth, admin, catégories :**
> le livrable est une **migration** depuis RecyClique 1.4.4 selon `references/ancien-repo/checklist-import-1.4.4.md` (copy + consolidate + security). Ce n’est **pas** une conception from scratch ni un simple copier-coller : à chaque import, appliquer une **analyse de cohérence** du code (alignement architecture, pas de doublon) et une **analyse de sécurité** (secrets, audit fichiers, CVE dépendances). Pour toute story qui livre des **écrans** : le rendu final doit être **identique** aux écrans 1.4.4 correspondants (référence audits et artefact 10).
```

#### 4.3.2 Section « Additional Requirements » → « UX v1 »

**AVANT :**
```markdown
**UX v1 :**
- Mêmes écrans que RecyClique 1.4.4 (copy + consolidate + security) ; pas de refonte UX pour la v1.
```

**APRÈS :**
```markdown
**UX v1 :**
- Mêmes écrans que RecyClique 1.4.4 ; pas de refonte UX pour la v1. Pour toute story livrant du front : rendu identique aux écrans 1.4.4 concernés ; méthode d’import = checklist (copy + consolidate + security) avec analyse de cohérence et de sécurité, pas de simple copier-coller.
```

#### 4.3.3 AC standard à ajouter aux stories qui livrent du front/UI

Pour **toute story dont le livrable inclut des écrans ou des composants UI** (liste non exhaustive : 2.x si UI presets, 3.1–3.5, 5.1–5.3, 6.1–6.3, 7.2, 8.1–8.7, etc.), ajouter le critère d’acceptation suivant (en plus des AC existants) :

**Texte proposé (à insérer dans les AC de chaque story concernée) :**

```markdown
**Et** [pour toute story livrant des écrans] le livrable respecte le **rendu des écrans 1.4.4** correspondants (référence : audits caisse/réception, artefact 10 traçabilité écran–API) et résulte d’une **analyse de cohérence et de sécurité** du code importé selon `references/ancien-repo/checklist-import-1.4.4.md` (copy + consolidate + security) — pas de simple copier-coller.
```

**Stories explicitement concernées (à mettre à jour) :**

- **Epic 2 :** 2.4 (presets — écran caisse).
- **Epic 3 :** 3.1, 3.2, 3.3, 3.4, 3.5 (auth, groupes, PIN, postes, mode verrouillé).
- **Epic 5 :** 5.1, 5.2, 5.3 (sessions, ventes, clôture).
- **Epic 6 :** 6.1, 6.2, 6.3 (postes réception, tickets, lignes, export/stats).
- **Epic 7 :** 7.2 (interface/API admin mapping si UI).
- **Epic 8 :** 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7 (tous les écrans admin et vie asso).

Les stories **purement API/BDD** (ex. 2.1, 2.2, 2.3, 4.1, 4.2, 7.1) gardent la règle brownfield en tête d’epic sans ce bloc AC « rendu écran » (sauf si une story ajoute plus tard un écran).

---

### 4.4 Checklist import 1.4.4 (référence)

Aucune modification obligatoire. La checklist actuelle (Copy, Consolidate, Security) couvre déjà l’analyse de cohérence (consolidate) et de sécurité (security). On peut ajouter en en-tête une phrase de rappel :

**Fichier :** `references/ancien-repo/checklist-import-1.4.4.md`

**Ajout optionnel** après « À chaque pioche… » :

```markdown
L’objectif est d’obtenir le **même rendu** que 1.4.4 tout en passant le code par une **analyse de cohérence** (Consolidate) et une **analyse de sécurité** (Security) — pas de reprise brute sans contrôle.
```

---

## 5. Handoff et prochaines étapes

### 5.1 Périmètre du changement

- **Portée :** **Modérée** — mise à jour des documents de planification (PRD, UX, epics/stories) et application des nouvelles AC sur les stories à venir et, si besoin, sur les stories déjà livrées (conformité progressive).
- **Destinataires :**
  - **Équipe de développement / agent d’implémentation** : appliquer les AC mis à jour pour toute story qui livre du front ; utiliser la checklist import 1.4.4 avec analyse cohérence + sécurité ; viser le même rendu que 1.4.4.
  - **PO / SM (toi)** : valider que la proposition te convient ; pas de réorganisation majeure du backlog, seulement renforcement des AC.

### 5.2 Critères de succès

- PRD, UX et epics mis à jour avec les formulations ci-dessus.
- Pour chaque nouvelle story livrant des écrans : AC contenant la règle « même rendu 1.4.4 » + « analyse cohérence et sécurité (checklist), pas copier-coller ».
- Écrans déjà livrés : conformité traitée soit dans des stories dédiées « conformité rendu 1.4.4 + revue cohérence/sécurité », soit au fil de l’eau lors des prochaines livraisons (décision à trancher selon la vélocité).

### 5.3 Actions immédiates proposées

1. **Appliquer les modifications** des sections 4.1 à 4.3 (PRD, UX, epics) dans les fichiers concernés.
2. **Ajouter l’AC standard** (bloc « Et […] le livrable respecte le rendu… ») dans les stories listées en 4.3.3.
3. **(Optionnel)** Ajouter la phrase de rappel dans `references/ancien-repo/checklist-import-1.4.4.md` (section 4.4).
4. **Communiquer** aux agents / dev : toute story front doit désormais satisfaire « mêmes écrans 1.4.4 » + « analyse cohérence + sécurité ».

---

## 6. Validation

- [x] **Approbation de la proposition :** Oui (mode Batch, acceptation utilisateur)
- [x] **Modifications des artefacts (4.1–4.3) appliquées**
- [x] **AC des stories concernées mis à jour (4.3.3)**
- [ ] **Handoff dev/PO effectué** (à faire en continu : tout agent/dev travaillant sur une story front applique les nouveaux AC)

---

*Document généré par le workflow Correct Course (BMM 4-implementation).*
