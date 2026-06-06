# Prompt recherche — Comptage pièces/billets à la fermeture de caisse (UX terrain + référentiel)

**Date :** 2026-06-06 (révision : prompt **autonome** pour Perplexity, sans accès au dépôt)  
**Cible :** Perplexity Pro — mode **Deep Research**  
**Usage interne dépôt :** débloquer le module comptage pièces/billets pour le pilote La Clique qui Recycle.  
**Réponse à ranger dans le dépôt :**  
`references/recherche/2026-06-06_comptage-pieces-billets-fermeture-caisse-ux-terrain_perplexity_reponse.md`

> **Instructions pour Strophe :** copier **uniquement** la section « Bloc copier-coller Perplexity » ci-dessous (tout le bloc, du titre jusqu'à la fin). Perplexity n'a pas accès au repo — tout le contexte utile est inclus dans ce bloc.

---

## Bloc copier-coller Perplexity (session unique — autonome)

```
# Recherche : comptage pièces et billets à la fermeture de caisse (France, 2026)

## Contexte organisationnel et produit (à lire avant les questions)

Je conçois un **logiciel de caisse** pour une **ressourcerie / boutique de réemploi** française : association **loi 1901**, en principe **non assujettie à la TVA**. Ce n'est pas un retail soumis NF525.

**Organisation pilote :** « La Clique qui Recycle » — bénévoles peu formés, rotation fréquente, poste caisse **partagé** (tablette ou PC tactile), clôture **quotidienne**.

**Fonctionnement caisse (déjà en place ou prévu) :**
- Une **session de caisse** = ouverture le matin (avec un **fond de caisse** en espèces, ex. 50 € laissés dans le tiroir) → ventes dans la journée → **fermeture** le soir.
- Paiements possibles : **espèces**, **chèque**, **carte bancaire**, parfois **dons en caisse** (surplus volontaire distinct de la vente).
- À la fermeture aujourd'hui : le bénévole saisit un **montant global** compté dans le tiroir et le système calcule l'**écart** par rapport au théorique.
- **Comptabilité** : logiciel associatif type **Paheko** (ou équivalent). Les écritures comptables sont envoyées **par session clôturée**, en **lot agrégé** (ventes, dons, remboursements, écart de caisse) — **pas** une écriture par ticket, **pas** le détail pièce par pièce côté compta.
- **Écart de caisse** : seuil de tolérance interne **2,00 €** par défaut (paramétrable). Au-delà → **blocage** de la clôture et alerte responsable. En dessous → écriture d'écart sur comptes type **658** (manque) / **758** (surplus) — à valider avec expert-comptable.

**Ce que je veux ajouter :**
- Un **écran de comptage par dénomination** : pour chaque type de pièce et billet en euros, le bénévole saisit une **quantité** ; le logiciel calcule le **total** et l'**écart** vs espèces théoriques de la session.
- Ce module sera **obligatoire** sur le site pilote (pas de contournement « passer l'étape »).
- Le détail pièces/billets sert au **contrôle terrain** et à l'**audit interne** ; la compta ne reçoit que les **totaux** et l'**écart agrégé**.

**Contraintes UX déjà décidées côté produit :**
- L'étape comptage s'insère dans un **assistant de fermeture** en plusieurs écrans (pas une page isolée).
- Ordre envisagé : (1) récapitulatif théorique → (2) **grille de comptage** → (3) écart éventuel + commentaire → (4) code PIN responsable → (5) clôture validée.
- Saisie **à l'écran** (pas de clavier numérique physique dédié type caisse retail pro).
- Total et écart calculés de préférence **côté serveur** (pas seulement dans le navigateur).

**Ce que je ne demande PAS dans cette recherche :**
- Pas de code, pas de schéma SQL, pas d'architecture logicielle détaillée.
- Pas de reprise complète de la compta associative générale (7070 réemploi, 7541 dons, etc.) — seulement ce qui impacte le **comptage espèces** et la **feuille de clôture**.

**Synthèse de recherches déjà connues (ne pas répéter longuement — compléter si lacune) :**
- Le comptage manuel pièces/billets est une **bonne pratique indispensable** dès qu'il y a des espèces.
- UX générique recommandée ailleurs : **grille dénominations × quantités**, total auto, écart affiché tout de suite, validation en deux temps possible.
- Analogies : feuilles de clôture papier pré-imprimées (retail associatif, ONG), cosignature possible, fond de caisse prédéfini laissé dans le tiroir.

---

## Consignes de réponse

- Langue : **français**.
- Citer des **sources vérifiables** (BCE, Banque de France, doctrine comptable associative, retours POS / retail, ressourceries si disponibles).
- Distinguer clairement : **obligation légale** / **bonne pratique métier** / **recommandation UX produit** / **à valider avec expert-comptable**.
- Structurer en **4 parties A, B, C, D** (ci-dessous).
- **Fin de chaque partie** : encadré **« Synthèse projet — retenir / rejeter / question ouverte »** (3 à 5 puces max).
- **Livrables finaux** (section dédiée en fin de réponse) : voir liste en bas.

---

## Partie A — Référentiel des dénominations (zone euro, France 2026)

L'application doit proposer une grille fixe de pièces et billets en euros.

1. Quelles sont les **dénominations légales en circulation** en zone euro en 2026 (pièces 1 cent à 2 €, billets 5 € à 500 €) ? Y a-t-il des billets **retirés**, **rares** ou **déconseillés en caisse** à exclure d'une grille standard (ex. 500 €) ?
2. Existe-t-il une **liste de référence officielle** (BCE, Trésor, service public) pour figer un référentiel produit ?
3. Faut-il gérer les **pièces commémoratives** ou une grille **strictement par valeur faciale** (ex. 8 pièces + 7 billets) suffit-elle pour une petite structure associative ?
4. **Rouleaux de pièces** ou **liasses de billets** : compte-t-on en **unités** ou par rouleau — impact sur l'UX ?
5. **Ordre d'affichage** recommandé (croissant / décroissant, pièces puis billets) — usages documentés en caisse / POS.

---

## Partie B — UX du comptage à la fermeture (bénévole, écran tactile)

1. **Grille dénominations × quantité** : comparer les patterns UX (boutons +/−, stepper, champ numérique, clavier virtuel) — **rapidité vs taux d'erreur** en fin de journée.
2. **Fond de caisse** (espèces laissées pour le lendemain, ex. 50 €) — quelle est la **meilleure pratique** ?
   - tout compter dans la grille (y compris le fond) ;
   - saisir le fond **à part** puis calculer « à remettre en banque / coffre » = total compté − fond ;
   - fond **prédéfini** + ajustement si le tiroir ne correspond pas ?
   Donner **une recommandation tranchée** avec justification.
3. **Validation en deux temps** (brouillon → relecture → confirmation) : quand indispensable vs friction excessive pour des bénévoles ?
4. **Session sans aucune vente en espèces** (uniquement CB/chèques) : masquer la grille, pré-remplir à zéro, ou exiger une case « aucune espèce encaissée » ?
5. **Erreurs fréquentes** (confusion 1 € / 2 €, oubli du fond, double comptage) et **garde-fous UX**.
6. **Accessibilité** : taille des boutons, contraste, feedback, usage une main — recommandations concrètes.
7. **Temps cible** : durée acceptable pour un comptage complet (benchmark) pour dimensionner le nombre d'étapes.

---

## Partie C — Lien comptage détaillé, montant global et écart

1. Le **montant théorique espèces** de la session doit-il **inclure** ou **exclure** le fond d'ouverture ? Pratiques opérationnelles et comptables.
2. Si le total de la grille = 247,30 € mais qu'un montant global 247,00 € avait été saisi : **quelle valeur doit faire foi** dans un logiciel moderne ?
3. Pour un écart ≤ 2 € : le **détail pièces/billets** doit-il être **archivé** comme justificatif même si la compta ne porte que l'écart agrégé ?
4. **Conservation** : durée et format (PDF, CSV, signature, cosignature) — obligations ou bonnes pratiques pour associations loi 1901 en France.
5. **Commentaire** : un seul commentaire d'écart global, ou possibilité de note par dénomination (ex. « rouleau de 2 € non ouvert ») ?

---

## Partie D — Terrain ressourcerie / boutique solidaire (France)

1. Retours d'expérience de **ressourceries, recycleries, boutiques solidaires** sur la **feuille de clôture** et le comptage monnaie — modèles papier ou outils numériques ?
2. **Double validation** (deux personnes cosignent) : fréquence réelle et mise en œuvre numérique simple ?
3. **Règles à afficher** en permanence sur l'écran (3 à 5 règles maximum pour former à la volée).
4. **Check-list de tests** avant mise en production pilote (scénarios manuels à valider).
5. **Risques** d'une première version « minimale » : grille standard 8 pièces + billets courants, pas de rouleaux, comptage obligatoire, pas de contournement.

---

## Livrables attendus (section finale de ta réponse)

1. **Tableau référentiel recommandé** avec colonnes : `code` (ex. EUR_200 pour 2 €), `libellé`, `type` (pièce/billet), `valeur_centimes`, `afficher_par_défaut` (oui/non), `ordre_affichage`.
2. **Wireframe textuel** (pas d'image) du parcours optimal en **5 à 7 étapes** depuis « Fermer la session » jusqu'à « Session clôturée ».
3. **Décision recommandée sur le fond de caisse** : une option tranchée + justification courte.
4. **5 arbitrages produit** encore ouverts après ta recherche, classés **P0** (bloquant) / **P1** (peut attendre).
5. **Bibliographie** : URLs ou références précises.
```

---

## Notes internes dépôt (ne pas envoyer à Perplexity)

- Après réception de la réponse : ventiler les arbitrages P0 vers la fiche `references/protocole-modules-recyclique/08-MOD-exemple-pilote-comptage-pieces-billets.md` et préparer les stories BMAD back/front.
- Cette recherche **complète** (ne remplace pas) les réponses compta mai 2026 déjà dans `references/recherche/2026-05-21_*`.
