# Prompt recherche — Trous restants Liaison Paheko (3e passe)

**Date :** 2026-05-21  
**Dernière QA prompt :** 2026-05-21 — **GO** (voir [rapport QA](2026-05-21_liaison-paheko-trous-recherche_prompt-qa.md))  
**Cible :** Perplexity Pro  
**Usage :** Compléter ce que les passes 1 et 2 n’ont **pas** tranché (Paheko opérationnel, plugin, lots d’écritures, procédures banque).  
**Réponse :** coller dans `2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md`  
**Contexte dépôt :** passes précédentes ventilées vers `references/migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md` et `…_repertoire-comptes-terrain-audio-recyclique.md`.

---

## Prompt Perplexity — copier-coller intégral (tout le texte ci-dessous)

```
# Recherche ciblée — trous restants RecyClique × Paheko (3e passe)

Tu es expert-comptable associations **loi 1901 non TVA**, PCA, et **documentation Paheko** (extension Caisse, dépôt banque, virements internes). Réponds en **français**, **sources URL** (paheko.cloud, compta-online, pennylane, indy, etc.). Ne invente pas de loi. Marque « à valider EC sur place » quand la décision finale relève du cabinet comptable de l’asso.

---

## A. Ce qui est DÉJÀ FIGÉ (ne pas remettre en cause sans preuve forte)

**RecyClique** = caisse web ressourcerie ; **Paheko** = compta. **Priorité produit** : fermeture caisse → Paheko opérationnelle. Clôture **par session** (pas une écriture par ticket) ; tickets détaillés archivés dans RecyClique **10 ans** (L123-22). **Module comptage pièces/billets obligatoire** à chaque fermeture (branché sur la clôture).

**Comptes retenus pour paramétrage et nouvelles écritures :**
- Ventes réemploi : **7070**
- Dons caisse (surplus volontaire séparé) : **7541**
- Espèces : **530**
- Chèques : **5112**
- Carte : **511** (valeurs à l’encaissement — **pas** 512 direct)
- Banque : **512**
- Écarts caisse (comptage obligatoire) : **658** (manque) / **758** (trop-perçu)
- Remboursement vente sur exercice **clos** : **672** (pas 467, pas 772)

**Rejeté :** 1630, oral « 53 » comme compte, 708/7041/7073, 511-205 et 511-210 **dans le plan Paheko** (uniquement données UI module comptage RecyClique), 467 pour remboursements.

**Clôture type validée (exemple session) :**
- **Pièce 1** — Débit 530 + 5112 + 511 / Crédit 7070 + 7541 (ventes + dons ventilés)
- **Pièce 2** — si écart comptage : 658 ou 758 ↔ 530
- **Plus tard** — dépôt chèques : Débit 512 / Crédit 5112 ; encaissement CB : 511 → 512

**Chèque unique vente + don** : une pièce, **deux lignes crédit** (7070 + 7541), débit **5112**.

**Hors v1 clôture :** textiles -18 sans € (trace kg RecyClique), CVN classe 8, Cerfa boutique, bien reçu en don puis revendu.

---

## B. Trous et contradictions — ta mission (8 blocs)

Pour **chaque** bloc R1–R8 : réponse structurée, recommandation actionnable, certitude (fort/moyen/faible), sources, et si **validation EC obligatoire**.

### R1 — Plugin / extension Caisse Paheko et comptes d’écart 678/778

**Contexte audit interne (extension Caisse Paheko)** : à la clôture native, l’écart physique vs théorique alimente `plugin_pos_sessions_balances.error_amount` et une écriture compta via comptes configurables **`POS::ERROR_DEBIT_ACCOUNT` / `POS::ERROR_CREDIT_ACCOUNT`** — en pratique souvent **678** (charge exceptionnelle) / **778** (produit exceptionnel). RecyClique doit utiliser **658/758** (gestion courante) pour les écarts du **module comptage**.

Questions :
1. La configuration de l’extension Caisse Paheko permet-elle de **modifier** les comptes d’écart (678/778 → 658/758) ? Où dans l’interface / doc ?
2. Si **non modifiable** : quelle stratégie pour une asso qui synchronise depuis RecyClique (écritures API) **et** utilise parfois la caisse native Paheko ?
3. Risque d’**double comptabilisation** ou d’incohérence d’audit si les deux jeux coexistent ?
4. Faut-il **désactiver** la clôture native Paheko une fois RecyClique en production ?

### R2 — Nombre de pièces / lots par session vs PRD technique

**PRD RecyClique (stratégie B retenue)** — batch de session = **plusieurs sous-écritures équilibrées** :
- **Transaction 1** : ventes + dons (ex. débit 530/5112/511, crédit 7070/7541)
- **Transaction 2** : remboursements **exercice courant** (ex. débit **7070**, crédit trésorerie)
- **Transaction 3** : remboursements **exercice antérieur clos** (ex. débit **672**, crédit trésorerie)

**Validation comptable 2e passe** : clôture « standard » = **2 pièces** : (1) ventes+dons ; (2) **écart de caisse** si comptage ≠ théorique (658/758 ↔ 530). Les remboursements ne sont pas dans ces 2 pièces.

**Recherche remboursements (avril 2026)** : avoir immuable dans RecyClique ; remboursement **même jour** peut être **net** dans la clôture ; J+N = écriture séparée. Compte remboursement souvent cité : **709** (RRR) **ou** débit **707/7070** — **à trancher**.

Questions :
1. Comment **réconcilier** PRD (3 transactions + écart ?) vs validation (2 pièces clôture + écart) **sans double comptabiliser** ?
2. L’**écart de caisse** doit-il être une **4e transaction** distincte (stratégie B étendue) ou inclus dans la transaction 1 ?
3. Remboursements **même jour** : intégrés au net transaction 1 ou **toujours** transaction 2 séparée ?
4. **709** vs **7070** en débit pour remboursement exercice courant — recommandation PCA ressourcerie ?
5. Modèle API Paheko : une écriture multi-lignes vs plusieurs écritures par session ?
6. Ordre : clôture Z **avant** ou **après** écritures remboursements de la journée ?

### R3 — Granularité compte 7541 (dons)

Plan Paheko terrain actuel : **754.10**, **754.11**, **754.115**, **754.111**, **754.12**, parfois **754.900** (sens inconnu).

Recherche 2e passe : **7541** seul suffit réglementairement ; sous-comptes = confort / subventionneurs.

Questions :
1. Pour une ressourcerie loi 1901 avec **subventions** et dons modérés en caisse : **7541 unique** ou sous-comptes dès v1 ?
2. Si sous-comptes : mapping recommandé (754.11 espèces, 754.115 chèques, 754.111 projets → quels numéros PCA exacts : 7541.1, 7541.5, 7542…) ?
3. Risque de **double arborescence** 754.xx vs 7541 — procédure de fusion sans perdre l’historique Paheko ?
4. Que peut désigner **754.900** dans les plans d’associations / ressourceries (si usage documenté) ?

### R4 — Migration historique 707 → 7070

L’asso a utilisé **707** la première année ; cible **7070** pour réemploi.

Questions :
1. Bonne pratique : **ne pas reclasser** l’historique vs reclasser — critères (impact bilan, subventions, comparabilité N-1) ?
2. Procédure Paheko pour **créer 7070** et basculer les paramètres sans casser les rapports ?
3. Impact sur les **tableaux de bord** Paheko et exports expert-comptable ?

### R5 — Compte 672 et fin d’exercice

Confirmé pour remboursements sur exercice clos. PCG 2025 : **672 doit être soldé / réimputé** en fin d’exercice (art. 1221-67 cité en recherche).

Questions :
1. Procédure type pour une **association** : où réimputer le solde 672 en fin d’exercice ?
2. RecyClique doit-il **bloquer** les écritures 672 après clôture d’exercice Paheko (ID exercice saisi manuellement) ?
3. Lien avec le **lot C** du PRD (remboursements antérieurs) : une écriture par remboursement ou regroupement mensuel acceptable ?

### R6 — Procédures Paheko post-clôture (banque)

Après pièce 1 RecyClique (5112 et 511 crédités) :

Questions :
1. **Dépôt chèques** : étapes exactes Paheko (écran, comptes, lien doc « dépôt banque chèque ») — 5112 → 512 ?
2. **Encaissement CB** : 511 → 512 au crédit bancaire — délai habituel, rapprochement ?
3. **Multi-comptes 512** (courant + Hello Asso + autre) : règles de choix du 512 cible ?
4. Compte **58** : quand l’utiliser pour un retrait espèces banque → caisse 530 (exemple chiffré) ?
5. **Journal** comptable à utiliser pour les écritures importées depuis RecyClique (CA, OD, autre) — doc Paheko ?

### R7 — Paramètres techniques liaison (hors code, niveau métier)

Questions :
1. Paheko accepte-t-il des écritures avec **libellé** type « Z caisse — SESSION {id} — Ventes + dons » — limite longueur, champs obligatoires API ?
2. **Exercice comptable** : pas d’API liste exercices — comment éviter les écritures sur mauvais exercice (contrôles métier recommandés) ?
3. **Seuil d’écart** caisse (±1 à 2 € proposé) : recommandation sectorielle ressourcerie / association retail ?
4. Checklist **mise en production** : 10 actions ordonnées (plan comptable, plugin, test pièces, dépôt chèques test, etc.)

### R8 — Fond de caisse, compte 531 et multi-caisse

**Contexte déjà documenté (ne pas réinventer — trancher les points ouverts)** :
- **Mono-caisse** : **530** suffit (fond = solde permanent).
- **Multi-caisse** (comportement cible RecyClique) : **1 caisse physique = 1 compte 53x** (531, 5311, 532, 5321, 5322, 533, 5331…) ; Paheko **Lieux de vente** = 1 lieu par poste ; compte espèces **par `cash_register`**, pas seed global 530 ; virements entre caisses via **58** uniquement.

Questions restantes pour Perplexity :
1. Écriture Paheko à l'**ouverture** de session (fond initial) vs seulement à la **clôture** (net journée) ?
2. **5112 / 511** : un compte global ou déclinaison par lieu quand N établissements ?
3. Cohérence **projets analytiques** Paheko par site avec cette grille 53x ?

---

## C. Livrables attendus (format strict)

1. **Tableau synthèse R1–R8** : Bloc | Question clé | Recommandation | Certitude | Valider EC (oui/non)

2. **Décisions RecyClique** (max 5) qu’on peut coder **sans** EC après cette 3e passe

3. **Décisions réservées EC** (max 5) — inchangées ou nouvelles

4. **Procédure opérationnelle** (liste numérotée) : du « fin de session RecyClique » au « rapprochement banque Paheko » (incluant dépôt chèques et CB)

5. **Modèle d’écritures par type d’événement** (tableaux débit/crédit) :
   - Clôture session standard (ventes+dons — confirmer ou ajuster)
   - Écart de caisse (658/758)
   - Remboursement **exercice courant** (7070 vs 709 — trancher)
   - Remboursement **exercice clos** (672)
   - Dépôt chèques banque (5112 → 512)
   - Crédit CB (511 → 512)
   - Fond de caisse / 531 si applicable

6. **3 contrôles sur le plan Paheko réel** (à faire avec le comptable sur place) :
   - Libellés **511-205 / 511-210** : vrais comptes du plan ou libellés d’écriture seulement ?
   - Cohérence **5112** (RecyClique) vs anciens comptes chèques terrain
   - Arborescence **754.xx** vs **7541** : risque double comptabilisation des dons

7. **Risques résiduels** (top 5) si on lance la v1 liaison sans réunion EC

---

## D. Hors scope

Développement API (détail endpoints), schéma SQL RecyClique, NF525, TVA, Cerfa détaillé, CVN classe 8 complète, HelloAsso 756, notes de frais 754.12, textiles -18 kg.

---

## E. Consignes

- Prioriser documentation **paheko.cloud** et retours d’expérience associations / ressourceries France.
- Distinguer : obligation légale / bonne pratique PCA / choix outil Paheko / décision cabinet EC.
- Un seul **plan comptable cohérent** — pas deux logiques RecyClique vs Paheko terrain divergentes.
- Orthographe : **RecyClique**, **Paheko**.
```

---

*Fin du prompt — tout le bloc entre les triples backticks ci-dessus est autonome pour Perplexity.*
