<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Catalogue des extensions Paheko officielles

Paheko distingue deux types d'extensions, toutes deux hébergées dans des dépôts séparés  :[^1]

- **Plugins** : code PHP compilé, installé dans `data/plugins/`, nécessite une approbation pour paheko.cloud
- **Modules** : templates **Brindille** (moteur de template interne) + fichier `module.ini`, plus légers, créables/importables par tout utilisateur[^2]

Les deux dépôts officiels sont :

- `fossil.kd2.org/paheko-plugins` → miroir Git : `github.com/paheko/paheko-plugins`[^3]
- `fossil.kd2.org/paheko-modules` → miroir Git : `github.com/paheko/paheko-modules`[^1]


## Extensions intégrées au core

La page de référence `paheko.cloud/extensions` liste **14 extensions officielles** livrées avec le core, activables via *Configuration → Extensions → Inactives → Activer*  :[^4][^5]


| Extension | Pertinence ressourcerie | Notes |
| :-- | :-- | :-- |
| **Caisse** | ⭐⭐⭐ Critique | Gestion caisse physique, produits, stock [^6] |
| **Saisie au poids** | ⭐⭐⭐ Critique | Entrées/sorties en kg, connectée à Caisse [^7] |
| **Réservations** | ⭐⭐ Utile | Dépôts, RDV, créneaux [^4] |
| **Reçus fiscaux** | ⭐⭐ Utile | Dons en nature, déductibilité [^4] |
| Reçu de don | ⭐ Optionnel | PDF de reçu simple [^4] |
| **Gestion de stock de vélos** | ⭐⭐ Adaptable | Stock générique réutilisable [^8] |
| Notes de frais | ⭐ Optionnel | Remboursements bénévoles [^4] |
| Modèles d'écritures | ⭐⭐ Utile | Écritures comptables récurrentes [^4] |
| Bordereau de remise de chèques | ⭐ Optionnel | Remise de chèques en banque [^4] |
| Cartes de membres | ⭐ Optionnel | Impression cartes adhérent [^4] |
| Horaires d'ouverture | ⭐ Optionnel | Affichage horaires sur site web [^4] |
| Notifications | ⭐ Optionnel | Alertes internes automatiques [^4] |
| Répartition géographique membres | — | Carte des adhérents [^4] |
| Statistiques web | — | Analytique site intégré [^4] |
| Suivi du temps | ⭐ Optionnel | Heures bénévoles [^4] |

## Extension Saisie au poids — détail intégration

C'est l'extension **la plus spécifique à une ressourcerie**. Elle s'intègre avec Caisse et Gestion des vélos via un onglet *Connexion avec les autres extensions*  :[^8]

- Associe les **catégories de produits Caisse** à des motifs de sortie Saisie au poids
- Import automatique après clôture de caisse (évite les doublons)
- Import depuis Gestion des vélos si les vélos ont un poids renseigné[^8]

> **Règle anti-doublon** : si une vente de vélo est enregistrée en Caisse *et* dans Gestion des vélos, n'utiliser **qu'une seule** des deux extensions pour le calcul du poids sorti.[^8]

## Versionnement et compatibilité

Les extensions officielles sont **livrées avec le core Paheko**, pas versionnées indépendamment. Elles suivent donc automatiquement la version de l'instance (actuellement 1.3.19). Pour les plugins tiers ou custom, la compatibilité minimale est déclarée dans `module.ini`. Il n'y a pas de dépôt public de "store" avec numéros de version par extension — la compatibilité est implicitement garantie pour toute extension issue du dépôt officiel et de la même branche 1.3.x.[^3][^2][^4]

## Installation en déploiement Docker

Pour une ressourcerie, l'**ordre recommandé d'activation** (certaines extensions comme Saisie au poids lisent la config de Caisse)  :[^6][^8]

1. **Caisse** — configurer produits + exercice comptable avant toute autre
2. **Saisie au poids** — configurer après Caisse (onglet Connexion extensions)
3. **Réservations** — indépendante, activable à tout moment
4. **Reçus fiscaux** — indépendante
5. **Modèles d'écritures** — complémentaire à la comptabilité

Aucune extension n'est pré-activée à l'installation : elles se trouvent toutes dans *Configuration → Extensions → Inactives*. En Docker, les plugins PHP tiers se déposent dans `data/plugins/` (volume persistant) ; les modules Brindille custom dans `data/modules/`.[^5][^2]

> **Sources** : [paheko.cloud/extensions](https://paheko.cloud/extensions)  · [paheko.cloud/extension-caisse](https://paheko.cloud/extension-caisse)  · [paheko.cloud/extension-saisie-au-poids](https://paheko.cloud/extension-saisie-au-poids?_dialog)  · [paheko.cloud/gestion-activation-extensions](https://paheko.cloud/gestion-activation-extensions)  · [github.com/paheko/paheko-plugins](https://github.com/paheko/paheko-plugins)[^7][^6][^4][^5][^3]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^9]</span>

<div align="center">⁂</div>

[^1]: https://github.com/paheko

[^2]: https://paheko.cloud/modules-developper

[^3]: https://github.com/paheko/paheko-plugins

[^4]: https://paheko.cloud/extensions

[^5]: https://paheko.cloud/gestion-activation-extensions

[^6]: https://paheko.cloud/extension-caisse

[^7]: https://paheko.cloud/extension-saisie-au-poids?_dialog

[^8]: https://paheko.cloud/extension-saisie-au-poids-import-gestion-velos-caisse

[^9]: https://wiki.hadoly.fr/documentation_technique:paheko

[^10]: https://wiki.infini.fr/index.php/Installation_de_paheko

[^11]: https://paheko.cloud/caisse-stock

[^12]: https://paheko.cloud/static/guide_a4.pdf

[^13]: https://paheko.cloud/caisse-configuration-produits-categories

[^14]: https://paheko.cloud/site-web

[^15]: https://paheko.cloud/extension-saisie-au-poids-configuration

[^16]: https://www.youtube.com/watch?v=u7y_XNqoDXA

[^17]: https://github.com/HluthWigg/docker-paheko

[^18]: https://docs.lacontrevoie.fr/technique/services-auxiliaires/paheko/

