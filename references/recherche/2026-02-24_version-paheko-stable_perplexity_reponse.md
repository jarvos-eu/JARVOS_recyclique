<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Version stable actuelle : **1.3.19** (2 février 2026)

La dernière version stable de Paheko est la **1.3.19**, publiée le lundi 2 février 2026. Elle est immédiatement disponible sur Paheko.cloud pour les instances hébergées, et distribuée via le dépôt officiel Fossil SCM à l'adresse `fossil.kd2.org/paheko` (miroir Git sur `github.com/paheko/paheko`). Les annonces de version sont faites sur `paheko.cloud/actu`.[^1][^2]

Pour mémoire, le jalonnement récent de la branche 1.3.x :


| Version | Date de sortie | Notes principales |
| :-- | :-- | :-- |
| 1.3.13 | 22 janv. 2025 | Correctifs et petites nouveautés [^1] |
| 1.3.14 | 10 mars 2025 | Budget prévisionnel, saisie au poids [^1] |
| 1.3.17 | 23 oct. 2025 | Gestion matériel, statut e-mail, réservations [^3] |
| 1.3.18 | déc. 2025 | Archivage d'activités [^4] |
| **1.3.19** | **2 fév. 2026** | **Dernière stable** [^1] |

## Politique de versionnement

Paheko suit un schéma `MAJOR.MINOR.PATCH` mais **sans versionnement sémantique (semver) formellement déclaré** ni version LTS officielle. Les releases sont régulières, toutes les 4 à 10 semaines en moyenne sur la branche 1.3.x active depuis septembre 2023. Il n'existe pas de branche de maintenance figée ou d'engagement LTS documenté  — la stratégie implicite est de rester sur la **dernière mineure** (`1.3.x`) tant qu'une nouvelle branche majeure (`1.4.x` ou `2.x`) n'est pas annoncée.[^2][^1]

## Compatibilité de l'API REST dans 1.3.x

La documentation officielle de l'API (publiée sur `paheko.cloud/api`) est marquée comme valable pour la version 1.3.13, et les routes documentées pour 1.3.17 dans vos guides internes couvrent l'ensemble des endpoints actifs. L'API suit un **modèle purement additif** au sein de 1.3.x : chaque nouvelle route ou paramètre indique explicitement son numéro de version minimum (`*(Depuis la version 1.3.x)*`), et aucune route existante n'est retirée ou modifiée dans une version patch/mineure. Exemples concrets :[^5]

- `user/categories`, `user/new`, `user/{ID}` (CRUD membres) → depuis **1.3.6**[^5]
- `services/subscriptions/import` → depuis **1.3.2**[^5]
- `accounting/transaction/{ID}/transactions` → depuis **1.3.7**[^5]
- `linked_subscriptions` dans les écritures → depuis **1.3.6**[^5]
- `download/files` (backup ZIP) → depuis **1.3.4**[^5]

Aucun breaking change documenté n'a été identifié entre 1.3.6 et 1.3.19. Les appels HTTP (Basic Auth, JSON, REST sur `/api/{chemin}/`) restent identiques.[^5]

## Recommandation pour v0.1.0

Pour votre middleware FastAPI ciblant Paheko comme backend :

- **Version cible : 1.3.19** — dernière stable au moment du développement, couvrant toutes les routes nécessaires (comptabilité, membres, activités).
- **Pas de gel sur 1.3.17** — la mise à jour vers 1.3.19 n'introduit aucun breaking change API et apporte des correctifs.
- **Stratégie de suivi** : restez sur la branche `1.3.x` et mettez à jour à chaque nouvelle release ; un changement de branche (vers `1.4.x` ou `2.x`) devra être testé explicitement.
- **Précaution** : indexer les routes utilisées sur leur version minimale (≥ 1.3.6 pour la quasi-totalité des routes membres/comptabilité) pour documenter les prérequis dans votre `README` ou votre `pyproject.toml`.

> **Sources primaires** : [paheko.cloud/actu](https://paheko.cloud/actu)  · [paheko.cloud/api](https://paheko.cloud/api)  · [paheko.cloud/version-1-3-17-...](https://paheko.cloud/version-1-3-17-gestion-materiel-statut-email-reservations)  · [github.com/paheko/paheko](https://github.com/paheko/paheko)[^3][^1][^2][^5]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://paheko.cloud/actu

[^2]: https://github.com/paheko/paheko

[^3]: https://paheko.cloud/version-1-3-17-gestion-materiel-statut-email-reservations

[^4]: https://paheko.cloud/version-1-3-18

[^5]: https://paheko.cloud/api

[^6]: contexte-pour-recherche-externe.md

[^7]: presentation-plateforme-recyclic.md

[^8]: paheko_guide_a4.pdf

[^9]: TODO Christophe - RecycClique \& Paheko.pdf

[^10]: 2025-01-30_RETRAITEMENT_recyclique-guide-complet-Paheko.md

[^11]: 00_JARVOS_mini.md

[^12]: JARVOS_nano analyse-opus_4.6

[^13]: appercu_ecosysteme.md

[^14]: 📋 __RecyClique - Système RAG Intelligent _ Dossier.pdf

[^15]: Comment les ressourceries doivent peuvent faire po.pdf

[^16]: Paheko RecyClique.md

[^17]: https://paheko.cloud/facturation-electronique-point-etape-octobre-2025

[^18]: https://paheko.cloud/faq-en-direct

[^19]: https://paheko.cloud/webinaires

[^20]: https://linuxfr.org/news/paheko-logiciel-libre-de-gestion-associative-libre-a-vous-du-4-fevrier-2025

[^21]: https://w3r.one/fr/blog/web/api-et-integration/normes-protocoles-api/api-versioning-meilleures-pratiques-approches

[^22]: https://fossil-scm.org/home/doc/tip/www/changes.wiki

[^23]: https://paheko.cloud/foire-aux-questions-la-cloture-des-comptes-29-01-2026

[^24]: https://linuxfr.org/news/paheko-1-3-refonte-de-la-gestion-des-membres-drive-integre-recus-fiscaux-etc

[^25]: https://fossil-scm.org/home/doc/f47b7052/www/changes.wiki

[^26]: https://paheko.cloud/infolettre-novembre-2026

[^27]: https://github.com/paheko

[^28]: https://paheko.cloud/versionnement

[^29]: https://paheko.cloud/nouveautes-1-3

[^30]: https://piaille.fr/@paheko

[^31]: https://paheko.cloud/static/guide_a4.pdf

[^32]: https://paheko.cloud/a-propos/nouveau/

[^33]: https://github.com/paheko/paheko-plugins

[^34]: https://www.nzqa.govt.nz/assets/qualifications-and-standards/qualifications/ncea/NCEA-subject-resources/Science/NZQASci-TechTermsEng-Mao.pdf

[^35]: https://github.com/kd2org/karadav/blob/main/README.md

