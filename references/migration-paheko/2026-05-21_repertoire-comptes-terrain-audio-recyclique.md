# Répertoire des comptes cités — terrain Paheko, recap, PRD, recherche

**Date :** 2026-05-21  
**Usage :** vérifier avec l’**expert-comptable et Carole** (réunion ou retour écrit). Pour Perplexity : le plan actuel est **recopié dans** [prompt validation](../recherche/2026-05-21_validation-comptes-liaison-paheko_perplexity_prompt.md) (bloc autonome).  
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

**Sources :** audio `2026-05-21-recyclique-terrain-paheko`, [recap](../artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md), [PRD](2026-04-15_prd-recyclique-caisse-compta-paheko.md), [recherche Perplexity](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md), [remboursements 04-02](../recherche/2026-04-02_remboursements-compta-associations-loi-1901_perplexity_reponse.md).

---

## 1. Clôture de caisse — trésorerie et tampons

| Compte | Libellé (tel que cité) | Rôle pour Recyclique | Workflow / moment | Statut | Notes |
|--------|------------------------|----------------------|-------------------|--------|-------|
| **530** | Caisse (espèces) | Débit encaissements espèces + dons espèces à la **clôture** ; crédit remboursements espèces | Fermeture session ; moyen paiement `cash` | **Retenu PRD** | Audio : aussi décrit comme « tampon » / cumul débit-crédit journée |
| **531** | (non nommé PCA) — fond de caisse | Fond de caisse : crédit/débit entre ouverture et fermeture | Clôture ; module comptage | **Terrain** → **EC** | Cité audio : « 531 crédit et 531 débit » — confirmer vs fond géré dans session Recyclique |
| **511** | Chèques / tampon ; **511 205** billets ; **511 210** pièces | Tampon avant banque ; ventilation billets vs pièces (comptage) | Clôture + remise banque | **Terrain** + **EC** | PRD utilise plutôt **5112** pour chèques — **aligner sur extrait Paheko** |
| **5112** | Chèques à encaisser | Débit ventes/dons par chèque | Moyen paiement `check` | **Retenu PRD** | Audio mélange 511 / 512 — voir ligne 512 |
| **512** | Banque ; CB ; « chèques à encaisser » ; tampon | Carte, virements, parfois chèques selon config Paheko | Moyens `card`, `transfer` | **Retenu PRD** + **Terrain** | Audio : plusieurs **512** possibles (espèces dons, virements dons) — **EC** |
| **1630** | « 1630 espèces » (doc recherche A) | **Incertain** — possible confusion STT avec 530 | — | **À trancher EC** | Segment 011 audio ; vérifier plan Paheko réel |
| **58** | Caisse (dans exemple IA décaissement) | Virements **internes** entre trésoreries uniquement | Décaissement / pas vente | **Terrain** → **EC** | Consensus audio fin séance : **pas** pour achat espèces courant |
| **53** | Caisse (formulation B) | Mouvements espèces en caisse (encaissement / décaissement) | Décaissements | **Terrain** → **EC** | Souvent = langage « classe 53 » ; rapprocher **530** |

---

## 2. Produits — ventes et dons (classe 70 / 75)

| Compte | Libellé | Rôle Recyclique | Workflow | Statut | Notes |
|--------|---------|-----------------|----------|--------|-------|
| **707** | Ventes de marchandises (générique) | **Ne pas** utiliser pour tout le réemploi (lisibilité) | — | **Ne pas utiliser** (terrain C) | 1re année asso parfois en 707 — à migrer |
| **7070** | Ventes de **réemploi** | Crédit ventes à la clôture ; défaut SuperAdmin | Toute vente payante réemploi | **Retenu v1** | Décision métier A + PRD |
| **7073** | Sous-compte textile (ex. seed test) | Ventilation par famille | — | **Ne pas utiliser** | Spec I1 : remplacer par 7070 |
| **754** | Dons (globalité oral) | Regroupement oral des dons | — | **Terrain** | Plan : sous-comptes en dessous |
| **754.1** / **754.10** / **754.11** | Dons manuels ; synthèse vs écriture courante | **754.11** = écritures quotidiennes dons (audio) | Dons caisse | **Terrain** + **Paheko existant** | 754.10 = synthèse (audio) |
| **7541** | Dons manuels (PCA) | Crédit **dons en caisse** (surplus, don explicite) | Clôture ; moyen `donation` | **Retenu PRD** | Remplace ancien défaut **708** |
| **754.115** | Dons manuels **chèque** | Séparer dons chèque vs espèces | Clôture + rapprochement banque | **Terrain** | PKO-002, PKO-011 — **EC** v1 ou v2 |
| **754.111** | Dons **projet** (ex. atelier cartes 69 €) | Affectation analytique projet | Encaissement atelier sans ligne produit | **Terrain** → **Hors v1** | PKO-009 |
| **754.12** | Abandon de frais bénévoles | Notes de frais / km | Module adjacent | **Hors v1** | PKO-023 |
| **754.900** | (cite oral, sens flou) | — | — | **À clarifier** | Vérifier audio / plan |
| **708** | Produits activités annexes | Ancien défaut don | — | **Ne pas utiliser** | Spec B1 corrigé → 7541 |
| **7041** | (STT « 704 1 ») | Probable **7541** | — | **Ne pas utiliser** | Erreur transcription |
| **771.3** | Libéralités exceptionnelles | Dons **ponctuels** importants | Pas caisse courante | **Hors v1** | Audio : vs 754.11 habituel |

---

## 3. Charges, écarts, exercices antérieurs

| Compte | Libellé | Rôle Recyclique | Workflow | Statut | Notes |
|--------|---------|-----------------|----------|--------|-------|
| **672** | Charges sur exercices antérieurs | **Débit** remboursement client si vente sur exercice **clos** | Opération spéciale remboursement | **Retenu PRD** | Candidat EC ; remplace **467** |
| **467** | Comptes débiteurs/créditeurs | Ancien défaut remboursement | — | **Ne pas utiliser** | Spec B2 |
| **658** | Charges diverses gestion courante | Écart caisse **manque** | Après module comptage | **Recherche** → **EC** | Paheko plugin cite **678** — harmoniser |
| **758** | Produits divers gestion courante | Écart caisse **trop-perçu** | Idem | **Recherche** → **EC** | Paheko plugin cite **778** |
| **678** / **778** | Erreur de caisse (plugin Paheko) | Écart clôture native Paheko | Si on réutilise logique plugin | **Paheko existant** | [audit-caisse-paheko](audits/audit-caisse-paheko.md) |
| **709** | (avoir) | Contre-passation remboursement J+N | Remboursements | **Recherche 04-02** | Recyclique fait plutôt 7070 débit + trésorerie crédit |
| **772** | Produits exercices antérieurs | Remboursement client | — | **Ne pas utiliser** | PRD : inadapté remboursement |
| **606** / **607** / **601** / **608** | Achats / charges | Décaissement achat courant (exemple 10 €) | Sortie caisse pour achat | **Hors v1** | Exemple conversation 471 — charge + banque ou 53 |

---

## 4. Attente et décaissements (débat terrain)

| Compte | Libellé | Rôle | Workflow | Statut | Notes |
|--------|---------|------|----------|--------|-------|
| **471** | Compte d’attente | Sortie espèces **sans affectation connue** ; monnaie en attente (débat) | Décaissement exceptionnel | **À trancher EC** | PKO-013 ; audio : éviter si achat connu |
| **471.5** | Compte de transit (proposition IA) | Variante proposée en séance | — | **À trancher EC** | Non retenu comme décision |
| **472** | Dépenses à classer | Rarement utilisé (audio) | — | **Hors v1** | |

---

## 5. Hors bilan / matière / CVN (classe 8)

| Compte | Libellé | Rôle Recyclique | Workflow | Statut | Notes |
|--------|---------|-----------------|----------|--------|-------|
| **86x / 87x** | Contributions volontaires en nature (emplois/ressources) | Valorisation optionnelle dons matière, bénévolat | Stats / rapport ; **pas** clôture caisse € | **Recherche** → **EC** | Textiles -18 : trace **kg** Recyclique v1 sans Paheko |
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
  → tickets (lignes payantes → futur 7070 ; lignes -18 → pas €)
  → payment_transactions (espèces, chèque, CB, don surplus → 7541)
  → fin de journée : MODULE comptage (pièces/billets) → écart documenté [658/758 EC]
  → fermeture session : snapshot par moyen de paiement
  → Paheko (lot) :
        Débit 530 / 5112 / 512… (selon moyens)
        Crédit 7070 (ventes)
        Crédit 7541 (dons caisse)
  → tickets PDF/CSV archivés dans Recyclique (justificatif)
```

**Hors ce schéma v1 :** remboursements (7070/672 + trésorerie), décaissements 471/53/58, ateliers 754.111, notes de frais 754.12, CVN classe 8.

---

## 8. Checklist validation EC (à cocher en réunion)

- [ ] Plan Paheko : liste exacte des comptes **530, 511, 5112, 512, 531, 7070, 7541** (+ sous-comptes 754.x si oui)
- [ ] Règle **511 205 / 210** vs comptage module Recyclique
- [ ] Écarts caisse : **658/758** ou **678/778**
- [ ] Chèque mixte vente + don : 2 lignes OK
- [ ] -18 kg : Recyclique seul OK pour v1
- [ ] Décaissements : 53/530/58/471 — report v2 confirmé

---

*Dernière mise à jour : 2026-05-21 — compléter après synthèse porteur et retour Carole / EC.*
