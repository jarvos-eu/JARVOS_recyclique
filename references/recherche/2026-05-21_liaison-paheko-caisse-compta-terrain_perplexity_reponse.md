# Recherche Perplexity — Liaison Paheko : fermeture caisse, comptage, dons, réemploi (terrain)

**Fichier :** `2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md`  
**Date :** 2026-05-21 · **IA :** Perplexity Pro  
**Prompt :** [2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_prompt.md](2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_prompt.md)  
**Ventilation :** [décisions](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) · [répertoire comptes](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) · [synthèse brainstorm](../artefacts/2026-05-21_06_synthese-recherche-liaison-paheko-brainstorm.md)

---

***

# Synthèse exécutive

Recyclique ferme une session de caisse et envoie un récapitulatif à Paheko — pas ticket par ticket. Cette approche est comptablement solide **à condition** que le détail des tickets soit conservé comme justificatif dans Recyclique. Le comptage physique des espèces à la clôture est une bonne pratique incontournable pour toute association avec caisse, même non NF525. Dans Paheko, la caisse est une extension paramétrable avec des moyens de paiement mappés sur des comptes (530, 512…) — les totaux par moyen de paiement peuvent alimenter une écriture agrégée. Les ventes de réemploi s'imputent en **7070** (sous-classe de 707) ; les dons volontaires en caisse en **7541**. Les dons matière (textiles -18) reçus sans flux monétaire ne génèrent **pas d'écriture en compta générale** sauf choix de valoriser les contributions volontaires en nature (comptes de classe 8, facultatif pour les petites structures). Toute décision finale sur les comptes et les écritures reste du ressort d'un expert-comptable.[^1][^2][^3][^4][^5][^6]

***

## Partie A — Fermeture de caisse en association réemploi

### A1. Bonnes pratiques de clôture (sans NF525)

Paheko confirme explicitement que sa caisse est destinée aux associations **non assujetties à la TVA** et n'est donc pas soumise à la certification NF525. Cela allège les contraintes légales, mais pas les exigences de bonne gestion. Les bonnes pratiques documentées pour les associations converge sur quatre points  :[^7][^2][^8]

- **Fréquence** : clôture à chaque session de caisse (journée ou événement), pas hebdomadaire
- **Qui fait quoi** : la même personne ne doit pas tenir la caisse et valider la clôture (séparation des fonctions, même sommaire)
- **Journal de caisse** : tenir un livre ou fichier chronologique avec solde d'ouverture, encaissements, décaissements, solde de fermeture — en format exportable ou PDF[^7]
- **Rapprochement banque** : les chèques et tickets CB du jour sont rapprochés en fin de mois lors du relevé bancaire ; les espèces déposées génèrent une pièce de versement[^2]


### A2. Comptage physique des espèces et gestion des écarts

Le comptage manuel est considéré **indispensable à chaque fermeture de caisse dès lors que des espèces sont encaissées**. Il consiste à compter pièces et billets par dénomination pour obtenir le solde réel, à comparer au solde théorique (fond de départ + encaissements - décaissements).[^1][^2][^7]

En cas d'écart  :[^2][^7]

- **Documenter systématiquement** : montant, date, hypothèse d'explication
- **Seuil de tolérance** : à définir en interne (ex. ±1 ou 2 €) ; au-delà, investigation obligatoire
- **Écriture comptable de l'écart** : passer en **658 « Charges diverses de gestion courante »** (écart négatif/manque) ou **758 « Produits divers de gestion courante »** (trop-perçu) — *à valider avec un expert-comptable*
- Opérationnellement : l'écart est noté sur la feuille de clôture signée, conservée comme justificatif


### A3. Paheko et la session de caisse

L'extension Caisse de Paheko  modélise :[^9][^3]

- Des **moyens de paiement** paramétrables, chacun mappé sur un compte (530 espèces, 512x CB, 511 chèques…)
- Un **fond de caisse** séparé par moyen de paiement informel depuis la v1.3.18[^10]
- Des **statistiques et totaux** par session accessibles dans « Gestion et statistiques »
- La caisse génère des **écritures comptables** liées à chaque vente ou adhésion enregistrée

En revanche, Paheko ne dispose pas (documentation publique actuelle) d'un module natif de « clôture de session » avec saisie du réel compté vs théorique. C'est précisément le rôle que jouerait Recyclique en envoyant les totaux à Paheko sous forme d'une écriture agrégée par session.

### A4. Risques du récap par session vers Paheko

L'approche « une écriture (ou lot) par session, pas ticket par ticket » est comptablement acceptable  **sous réserve de** :[^1]


| Condition | Explication |
| :-- | :-- |
| Justificatifs internes | Tickets détaillés conservés dans Recyclique (export quotidien recommandé) |
| Totaux ventilés par compte | L'écriture Paheko doit distinguer 7070, 7541, 530, 512, 511… |
| Traçabilité des dons | Les dons en caisse ne doivent pas être agrégés avec les ventes dans la même ligne |
| Conservation | Durée : 10 ans pour les pièces comptables justificatives (*à valider EC*) |

Un récap non ventilé (une seule ligne « recettes du jour ») serait risqué en cas de contrôle ou d'audit.[^1]

### A5. UX du module comptage monnaie — analogies autres secteurs

Des exemples applicables par analogie  :[^7][^2]

- **Retail associatif / supermarché solidaire** : comptage par tiroir avec grille pièces/billets pré-imprimée (5×2 €, 3×1 €…) — total auto-calculé
- **ONG / humanitaire** : feuille de clôture cosignée par deux personnes, archivée PDF
- **Coopératives** : fond de caisse prédéfini laissé dans le tiroir, seul l'excédent est versé ; la « feuille de versement » = justificatif du dépôt banque
- **UX recommandée** : interface grille de comptage (dénominations × quantités = total), affichage immédiat de l'écart vs théorique, validation en deux étapes (saisie puis confirmation)

***

> **Pour Recyclique — Partie A**
> - ✅ **Retenir** : clôture par session obligatoire, comptage espèces = module dédié (décision déjà prise OK), feuille de clôture PDF exportable à archiver
> - ✅ **Retenir** : l'écriture agrégée vers Paheko est valide si le détail ticket reste dans Recyclique comme justificatif
> - ✅ **Retenir** : ventiler l'écriture Paheko par compte (7070, 7541, 530, 512, 511) et par moyen de paiement — pas une ligne unique
> - ❌ **Rejeter** : agréger don + vente sur la même ligne comptable dans Paheko
> - ❓ **Question EC** : quel compte pour les écarts de caisse (658/758) et quel seuil de tolérance raisonnable pour une boutique réemploi ?

***

## Partie B — Ventes réemploi (7070), dons en caisse (7541), paiements mixtes

### B1. Compte 7070 vs 707 — usages réels

Le Plan Comptable Associatif (PCA) utilise la **classe 70** pour les ventes, avec une numérotation adaptée  :[^11][^12]

- **707** = ventes de marchandises (plan comptable général)
- **7070** (ou **70700** selon les plans) = sous-compte spécifique que les ressourceries utilisent pour distinguer les **ventes de biens de réemploi** des autres recettes commerciales

Le risque de mélange est réel : si tout est mis en 707, on perd la lisibilité sur la part « réemploi » des recettes, ce qui peut compliquer les rapports d'activité et les demandes de subventions. *À confirmer avec un expert-comptable spécialisé associations.*

### B2. Compte 7541 et ventilation 754.x

Le compte **7541 « Dons manuels »** est le compte standard PCA pour les dons reçus en caisse  :[^13][^12]

- Les **dons en espèces** transitent par le compte 530 (Caisse) avant d'être éventuellement versés en banque (512)
- Les **dons par chèque** passent par un compte transitoire **511 « Chèques à encaisser »** puis 512 banque lors de la remise
- La ventilation en sous-comptes **754.1** (espèces), **754.2** (chèques), **754.3** (projets affectés) est une bonne pratique — pas une obligation légale — qui facilite le rapprochement bancaire mensuel[^12]


### B3. Chèque unique = don + vente : plusieurs lignes sur une même pièce

Un chèque de 15 € couvrant 12 € de vente + 3 € de don volontaire : la **bonne pratique** est de saisir **une seule pièce comptable** (le chèque) avec **deux lignes**  :[^4]

- Ligne 1 : débit 511 / crédit 7070 = 12 €
- Ligne 2 : débit 511 / crédit 7541 = 3 €

Il n'y a **aucun découpage physique du chèque**. C'est l'écriture comptable qui ventile, pas le support. Contra-exemple à éviter absolument : enregistrer les 15 € en 7070 puis faire une « régularisation » ultérieure — cela crée des flux incohérents difficiles à auditer.

### B4. Surplus volontaire vs don saisi par erreur

La distinction UX est critique  :[^2][^7]

- **Surplus volontaire** : le client dit « gardez la monnaie » après paiement d'une vente → c'est un **don en caisse** → saisir séparément en 7541 dans Recyclique, pas dans la ligne vente
- **Don saisi comme moyen de paiement par erreur** : si l'opérateur saisit le surplus en « paiement » pour solder la transaction, la vente est correcte mais le don disparaît dans la recette — risque de sous-déclaration des dons

Bonne pratique UX : proposer explicitement **après validation du paiement** un bouton « Le client souhaite faire un don supplémentaire ? » — séparation claire des flux.

### B5. Paheko : moyens de paiement et écritures multi-lignes

Paheko permet de configurer autant de moyens de paiement que nécessaire, chacun mappé sur un compte comptable. L'extension Caisse génère des écritures automatiques à chaque vente. Pour les paiements mixtes (5 € espèces + 7 € CB) :[^3]

- Paheko gère nativement le **paiement en plusieurs fois** (selon la doc sommaire )[^14]
- Chaque moyen de paiement alimentera son compte de trésorerie respectif (530 espèces, 512 CB)
- La ventilation multi-produits (vente + don sur un même ticket) dépend de la configuration des **produits** dans l'extension Caisse — chaque produit est mappé sur son compte de produit[^15]

***

> **Pour Recyclique — Partie B**
> - ✅ **Retenir** : utiliser 7070 pour ventes réemploi et 7541 pour dons caisse — deux produits distincts dans Recyclique, deux lignes dans l'écriture Paheko
> - ✅ **Retenir** : paiement mixte ticket = plusieurs lignes écriture Paheko (une par compte de produit, une par moyen de paiement) — la mécanique Paheko le supporte via mapping produits/comptes
> - ✅ **Retenir** : surplus volontaire = bouton don explicite dans l'UX Recyclique, pas inclus dans le solde de vente
> - ❌ **Rejeter** : agréger 7070 et 7541 dans le même total de session sans ventilation
> - ❓ **Question EC** : faut-il des sous-comptes 754.1/754.2 (espèces/chèques) dès le départ, ou 7541 unique suffit-il pour une petite ressourcerie ?

***

## Partie C — Dons matière / textiles -18, sorties sans flux monétaire

### C1. Traitement comptable des apports/sorties sans contrepartie monétaire

Pour une association de réemploi, les **marchandises reçues par don** (textiles, vaisselle…) entrent dans un **flux hors bilan** tant qu'elles ne sont pas vendues  :[^5][^4]

- **Entrée du don matière** : information hors bilan en « engagements reçus » (valeur estimée à la valeur vénale) — *si l'association choisit de les valoriser*
- **Vente ultérieure** : solde de l'engagement hors bilan + écriture 7541 (pas 7070) pour la recette de vente d'un bien reçu en don[^4]
- **Sortie matière sans vente** (textile -18 donné gratuitement en boutique) : pas d'écriture en compta générale standard — reste dans l'outil métier


### C2. Textiles -18 et contributions volontaires en nature (CVN)

Le PCA modernisé (applicable depuis 2020, consolidé 2025) introduit les comptes de **classe 8** pour les **contributions volontaires en nature**  :[^6][^5]

- **Compte 86x** (emplois) / **87x** (ressources) : permettent de retracer bénévolat, mises à disposition, dons en nature valorisés
- **Application aux textiles -18** : si l'association valorise ces sorties (ex. en kg × prix de marché estimé), elle peut les enregistrer en classe 8
- **Mais** : c'est **facultatif** pour les petites structures, et nécessite une information « fiable et quantifiable »  — un suivi kg dans Recyclique suffit sans forcément alimenter Paheko[^6]

La trace reste **hors compta générale** dans la majorité des petites ressourceries, dans l'outil métier (Recyclique) uniquement.

### C3. Ticket mixte : partie don -18 + partie payante

En pratique, le ticket mixte génère deux natures de flux  :[^5][^4]

- **Partie payante** → écriture comptable normale (7070 + compte de trésorerie)
- **Partie don matière -18** → aucune écriture monétaire ; trace dans Recyclique (article, quantité, éventuellement kg)

Le jour de la clôture, Recyclique envoie à Paheko **uniquement les totaux monétaires** ; la ligne « don -18 » ne génère aucun flux € et n'apparaît pas dans l'écriture Paheko. La traçabilité est assurée par Recyclique qui conserve le ticket complet. C'est une séparation propre et cohérente avec les pratiques documentées.[^5]

### C4. Périmètre expert-comptable vs logiciel métier

| Domaine | Qui décide |
| :-- | :-- |
| Choix de valoriser ou non les CVN (classe 8) | Expert-comptable + AG de l'association |
| Comptes à utiliser (7541 vs 7070 pour vente d'un bien reçu en don) | Expert-comptable |
| Seuil à partir duquel tracer en hors bilan | Expert-comptable |
| Suivi kg, comptage pièces, catégories produits | Outil métier (Recyclique) — pas de Paheko |
| Export des justificatifs tickets pour audit | Recyclique (archivage) |
| Valorisation des textiles -18 pour rapport d'activité | Outil métier + décision associative |


***

> **Pour Recyclique — Partie C**
> - ✅ **Retenir** : ligne « don matière / -18 » sur un ticket = aucun flux € à envoyer à Paheko ; traçabilité Recyclique seule suffit
> - ✅ **Retenir** : ticket mixte → seule la partie payante alimente l'écriture de clôture Paheko
> - ✅ **Retenir** : prévoir un champ « kg » ou « unités » dans Recyclique pour le suivi matière (statistiques internes, rapports subventions) sans écriture Paheko
> - ❌ **Rejeter** : tenter d'envoyer les sorties matière à Paheko sans décision préalable de l'EC sur la valorisation CVN
> - ❓ **Question EC** : l'association doit-elle adopter la comptabilisation en classe 8 (CVN) pour les textiles -18, et si oui, à partir de quel volume annuel cela devient-il utile ?

***

## Questions à poser à l'expert-comptable

1. **Quel compte pour les écarts de caisse** (trop-perçu ou manque) — 658/758 ou autre — et quel seuil de tolérance est raisonnable pour notre activité ?
2. **7070 ou autre sous-compte** pour les ventes de réemploi : quelle numérotation adopter dans notre plan comptable Paheko pour distinguer les ventes réemploi des autres recettes ?
3. **7541 en sous-comptes 754.1/754.2** (espèces vs chèques) dès le démarrage, ou un seul 7541 suffit-il pour notre taille ?
4. **Chèque unique couvrant vente + don** : confirmer qu'une seule pièce avec deux lignes (7070 + 7541) est la bonne pratique, et comment la documenter simplement en boutique ?
5. **Justificatifs tickets** conservés dans Recyclique (pas dans Paheko) : quelle durée de conservation, quel format acceptable, et faut-il un export périodique signé ?
6. **Vente d'un bien reçu en don** (ex. vaisselle donnée, revendue 2 €) : faut-il utiliser 7541 ou 7070, et faut-il valoriser l'entrée hors bilan ?
7. **Contributions volontaires en nature (textiles -18)** : faut-il les enregistrer en classe 8, à partir de quel seuil annuel, et qui est responsable de la valorisation ?
8. **Dons en caisse avec reçu fiscal** : à partir de quel montant et dans quelles conditions doit-on émettre un reçu Cerfa 11580 pour un don reçu en boutique réemploi ?

***

## Annexe — Sources utiles

- **Paheko — Extension Caisse** : [paheko.cloud/extension-caisse](https://paheko.cloud/extension-caisse)[^9]
- **Paheko — Configuration moyens de paiement** : [paheko.cloud/caisse-configuration-paiement](https://paheko.cloud/caisse-configuration-paiement)[^3]
- **Paheko — Caisse et NF525** (non-TVA confirmé) : [paheko.cloud/caisse-nf525-loi-de-finances](https://paheko.cloud/caisse-nf525-loi-de-finances-certification-attestation)[^8]
- **Paheko — Clôture des comptes FAQ 2026** : [paheko.cloud/foire-aux-questions-la-cloture-des-comptes-29-01-2026](https://paheko.cloud/foire-aux-questions-la-cloture-des-comptes-29-01-2026)[^16]
- **Compta-online — Dons manuels 7541** : [compta-online.com/comptabiliser-le-don-une-association](https://www.compta-online.com/comptabiliser-le-don-une-association-compte-6238-ou-6713-ao2946)[^13]
- **Compta-online — Don matériel, hors bilan, 7541** : [compta-online.com/valorisation-un-don-materiel-pour-une-association](https://www.compta-online.com/valorisation-un-don-materiel-pour-une-association-et-recu-fiscal-t72755)[^4]
- **Institut ISBL — Dons en nature et CVN (PCA 2020)** : [institut-isbl.fr/nouveau-plan-comptable-associatif-les-dons-en-nature](https://institut-isbl.fr/nouveau-plan-comptable-associatif-les-dons-en-nature-ne-sont-pas-tous-des-cvn/)[^5]
- **Associathèque — Contributions volontaires en nature** : [associatheque.fr](https://www.associatheque.fr/fr/gerer-une-association/index.html?amcpage=27)[^6]
- **AssoConnect — Bonnes pratiques gestion caisse** : [help.assoconnect.com](https://help.assoconnect.com/hc/fr/articles/10136128077842-Les-bonnes-pratiques-de-la-gestion-d-une-caisse)[^2]
- **Pennylane — Plan comptable associations 2025** : [pennylane.com/fr/fiches-pratiques/plan-comptable/plan-comptable-associations](https://www.pennylane.com/fr/fiches-pratiques/plan-comptable/plan-comptable-associations)[^12]
- **Topcaisse — Fermeture de caisse** : [topcaisse.fr/fermeture-de-caisse](https://www.topcaisse.fr/fermeture-de-caisse/)[^7]
<span style="display:none">[^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40][^41]</span>

<div align="center">⁂</div>

[^1]: https://libeo.io/blog/comment-faire-une-cloture-de-caisse

[^2]: https://help.assoconnect.com/hc/fr/articles/10136128077842-Les-bonnes-pratiques-de-la-gestion-d-une-caisse

[^3]: https://paheko.cloud/caisse-configuration-paiement

[^4]: https://www.compta-online.com/valorisation-un-don-materiel-pour-une-association-et-recu-fiscal-t72755

[^5]: https://institut-isbl.fr/nouveau-plan-comptable-associatif-les-dons-en-nature-ne-sont-pas-tous-des-cvn/

[^6]: https://www.associatheque.fr/fr/gerer-une-association/index.html?amcpage=27

[^7]: https://www.topcaisse.fr/fermeture-de-caisse/

[^8]: https://paheko.cloud/caisse-nf525-loi-de-finances-certification-attestation

[^9]: https://paheko.cloud/extension-caisse

[^10]: https://paheko.cloud/version-1-3-18

[^11]: https://www.mooncard.co/fr/cas-usage/comptabilite/plan-comptable/associatif

[^12]: https://www.pennylane.com/fr/fiches-pratiques/plan-comptable/plan-comptable-associations

[^13]: https://www.compta-online.com/comptabiliser-le-don-une-association-compte-6238-ou-6713-ao2946

[^14]: https://paheko.cloud/sommaire

[^15]: https://paheko.cloud/caisse-configuration-produits-categories

[^16]: https://paheko.cloud/foire-aux-questions-la-cloture-des-comptes-29-01-2026

[^17]: https://www.ess-bretagne.org/uploads/files/cress_ressources/20240531_Portraits_recycleries-complet.pdf

[^18]: https://www.ressourcerie-acora42.com/association-loi-1901

[^19]: https://www.legalplace.fr/guides/association-loi-1901-vente-objets/

[^20]: https://ressourcerie.fr/wp-content/uploads/2024/08/Guide-RNRR-partenariats-5-teaser-1.pdf-1.pdf

[^21]: https://www.legalstart.fr/fiches-pratiques/association/dissolution-association-que-faire-de-l-argent/

[^22]: https://paheko.cloud/nouveautes-version-1-3-12

[^23]: https://www.keobiz.fr/le-mag/don-compte-comptable/

[^24]: https://www.laressourceriecreative.com

[^25]: https://paheko.cloud/video-comptabilite

[^26]: https://www.instagram.com/p/DU_DhMvCrqp/

[^27]: https://paheko.cloud

[^28]: https://www.pennylane.com/fr/fiches-pratiques/plan-comptable/compte-comptable-don

[^29]: https://associations.gouv.fr/associations-en-difficultes

[^30]: https://paheko.cloud/nouvelles-fin-annee

[^31]: https://fr.wikipedia.org/wiki/Paheko

[^32]: https://wiki.kaz.bzh/paheko/start

[^33]: https://paheko.cloud/foire-aux-questions-25-02-2026

[^34]: https://docs.lacontrevoie.fr/technique/services-auxiliaires/paheko/

[^35]: https://wiki.infini.fr/index.php/Installation_de_paheko

[^36]: https://www.concur.fr/blog/article/plan-comptable-association-pca-2025-definition-obligations-et-bonnes-pratiques

[^37]: https://soyezresolu.org/organiser/paheko/

[^38]: https://www.assoconnect.com/blog/23661-plan-comptable-des-associations-modele-a-telecharger-et-conseils

[^39]: https://paheko.cloud/static/guide_livret.pdf

[^40]: https://done.fr/dons-nature-associations

[^41]: https://paheko.cloud/fonctionnalites-caisse

