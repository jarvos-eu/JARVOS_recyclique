# Analyse déclarations — Refashion / DPAV textile (La Clique)

**Date :** 2026-07-07  
**Partenaire :** Refashion — **REP Textiles, Linge de maison, Chaussures (TLC)**  
**Rôle La Clique :** **DPAV** (détenteur de point d’apport volontaire) — structure ESS au sens loi 2014-856  
**Sources :** 5 fichiers sous `partenaires/refashion/` — **pas de `declarations-la-clique/`**

---

## Résumé exécutif

Refashion est l’éco-organisme de la filière **TLC**. La Clique n’a pas encore de grilles trimestrielles remplies dans le dépôt K-Drive : seulement le **dossier de conventionnement DPAV** (formulaire vierge 2025, contrat-type ESS 2024, matrice PAV) et la **documentation AMI TLC 2025** du RNRR (appel à projets cofinancement réemploi, distinct des déclarations REP). Les obligations déclaratives passent par le **Portail Refashion** : tonnages **par PAV**, destinations (réemploi local, opérateur de tri, repreneurs identifiés), délai **40 jours** après clôture trimestrielle. La méthodologie sans balance homologuée peut reposer sur l’**enregistrement des ventes et dons** — aligné avec les besoins stats LCQ-001…003.

---

## Obligations déclaration (contrat-type DPAV ESS 2024)

| Obligation | Détail |
|------------|--------|
| **Périodicité** | Trimestrielle — art. 12.3 et 15.3 |
| **Délai** | Au plus tard **40 jours** après fin de trimestre |
| **Canal** | **Portail** `https://refashion.fr` (extranet, facturation électronique) |
| **Contenu** | Quantités **par PAV** (origine, poids) ; destination des tonnages (annexe 6 repreneurs / opérateurs de tri) ; tickets de pesée sur balance homologuée **ou** méthodologie alternative |
| **PAV** | Matrice point d’apport à jour ; mise à jour **quotidienne** des adresses (formulaire conventionnement) |
| **Signalétique** | Logo Repère + consignes harmonisées sur chaque PAV (annexe 1) |
| **Surplus / écrémé** | Partenariat repreneur obligatoire (SIRET dans le dossier) ; reprise Refashion si refus opérateurs de tri |
| **Collectes ponctuelles** | Déclaration sous 3 mois (annexe 4) — dates, PAV participants, tonnages, destinataires |
| **Soutien financier collecte** | Chapitre II.C — **actuellement nul** tant que l’Observatoire n’a pas réactualisé les coûts (art. 15.2) ; facturation post-déclaration si montant > 0 |

**Exclusions du périmètre « collecte soutenue » :** TLC **d’occasion** (non déchets au moment de la remise) — art. 13 ; articles **humides ou souillés**.

**Méthodologies sans pesée** (formulaire conventionnement) : enregistrement ventes/dons · reconstitution par borne · reconstitution par sacs collectés.

---

## Inventaire dépôt

| Fichier | Emplacement | Nature |
|---------|-------------|--------|
| `demande_conventionnement_DPAV_refashion_2025_vdef.pdf` | `referentiels-officiels/` | Formulaire **vierge** — identification DPAV, réseau (case RNRR), pesée, repreneurs |
| `Contrat_Type_DPAV_ESS_version_2024.pdf` | `referentiels-officiels/` | Contrat-type ESS — traçabilité, déclarations, signalétique, annexes 1–7 |
| `Matrice point d'apport.xls` | `referentiels-officiels/` | Grille **PAV** : type (conteneur, association/vestiaire, boutique, déchèterie, ponctuel), adresse, horaires, GPS |
| `250203_AMI_TLC_Catalogue_actions_2025_.xlsx` | `divers/` | **Catalogue AMI** RNRR — 4 axes, montants indicatifs, livrables (hors décla REP) |
| `250203_WIKI_Prsentation_AMI_TLC_2025.pptx` | `divers/` | Présentation AMI — calendrier 2025, pièces (dont **convention DPAV**), FAQ |

**Manquant :** convention signée, déclarations trimestrielles remplies, captures Portail, liste repreneurs complétée, factures soutien Refashion.

---

## AMI TLC 2025 (RNRR — hors déclaration REP)

Appel à projets **Fonds réemploi TLC** (enveloppe adhérents ~673 k€). **Prérequis candidature :** adhérent RNRR à jour, engagement observatoire, **conventionnement Refashion**, dossier avant **06/03/2025**. Contact : `ami-tlc@ressourceries-recycleries.org`.

| Axe | Exemples éligibles | Lien Recyclique |
|-----|-------------------|-----------------|
| 1 — Pédagogie / formation | Tri, merchandising, couture, sensibilisation | Stats ateliers, formations |
| 2 — Remise en état | Machines à coudre, logistique, upcycling | Traçabilité atelier + pièces |
| 3 — Surfaces commerciales | E-commerce, merchandising, **balances / traçabilité** | LCQ-003 ventes ; matériel pesée |
| 4 — Boutiques éphémères | Camion, itinérance TLC | Flux sortie dédiés |

L’AMI peut financer balances, gerbeurs, outils de traçabilité — utile pour passer d’une méthodologie « ventes/dons » à une pesée homologuée.

---

## Mapping brouillon Recyclique → Refashion

**Unité déclarée :** **tonnes** (agrégation kg terrain).

**Granularité Refashion :** par **PAV** (boutique = typologie « Boutique / Point de Vente » ou « Association / Vestiaire » selon accessibilité cartographie).

```
Textile (catégorie boutique La Clique)
├── entrée_don              → collecte PAV (Original, tout venant)
├── entrée_don_moins_18     → idem ; trace kg Recyclique (hors € Paheko)
├── écrémage_local          → réemploi Locale ; justificatifs annexe 6
├── sortie_vente_boutique   → réemploi Locale (LCQ-003)
├── sortie_don_structure    → cession Locale (friperie, vestiaire…)
├── sortie_tri_repreneur    → opérateur de tri / repreneur SIRET (annexe 6)
├── sortie_recyclage        → via opérateur de tri conventionné
└── surplus_refashion       → demande reprise chapitre II.D (refus OT, min. 2 m³)
```

| Concept Refashion | Équivalent terrain La Clique |
|-------------------|------------------------------|
| TLC Usagés | Textile / linge / chaussures collectés (déchets REP) |
| TLC d’Occasion | Pièces encore qualifiées non-déchet — **hors** soutien collecte II.C |
| PAV | Boutique, point de dépôt, éventuel conteneur ou collecte ponctuelle |
| Utilisation Locale | Vente boutique, don interne, remise en état avant revente |
| Ecrémage | Tri « bon état » conservé en structure avant export surplus |

**Distinction métier critique :** catégorie racine **Textile** Recyclique ≠ sous-ensemble **chaussures** / **linge de maison** — Refashion les déclare dans le même agrégat TLC ; sous-ventilation optionnelle si le Portail le permet (à vérifier sur extranet).

**Chevauchements à éviter :** **Cintres**, accessoires non-TLC, **décoration textile** pouvant relever EA (Ecomaison) selon [categories-decla-eco-organismes.md](../../../migration-paheko/categories-decla-eco-organismes.md).

---

## Cas particuliers La Clique

- **Dons textile −18 ans** : fréquents en caisse, **kg sans €** — comptent dans la collecte déclarée si méthodologie « enregistrement ventes et dons » ; pas de flux Paheko clôture v1.
- **Tickets mixtes** (don −18 + ligne payante) : agrégation stats doit séparer les flux pour la décla Refashion.
- **Pas de balance homologuée** documentée dans le dépôt — risque audit art. 9 ; AMI ou investissement matériel possible.
- **Réseau RNRR** coché sur le formulaire — cohérent avec parcours AMI ; conventionnement DPAV **prérequis** des deux côtés.
- La Clique déclare déjà **Ecomaison** + **Ecologic** ; Refashion = **3ᵉ filière REP** active ou en cours d’activation.

---

## Gaps / questions

| # | Gap | Question |
|---|-----|----------|
| 1 | Formulaire conventionnement **non rempli** dans le dépôt | Dossier envoyé à `collecte@refashion.fr` ? Statut convention ? |
| 2 | Aucun export trimestriel type eco-maison | Format exact du Portail (colonnes, modèles) ? |
| 3 | Liste repreneurs / opérateurs de tri absente | Qui reprend le surplus TLC aujourd’hui (SIRET) ? |
| 4 | PAV non cartographiés dans la matrice | Combien de points (boutique seule vs conteneurs) ? |
| 5 | AMI 2025 — échéances mars 2025 passées | La Clique lauréate ou candidature 2026 ? |
| 6 | Soutien financier collecte = 0 € (art. 15.2) | Impact motivation décla vs traçabilité réglementaire seule ? |
| 7 | Aucun mapping Refashion dans le code | Epic 9 — partenaire `refashion` + config PAV ? |

---

## Pistes patch 1.4.5

Hors scope immédiat (**priorité Ecomaison T4 2025**). Préparer néanmoins :

1. **Stats textile** avec sous-flux vente / don / recyclage (LCQ-001…003) → alimentation méthodologie pesée alternative.
2. Entité **`pav_refashion`** (id interne, adresse, typologie matrice) liée au site boutique.
3. Export trimestriel brouillon : kg Textile (+ Chaussures, Linge si ventilés) par PAV et par destination.
4. Ne pas confondre module décla REP et **suivi AMI** (pièces justificatives projets RNRR).

---

## Références locales

- Inventaire dépôt : [artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md](../../../artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md)
- Vision module agnostique : [vision-projet/vision-module-decla-eco-organismes.md](../../../vision-projet/vision-module-decla-eco-organismes.md)
- Analyses sœurs : [valdelia](../valdelia/2026-07-07_analyse-declarations-mapping.md) · [recyclivre](../recyclivre/2026-07-07_analyse-declarations-mapping.md)
