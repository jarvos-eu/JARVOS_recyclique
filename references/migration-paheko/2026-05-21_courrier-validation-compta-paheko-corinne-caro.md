# Courrier — validation compta caisse RecyClique × Paheko

**Date :** 21 mai 2026  
**De :** Strophe (RecyClique / La Clique)  
**Pour :** Corinne (comptable) · Caro (compta terrain Paheko)  
**Objet :** Validation plan comptable + fermeture caisse (suite réunion terrain mai 2026)

---

Bonjour Corinne, bonjour Caro,

Voici la **proposition consolidée** (réunion + 3 passes recherche) : comptes, fermeture, écritures Paheko. Merci de cocher / corriger en fin de doc.  
*§5 = complément compta pour Corinne ; §2–§4 = langage simple pour Caro et moi.*

Strophe

---

## 1. Décisions proposées (à valider)

- Clôture **par session** : on envoie à Paheko un **petit nombre d’écritures récap** (pas une par ticket) ; tickets = justificatifs dans RecyClique.
- **Toujours** une écriture « **récap du jour** » (ventes + dons en €) ; **+** une écriture **par remboursement** s’il y en a ; **+** une écriture « **écart de caisse** » si le comptage diffère du théorique (≤ 2 €).
- Comptage pièces/billets **obligatoire** à chaque fermeture.
- **1 caisse physique = 1 compte 53x** (Lieux de vente Paheko) ; **530** seulement si une seule caisse.
- Écritures via **API RecyClique** ; **synchro auto** extension Caisse Paheko **coupée** sur ces postes (anti-doublon).
- **Dons textile aux moins de 18 ans** (ligne « −18 » en caisse, pas une remise %) : pas d’€ en clôture v1 (à trancher à part, Corinne).

---

## 2. Fermeture de caisse (workflow)

### 2.1 À la fermeture

| Étape | En pratique |
|-------|-------------|
| 1 | Le bénévole lance la **fermeture** de session. |
| 2 | **Comptage** obligatoire : pièces, billets, fond de caisse (ex. 50 € laissés pour le lendemain). |
| 3 | Si l’écart entre comptage et théorique est **supérieur à 2 €** → **on bloque** la clôture (alerte responsable). |
| 4 | Si écart **≤ 2 €** → on peut clôturer ; l’écart part en compta (compte de charge ou produit divers). |
| 5 | RecyClique calcule un **Z** (totaux : ventes, dons, CB, chèques, remboursements). |
| 6 | Envoi à Paheko des **écritures de clôture** (au minimum le récap du jour — voir § 2.2). |
| 7 | Plus tard, côté Paheko : **dépôt des chèques** et **encaissement CB** vers la banque (pas forcément le soir même). |

### 2.2 Quelles écritures partent dans Paheko le soir ?

**Principe :** une **journée de caisse** = une **session** fermée. On ne recopie pas chaque ticket dans Paheko. On envoie seulement des **totaux du jour**, découpés en **3 types d’écritures possibles** (nos codes internes **T1, T2, T3** — détail compta § 5.2).

---

#### Écriture A — Récap du jour (**T1**) — **systématique**

**Quand :** à **chaque** fermeture, sans exception.

**Ce qu’elle contient :** tout l’argent encaissé dans la journée, ventilé par moyen de paiement, face aux **ventes** et aux **dons en euros** (pas les dons textile moins de 18 ans).

| Côté débit (entrées d’argent) | Côté crédit (produits) |
|------------------------------|-------------------------|
| Espèces en caisse (**530** ou **531, 532…**) | Ventes réemploi **7070** |
| Chèques reçus **5112** | Dons en caisse **7541** |
| Carte **511** | |

*Exemple :* 200 € de ventes + 2 € de don → une seule pièce qui équilibre espèces / chèques / CB avec 7070 + 7541.

---

#### Écriture B — Remboursement (**T2**) — **seulement s’il y a eu des remboursements**

**Quand :** un client a été remboursé pendant la session (espèces rendues, etc.).

**Règle :** **un remboursement = une écriture** dans Paheko (pas mélangé dans le récap du jour).

| Situation | Compte débité | Compte crédité (sortie d’argent) |
|-----------|--------------|----------------------------------|
| La vente d’origine est sur l’**exercice en cours** | **7070** (annule la vente) | Caisse **53x** ou chèques **5112** |
| La vente d’origine est sur un **exercice déjà clos** | **672** (charge exercice antérieur) | Idem |

*Exemple :* 2 remboursements dans la journée → **2 écritures B** en plus du récap A.

---

#### Écriture C — Écart de caisse (**T3**) — **seulement après comptage pièces/billets**

**Quand :** après comptage, le **physique** (ce qu’il y a dans le tiroir) ne colle pas exactement au **théorique** (ce que RecyClique attend).

| Écart | Comportement |
|-------|----------------|
| **≤ 2 €** | On peut clôturer ; une écriture C enregistre le petit écart (**658** si manque, **758** si surplus). |
| **> 2 €** | **Clôture bloquée** — il faut recompter ou faire corriger avant d’envoyer quoi que ce soit à Paheko. |

*Exemple :* il manque 1,50 € dans le tiroir → écriture C : débit **658** 1,50 € / crédit caisse **530** 1,50 €.

---

#### Combien d’écritures au total ? (exemples)

| Situation du soir | Écritures Paheko |
|-------------------|------------------|
| Journée normale, comptage OK, pas de remboursement | **1** — récap A seulement |
| Idem + écart 1,50 € | **2** — A + C |
| 1 remboursement, comptage OK | **2** — A + B |
| 1 remboursement + écart 1 € | **3** — A + B + C |
| 3 remboursements, pas d’écart | **4** — A + 3× B |

**Ordre d’envoi :** récap A → remboursements B (un par un) → écart C si besoin.

> **Codes T1 / T2 / T3** = raccourcis technique pour ces trois **types** d’écritures (pas « 3 écritures max » si plusieurs remboursements).

### 2.3 Après la clôture (Paheko)

| Opération | Comptes concernés |
|-----------|-------------------|
| Dépôt chèques en banque | **512** (banque) ← **5112** (chèques à encaisser) |
| Crédit CB sur le compte | **512** ← **511** (valeurs à l’encaissement) |
| Retrait espèces banque → caisse | Passage par **58** (virement interne), pas direct |

---

## 3. Plan comptable retenu (vue Caro / Strophe)

### 3.1 Comptes qu’on utilise pour la caisse v1

| Rôle | Numéro | En clair |
|------|--------|----------|
| Ventes réemploi | **7070** | Tout ce qui est vendu (réemploi), pas le compte 707 générique. |
| Dons en caisse (€) | **7541** | Dons manuels / surplus donné en caisse — **un seul compte** en v1. |
| Espèces en caisse | **530** ou **531, 532, 533…** | **530** si une seule caisse dans l’asso ; sinon **un numéro par caisse** (voir § 4). |
| Chèques reçus | **5112** | Chèques à encaisser (pas 511 pour les chèques). |
| Carte bancaire | **511** | CB en attente d’encaissement (pas 512 direct à la vente). |
| Banque | **512** | Compte courant (un sous-compte par banque si plusieurs). |
| Écart caisse (manque) | **658** | Petite différence négative après comptage. |
| Écart caisse (surplus) | **758** | Petite différence positive après comptage. |
| Remboursement sur vente **déjà clôturée** (exercice passé) | **672** | Charge sur exercices antérieurs. |
| Virements entre caisses / banque | **58** | Transit — le solde doit revenir à zéro. |

### 3.2 Comptes qu’on ne veut plus utiliser (erreurs ou confusion terrain)

| Numéro | Pourquoi |
|--------|----------|
| **707** (générique) | On passe tout le réemploi en **7070** pour les **nouvelles** écritures. |
| **708**, **467** | Anciens défauts logiciel — remplacés par **7541** / **672**. |
| **709** | Pas pour nos remboursements : on débite **7070** (exercice courant) ou **672** (exercice clos). |
| **678 / 778** | Comptes d’écart de la caisse native Paheko — RecyClique utilise **658 / 758**. |
| **1630** | N’existe pas au PCG — confusion avec la caisse **530**. |
| **511 205 / 511 210** | Ce sont des **données de comptage** dans RecyClique, **pas** des comptes dans le plan Paheko. |
| **511** pour les chèques | Les chèques vont sur **5112**. |
| **471 / 472** | Pas en fonctionnement normal boutique (sauf cas exceptionnel à trancher). |

### 3.3 Exemple de clôture (une caisse, compte 530)

**Hypothèse :** ventes 200 €, don 2 €, espèces 122 €, chèques 30 €, CB 50 €.

**Écriture A (récap du jour)**

- Débit **530** : 122 € (espèces nettes)  
- Débit **5112** : 30 €  
- Débit **511** : 50 €  
- Crédit **7070** : 200 €  
- Crédit **7541** : 2 €  

**Écriture C (écart)** — si comptage : manque 1,50 €

- Débit **658** : 1,50 €  
- Crédit **530** : 1,50 €  

**Chèque avec vente + don sur le même chèque :** un seul débit **5112**, **deux lignes crédit** (**7070** + **7541**) — pas de découpage physique du chèque.

---

## 4. Plusieurs caisses (magasins, stands)

| Règle | Détail |
|-------|--------|
| 1 caisse physique = 1 compte **53x** | Ex. magasin A caisse 1 → **531**, caisse 2 → **5311**, magasin B → **532**, etc. |
| Paheko | Chaque caisse RecyClique = un **Lieu de vente** Paheko, avec le bon compte espèces. |
| **530** seul | Uniquement si l’association n’a **qu’une seule** caisse physique. |

**Grille proposée (7 postes — à valider avec Corinne)**

| Compte | Lieu type |
|--------|-----------|
| **531** | Établissement A — caisse 1 |
| **5311** | Établissement A — caisse 2 |
| **532** | Établissement B — caisse 1 |
| **5321** | Établissement B — caisse 2 |
| **5322** | Établissement B — caisse 3 |
| **533** | Stand / mobile 1 |
| **5331** | Stand / mobile 2 |

**Fond de caisse (ex. 50 € laissés chaque soir)** : géré dans RecyClique comme **solde permanent** sur le compte 53x du poste — **pas d’écriture Paheko à chaque ouverture**.

---

## 5. Complément compta (Corinne) — schémas et contrôles

### 5.1 API / synchro

- `POST /accounting/transaction`, `ADVANCED`, `id_year: current`, libellé ≤ 200 car.
- Synchro auto extension Caisse **off** (exercice vide) — pas de doublon **678/778**.

### 5.2 Schéma des pièces (codes T1 / T2 / T3 = écritures A / B / C du § 2.2)

| Code | = § 2.2 | Schéma type |
|------|---------|-------------|
| **T1** | Récap du jour | D **53x** / **5112** / **511** — C **7070** / **7541** |
| **T2a** | Remb. exercice **ouvert** | D **7070** — C trésorerie — **une pièce par remboursement** |
| **T2b** | Remb. exercice **clos** | D **672** — C trésorerie — **une pièce par remboursement** |
| **T3** | Écart comptage | D **658** C **53x** (manque) ou D **53x** C **758** (surplus) — si \|écart\| ≤ **2 €** |

**Post-clôture trésorerie :** bordereau chèques **D 512 / C 5112** ; encaissement CB **D 512 / C 511** ; mouvements inter-caisses ou banque ↔ caisse via **58** (solde ≈ 0).

### 5.3 Produits et dons

- **7070** : ventes de réemploi (création du compte ; **pas de reclassification** automatique **707 → 7070** sur N-1 — note annexe au rapport si besoin).
- **7541** : dons manuels en caisse, v1 **compte unique** ; **7542** réservé aux dons **affectés projet** si exigence subventionneur ; **fusion 754.xx → 7541** proposée en **OD d’ouverture N+1** (à valider).
- Dons **textile aux moins de 18 ans** (et dons matière hors €) : hors flux clôture v1 ; traçabilité RecyClique (kg, article) ; **classe 8 / CVN** : à trancher avec toi (hors clôture v1).

### 5.4 Points de contrôle sur le plan Paheko actuel

1. Absence de **511-205 / 511-210** dans le plan (réservés au module comptage RecyClique).  
2. Convergence chèques sur **5112** (alignement terrain / RecyClique).  
3. Arborescence **754** : pas de double comptabilisation **754.xx** + **7541** ; identifier le compte **754.900** si présent.  
4. Création si manquants : **7070, 5112, 658, 758, 672, 58**.  
5. **672** : procédure de **réimputation en fin d’exercice** (OD proposée **D 658 / C 672** — compte cible et calendrier à confirmer, PCG 2025).

### 5.5 Risques résiduels (top 5)

| # | Risque | Mitigation |
|---|--------|------------|
| 1 | Doublon synchro auto Paheko + API RecyClique | Exercice vide en config caisse native |
| 2 | Exercice incorrect (`id_year`) | `current` + contrôle `GET /accounting/years` |
| 3 | **672** non soldé en fin d’exercice | OD fin d’exercice + alerte |
| 4 | Double compta dons **754.xx** + **7541** | Contrôle plan + fusion N+1 |
| 5 | Erreur API non traitée | Journalisation HTTP ≠ 200, archivage `id` pièces |

---

## 6. Ce qu’on vous demande de valider

### 6.1 Cases à cocher (réunion ou retour écrit)

**Plan comptable**

- [ ] Comptes **7070, 7541, 5112, 511, 512, 658, 758, 672, 58** : OK pour La Clique  
- [ ] Grille **53x** (531–5331 ou autre numérotation) : validée / à ajuster : _______________  
- [ ] **530** mono-caisse OU **53x** multi-caisses : notre situation → _______________  
- [ ] Pas de **511-205/210** dans le plan Paheko  
- [ ] Arborescence **754** : pas de doublon ; **754.900** identifié : _______________  
- [ ] **Ne pas** reclasser l’historique **707 → 7070** sur N-1 : OK / non OK  

**Fermeture & écritures**

- [ ] Modèle clôture : **récap du jour** (A/T1) + **remboursements** (B/T2, 672 si exercice clos) + **écart** (C/T3) : OK  
- [ ] Seuil écart **± 2 €** (blocage au-delà) : OK / autre seuil : _____ €  
- [ ] Écarts en **658/758** (pas 678/778) : OK  
- [ ] Chèque mixte vente + don : **2 crédits** sur **5112** : OK  
- [ ] **Désactiver** synchro auto caisse Paheko sur postes RecyClique : OK  

**Organisation**

- [ ] Tableau **poste RecyClique ↔ Lieu de vente Paheko ↔ compte 53x** à remplir ensemble  
- [ ] Journaux Paheko pour import API (Recettes / OD / Banque) : _______________  
- [ ] **672** : réimputation fin d’exercice (compte, date) : _______________  
- [ ] **7542** nécessaire ? oui / non  
- [ ] Caisse native Paheko encore utilisée en parallèle ? oui / non → procédure anti-doublon  

**Hors périmètre immédiat (pour mémoire)**

- [ ] Dons textile moins de 18 ans, CVN classe 8, Cerfa, bien don revendu : traitement ultérieur (Corinne)  

### 6.2 Questions ouvertes (prioritaires)

1. **Numérotation définitive des caisses** (531–5331 vs format long type 531001) ?  
2. **5112** et **511** : comptes uniques ou ventilés par établissement / banque / TPE ?  
3. **Réimputation 672** : compte de charge cible et calendrier OD ?  
4. **Fusion 754.xx → 7541** : validée en début de N+1 ?  
5. Y a-t-il aujourd’hui des **écritures Paheko** générées par l’extension Caisse **en parallèle** de ce qu’on prépare ?

---

*21 mai 2026 — retours : OK / à modifier directement sur ce doc ou par mail.*
