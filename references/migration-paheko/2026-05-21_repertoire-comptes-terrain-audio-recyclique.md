# Répertoire des comptes cités — terrain Paheko, recap, PRD, recherche

**Date :** 2026-05-21  
**Usage :** vérifier avec l’**expert-comptable et Carole** (réunion ou retour écrit).  
**Dernière validation Perplexity :** [2e passe](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md) · [3e passe trous](../recherche/2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md) (2026-05-21). **Multi-caisse :** [lieux de vente](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md). **Clôture :** [procédure T1/T2/T3](2026-05-21_procedure-cloture-liaison-paheko-recyclique.md).  
**Légende statut :**

| Statut | Signification |
|--------|----------------|
| **Retenu v1** | Direction produit + recherche — à valider EC mais implémentable en paramétrage |
| **Retenu PRD** | Déjà dans PRD / spec SuperAdmin |
| **Terrain** | Dit en réunion mai 2026 — pas encore tranché produit |
| **Paheko existant** | Déjà configuré ou vu dans Paheko La Clique |
| **À trancher EC** | Décision comptable obligatoire |
| **Hors v1** | Pas dans la première vague fermeture caisse |
| **Ne pas utiliser** | Erreur seed, historique, ou rejeté |

**Sources :** audio `2026-05-21-recyclique-terrain-paheko`, [recap](../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md), [PRD](2026-04-15_prd-recyclique-caisse-compta-paheko.md), [recherche 1re passe](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md), [validation 2e passe](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md), [multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md), [remboursements 04-02](../recherche/2026-04-02_remboursements-compta-associations-loi-1901_perplexity_reponse.md).

---

## 1. Clôture de caisse — trésorerie et tampons

| Compte | Libellé (tel que cité) | Rôle pour Recyclique | Workflow / moment | Statut | Notes |
|--------|------------------------|----------------------|-------------------|--------|-------|
| **530** | Caisse (espèces) générique | Débit espèces clôture **si une seule caisse** dans l'asso | `cash` mono-site | **Retenu v1** (mono) | Multi-caisse : éviter comme compte terminal — voir **53x** §1 bis |
| **531** | Caisse siège / établ. A caisse 1 | 1er poste physique d'un établissement | Par `cash_register` | **Retenu v1** (multi) | Ex. Paheko « magasin sud » ; [multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) |
| **5311** | Établ. A — caisse 2 | 2e caisse même établissement | Idem | **Retenu v1** (multi) | Grille type 7 caisses — **EC** valide numéros |
| **532** | Établ. B — caisse 1 | Autre établissement | Idem | **Retenu v1** (multi) | |
| **5321** | Établ. B — caisse 2 | | Idem | **Retenu v1** (multi) | |
| **5322** | Établ. B — caisse 3 | | Idem | **Retenu v1** (multi) | |
| **533** | Stand / mobile 1 | Caisse nomade | Idem | **Retenu v1** (multi) | |
| **5331** | Stand / mobile 2 | | Idem | **Retenu v1** (multi) | |
| **511** | Valeurs à l’encaissement | **Carte bancaire** (CB), pas chèques | Moyen `card` | **Retenu v1** | Validation : CB → **511**, pas 512 ; chèques → **5112** |
| **511 205** | Billets (comptage) | **Module comptage RecyClique** — pas compte Paheko | Comptage fermeture | **Ne pas utiliser** (plan) | Supprimer du plan Paheko si présent ; garder en UI RecyClique |
| **511 210** | Pièces (comptage) | Idem | Comptage | **Ne pas utiliser** (plan) | Idem 511 205 |
| **511 220** | Tampon virements | Virements entrants | — | **À corriger** | → **512** ou **58** (virement interne), pas sous-compte 511 |
| **5112** | Chèques à encaisser | Débit ventes/dons par chèque ; solde au dépôt banque | Moyen `check` | **Retenu v1** | Standard Paheko ; aligner config terrain qui utilisait 511 |
| **512** | Banque | Compte(s) courant(s) ; crédit CB/chèques après encaissement | `transfer` ; dépôt 5112→512 | **Retenu v1** | Plusieurs 512 possibles si plusieurs banques — **EC** si multi-banques |
| **1630** | « 1630 espèces » | — | — | **Ne pas utiliser** | N’existe pas PCG/PCA — confusion avec **530** |
| **58** | Virements internes | Transit entre trésoreries (ex. retrait banque → caisse) | Virements internes | **Retenu v1** | Solde ≈ 0 ; **jamais** achats espèces magasin |
| **53** | Oral « caisse » (classe) | — | — | **Ne pas utiliser** comme compte | Saisir le **53x** du poste (531, 532…), pas « 53 » |

---

## 1 bis. Multi-caisse — règle récap

Voir [2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md). En bref : **`cash_registers`** RecyClique = **Lieu de vente** Paheko ; compte espèces **par poste** ; virements entre caisses via **58**.

---

## 2. Produits — ventes et dons (classe 70 / 75)

| Compte | Libellé | Rôle Recyclique | Workflow | Statut | Notes |
|--------|---------|-----------------|----------|--------|-------|
| **707** | Ventes de marchandises (générique) | **Ne pas** utiliser pour tout le réemploi (lisibilité) | — | **Ne pas utiliser** (terrain C) | 1re année asso parfois en 707 — à migrer |
| **7070** | Ventes de **réemploi** | Crédit ventes à la clôture ; défaut SuperAdmin | Toute vente payante réemploi | **Retenu v1** | Décision métier A + PRD |
| **7073** | Sous-compte textile (ex. seed test) | Ventilation par famille | — | **Ne pas utiliser** | Spec I1 : remplacer par 7070 |
| **754** | Dons (globalité oral) | Regroupement oral des dons | — | **Terrain** | Plan : sous-comptes en dessous |
| **754.1** / **754.10** / **754.11** | Dons manuels ; synthèse vs écriture courante | **754.11** = écritures quotidiennes dons (audio) | Dons caisse | **Terrain** + **Paheko existant** | 754.10 = synthèse (audio) |
| **7541** | Dons manuels (PCA) | Crédit **dons en caisse** (surplus, don explicite) | Clôture T1 ; moyen `donation` | **Retenu v1** | **Seul compte don caisse v1** ; fusion 754.xx → N+1 (EC) |
| **7542** | Dons affectés projet | Si subventionneur l’exige | Clôture T1 | **À trancher EC** | 3e passe R3 — sinon rester sur **7541** |
| **754.115** | Dons manuels **chèque** | Séparer dons chèque vs espèces | Clôture + rapprochement banque | **À trancher EC** | Utile si volume ; sinon fusion **7541** |
| **754.111** | Dons **projet** | Affectation projet | Ateliers | **À trancher EC** / **Hors v1** | PKO-009 ; candidat **7542** dons affectés |
| **754.12** | Abandon de frais bénévoles | Notes de frais / km | Module adjacent | **Hors v1** | PKO-023 |
| **754.900** | (cite oral, sens flou) | — | — | **À clarifier** | Identifier dans plan Paheko réel avant décision |
| **708** | Produits activités annexes | Ancien défaut don | — | **Ne pas utiliser** | Spec B1 corrigé → 7541 |
| **7041** | (STT « 704 1 ») | Probable **7541** | — | **Ne pas utiliser** | Erreur transcription |
| **771.3** | Libéralités exceptionnelles | Dons **ponctuels** importants | Pas caisse courante | **Hors v1** | Audio : vs 754.11 habituel |

---

## 3. Charges, écarts, exercices antérieurs

| Compte | Libellé | Rôle Recyclique | Workflow | Statut | Notes |
|--------|---------|-----------------|----------|--------|-------|
| **672** | Charges sur exercices antérieurs | **Débit** remboursement client si vente sur exercice **clos** | Opération spéciale remboursement | **Retenu v1** | Confirmé validation ; **réimputation fin d’exercice** — **EC** |
| **467** | Comptes débiteurs/créditeurs | Ancien défaut remboursement | — | **Ne pas utiliser** | Spec B2 |
| **658** | Charges diverses gestion courante | Écart caisse **manque** (T3) | Après module comptage | **Retenu v1** | Seuil **±2 €** ; blocage clôture si dépassé |
| **758** | Produits divers gestion courante | Écart caisse **trop-perçu** (T3) | Idem | **Retenu v1** | Idem |
| **678** / **778** | Erreur de caisse (natif Paheko) | Clôture extension Caisse native | — | **Ne pas utiliser** (RecyClique) | Pas de 678/778 plugin documenté ; **désactiver synchro auto** Paheko — 3e passe R1 |
| **709** | (avoir) | Contre-passation remboursement | — | **Ne pas utiliser** | Remb. courant → **7070** débit ; clos → **672** (T2) |
| **772** | Produits exercices antérieurs | Remboursement client | — | **Ne pas utiliser** | PRD : inadapté remboursement |
| **606** / **607** / **601** / **608** | Achats / charges | Décaissement achat courant (exemple 10 €) | Sortie caisse pour achat | **Hors v1** | Exemple conversation 471 — charge + banque ou 53 |

---

## 4. Attente et décaissements (débat terrain)

| Compte | Libellé | Rôle | Workflow | Statut | Notes |
|--------|---------|------|----------|--------|-------|
| **471** | Compte d’attente | Sortie espèces **sans affectation connue** ; monnaie en attente (débat) | Décaissement exceptionnel | **À trancher EC** | PKO-013 ; audio : éviter si achat connu |
| **471.5** | Compte de transit (proposition IA) | Variante proposée en séance | — | **À trancher EC** | Non retenu comme décision |
| **472** | Dépenses à classer | Doublon 471 pour boutique | — | **Ne pas utiliser** | Validation : quasi-inutile en fonctionnement normal |

---

## 5. Hors bilan / matière / CVN (classe 8)

| Compte | Libellé | Rôle Recyclique | Workflow | Statut | Notes |
|--------|---------|-----------------|----------|--------|-------|
| **86x / 87x** | Contributions volontaires en nature (emplois/ressources) | Valorisation optionnelle dons matière, bénévolat | Stats / rapport ; **pas** clôture caisse € | **Recherche** → **EC** | Dons textile **moins de 18 ans** : trace **kg** RecyClique v1 sans Paheko |
| Engagements hors bilan | (pas de numéro unique) | Entrée don matière si valorisation | Réception / stock | **EC** | Recherche C1 — vente ultérieur bien donné : 7541 vs 7070 |

---

## 6. Autres comptes cités (périmètre connexe)

| Compte | Contexte | Lien Recyclique |
|--------|----------|-----------------|
| **756** | Cotisations (HelloAsso spec) | Paiements en ligne — hors caisse magasin |
| **603** | Variation stocks (guide 2025) | Flux matière historique — pas clôture caisse v1 |

---

## 7. Matrice workflow → comptes (v1 fermeture)

```text
Journée caisse (Recyclique)
  → tickets (lignes payantes → futur 7070 ; lignes don textile −18 ans → pas €)
  → payment_transactions (espèces, chèque, CB, don surplus → 7541)
  → fin de journée : MODULE comptage (pièces/billets) → écart documenté [658/758 EC]
  → fermeture session : snapshot par moyen de paiement
  → Paheko **T1** (ventes + dons), **par poste** :
        Débit 53x / 5112 / 511 — Crédit 7070 + 7541
  → Paheko **T2** si remboursements : 7070 ou 672 débit — trésorerie crédit (1 pièce / remb.)
  → Paheko **T3** si écart ≤ 2 € : 658 ou 758 ↔ 53x du poste
  → Plus tard : chèques 5112→512 ; CB 511→512 ; virements 58
  → tickets PDF/CSV archivés dans Recyclique (justificatif)
```

**Hors ce schéma v1 :** remboursements (7070/672 + trésorerie), décaissements 471/58, ateliers 754.111, notes de frais 754.12, CVN classe 8.

---

## 8. Checklist validation EC (à cocher en réunion)

- [ ] Plan Paheko : **53x** (ou **530** si mono-caisse), **511**, **5112**, **512**, **7070**, **7541** — pas de **511-205/210** dans le plan
- [ ] Cohérence chèques : tout converge sur **5112** (RecyClique = Paheko terrain)
- [ ] Arborescence **754** : pas de double 754.xx + 7541
- [ ] **Grille 53x** multi-postes (531–5331) validée EC — voir [multi-caisse](2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md)
- [ ] Tableau **poste RecyClique → lieu Paheko → compte 53x**
- [ ] Écarts : **658/758** (T3), seuil **±2 €** ; synchro auto Paheko caisse **désactivée**
- [ ] Migration **707 → 7070** N-1 : **non** (note annexe seulement)
- [ ] **672** : procédure fin d’exercice
- [ ] Chèque mixte vente + don : 2 lignes crédit (confirmé recherche)
- [ ] Dons textile moins de 18 ans (kg) : RecyClique seul OK v1
- [ ] **754.900** identifié dans plan réel

---

*Dernière mise à jour : 2026-05-21 — 2e + 3e passe Perplexity, procédure T1/T2/T3.*
