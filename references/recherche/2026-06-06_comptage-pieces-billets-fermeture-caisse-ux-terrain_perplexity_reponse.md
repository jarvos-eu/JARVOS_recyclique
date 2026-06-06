Je recommande pour RecyClique un référentiel monétaire **canonique** de 15 dénominations juridiques, avec 14 lignes affichées par défaut et le billet de 500 € conservé en base mais masqué par défaut, car il a toujours cours légal tout en n’étant plus émis depuis 2019.[^1][^2][^3][^4]
Pour le produit, le bon choix est de faire du comptage par dénomination la seule vérité de caisse en fermeture, et de traiter le détail comme un justificatif interne archivé avec la session, même si la compta ne reçoit que des totaux agrégés.[^5][^6]

## A — Référentiel

**Obligation légale.** En 2026, les pièces en euros circulent en 8 dénominations : 1, 2, 5, 10, 20 et 50 centimes, puis 1 € et 2 €.  Les billets en euros existent en 7 dénominations légales : 5, 10, 20, 50, 100, 200 et 500 €.  Le billet de 500 € reste à cours légal et conserve sa valeur, mais il n’est plus émis depuis 2019 et ne fait plus partie de la série « Europe ».[^2][^3][^4][^1]

**Liste officielle de référence.** Pour figer le référentiel produit, la source la plus solide est la BCE pour les billets, complétée par une source de l’Eurosystème pour les pièces et par la Banque de France pour le statut opérationnel du 500 € en France.  Les billets de première série restent par ailleurs valables, ce qui veut dire qu’il ne faut pas distinguer les séries dans la grille de comptage.[^3][^4][^1][^2]

**Bonne pratique métier / recommandation UX produit.** Pour une petite structure associative, une grille strictement par valeur faciale suffit ; il n’y a pas d’intérêt métier à distinguer les faces nationales ou les variantes graphiques si la clôture et la compta ne manipulent que la valeur monétaire. Le plus robuste est donc de stocker 15 dénominations canoniques, d’afficher par défaut 14 lignes et d’ouvrir le 500 € via une action secondaire du type « Afficher les coupures rares ». Comptez en **unités**, pas en rouleaux ni en liasses dans la V1 ; les rouleaux peuvent devenir plus tard un raccourci optionnel, mais ne doivent pas remplacer l’unité de base car ils compliquent l’UX et les corrections. L’ordre d’affichage que je recommande est décroissant, billets puis pièces, car il colle au geste réel de fermeture : on sécurise d’abord les montants forts, puis l’appoint.

> **Synthèse projet — retenir / rejeter / question ouverte**
> - **Retenir :** référentiel légal fixe à 15 lignes, sans distinction de série ni de face nationale.[^4][^1][^3]
> - **Retenir :** 500 € présent dans le modèle de données mais masqué par défaut en UI.[^1][^2][^4]
> - **Rejeter :** une grille séparant pièces commémoratives, séries de billets ou rouleaux dès la V1.
> - **Question ouverte :** bouton simple « afficher les coupures rares » ou section repliée persistante selon la fréquence terrain du 100/200/500 €.

## B — UX fermeture

**Pattern de saisie.** Sur écran tactile partagé par des bénévoles, le meilleur compromis n’est ni le « +/− seulement » ni le champ libre seul, mais un pattern hybride : grand champ quantité, boutons +/− larges, remise à zéro explicite, total calculé automatiquement. Le « +/− seulement » réduit les erreurs mais devient trop lent dès qu’il y a beaucoup de pièces ; le champ libre seul est rapide mais crée plus d’inversions, de zéros oubliés et de doubles saisies.

**Fond de caisse : recommandation tranchée.** Il faut **tout compter dans la grille**, y compris le fond de caisse, puis laisser le système calculer séparément : total compté, espèces théoriques de clôture, fond à laisser, montant à remettre en coffre/banque. Cette option est la plus sûre parce qu’elle colle à la réalité physique du tiroir et évite l’erreur la plus classique : oublier que le fond fait partie de ce qui est réellement présent. Le fond doit être paramétré comme cible de fermeture, pas saisi comme une seconde vérité concurrente.

**Validation, cas sans espèces, garde-fous, accessibilité.** Je recommande une relecture obligatoire mais légère : écran de vérification systématique, puis confirmation forte seulement si espèces théoriques non nulles, écart non nul, ou présence d’une coupure rare. Si la session n’a eu aucune vente en espèces mais qu’un fond de caisse existe, il faut quand même compter le tiroir ; s’il n’y a ni fond ni mouvement espèces, une attestation « aucune espèce encaissée ni détenue » suffit. Les garde-fous les plus utiles sont : visuel très net entre 1 € et 2 €, verrouillage du montant global manuel, alerte sur quantités improbables, total serveur faisant foi, boutons d’au moins 44 px, contraste élevé, retour haptique/visuel à chaque saisie et temps cible de 90 secondes à 3 minutes pour une fermeture normale.

> **Synthèse projet — retenir / rejeter / question ouverte**
> - **Retenir :** saisie hybride champ quantité + steppers + total auto.
> - **Retenir :** compter tout le tiroir, fond inclus, puis déduire le fond cible après coup.
> - **Retenir :** écran de relecture toujours présent, confirmation renforcée seulement sur cas à risque.
> - **Rejeter :** un second champ « montant global compté » indépendant de la grille.
> - **Question ouverte :** faut-il rendre la relecture skippable quand total théorique = total compté et zéro écart pendant plusieurs jours consécutifs.

## C — Théorique, écart, archivage

**Montant théorique espèces.** Opérationnellement, le théorique de clôture doit **inclure le fond d’ouverture** et tous les mouvements espèces de la session, sinon on compare le tiroir réel à une base tronquée. Le montant « à laisser pour demain » et le montant « à retirer » doivent être des calculs dérivés, jamais la base de rapprochement.

**Valeur qui fait foi.** Si la grille donne 247,30 € et qu’un champ global dit 247,00 €, c’est la grille qui doit faire foi ; dans un logiciel moderne, le champ global devient inutile ou purement dérivé. Deux chiffres de vérité sur la même clôture créent plus d’erreurs qu’ils n’en préviennent.

**Conservation et justificatifs.** Les documents financiers d’une association doivent être conservés au moins 10 ans, et la même durée est recommandée pour les pièces justificatives classées de façon ordonnée et chronologique.  Dans ce cadre, le détail pièces/billets doit être archivé avec la session de clôture, même si l’écriture comptable transmise reste agrégée.  Le format le plus solide est : enregistrement structuré en base, feuille de clôture PDF reconstituable, export CSV optionnel, horodatage, identité du clôturant et du validateur, plus commentaire global obligatoire en cas d’écart. Pour les comptes d’écart, la logique 658/758 évoquée est cohérente en pratique, mais le paramétrage exact et la valeur probante de la feuille de clôture sont bien à valider avec l’expert-comptable.[^6][^5]

> **Synthèse projet — retenir / rejeter / question ouverte**
> - **Retenir :** théorique espèces de clôture = fond d’ouverture + mouvements espèces session.
> - **Retenir :** le total de la grille est la seule valeur comptée faisant foi.
> - **Retenir :** archivage du détail de comptage avec la session pendant 10 ans minimum.[^5][^6]
> - **Rejeter :** notes par dénomination visibles en permanence dans la grille.
> - **Question ouverte :** PDF de clôture généré systématiquement ou seulement en cas d’écart / contrôle.

## D — Terrain ressourcerie

**Terrain et double validation.** Je n’ai pas identifié ici de référentiel national spécifique aux ressourceries sur la feuille de clôture espèces ; il faut donc viser une solution très simple, très guidée et robuste à la rotation des bénévoles. En pratique, je recommande une double validation conditionnelle, pas systématique : obligatoire au-delà du seuil d’écart, en présence d’un 200/500 €, après remboursement cash, ou quand le clôturant signale une anomalie.

**Règles à afficher en permanence.** Les 4 règles les plus utiles sont : « Comptez tout le tiroir, fond compris », « Saisissez des quantités, jamais des montants », « Le total de la grille fait foi », « Commentez tout écart ou coupure rare ». Cela forme à la volée sans surcharger l’écran.

**Tests pilote et risques V1.** Avant mise en production, je validerais au minimum : session normale avec espèces, session sans espèces mais avec fond, écart inférieur au seuil, écart supérieur au seuil, remboursement cash, présence d’un billet rare, panne réseau en fin de clôture, et reprise après abandon au milieu de l’assistant. Le principal risque d’une V1 trop minimale n’est pas l’absence de rouleaux ; c’est plutôt d’exclure complètement les coupures rares alors qu’elles restent légales, ou de conserver un champ manuel global en parallèle du détail.[^2][^4][^1]

> **Synthèse projet — retenir / rejeter / question ouverte**
> - **Retenir :** V1 simple, obligatoire, sans rouleaux ni liasses comme unité primaire.
> - **Retenir :** cosignature seulement sur cas à risque, pas sur toutes les fermetures.
> - **Retenir :** 4 règles fixes affichées pendant le comptage.
> - **Rejeter :** suppression totale du 500 € du référentiel, alors qu’il reste légal.[^4][^1][^2]
> - **Question ouverte :** faut-il imposer une photo/scan de la feuille papier seulement en mode dégradé hors ligne.

## Livrables

### 1) Tableau référentiel recommandé

| code | libellé | type | valeur_centimes | afficher_par_défaut | ordre_affichage |
| :-- | :-- | --: | --: | :-- | --: |
| EUR_50000 | 500 € (rare, non émis mais toujours légal) [^1][^2][^4] | billet | 50000 | non | 1 |
| EUR_20000 | 200 € [^1][^4] | billet | 20000 | oui | 2 |
| EUR_10000 | 100 € [^1][^4] | billet | 10000 | oui | 3 |
| EUR_5000 | 50 € [^1][^4] | billet | 5000 | oui | 4 |
| EUR_2000 | 20 € [^1][^4] | billet | 2000 | oui | 5 |
| EUR_1000 | 10 € [^1][^4] | billet | 1000 | oui | 6 |
| EUR_500 | 5 € [^1][^4] | billet | 500 | oui | 7 |
| EUR_200 | 2 € [^3] | pièce | 200 | oui | 8 |
| EUR_100 | 1 € [^3] | pièce | 100 | oui | 9 |
| EUR_050 | 50 c [^3] | pièce | 50 | oui | 10 |
| EUR_020 | 20 c [^3] | pièce | 20 | oui | 11 |
| EUR_010 | 10 c [^3] | pièce | 10 | oui | 12 |
| EUR_005 | 5 c [^3] | pièce | 5 | oui | 13 |
| EUR_002 | 2 c [^3] | pièce | 2 | oui | 14 |
| EUR_001 | 1 c [^3] | pièce | 1 | oui | 15 |

Le référentiel légal couvre donc 8 pièces et 7 billets ; le seul écart recommandé entre droit et interface est de **masquer par défaut** le 500 € sans le supprimer du modèle.[^3][^1][^2][^4]

### 2) Wireframe textuel du parcours optimal

1. **Fermer la session**
Affichage du récapitulatif théorique : fond d’ouverture, espèces encaissées, remboursements espèces, dons caisse en espèces, espèces théoriques de clôture.
2. **Compter le tiroir**
Grille billets puis pièces, quantités saisies, total recalculé en direct, section repliée « coupures rares ».
3. **Vérifier le résultat**
Affichage côte à côte : théorique, compté, écart, fond cible à laisser, montant à retirer.
4. **Qualifier l’écart**
Si écart = 0, validation simple ; sinon commentaire obligatoire, suggestion de recomptage, alerte si seuil dépassé.
5. **Relire et confirmer**
Écran compact de relecture avec identité du clôturant, heure, totaux, et rappel « le total de la grille fera foi ».
6. **Code PIN responsable**
Toujours demandé sur le site pilote, avec message renforcé si seuil dépassé ou coupure rare présente.
7. **Session clôturée**
Résumé final, statut validé/bloqué, numéro de clôture, export feuille PDF/CSV optionnel, transmission comptable agrégée prête.

### 3) Décision recommandée sur le fond de caisse

**Option retenue : compter tout le tiroir dans la grille, fond compris, puis déduire le fond cible après calcul.**

Justification courte : c’est la seule option qui compare la réalité physique du tiroir au théorique complet, réduit l’oubli du fond et évite d’avoir deux chiffres concurrents pour une même clôture.

### 4) Arbitrages produit encore ouverts

- **P0 — Source de vérité comptée :** supprimer totalement le champ « montant global compté » ou le garder en lecture seule comme dérivé de la grille.
- **P0 — Formule de théorique espèces :** figer précisément quels mouvements entrent dans le théorique de clôture, notamment dons cash, remboursements et éventuels retraits manuels.
- **P0 — Session sans espèces :** imposer le comptage si un fond existe, et n’autoriser l’attestation simple que si aucun cash n’est physiquement détenu.
- **P1 — Coupures rares :** 500 € seul masqué, ou 200 € + 500 € dans un panneau « rares » selon la réalité du site pilote.
- **P1 — Preuve de clôture :** PDF systématique pour chaque session ou PDF seulement sur écart, seuil dépassé, ou cosignature.


### 5) Bibliographie

- BCE, **Banknotes** — dénominations des billets et arrêt d’émission du 500 € : [ecb.europa.eu/euro/banknotes/html/index.en.html](https://www.ecb.europa.eu/euro/banknotes/html/index.en.html).[^1]
- BCE, **Les billets en circulation** — statut des séries et maintien de valeur/cours légal : [ecb.europa.eu/euro/banknotes/current/html/index.fr.html](https://www.ecb.europa.eu/euro/banknotes/current/html/index.fr.html).[^4]
- Banque de France, **Billets** — confirmation que le 500 € reste en circulation et à cours légal mais n’est plus émis : [banque-france.fr/fr/billets](https://www.banque-france.fr/fr/billets).[^2]
- Banque de France, **Les pièces et les billets en euro** — page grand public sur les dénominations et le statut du 500 € : [banque-france.fr/fr/a-votre-service/particuliers/mieux-connaitre-moyens-paiement/pieces-billets-en-euro](https://www.banque-france.fr/fr/a-votre-service/particuliers/mieux-connaitre-moyens-paiement/pieces-billets-en-euro).[^7]
- Banco de España, **Euro coins** — 8 dénominations officielles des pièces : [bde.es/wbe/en/areas-actuacion/billetes-monedas/monedas-euros/](https://www.bde.es/wbe/en/areas-actuacion/billetes-monedas/monedas-euros/).[^3]
- Préfecture de l’Isère / Service-public, **Délais de conservation des documents d’association** — 10 ans pour les documents financiers, 6 ans pour les documents fiscaux : [isere.gouv.fr/Demarches/Demarches-ASSOCIATIONS/Associations-loi-1901/F-DELAIS-DE-CONSERVATION-DES-DOCUMENTS](https://www.isere.gouv.fr/Demarches/Demarches-ASSOCIATIONS/Associations-loi-1901/F-DELAIS-DE-CONSERVATION-DES-DOCUMENTS).[^5]
- HelloAsso, **Comment classer et conserver les pièces comptables** — recommandation pratique de classement ordonné/chronologique et rappel des 10 ans : [helloasso.com/blog/comment-classer-et-conserver-les-pieces-comptables/](https://www.helloasso.com/blog/comment-classer-et-conserver-les-pieces-comptables/).[^6]

Souhaitez-vous maintenant une version plus directement exploitable en **spécification produit** avec critères d’acceptation écran par écran ?
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://www.ecb.europa.eu/euro/banknotes/html/index.en.html

[^2]: https://www.banque-france.fr/fr/billets

[^3]: https://www.bde.es/wbe/en/areas-actuacion/billetes-monedas/monedas-euros/

[^4]: https://www.ecb.europa.eu/euro/banknotes/current/html/index.fr.html

[^5]: https://www.isere.gouv.fr/Demarches/Demarches-ASSOCIATIONS/Associations-loi-1901/F-DELAIS-DE-CONSERVATION-DES-DOCUMENTS

[^6]: https://www.helloasso.com/blog/comment-classer-et-conserver-les-pieces-comptables/

[^7]: https://www.banque-france.fr/fr/a-votre-service/particuliers/mieux-connaitre-moyens-paiement/pieces-billets-en-euro

[^8]: contexte-pour-recherche-externe.md

[^9]: presentation-plateforme-recyclic.md

[^10]: paheko_guide_a4.pdf

[^11]: TODO Christophe - RecycClique \& Paheko.pdf

[^12]: 2025-01-30_RETRAITEMENT_recyclique-guide-complet-Paheko.md

[^13]: 00_JARVOS_mini.md

[^14]: JARVOS_nano analyse-opus_4.6

[^15]: appercu_ecosysteme.md

[^16]: 📋 __RecyClique - Système RAG Intelligent _ Dossier.pdf

[^17]: Comment les ressourceries doivent peuvent faire po.pdf

[^18]: Paheko RecyClique.md

[^19]: https://link.springer.com/10.1007/978-3-030-34564-8_7

[^20]: https://www.semanticscholar.org/paper/fda97b3ecde1781eeeaf6589b087bce248cae609

[^21]: https://kluwerlawonline.com/journalarticle/European+Business+Law+Review/36.4/EULR2025051

[^22]: http://www.emerald.com/jes/article/29/6/370-387/226664

[^23]: https://www.mdpi.com/2673-2688/6/10/241

[^24]: https://link.springer.com/10.1007/s00181-020-01939-8

[^25]: https://www.semanticscholar.org/paper/5b3d246ee63fd61e05e1350aa3b5cdb1576e7e9d

[^26]: http://link.springer.com/10.1007/978-3-540-45126-6_8

[^27]: https://www.centralbank.ie/consumer-hub/notes-and-coins/euro-banknotes

[^28]: https://www.lemonde.fr/economie/article/2019/01/28/clap-de-fin-pour-le-billet-de-500-euros_5415453_3234.html

[^29]: https://fr.slideshare.net/slideshow/archives-conserver-associations-loi-1901compressed-1/69301090

[^30]: https://www.lafinancepourtous.com/2019/01/10/fin-du-billet-de-500-euros-et-nouveaux-billets-de-100-et-200-euros/

[^31]: https://tyls.com/ressources/blog/delais-conservation-documents-association

[^32]: https://www.ecb.europa.eu/stats/policy_and_exchange_rates/banknotes+coins/circulation/html/index.en.html

[^33]: https://www.ecb.europa.eu/pub/pdf/other/euroleafleten.pdf

[^34]: https://silexo.fr/uploads/Quels sont les délais de conservation des documents d'une association (Service-Public.fr).pdf

