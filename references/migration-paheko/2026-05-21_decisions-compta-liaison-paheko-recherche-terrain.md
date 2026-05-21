# Décisions compta — Liaison Paheko (recherche terrain + Perplexity 2026-05-21)

**Date :** 2026-05-21  
**Statut :** décisions **produit / brainstorm** — les points marqués **EC** restent à valider par l’expert-comptable avant figement BMAD ou implémentation.  
**Sources :** [recherche Perplexity](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md), [recap terrain](../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md), [PRD caisse-compta](2026-04-15_prd-recyclique-caisse-compta-paheko.md), arbitrages porteur produit (2026-05-21).

**Ne remplace pas** le PRD du 15/04 pour l’implémentation technique (tables, API, outbox) : ce fichier **fige l’orientation métier** après recherche.

---

## 1. Décisions figées (produit)

| # | Décision | Justification courte |
|---|----------|----------------------|
| D1 | **Priorité chantier** : fermeture caisse → Paheko (liaison), pas réception d’abord | Porteur produit — chantier en cours |
| D2 | **Clôture par session** : un récap/jour vers Paheko, **pas** une écriture par ticket | PRD §2.1 + recherche A4 + pratique asso |
| D3 | **Détail tickets** conservé dans Recyclique comme **justificatif** (export/archivage) | Condition légale de validité du récap agrégé |
| D4 | **Écriture Paheko ventilée** : lignes distinctes 7070, 7541, 530, 511/512… — **pas** une ligne « recettes du jour » | Recherche A4, B |
| D5 | **Module comptage pièces/billets** : **obligatoire**, **module séparé** branché sur la fermeture | Porteur produit + recherche A2/A5 |
| D6 | **Fermeture** : PDF ou export feuille de clôture archivable ; écart documenté | Recherche A2 |
| D7 | **Ventes réemploi** → compte produit **`7070`** (pas 707 générique) | Terrain (C refuse 707) + PRD + recherche B1 |
| D8 | **Dons en caisse** (surplus volontaire) → **`7541`**, **séparés** des ventes dans l’écriture | PRD + recherche B |
| D9 | **Surplus volontaire** : flux **don explicite** en caisse (pas noyé dans le paiement vente) | Recherche B4 |
| D10 | **Chèque don + vente** : **une pièce, plusieurs lignes** comptables — **pas** de découpage physique du chèque | Terrain PKO-006/007 + recherche B3 |
| D11 | **Ticket mixte** (don matière -18 + ligne payante) : **fréquent** → géré **v1** | Porteur produit |
| D12 | **Ligne don matière / -18** : **aucun €** vers Paheko ; traçabilité **Recyclique** (kg, article) | Recherche C + recap PKO-016/016b |
| D13 | **Clôture Paheko** : envoyer **uniquement les totaux monétaires** du jour | Conséquence D11, D12 |
| D14 | **Pas d’envoi Paheko** des sorties matière -18 sans décision EC sur CVN (classe 8) | Recherche C2, C4 |
| D15 | **Bug « don » par défaut** en caisse : **hors priorité** brainstorm (correctif attendu v2 caisse) | Porteur produit |

---

## 2. Aligné PRD existant (inchangé, rappel)

| Sujet | Valeur | Fichier |
|--------|--------|---------|
| Source de vérité paiements | `payment_transactions` | PRD §2.2 |
| `free` | Vente à 0 €, pas moyen de paiement | PRD §4.4 |
| Remboursement exercice clos | Compte candidat **`672`**, validation EC | PRD §6.7, spec SuperAdmin B2 |
| Batch Paheko | Stratégie B : ventes+dons / remb. courant / remb. antérieur | PRD §9.2 |
| Exercice Paheko | Saisie manuelle ID (pas API liste) | Spec SuperAdmin M5 |

---

## 3. Rejeté explicitement

| Sujet | Raison |
|--------|--------|
| Agréger don + vente sur **une seule ligne** crédit en clôture | Recherche B, terrain |
| Envoyer sorties matière -18 à Paheko **sans** cadre EC (CVN / hors bilan) | Recherche C |
| Ventilation par **famille produit** en clôture (ex. 7073 textile seul) | Décision PRD + spec I1 |
| Prorata **physique** d’un chèque entre don et vente | Terrain PKO-006 |

---

## 4. En attente expert-comptable (ne pas coder comme définitif)

Voir [questions consolidées](#6-questions-expert-comptable-et-suite-porteur) et [répertoire comptes](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md).

| Thème | Candidat produit | Bloquant v1 ? |
|--------|------------------|---------------|
| Écarts de caisse (trop-perçu / manque) | 658 / 758 (recherche) ; audit Paheko cite 678/778 | Non si écart documenté ; écriture auto = v2 |
| Sous-comptes 754.11 / 754.115 / 754.111 (espèces, chèque, projet) | Terrain Paheko | Non — 7541 unique possible v1 |
| 511 vs 512 vs 511 205/210 (billets/pièces) | Audio Carole / B | Oui pour **paramétrage** moyens de paiement |
| 53 vs 530 vs 58 vs 471 décaissements | Audio IDEA-013 | Plutôt **v2** (décaissements caisse) |
| Classe 8 CVN pour textiles -18 | Recherche C2 | Non pour clôture caisse v1 |
| Vente d’un bien **reçu en don** puis revendu (7541 vs 7070, hors bilan) | Recherche EC #6 | Cas SAV / v2 |
| Reçu fiscal Cerfa don en boutique | Recherche EC #8 | Hors clôture |

---

## 5. Écarts documentés (à harmoniser)

| Sujet | PRD / spec dev | Terrain / Paheko existant | Action |
|--------|----------------|---------------------------|--------|
| Compte vente clôture | `7070` | Historique parfois `707` (1re année) | EC + migration plan Paheko |
| Écarts caisse | — | Perplexity 658/758 ; plugin Paheko 678/778 | **EC** tranche un jeu de comptes |
| Espèces | `530` (PRD) | Audio aussi « 53 », « 1630 » (probable confusion STT) | Répertoire + EC |
| Fond de caisse | PRD fond session | Audio **531** débit/crédit | EC |
| Don défaut seed | `7541` (corrigé depuis 708) | — | Spec B1 déjà |

---

## 6. Questions expert-comptable et suite porteur

### 6.1 Liste pour EC (recherche + terrain)

1. Écarts de caisse : **658/758** ou **678/778** (ou autre) et seuil de tolérance boutique réemploi ?
2. **7070** : numérotation exacte dans le plan Paheko de l’asso (7070 vs 70700) ?
3. **7541** seul ou sous-comptes **754.11 / 754.115** (espèces / chèques) dès le démarrage ?
4. Chèque unique vente + don : confirmer **2 lignes** (7070 + 7541) sur même pièce ?
5. Justificatifs tickets Recyclique : durée, format, export signé périodique ?
6. Bien reçu en don puis **revendu** : 7541 ou 7070 + hors bilan ?
7. Textiles **-18** : classe **8** (CVN) utile à partir de quel volume annuel ?
8. Reçu fiscal **Cerfa** don en caisse : seuils et conditions ?

### 6.2 Suite porteur produit (hors EC)

| Étape | Action |
|-------|--------|
| 1 | Synthèse consultations (après Perplexity) → [artefact 06](../artefacts/2026-05-21_06_synthese-recherche-liaison-paheko-brainstorm.md) |
| 2 | Brainstorm **atelier fermeture** : parcours + branchement module comptage |
| 3 | Brainstorm **atelier ticket mixte** (lien recap, pas PKO en réunion) |
| 4 | Quand stable → epic BMAD « Liaison Paheko v1 » (hors scope de ce fichier) |

---

## 7. Liens

- Répertoire comptes (audio + PRD + recherche) : [2026-05-21_repertoire-comptes-terrain-audio-recyclique.md](2026-05-21_repertoire-comptes-terrain-audio-recyclique.md)
- Prompt / réponse Perplexity : [prompt](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_prompt.md) · [réponse](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md)
