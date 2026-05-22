# Vision fixée — flux d'objets, réception, étiquettes (code-barres / QR), webcam

**Date :** 2026-05-22  
**Statut :** document de **vision produit** figée pour alignement terrain / produit / technique (non spec d'implémentation).  
**Public cible en premier lieu :** super admin et direction d'association ; lecture possible par toute l'équipe sans jargon obligatoire.

---

## 1. Pourquoi ce document

Les transcriptions terrain (mai 2026) et le recap associé ont fait émerger beaucoup d'idées sur la **réception**, les **étiquettes**, le **poids**, les **photos** et le lien avec la **caisse** et la **compta**. Ce fichier **fixe la vision** : ce qu'on vise comme fil conducteur, ce qui est hors sujet ici, et où aller chercher le détail chiffré (idées REC-*, PKO-*).

**Sources de vérité détaillées (idées non figées) :**

- Recap idées terrain : [../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md](../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md)
- PRD multisite / kiosques / scan (cadrage technique cible) : [2026-04-19_prd-recyclique-architecture-permissions-multisite-kiosques-bmad.md](2026-04-19_prd-recyclique-architecture-permissions-multisite-kiosques-bmad.md)

---

## 2. L'énoncé en une phrase

**Chaque objet qui entre dans l'asso porte une identité numérique stable (code-barres ou QR) qui relie la réception, le stock et la caisse, et alimente la traçabilité vers la compta (euros et matière selon les règles Paheko / **PKO-000**), sans refaire la saisie à chaque étape.**

La **webcam** et la **bascule** ne sont pas la vision en elles-mêmes : ce sont des **moyens** pour enregistrer vite et bien **poids**, **catégorie** et **contexte visuel**, au service de cette identité et de ce parcours.

---

## 3. Le parcours cible (métier)

1. **Entrée** — L'objet arrive ; on le pèse, on le regarde (y compris via une ou deux webcams si le poste le prévoit), on confirme ou corrige la **famille** / catégorie proposée.
2. **Décision courte** — Prix fixe, prix plancher, estimation, ou simple étape « à valider » selon la politique du site.
3. **Étiquette** — Impression d'une étiquette **code-barres ou QR** qui pointe vers la **fiche objet** dans Recyclique.
4. **Vie dans l'asso** — Déplacements, réparations, zones tampon, réservations : autant d'étapes où **un scan** met à jour ou affiche l'état, sans perdre la trace.
5. **Caisse** — Le même code remonte **poids** et **prix** (selon ce qui a été fixé à la réception), pour un ticket clair.
6. **Sorties** — Recyclage, don, vente : le parcours reste **traçable** ; la partie euros et la partie « matière / dons » suivent les règles Paheko déjà cadrées ailleurs (ne pas confondre avec ce document).

Ce parcours est l'ancrage **REC-001** « poste réception idéal » du recap, généralisé en vision plateforme.

---

## 4. Règles métier que la vision porte (déjà posées côté terrain)

- **Pas de vente « au lot opaque » pour le client** : un carton peut exister en **logistique interne**, mais le ticket de caisse reste en **lignes lisibles** (alignement **REC-012**).
- **Double lecture** : Recyclique suit **objets et tickets** ; l'argent réel suit Paheko — la vision réception ne remplace pas ce cadre (**PKO-000** dans le recap).

---

## 5. Ce que le super admin configure (périmètre de gouvernance)

Le super admin ne « code » pas : il **cadre** pour un ou plusieurs sites :

- **Quand** étiqueter (à l'entrée, au tri fin, ou selon la **famille d'objets**) — tension documentée **REC-004**, la vision impose que ce soit **paramétrable**, pas une règle unique imposée à toutes les assos.
- **Quels parcours** pour quels types d'objets (réparation, mise en rayon, besoin prioritaire) — alignement **REC-002** / **REC-008** (moteur de workflows = intention cible, à affiner en produit).
- **Cohérence multi-sites** : mêmes principes d'identité objet et de scan, avec **surcharges** possibles par site (tarifs, catégories masquées, politique d'étiquette).

---

## 6. Hors périmètre de cette vision (rappel)

- Choix comptables précis (écritures, comptes, expert-comptable) : voir [le guide liaison Paheko compta](../migration-paheko/2026-05-21_guide-liaison-paheko-compta.md) et les fiches **PKO-*** du recap.
- Omnicanal, vente en ligne, mutualisation réseau des estimations : **pistes** (**REC-016**, **REC-014**), pas des engagements de cette vision v1.

---

## 7. Critères de succès (comment savoir que la vision est atteinte)

- Un bénévole peut expliquer en **deux phrases** le chemin d'un objet de l'entrée à la caisse.
- **Un scan** suffit pour retrouver au minimum poids, état et prix (ou fourchette) sans ressaisir ; **photo** et **emplacement** lorsque la fiche les enregistre (objectif cible aligné **REC-007** / entrée **REC-001**).
- Le super admin peut **expliquer** à une nouvelle ressourcerie **où** elle se différencie des autres surtout sur **étapes** et **moment d'étiquetage**, sans casser la logique commune.

---

## 8. Suite documentaire recommandée

- Ateliers brainstorm **Réception v1** décrits en fin de recap **2026-05-21_02** (priorité : poste pesée + workflow + arbitrage étiquette).
- Toute spec technique (API, écrans, matériel) doit **référencer** ce document comme **but métier** ; les écarts doivent être assumés et tracés (ADR ou sprint-change).

---

*Vision rédigée pour stabiliser l'interprétation des transcriptions ; les fiches REC-*/PKO-* du recap restent la matière exhaustive et les questions ouvertes.*
