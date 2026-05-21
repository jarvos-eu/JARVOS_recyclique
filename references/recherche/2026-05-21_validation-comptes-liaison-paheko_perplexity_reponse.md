# Recherche Perplexity — Validation comptes Liaison Paheko (2e passe)

**Fichier :** `2026-05-21_validation-comptes-liaison-paheko_perplexity_reponse.md`  
**Date :** 2026-05-21 · **IA :** Perplexity Pro  
**Prompt :** [2026-05-21_validation-comptes-liaison-paheko_perplexity_prompt.md](2026-05-21_validation-comptes-liaison-paheko_perplexity_prompt.md)  
**Ventilation :** [décisions](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) · [répertoire](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md) · [synthèse](../artefacts/2026-05-21_09_synthese-validation-comptes-perplexity.md) · [multi-caisse](../migration-paheko/2026-05-21_multi-caisse-lieux-vente-paheko-recyclique.md) · [QA ventilation](../artefacts/2026-05-21_10_qa-ventilation-compta-paheko-2026-05-21.md) · [prompt trous](2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md)

---

# Audit comptable RecyClique × Paheko — Validation plan comptable et paramètres

***

## 1. Tableau récap des 11 questions

| \# | Question | Recommandation | Certitude | Source | Valider EC |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Q1 | Architecture trésorerie clôture | **530** = caisse espèces ; **5112** = chèques à encaisser (PCA/PCG standard) ; **511** = CB/valeurs à l'encaissement ; **512** = compte(s) bancaire(s). Pas besoin de 511-205/511-210 comme sous-comptes séparés pour le comptage — c'est une gestion interne RecyClique, pas un plan comptable. Plusieurs 512 sont possibles (512A courant, 512B Hello Asso, etc.) mais non obligatoires au départ. | Fort | [^1][^2][^3] | Non pour 530/5112 ; oui pour multi-512 si plusieurs banques |
| Q2 | 530 vs « 53 » oral | **530** est le sous-compte standard PCA/PCG pour la caisse. « 53 » oral = raccourci de classe, pas un compte à créer. Dans Paheko, le compte à utiliser est **530** (voire **531** pour une deuxième caisse physique distincte). | Fort | [^4][^3] | Non |
| Q3 | Compte 1630 | **1630 n'existe pas** dans le PCG ni le PCA comme compte espèces. La classe 16 = emprunts et dettes financières. Probablement une confusion orale avec **530**. À supprimer de tout document interne. | Fort | [^5] | Non |
| Q4 | Fond de caisse 531 | **531** est un compte PCG valide pour une *deuxième caisse* ou caisse du siège social distincte [^6][^7]. Si l'association n'a qu'une seule caisse boutique, le fond de caisse peut rester géré via **530** (solde permanent) sans créer 531. Si deux caisses physiques coexistent, utiliser 530 + 531. | Moyen | [^6][^7][^8] | Oui — choix à figer avec EC |
| Q5 | Écarts de caisse : 658/758 vs 678/778 | **658/758** = charges/produits de gestion courante (différences de règlement, petits écarts opérationnels récurrents). **678/778** = charges/produits *exceptionnels* (événements inhabituels, corrections d'erreurs). Pour des écarts de caisse quotidiens d'une boutique associative, **658/758 est plus approprié**. Le plugin Paheko qui utilise 678/778 traite ces écarts comme exceptionnels, ce qui est techniquement acceptable mais moins précis pour un usage récurrent. RecyClique doit aligner sur **658/758**. Seuil de tolérance usuel : ±1 à 2 € (à documenter en règlement intérieur). | Fort | [^9][^10][^11][^12] | Oui — confirmer avec EC le choix 658/758 vs 678/778 |
| Q6 | 7541 vs sous-comptes 754.x | **7541** seul suffit pour démarrer. Les sous-comptes 754.11, 754.115, 754.111 sont des raffinements utiles mais non obligatoires. Si l'association veut distinguer dons espèces / chèques / projets affectés, créer les sous-comptes dès la v1 est préférable pour ne pas migrer plus tard. Si le volume est faible, **7541 unique** est parfaitement régulier. | Moyen | [^13] | Oui — arbitrage avec EC selon volume et exigences subventionneurs |
| Q7 | Compte 58 | **58 = virements internes trésorerie exclusivement** : transit lors d'un retrait banque → caisse ou dépôt caisse → banque [^14][^4][^15]. Solde théorique = zéro en permanence. N'utiliser **jamais** pour des achats espèces magasin (530 débit → 6xx crédit direct). | Fort | [^14][^4][^15] | Non |
| Q8 | 471/472 | **471** (décaissements à classer) et **472** (dépenses à classer) sont des comptes d'attente ponctuels pour flux en suspens. En boutique réemploi, ils ne sont **pas nécessaires en fonctionnement normal** : sortie monnaie = 530 débit → 6xx crédit direct ; retour différé connu = 530 crédit → 672 ou 7xxx si remboursement. Utiles uniquement pour une opération dont la nature n'est pas encore déterminée au moment de la saisie. | Fort | [^5] | Non sauf cas particulier |
| Q9 | 7070 vs 707 vs 70700 | Le PCA adapte la classe 70 librement sous réserve de cohérence interne. **7070** est une convention adoptée par beaucoup de ressourceries pour isoler les ventes de réemploi. Migration depuis 707 : créer le compte 7070 dans Paheko, basculer le paramètre RecyClique, les écritures historiques 707 restent — ne pas reclasser rétroactivement sans accord EC. | Fort | [^13][^5] | Oui — migration historique à valider avec EC |
| Q10 | Chèque vente + don | **Confirmé** : une seule pièce comptable, deux lignes. Débit **5112** (chèques à encaisser, compte standard Paheko [^16][^17]) / Crédit **7070** pour la partie vente + Crédit **7541** pour le don. Pas de compte 511 pour les chèques. | Fort | [^16][^17][^1] | Non |
| Q11 | 672 remboursement exercice clos | **Confirmé** : **672** est le bon compte pour les charges/remboursements d'exercices antérieurs [^18][^19][^20]. **467** (compte de bilan, créditeurs divers) est inadapté car il ne clôture jamais proprement. **772** (produits sur exercices antérieurs) serait la contrepartie côté *produit* mais n'est pas pertinent pour un remboursement client. Attention : selon PCG 2025 art. 1221-67, le compte 672 doit être soldé (réimputé) en fin d'exercice [^18]. | Fort | [^18][^19][^20] | Oui — conditions d'utilisation et solde fin d'exercice à valider avec EC |


***

## 2. Plan comptable cible — Audit complet D.1 + D.2 + D.3

| Compte actuel | Où | Compte recommandé | Action | Commentaire |
| :-- | :-- | :-- | :-- | :-- |
| **530** | Paheko + RecyClique | **530** | ✅ Correct | Caisse espèces — conserver tel quel |
| **531** | Paheko (fond de caisse) | **530 ou 531** | ⚠️ À trancher | Si une seule caisse physique : rester sur 530 et gérer le fond comme solde permanent. Si deux caisses distinctes : 531 justifié. Valider EC. |
| **511** | Paheko + RecyClique (CB) | **511** | ✅ Correct pour CB | Le compte 511 « Valeurs à l'encaissement » s'utilise bien pour les paiements CB (crédit instantané différé d'un ou deux jours) [^1][^21] |
| **511 205** (billets) | Paheko terrain | **Supprimer comme compte PCA** | ❌ Supprimer | Ce n'est pas un compte PCA — c'est une donnée de comptage RecyClique. Garder uniquement dans l'interface RecyClique (module comptage) |
| **511 210** (pièces) | Paheko terrain | **Supprimer comme compte PCA** | ❌ Supprimer | Idem — appartient au module comptage RecyClique, pas au plan Paheko |
| **511 220** (virements tampon) | Paheko terrain | **512 ou 58** | ❌ À corriger | Les virements entrants vont directement en 512. Si transit entre deux 512 : utiliser 58. Pas de sous-compte 511 pour virements. |
| **512** | Paheko (banque + CB ?) | **512** | ✅ Correct pour banque | CB ne doit pas aller en 512 directement — voir 511 CB. Plusieurs 512 OK si plusieurs comptes bancaires réels. |
| **5112** | RecyClique seeds | **5112** | ✅ Correct | Standard PCG pour chèques à encaisser [^17][^1]. C'est ce que Paheko utilise nativement [^16]. Aligner Paheko terrain sur 5112 (pas 511 205/210). |
| **707** | Paheko (1re année) | **7070** | ❌ À migrer | Créer 7070 dans Paheko, basculer RecyClique. Ne pas reclasser rétroactivement les 707 sans accord EC. |
| **7070** | RecyClique cible | **7070** | ✅ Correct | Ventes réemploi — conserver |
| **754** | Paheko oral | **7541** | ❌ Remplacer | 754 seul n'est pas un compte terminal valide — utiliser 7541 |
| **754.10** (synthèse) | Paheko | **7541** | ❌ Fusionner | Compte de synthèse redondant si 7541 existe — simplifier |
| **754.11** (écritures courantes) | Paheko | **7541** | ⚠️ À trancher | Si sous-comptes voulus : renommer en 7541.1. Sinon, fusionner en 7541. Valider EC. |
| **754.115** (dons chèques) | Paheko | **7541 ou 7541.5** | ⚠️ À trancher | Utile si rapprochement bancaire dons-chèques. Valider EC. |
| **754.111** (projets affectés) | Paheko | **7541.1 ou 7542** | ⚠️ À renommer | Les dons affectés méritent un sous-compte distinct — valider avec EC le numéro (7542 existe dans certains PCA pour dons affectés) |
| **754.12** (abandon frais bénévoles) | Paheko | **754.12** | ✅ Hors scope caisse v1 | Correct mais hors périmètre RecyClique v1 |
| **7541** | RecyClique cible | **7541** | ✅ Correct | Dons manuels PCA [^13] |
| **1630** | Doc interne oral | **Supprimer** | ❌ Supprimer | N'existe pas en PCA/PCG — confusion avec 530 |
| **53** oral | Terrain Paheko | **530** | ❌ Corriger libellé | Raccourci de classe — toujours utiliser 530 |
| **58** | Paheko (virements) | **58** | ✅ Correct si usage = virements internes uniquement | Ne jamais utiliser pour achats ou charges [^14][^4] |
| **471** | Paheko (attente) | **471 si strictement nécessaire** | ⚠️ Limiter | Réserver aux seuls flux en suspens non identifiés. Usage courant = inutile. |
| **472** | Paheko (dépenses à classer) | **Supprimer ou limiter** | ❌ Quasi-inutile | Doublon de 471 pour le contexte boutique réemploi |
| **678** | Paheko plugin caisse | **658** | ⚠️ À remplacer dans RecyClique | 678 = exceptionnel ; 658 = gestion courante. Écarts de caisse quotidiens = 658. Vérifier si modifiable dans le plugin Paheko. |
| **778** | Paheko plugin caisse | **758** | ⚠️ À remplacer dans RecyClique | Idem symétrique — 758 pour trop-perçu de caisse courant |
| **771.3** (libéralités exceptionnelles) | Paheko | **771.3** | ✅ Conserver mais clarifier | Utiliser pour dons *exceptionnels* de montant significatif, non pour les surplus de caisse quotidiens (→ 7541) |
| **754.900** (oral) | Paheko oral | **À clarifier** | ❓ Identifier | Sens inconnu — vérifier dans Paheko réel avant toute décision |
| **708** | RecyClique ancien | **7541** | ❌ Supprimer | Produits annexes ≠ dons manuels — migration faite, confirmer suppression |
| **467** | RecyClique ancien | **672** | ❌ Supprimer | Compte de bilan inadapté pour remboursement — migration faite, confirmer |
| **7073** | RecyClique test | **7070** | ❌ Supprimer | Ventilation par famille textile refusée — tout en 7070 |
| **7041** | RecyClique erreur | **7541** | ❌ Supprimer | Erreur transcription — jamais utiliser |


***

## 3. Les 5 décisions que RecyClique peut figer en SuperAdmin SANS attendre l'EC

1. **Compte ventes = 7070** (remplace 707 legacy) — mapping produit RecyClique → écriture Paheko
2. **Compte dons caisse = 7541** (remplace 708 et 7041) — confirmé PCA[^13]
3. **Compte chèques = 5112** (standard Paheko/PCG ) — pas 511, pas 511-205[^17]
4. **Compte CB = 511** (valeurs à l'encaissement, pas 512)[^1]
5. **Écarts de caisse = 658** (manque) / **758** (trop-perçu) — usage gestion courante, plus précis que 678/778 du plugin[^9][^11]

***

## 4. Les 5 décisions RÉSERVÉES à l'EC sur place

1. **530 seul ou 530 + 531** pour le fond de caisse : si une seule caisse physique, 530 suffit ; si deux caisses, 531 à créer — décision sur la structure physique réelle
2. **7541 unique ou sous-comptes 754.11 / 754.115 / 754.111** : niveau de granularité des dons selon exigences des subventionneurs et volume de l'activité don
3. **Migration 707 → 7070** sur les exercices historiques : à ne faire que sur instruction EC (impact tableaux de bord, comparabilité N-1/N)
4. **672 en cours d'exercice** : valider les conditions d'utilisation et surtout la réimputation obligatoire en fin d'exercice[^18]
5. **678/778 dans le plugin Paheko** : vérifier si le plugin permet de modifier ces comptes ou s'il faut une écriture corrective manuelle ; trancher avec EC si coexistence 658/758 (RecyClique) + 678/778 (plugin) est acceptable ou génère une incohérence d'audit

***

## 5. Les 3 points de contrôle à faire vérifier avec le comptable sur le plan Paheko réel

1. **Libellés 511-205 et 511-210** : vérifier dans l'interface Paheko si ces « comptes » sont de vrais comptes du plan ou des libellés d'écritures de journal — s'ils sont dans le plan comptable, les supprimer ; s'ils sont seulement des libellés de lignes d'écriture, ils sont inoffensifs mais trompeurs
2. **Cohérence 5112 (RecyClique) vs 511-x (Paheko terrain)** : en l'état, RecyClique envoie les chèques en 5112 et Paheko terrain utilise 511-205 — vérifier que toutes les écritures chèques convergent bien sur le même compte dans Paheko, sinon le dépôt en banque  ne fonctionnera pas (bouton « Dépôt en banque » sur compte 5112)[^17]
3. **Arborescence 754.10 / 754.11 / 754.115 / 7541** : vérifier qu'il n'existe pas deux arborescences parallèles (une en 754.xx et une en 7541) — si c'est le cas, choisir l'une, migrer les soldes, supprimer l'autre pour éviter la double comptabilisation des dons

***

## 6. Écriture(s) type clôture de session — Exemple chiffré

**Contexte de la session :**

- 120 € ventes espèces
- 30 € ventes chèques
- 50 € ventes CB
- 2 € don espèces (surplus volontaire)

**Recommandation : 2 pièces comptables par session**, séparées pour lisibilité et facilité de rapprochement.

***

### Pièce 1 — Ventes et dons de la session

*Libellé : « Z caisse — SESSION 2026-05-21 — Ventes + dons »*


| Compte | Libellé | Débit | Crédit |
| :-- | :-- | :-- | :-- |
| 530 | Espèces — ventes | 120,00 |  |
| 5112 | Chèques à encaisser | 30,00 |  |
| 511 | CB à encaisser | 50,00 |  |
| 530 | Espèces — don caisse | 2,00 |  |
| 7070 | Ventes réemploi |  | 200,00 |
| 7541 | Dons manuels |  | 2,00 |
| **Total** |  | **202,00** | **202,00** |

> ⚠️ Note : les 120 € espèces ventes et les 2 € espèces dons peuvent être regroupés sur une seule ligne 530 débit de 122 € si le module comptage de RecyClique confirme le total espèces. Les séparer (deux lignes 530) est possible mais non obligatoire si 7070 et 7541 sont bien distingués côté crédit.

***

### Pièce 2 — Écart de caisse (si comptage révèle un écart)

*Libellé : « Z caisse — SESSION 2026-05-21 — Écart comptage »*

**Exemple : comptage réel = 121,50 € espèces au lieu de 122 € théoriques → manque de 0,50 €**


| Compte | Libellé | Débit | Crédit |
| :-- | :-- | :-- | :-- |
| 658 | Écart caisse — manque | 0,50 |  |
| 530 | Caisse espèces |  | 0,50 |
| **Total** |  | **0,50** | **0,50** |

**Exemple inverse : trop-perçu de 0,50 €**


| Compte | Libellé | Débit | Crédit |
| :-- | :-- | :-- | :-- |
| 530 | Caisse espèces | 0,50 |  |
| 758 | Écart caisse — excédent |  | 0,50 |


***

### Nota bene — Dépôt ultérieur des chèques en banque

Le 5112 ne se solde pas à la clôture de session. Il se solde **lors du dépôt physique en banque** via la procédure Paheko  :[^17]


| Compte | Débit | Crédit |
| :-- | :-- | :-- |
| 512 (compte courant) | 30,00 |  |
| 5112 |  | 30,00 |

La CB (511) se solde de même lors du crédit bancaire effectif.

***

**Sources principales mobilisées :** documentation Paheko  ; PCG comptes de trésorerie  ; comptes 658/758  ; compte 672  ; PCA associations  ; compte 531.[^22][^3][^23][^10][^24][^2][^11][^14][^4][^15][^5][^16][^6][^7][^19][^21][^8][^20][^9][^13][^18][^1][^17]

> **Rappel réglementaire :** les justificatifs tickets RecyClique doivent être conservés 10 ans (Code de commerce L123-22). Toutes les décisions marquées « Valider EC » ci-dessus doivent être confirmées par un expert-comptable connaissant le plan Paheko réel de l'association avant mise en production.
<span style="display:none">[^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37]</span>

<div align="center">⁂</div>

[^1]: https://www.compta-online.com/comment-comptabiliser-un-reglement-client-ao2624

[^2]: https://www.compta-online.com/comptes-de-tresorerie-ao27

[^3]: https://paheko.cloud/retraits-especes-caisse-comptabilisation

[^4]: https://www.indy.fr/guide/tenue-comptable/plan-comptable/compte-classe-cinq/compte-58/

[^5]: https://drome.franceolympique.com/wp-content/uploads/2023/03/FC-N°49-Le-Plan-Comptable-des-Associations.pdf

[^6]: https://www.pennylane.com/fr/fiches-pratiques/plan-comptable/compte-531-caisse-siege-social

[^7]: https://www.l-expert-comptable.com/plan-comptable/comptes-531-caisse-siege-social

[^8]: https://www.compta-online.com/comptabiliser-le-fonds-de-caisse-t63496

[^9]: https://www.compta-online.com/comptabiliser-les-ecarts-de-reglement-les-comptes-658-et-758-ao1696

[^10]: https://www.compta-online.com/comptabilisation-des-ecarts-t62046

[^11]: https://www.compta-facile.com/comptabilisation-ecarts-de-reglement-clients-fournisseurs-difference/

[^12]: https://www.pennylane.com/fr/fiches-pratiques/plan-comptable/compte-678-autres-charges-exceptionnelles

[^13]: https://www.pennylane.com/fr/fiches-pratiques/plan-comptable/plan-comptable-associations

[^14]: https://www.dougs.fr/ressources/pcg/classe-5/compte-58/

[^15]: https://paheko.cloud/gestion-virements-internes

[^16]: https://paheko.cloud/encaisser-un-paiement-de-plusieurs-activites

[^17]: https://paheko.cloud/depot-banque-cheque

[^18]: https://www.pennylane.com/fr/fiches-pratiques/plan-comptable/compte-672-charges-sur-exercices-anterieurs

[^19]: https://www.indy.fr/guide/tenue-comptable/plan-comptable/compte-classe-six/compte-672/

[^20]: https://www.compta-online.com/672-charges-sur-exercices-anterieurs-t38827

[^21]: https://www.l-expert-comptable.com/plan-comptable/compte-511-valeurs-l-encaissement

[^22]: https://paheko.cloud/caisse-configuration-paiement

[^23]: https://www.legalstart.fr/fiches-pratiques/comptabilite-entreprise/plan-comptable-association/

[^24]: https://paheko.cloud/extension-caisse

[^25]: https://paheko.cloud/video-comptabilite

[^26]: https://paheko.cloud/static/guide_a4.pdf

[^27]: https://paheko.cloud/caisse-lieux-de-vente

[^28]: https://wiki.kaz.bzh/paheko/start

[^29]: https://www.assoconnect.com/blog/23661-plan-comptable-des-associations-modele-a-telecharger-et-conseils

[^30]: https://paheko.cloud/foire-aux-questions-25-02-2026

[^31]: https://www.aecom.org/plan-comptable-association/

[^32]: https://paheko.cloud/nouveautes-version-1-3-13

[^33]: https://paheko.cloud/static/guide_a5.pdf

[^34]: https://www.l-expert-comptable.com/plan-comptable/compte-7718-autres-produits-exceptionnels-sur-operations-de-gestion

[^35]: https://www.compta-online.com/charges-exceptionnelles-ao7162

[^36]: https://www.crcf-edu.fr/veille/actualite-comptable-nouvelle-definition-du-resultat-exceptionnel-suppression-de-la-technique-du-transfert-de-charges-nouveau-plan-de-comptes-et-simplification-des-etats-financiers-dans-le-reglemen/

[^37]: https://www.legalstart.fr/fiches-pratiques/comptabilite-entreprise/fonds-de-caisse/

