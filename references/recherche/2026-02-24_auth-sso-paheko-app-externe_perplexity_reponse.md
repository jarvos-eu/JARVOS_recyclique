<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Authentification API : HTTP Basic uniquement

La documentation officielle Paheko est sans ambiguïté : **l'API REST n'accepte que l'authentification HTTP Basic** (identifiant + mot de passe dans l'URL ou en header `Authorization: Basic …`). Il n'existe **aucun mécanisme token, JWT, OAuth2 ou API key** côté Paheko :[^1]

```bash
# Seule forme supportée
curl https://compte-api:motdepasse@mon-paheko.tld/api/accounting/years
```

Les identifiants API se créent dans *Configuration → Fonctions avancées → API*. Ces identifiants sont distincts des comptes utilisateurs normaux et peuvent avoir des droits restreints (lecture seule, administration, etc.).[^1]

**Il n'y a pas de durée de vie ni de renouvellement** — les identifiants API sont permanents jusqu'à suppression manuelle.

## SSO Paheko : consommateur OIDC depuis 1.3.16

Paheko **ne joue pas le rôle de fournisseur d'identité (IdP)**. C'est l'inverse : depuis la version **1.3.16** (octobre 2025), Paheko peut **consommer** un IdP externe via **OpenID Connect** pour l'auto-hébergement. La documentation de référence est la page wiki `Configuration SSO et LDAP` (mentionnée dans les notes de version 1.3.16).[^2]

Ce que cela signifie concrètement :


| Scénario | Support Paheko |
| :-- | :-- |
| Paheko se connecte à un IdP OIDC externe (Keycloak, etc.) | ✅ Depuis 1.3.16 (auto-hébergement uniquement) |
| Paheko se connecte via LDAP | ✅ Documenté dans `Configuration SSO et LDAP` |
| Paheko **expose** un endpoint OIDC pour d'autres apps | ❌ Non supporté |
| API avec Bearer token / OAuth2 | ❌ Non supporté |

> **Important** : le support OpenID Connect est réservé à l'**auto-hébergement**. Les instances Paheko.cloud hébergées ne proposent pas cette configuration.[^2]

## Scénario RecyClique : options disponibles

Pour votre architecture FastAPI → Paheko, il faut distinguer les deux flux :

### Flux 1 — Appels API backend (FastAPI → Paheko)

C'est le cas le plus simple et entièrement documenté. Utiliser un **compte de service dédié** avec HTTP Basic :

```python
# Python / httpx (ou requests)
import httpx

PAHEKO_API_USER = "api-recyclique"
PAHEKO_API_PASS = "motdepasse-fort-depuis-env"

async with httpx.AsyncClient(
    base_url="https://paheko.monasso.tld/api/",
    auth=(PAHEKO_API_USER, PAHEKO_API_PASS),
    verify=True  # TLS obligatoire
) as client:
    r = await client.get("accounting/years/current/journal")
```

Les credentials ne doivent **jamais** figurer dans le code — les passer via variables d'environnement (`PAHEKO_API_USER`, `PAHEKO_API_PASS` dans `.env`).[^1]

### Flux 2 — Login utilisateur Recyclic ↔ Paheko (SSO)

Il n'existe pas de solution SSO native « Paheko comme IdP ». Les options réalistes sont :

1. **Keycloak / Authentik comme IdP commun** *(recommandé pour le long terme)* : configurer Paheko 1.3.16+ pour consommer cet IdP OIDC, **et** configurer FastAPI/React pour le même IdP. L'utilisateur se connecte une seule fois sur l'IdP. Requiert un IdP tiers à déployer (Keycloak, Authentik, Zitadel).[^2]
2. **Auth séparée par application** *(approche v0.1.0)* : les utilisateurs ont un compte Paheko (pour l'interface Paheko) et un compte FastAPI/JWT (pour l'interface Recyclic). Pas de SSO — deux sessions indépendantes. Simple à implémenter, acceptable pour un MVP.
3. **LDAP partagé** : si un annuaire LDAP existe déjà dans l'infrastructure, Paheko peut s'y connecter (configuration SSO LDAP documentée dans le wiki Paheko), et FastAPI peut l'interroger également via `python-ldap` ou `ldap3`.[^2]

## Recommandation pour v0.1.0

Pour un compte de service **FastAPI → Paheko** :

- Créer un utilisateur API dédié nommé `api-recyclique` dans *Configuration → API* avec **uniquement les droits nécessaires** (comptabilité en lecture/écriture, membres en lecture)[^1]
- Stocker les credentials en variables d'environnement, jamais en dur
- Forcer **HTTPS** sur toutes les requêtes (TLS requis, HTTP Basic en clair sinon)
- **Ne pas utiliser** le compte admin Paheko comme compte de service

Pour le SSO, différer à la **v0.2.0** avec déploiement d'un IdP léger (Authentik ou Keycloak), qui permettra aussi de centraliser les comptes bénévoles entre Recyclic et Paheko via OIDC.[^2]

> **Sources** : [paheko.cloud/api](https://paheko.cloud/api)  · [paheko.cloud/nouvelle-version-1-3-16](https://paheko.cloud/nouvelle-version-1-3-16-diverses-ameliorations-et-petites-nouveautes)[^1][^2]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://paheko.cloud/api

[^2]: https://paheko.cloud/nouvelle-version-1-3-16-diverses-ameliorations-et-petites-nouveautes

[^3]: https://paheko.cloud/static/guide_a4.pdf

[^4]: https://www.le-pic.org/spip.php?article1213

[^5]: https://paheko.cloud/sommaire

[^6]: https://dev.apidae-tourisme.com/documentation-technique/oauth/authentification-avec-un-token-oauth2/

[^7]: https://docs.sophos.com/central/enterprise/help/fr-fr/SettingsAndPolicies/SophosSignin/OpenIDConnectIDP/index.html

[^8]: https://dev.apidae-tourisme.com/documentation-technique/v2/oauth/authentification-avec-un-token-oauth2/

[^9]: https://docs.logto.io/fr/integrations/oidc-sso

[^10]: https://datacraft.ovh/extrait/gerer-lauthentification-token-oauth/

[^11]: https://data.rte-france.org/documents/20182/22648/EN_GuideOauth2_v5.1.pdf/54d3d183-f20f-4290-9417-bcae122b9e46

[^12]: https://paheko.cloud/version-1-3-18

[^13]: https://console.openapi.com/fr/apis/oauth/documentation

[^14]: https://docs.sophos.com/central/partner/help/fr-fr/Help/Configure/SettingsAndPolicies/SophosSignin/OpenIDConnectIDP/index.html

[^15]: http://documentation.veremes.net/vmap2/administrator/authentification/sso.html

[^16]: https://paheko.cloud/nouveautes-1-3

[^17]: https://paheko.cloud/configuration-logiciel

[^18]: https://docs.sekoia.io/getting_started/sso/openid_connect/

[^19]: https://github.com/dani-garcia/vaultwarden/wiki/Enabling-SSO-support-using-OpenId-Connect

[^20]: https://rs.ppgg.in/configuration/enabling-sso-support-using-openid-connect

[^21]: https://paheko.cloud/configuration?_dialog

[^22]: https://paheko.cloud/hebergeurs-paheko

[^23]: https://www.open3a.de/2025/07/openid-connect-sso/

