# Prompt recherche — Liaison Paheko : fermeture caisse, comptage, dons, réemploi (terrain)

**Date :** 2026-05-21  
**Cible :** Perplexity Pro (mode recherche approfondie / Deep Research)  
**Usage :** Nourrir le brainstorm « module Liaison Paheko » avant figement BMAD. Priorité produit : **fermer la caisse → compta Paheko** (chantier en cours).  
**Réponse attendue :** coller ou exporter vers  
`references/recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md`

**Contexte projet :** joindre ou coller en tête de session  
`references/recherche/contexte-pour-recherche-externe.md`  
+ préciser pour cette recherche : **Recyclique = caisse et tickets** ; **Paheko = comptabilité** ; clôture = **une écriture (ou lot) par session de caisse**, pas ticket par ticket (décision produit avril 2026).

**Recherche déjà faite (ne pas répéter, seulement compléter si utile) :**  
`references/recherche/2026-04-02_remboursements-compta-associations-loi-1901_perplexity_reponse.md` (remboursements, conservation pièces, clôture agrégée).

**Sources terrain (idées, pas loi) :**  
`references/artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md` (réunion Paheko mai 2026).

---

## Décisions déjà prises côté porteur produit (à respecter dans les recommandations)

- **Priorité** : boucler d’abord la **fermeture de caisse → Paheko**.
- **Comptage pièces et billets** à la fermeture : **obligatoire** ; ce sera un **module séparé** branché sur la fermeture (pas un détail optionnel caché).
- **Tickets mixtes** (ex. habits donnés -18 + vaisselle payante sur le même ticket) : **fréquents** → à traiter dès la première vague fonctionnelle.
- **Validation comptable finale** : après cette recherche, synthèse humaine + expert-comptable ; ne pas présenter les réponses Perplexity comme décision définitive.

---

## Consignes générales pour Perplexity

- Répondre en **français**.
- Citer des **sources vérifiables** (PCA / plan comptable associatif, doctrine ordres professionnels, doc Paheko, retours d’expérience ressourceries/recycleries France si disponibles).
- **Ne pas inventer** d’articles de loi : citer précisément ou écrire « à valider avec un expert-comptable ».
- Distinguer clairement : **obligation légale** / **bonne pratique métier** / **choix d’outil (Paheko, Recyclique)** / **périmètre EC**.
- Structurer la réponse en **trois parties** (A, B, C) ci-dessous, avec en fin de chaque partie un encadré **« Pour Recyclique — retenir / rejeter / question EC »** (3 à 5 puces max).

---

## Partie A — Fermeture de caisse en association (ressourcerie / boutique réemploi)

**Contexte :** association loi 1901, **non assujettie TVA** (cas type), ventes au comptant en boutique, plusieurs moyens de paiement (espèces, chèque, carte), parfois **dons en caisse** (surplus volontaire distinct de la vente).

**Questions :**

1. En France, quelles sont les **bonnes pratiques** de fermeture de caisse pour ce type de structure (pas retail NF525) : fréquence, qui compte quoi, journal de caisse, rapprochement banque ?
2. **Comptage physique** des espèces (pièces, billets) : quand est-il considéré indispensable ? Comment les structures gèrent-elles l’**écart** (trop-perçu / manque) comptablement et opérationnellement ?
3. Comment **Paheko** (ou logiciels équivalents associations) modélisent-ils la **session de caisse** et la **clôture** (théorique vs réel, fond de caisse) ? Points documentés wiki / API si connus.
4. Pour une app externe (Recyclique) qui envoie les totaux du jour : quels **risques** si la compta reçoit un **récap par session** sans ressaisie ticket par ticket (à condition de garder le détail en justificatif interne) ?
5. **Module comptage monnaie** branché sur la fermeture : exemples d’UX ou de processus dans d’autres secteurs (retail associatif, ONG, coopératives) applicables par analogie.

---

## Partie B — Ventes réemploi (7070) et dons en caisse (7541), espèces vs chèques

**Contexte :** ventes de réemploi créditées typiquement en **7070** (pas 707 générique) ; dons manuels en caisse en **7541** ; parfois sous-comptes **754.x** (espèces, chèques, projets). Paiements **mixtes** sur un ticket (ex. 5 € espèces + 7 € carte). **Surplus** : client paie 10 € pour une vente de 8 € → 8 € vente + 2 € don.

**Questions :**

1. PCA / usages associations : compte **7070** (ou équivalent réemploi) vs comptes **707** génériques — usages réels et risques de mélange.
2. **7541** et ventilation **754.x** : quand séparer dons **espèces** et dons **chèques** (comptes transitoires 511/512, rapprochement banque fin de mois) ?
3. **Un chèque** qui couvre à la fois un **don** et une **vente** : pratiques comptables recommandées — **plusieurs lignes** sur une même pièce sans « découper » physiquement le chèque ? Contre-exemples à éviter.
4. **Dons en caisse** distincts du paiement : traitement du surplus volontaire vs don saisi comme moyen de paiement par erreur (bonnes pratiques UX + compta).
5. Alignement avec **Paheko** : moyens de paiement paramétrables, écritures multi-lignes, journaux de caisse — ce qui est documenté ou observé en pratique.

---

## Partie C — Dons matière / textiles (-18), kg, sans flux monétaire

**Contexte :** en boutique réemploi, des **lignes ticket** peuvent être des dons de produits (ex. textiles -18) **sans encaissement** ; la ressourcerie trace aussi des **sorties matière en kg**. Paheko enregistre surtout les **flux en euros**. Tension terrain : faut-il une **trace comptable** dans Paheko pour la matière sortie sans € ?

**Questions :**

1. Pour une association de réemploi, comment traiter comptablement (ou **ne pas** traiter en compta générale) les **apports / sorties de marchandises** sans contrepartie monétaire immédiate ?
2. Existe-t-il des pratiques (analytique, comptes de produits en nature, stocks, dons en nature) pertinentes pour des **textiles -18** ou déchets valorisés — ou la trace reste-t-elle **hors compta** (outil métier seulement) ?
3. Cas **ticket mixte** : partie « don -18 » + partie payante — comment les structures séparent **traçabilité magasin** et **écritures €** le jour de la clôture ?
4. Ce qui doit **obligatoirement** rester du ressort **expert-comptable** vs ce qu’un logiciel métier peut documenter sans écriture Paheko.

---

## Livrable attendu (format de sortie)

1. **Synthèse exécutive** (10–15 lignes) pour un porteur produit non comptable.
2. **Parties A, B, C** avec sous-titres, tableaux si utile, sources en bas de section.
3. **Encadrés « Pour Recyclique »** après A, B, C.
4. **Liste finale** : « Questions à poser à l’expert-comptable » (max 8, formulées en français courant, sans jargon dev).
5. **Annexe** : liens URL des sources les plus utiles.

---

## Bloc à copier-coller dans Perplexity (version courte)

```
Recherche approfondie — association loi 1901 non-TVA, ressourcerie France, boutique réemploi.

Recyclique = caisse (tickets, sessions). Paheko = compta. À la fermeture de journée : récap session vers Paheko (pas ticket par ticket), comptage pièces/billets obligatoire (module dédié), tickets mixtes don matière + vente payante fréquents.

Réponds en français, 3 parties :
A) Fermeture de caisse associative : bonnes pratiques, écarts, comptage espèces, session/clôture Paheko, risques récap session.
B) Ventes réemploi 7070, dons caisse 7541/754.x, espèces vs chèques, surplus volontaire, chèque unique = plusieurs lignes comptables don+vente.
C) Dons matière/textiles -18 sans € : trace compta ou hors compta, ticket mixte, périmètre expert-comptable.

Sources vérifiables. Ne pas inventer la loi. Fin de chaque partie : encadré "Pour Recyclique — retenir/rejeter/question EC". Fin : max 8 questions pour expert-comptable en langage simple.

Ne pas répéter une recherche déjà faite sur remboursements caisse associations (avril 2026) — compléter seulement.
```
