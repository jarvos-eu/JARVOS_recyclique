---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: []
workflowType: 'research'
lastStep: 6
research_type: 'technical'
research_topic: 'SSO transversal RecyClique-Paheko multi-structures'
research_goals: 'Définir une architecture SSO réaliste pour garder une surface RecyClique, valider ce qui est possible avec Paheko existant, couvrir la résilience si Paheko est indisponible, et préparer le cadrage Epic/Stories.'
user_name: 'Strophe'
date: '2026-02-28'
web_research_enabled: true
source_verification: true
---

# Research Report: technical

**Date:** 2026-02-28
**Author:** Strophe
**Research Type:** technical

---

## Research Overview

Cette recherche couvre la mise en place d'un SSO transversal RecyClique-Paheko multi-structures avec une contrainte forte: conserver une surface utilisateur principale RecyClique, tout en alignant la gouvernance des identités sur Paheko. L'analyse combine standards OIDC/OAuth, documentation Paheko, patterns d'architecture (SPA+BFF+IdP), et contraintes de résilience en cas d'indisponibilité IdP/Paheko.

Le résultat principal est un modèle cible pragmatique: IdP central pour le SSO, RecyClique comme façade opérationnelle, Paheko comme source de vérité métier des membres, avec extension locale minimale pour les attributs spécifiques RecyClique. Les rôles sensibles (Super Admin/Admin) conservent l'accès Paheko, les bénévoles restent limités par défaut à RecyClique sauf exception explicite.

Point structurant confirmé: l'API Paheko standard permet une partie du périmètre (membres), mais ne couvre pas nativement toute la gestion avancée groupes/permissions cross-plateforme attendue. Une trajectoire en deux temps est donc recommandée: API Paheko d'abord, puis plugin Paheko dédié pour compléter le RBAC cible.

---

<!-- Content will be appended sequentially through research workflow steps -->

## Technical Research Scope Confirmation

**Research Topic:** SSO transversal RecyClique-Paheko multi-structures
**Research Goals:** Définir une architecture SSO réaliste pour garder une surface RecyClique, valider ce qui est possible avec Paheko existant, couvrir la résilience si Paheko est indisponible, et préparer le cadrage Epic/Stories.

**Technical Research Scope:**

- Architecture Analysis - design patterns, frameworks, system architecture
- Implementation Approaches - development methodologies, coding patterns
- Technology Stack - languages, frameworks, tools, platforms
- Integration Patterns - APIs, protocols, interoperability
- Performance Considerations - scalability, optimization, patterns

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for critical technical claims
- Confidence level framework for uncertain information
- Comprehensive technical coverage with architecture-specific insights

**Scope Confirmed:** 2026-02-28

## Technology Stack Analysis

### Programming Languages

Pour ce sujet SSO, les langages ne sont pas le facteur de risque principal ; c'est surtout la conformité aux standards OIDC/OAuth et la séparation des responsabilités (front, BFF, API, IdP). Côté stack existante, le couple React + FastAPI reste viable pour un SSO moderne, à condition d'appliquer PKCE/BFF et de ne pas laisser les tokens sensibles en stockage navigateur persistant.
_Popular Languages: TypeScript (SPA/BFF edge), Python (API), Java pour certains IdP comme Keycloak._
_Emerging Languages: Go et Rust apparaissent surtout côté gateways/infra, moins pertinent ici à court terme._
_Language Evolution: La tendance est de standardiser le protocole (OIDC) plutôt que de changer de langage._
_Performance Characteristics: Le point critique perf est la validation de jetons/JWKS et les échanges réseau IdP, pas le langage applicatif._
_Source: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-24_

### Development Frameworks and Libraries

Pour RecyClique, il faut privilégier des briques OIDC éprouvées plutôt que du custom auth. Côté IdP, deux candidats réalistes : Keycloak (mature, multi-tenant via Organizations) et Authentik (OIDC provider complet, setup souvent plus léger). Côté backend FastAPI, la pratique recommandée est la validation stricte JWT (issuer, audience, exp, signature) avec JWKS.
_Major Frameworks: Keycloak, Authentik, bibliothèques OIDC/OAuth2 standards côté FastAPI._
_Micro-frameworks: wrappers FastAPI-Keycloak et middlewares OIDC réduisent le code bespoke._
_Evolution Trends: Renforcement du modèle BFF pour SPA sensibles._
_Ecosystem Maturity: Keycloak et Authentik disposent d'une documentation active et de déploiements production fréquents._
_Source: https://docs.goauthentik.io/add-secure-apps/providers/oauth2_
_Source: https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.0/html/server_administration_guide/managing_organizations_

### Database and Storage Technologies

Le SSO ne nécessite pas de changer la base métier RecyClique immédiatement. En revanche, il faut prévoir un petit stockage de mapping d'identité (subject OIDC -> user RecyClique/structure/roles), avec cache court pour limiter l'impact d'une indisponibilité temporaire IdP/Paheko.
_Relational Databases: PostgreSQL convient pour le mapping identités/structures/roles._
_NoSQL Databases: Pas indispensable au démarrage pour ce périmètre._
_In-Memory Databases: Redis utile pour sessions serveur, cache introspection/JWKS, throttling auth._
_Data Warehousing: Hors sujet pour la phase SSO initiale._
_Source: https://keycloak.org/2024/06/announcement-keycloak-organizations_

### Development Tools and Platforms

Le besoin principal est l'outillage sécurité et observabilité autour de l'auth : logs corrélés, traces de login, alertes sur erreurs d'émission/validation de tokens, et tests e2e de parcours SSO. Le reste de la toolchain peut rester inchangé.
_IDE and Editors: inchangé (VS Code/Cursor, etc.)._
_Version Control: inchangé (Git, PR review renforcée sur sécurité)._
_Build Systems: inchangé, mais pipeline doit inclure tests auth/claims/régression._
_Testing Frameworks: tests API + parcours front de login/logout/refresh + scénarios d'indispo IdP._
_Source: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-24_

### Cloud Infrastructure and Deployment

Le choix structurant est l'hébergement de l'IdP (interne/managed) et sa HA. Pour multi-structures, une architecture "single realm + organizations" (ou équivalent) peut réduire la charge d'admin, mais nécessite une gouvernance stricte des claims de tenant.
_Major Cloud Providers: tous compatibles via conteneurs et reverse proxy standard._
_Container Technologies: Docker/Kubernetes adaptés pour IdP + API + proxy._
_Serverless Platforms: moins prioritaire pour le coeur auth stateful._
_CDN and Edge Computing: utile pour front, neutre pour logique SSO centrale._
_Source: https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.0/html/server_administration_guide/managing_organizations_

### Technology Adoption Trends

La tendance claire est : abandon des patterns SPA anciens (implicit flow), adoption de PKCE et progression du modèle BFF pour réduire l'exposition des tokens. Pour le multi-tenant, la préférence va vers une isolation logique forte (claims + org) sans multiplier excessivement les realms/instances sauf besoin de séparation dure.
_Migration Patterns: custom auth -> OIDC standard + claims structurés._
_Emerging Technologies: fonctionnalités "Organizations" et federation IdP plus natives._
_Legacy Technology: implicit flow et stockage localStorage des tokens sont à éviter._
_Community Trends: hausse des implémentations avec PKCE + contrôles issuer/audience/signature stricts._
_Source: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-24_
_Source: https://keycloak.org/2024/06/announcement-keycloak-organizations_

## Integration Patterns Analysis

### API Design Patterns

Le pattern cible recommandé est: RecyClique (UI) -> BFF/API RecyClique -> IdP OIDC, avec validation systématique des jetons côté API (issuer, audience, expiration, signature). Pour les appels inter-services, standardiser un profil de JWT réduit le couplage entre composants.
_RESTful APIs: endpoints auth explicites (login callback, logout, refresh/session) et endpoints métier découplés._
_GraphQL APIs: non nécessaire pour le coeur SSO initial._
_RPC and gRPC: utile seulement si microservices internes à fort volume._
_Webhook Patterns: possible pour provisioning/sync utilisateurs depuis IdP, mais pas requis en phase 1._
_Source: https://www.rfc-editor.org/rfc/rfc9068.html_
_Source: https://www.rfc-editor.org/rfc/rfc8414_

### Communication Protocols

Le protocole pivot est OIDC/OAuth2 sur HTTPS. Le navigateur doit éviter de manipuler des secrets durables ; le modèle BFF diminue le risque d'exposition des tokens dans la SPA.
_HTTP/HTTPS Protocols: flux OAuth/OIDC et appels API standard._
_WebSocket Protocols: non prioritaire pour login, peut rester découplé._
_Message Queue Protocols: seulement pour événements de provisioning/audit._
_grpc and Protocol Buffers: optionnel, pas nécessaire pour l'interop RecyClique-Paheko à court terme._
_Source: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-24_
_Source: https://openid.net/specs/openid-connect-core-1_0.html_

### Data Formats and Standards

Format principal: JWT signé pour ID/access tokens, claims structurés pour tenant/organisation/roles. Les métadonnées IdP doivent être découvertes automatiquement via endpoint well-known pour éviter les config manuelles fragiles.
_JSON and XML: JSON partout pour OIDC/OAuth metadata et réponses API._
_Protobuf and MessagePack: sans gain clair sur ce périmètre auth._
_CSV and Flat Files: hors sujet pour l'authentification._
_Custom Data Formats: à éviter pour les claims d'auth ; préférer conventions standard._
_Source: https://www.rfc-editor.org/rfc/rfc8414_
_Source: https://www.rfc-editor.org/rfc/rfc9068.html_

### System Interoperability Approaches

Interop la plus robuste: IdP commun + applications clientes (RecyClique et Paheko) fédérées. RecyClique reste la surface principale, mais Paheko peut être branché comme client OIDC ou via SSO custom si nécessaire.
_Point-to-Point Integration: possible mais fragile si on couple directement RecyClique a Paheko pour l'auth._
_API Gateway Patterns: utile pour centraliser validation jetons, rate limiting, audit._
_Service Mesh: non requis pour démarrage, utile seulement à grande échelle._
_Enterprise Service Bus: surdimensionné pour ce contexte._
_Source: https://fossil.kd2.org/paheko/wiki?name=Configuration+SSO+et+LDAP_
_Source: https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.0/html/server_administration_guide/managing_organizations_

### Microservices Integration Patterns

Même si RecyClique n'est pas totalement microservices, on peut reprendre les patterns de résilience: validation locale JWT quand possible, introspection/révocation pour jetons opaques ou invalidation active.
_API Gateway Pattern: centralisation authn/authz et traçabilité._
_Service Discovery: secondaire ici._
_Circuit Breaker Pattern: important pour indispo IdP/Paheko afin d'éviter panne en cascade._
_Saga Pattern: utile surtout pour provisioning cross-systèmes, pas pour login nominal._
_Source: https://datatracker.ietf.org/doc/html/rfc7662_
_Source: https://datatracker.ietf.org/doc/html/rfc7009_

### Event-Driven Integration

Pour SSO, l'événementiel sert surtout à la synchronisation asynchrone (création compte, changement rôle, désactivation). Le login lui-même doit rester synchrone et simple.
_Publish-Subscribe Patterns: propagation des changements de rôles/organisations._
_Event Sourcing: non nécessaire pour première implémentation._
_Message Broker Patterns: utile si besoin de rejouer les syncs et absorber des pannes temporaires._
_CQRS Patterns: optionnel, pas indispensable au démarrage._
_Source: https://keycloak.org/2024/06/announcement-keycloak-organizations_

### Integration Security Patterns

Sécurité intégration: PKCE, validation stricte des claims, rotation secrets, logout/revocation cohérents, et séparation claire "auth centrale" vs "droits métier locaux par structure".
_OAuth 2.0 and JWT: base standard pour authn/authz inter-apps._
_API Key Management: réservé aux appels techniques non utilisateur._
_Mutual TLS: recommandé pour échanges backend sensibles inter-services._
_Data Encryption: TLS obligatoire + stockage secret hors code._
_Source: https://openid.net/specs/openid-connect-core-1_0.html_
_Source: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-24_
_Source: https://datatracker.ietf.org/doc/html/rfc7009_

## Architectural Patterns and Design

### System Architecture Patterns

Le pattern le plus robuste pour votre cas est **BFF + IdP central**: la SPA RecyClique ne gère pas directement les tokens d'accès; un backend dédié gère OAuth/OIDC, session cookie sécurisée, et proxifie les appels API. Cela garde "la surface RecyClique" tout en réduisant le risque XSS sur les tokens.
_Source: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-24_

### Design Principles and Best Practices

Principes directeurs recommandés: standard-first (OIDC/OAuth, pas de protocole maison), séparation authn/authz (identité centralisée, droits métier par structure), et "least privilege" sur scopes/claims. Pour le multi-structures, il faut formaliser un claim de contexte organisationnel/tenant à chaque requête sensible.
_Source: https://openid.net/specs/openid-connect-core-1_0.html_
_Source: https://csrc.nist.gov/pubs/sp/800/63/C/4/final_

### Scalability and Performance Patterns

La montée en charge de l'auth repose surtout sur l'IdP et la base associée: cache JWKS, validation locale JWT, limitation des introspections synchrones, et sessions courtes côté BFF. Pour la haute dispo IdP, l'architecture multi-site exige des arbitrages clairs entre cohérence forte et disponibilité.
_Source: https://www.keycloak.org/high-availability/multi-cluster/concepts_
_Source: https://www.rfc-editor.org/rfc/rfc9068.html_

### Integration and Communication Patterns

Pattern d'intégration recommandé: discovery automatique via well-known metadata, flux Authorization Code + PKCE, logout fédéré (au moins back-channel pour fiabilité inter-apps), et normalisation des claims transportés entre RecyClique/Paheko/IdP.
_Source: https://www.rfc-editor.org/rfc/rfc8414_
_Source: https://openid.net/specs/openid-connect-backchannel-1_0.html_

### Security Architecture Patterns

Sécurité cible: session HTTP-only côté BFF, rotation des secrets, validation systématique des claims (`iss`, `aud`, `exp`, `sub`), et stratégie explicite de révocation/logout. Pour Paheko, l'usage OIDC est possible mais doit intégrer ses limitations de comptes "virtuels" et le mapping des permissions.
_Source: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-24_
_Source: https://fossil.kd2.org/paheko/wiki?name=Configuration+SSO+et+LDAP_
_Source: https://datatracker.ietf.org/doc/html/rfc7009_

### Data Architecture Patterns

Conserver un annuaire d'identité central (IdP) et un mapping local minimal dans RecyClique: `subject oidc -> utilisateur local -> structure -> rôles/permissions`. Ce mapping permet résilience fonctionnelle, audit, et contrôle fin des accès même si une partie de la fédération est perturbée.
_Source: https://csrc.nist.gov/pubs/sp/800/63/C/4/final_
_Source: https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.0/html/server_administration_guide/managing_organizations_

### Deployment and Operations Architecture

Architecture ops recommandée: IdP déployé en haute dispo (au minimum 2 nœuds + base résiliente), supervision active, runbooks de reprise, et tests réguliers de panne (IdP down, Paheko down, coupure réseau). Important: définir un mode dégradé explicite pour RecyClique (ce qui reste autorisé, ce qui est bloqué).
_Source: https://www.keycloak.org/high-availability/multi-cluster/concepts_

## Implementation Approaches and Technology Adoption

### Technology Adoption Strategies

Stratégie recommandée en 3 phases: (1) brancher un IdP central sans casser le login actuel, (2) activer SSO pour un périmètre pilote (admin/super admin), (3) basculer progressivement le reste. Cette approche limite le risque opérationnel et permet un rollback clair.
_Source: https://csrc.nist.gov/pubs/sp/800/63/C/4/final_

### Development Workflows and Tooling

Implémentation orientée sécurité-by-default: tests automatiques des claims de rôle/structure, scénarios logout global, et vérification systématique des erreurs de fédération. Les pipelines doivent inclure des tests de non-régression auth à chaque merge.
_Source: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-24_

### Testing and Quality Assurance

Je recommande un plan de tests couvrant: login nominal, refus d'accès Paheko pour bénévole, accès Paheko autorisé pour admin/super-admin, changement de rôle en temps réel, et indisponibilité IdP/Paheko. Ajouter des tests de session/logout front-channel/back-channel pour éviter les sessions fantômes.
_Source: https://openid.net/specs/openid-connect-backchannel-1_0.html_

### Deployment and Operations Practices

Ops cible: IdP HA, supervision de santé et latence d'auth, rotation de secrets planifiée, backups testés, et runbooks d'incident. En mode dégradé, conserver une auth de secours strictement limitée et auditée (pas de bypass global).
_Source: https://www.keycloak.org/high-availability/multi-cluster/concepts_

### Team Organization and Skills

Compétences clés à aligner: IAM/OIDC (claims, scopes, logout), sécurité applicative web, exploitation IdP, et modélisation RBAC multi-structures. Un binôme "produit + sécurité" est utile pour arbitrer les règles d'accès Paheko.
_Source: https://openid.net/specs/openid-connect-core-1_0.html_

### Cost Optimization and Resource Management

Pour maîtriser les coûts: commencer avec un seul IdP central, architecture simple BFF, et périmètre d'accès Paheko restreint (admin/super-admin seulement). Reporter les intégrations lourdes (provisioning SCIM complet) après stabilisation.
_Source: https://www.rfc-editor.org/rfc/inline-errata/rfc7643.html_
_Source: https://www.potaroo.net/ietf/rfc/rfc7644.html_

### Risk Assessment and Mitigation

Risques majeurs: panne IdP, mauvaise attribution de rôles, dérive des claims multi-structures, et sessions non révoquées. Mitigation: principe "fail closed" sur routes sensibles, matrice d'autorisations explicite, et journalisation d'audit corrélée.
_Source: https://datatracker.ietf.org/doc/html/rfc7009_
_Source: https://datatracker.ietf.org/doc/html/rfc7662_

## Technical Research Recommendations

### Implementation Roadmap

Roadmap proposée:
1) Cadrer le modèle rôles/structures (Super Admin, Admin, Bénévole + exceptions).
2) Déployer IdP pilote et BFF auth.
3) Activer accès Paheko uniquement pour Admin/Super Admin.
4) Migrer progressivement les utilisateurs.
5) Exécuter tests de panne et valider mode dégradé.

### Technology Stack Recommendations

- Pattern: RecyClique SPA + BFF + IdP OIDC.
- IdP: Keycloak (fort multi-tenant) ou Authentik (opération plus légère), choix final selon capacité ops.
- Standards: OIDC Core, metadata discovery, révocation/introspection, logout back-channel.

### Skill Development Requirements

- Formation courte OIDC/OAuth pour l'équipe.
- Atelier RBAC multi-structures et gouvernance des exceptions.
- Exercices de réponse incident auth (IdP/Paheko down).

### Success Metrics and KPIs

- Taux de succès login SSO.
- Temps moyen d'authentification.
- Zéro accès Paheko non autorisé (bénévole).
- Temps de reprise après incident IdP.
- Nombre d'incidents de mapping rôles/structure.

## Research Synthesis

### Executive Summary

Le SSO transversal est faisable et pertinent, mais ne doit pas être implémenté comme un couplage direct RecyClique <-> Paheko. L'architecture recommandée est: RecyClique (UI) -> BFF/API RecyClique -> IdP OIDC central, avec Paheko et RecyClique consommateurs du même référentiel d'identité fédérée. Cette approche maintient une expérience unifiée, réduit les risques de sécurité côté navigateur, et permet d'appliquer une politique multi-structures cohérente.

La gouvernance métier validée est la suivante: Paheko est la source de vérité des membres et de leur organisation métier; RecyClique ajoute uniquement les attributs applicatifs locaux (périmètres d'action, contraintes opérationnelles). Les règles d'accès Paheko sont explicites: Super Admin et Admin autorisés, bénévoles non autorisés par défaut sauf exception tracée.

La limite principale identifiée est API: l'API Paheko couvre bien la gestion des membres, mais pas tout le besoin de pilotage groupes/permissions cross-plateforme au niveau de finesse attendu. Décision recommandée: démarrer immédiatement avec ce que l'API couvre, et inscrire la création d'un plugin Paheko comme chantier prioritaire de consolidation RBAC.

### Key Findings

- Le pattern BFF est le plus robuste pour SPA/OIDC et réduit l'exposition des tokens.
- Paheko supporte OIDC en client (et callback), ce qui facilite l'alignement SSO.
- L'API Paheko est exploitable pour les membres mais partielle pour le RBAC avancé.
- Une architecture multi-structures fiable exige des claims de tenant/organisation gouvernés.
- La résilience doit être pensée dès le départ (mode dégradé, fail closed, runbooks).

### 1. Technical Research Introduction and Methodology

Méthode appliquée:
- Vérification de standards (OIDC/OAuth, metadata discovery, JWT profile, revocation/introspection).
- Vérification de la documentation Paheko (SSO OIDC/LDAP, API publique).
- Validation croisée architecture/sécurité/résilience avec sources officielles.

Objectif atteint:
- architecture cible claire,
- limites API Paheko objectivées,
- trajectoire d'implémentation progressive définie.

### 2. Technical Landscape and Architecture Analysis

Architecture recommandée:
- IdP central (Keycloak ou Authentik),
- RecyClique en façade,
- Paheko comme système métier de référence membres,
- mapping local RecyClique pour attributs applicatifs.

Anti-pattern à éviter:
- double auth indépendante non synchronisée,
- stockage tokens sensibles dans le front,
- RBAC divergent entre Paheko et RecyClique.

### 3. Implementation Approaches and Best Practices

Approche en 2 étapes:
1) Implémenter tout le périmètre couvert par API Paheko.
2) Développer un plugin Paheko pour exposer les capacités manquantes (groupes/permissions avancées, mapping robuste, événements de synchro).

Principe produit:
- une seule politique d'accès cross-plateforme,
- UI de gestion possible depuis RecyClique, mais écriture effective vers la source de vérité Paheko.

### 4. Technology Stack Evolution and Current Trends

Tendance dominante confirmée:
- Authorization Code + PKCE,
- généralisation BFF pour SPA sensibles,
- gouvernance identité centralisée et claims standardisés.

### 5. Integration and Interoperability Patterns

Intégration cible:
- discovery well-known,
- validation JWT stricte,
- logout fédéré,
- mécanismes de révocation/introspection selon type de token.

Interop Paheko:
- possible via OIDC client + API membres,
- compléments nécessaires via plugin pour RBAC avancé.

### 6. Performance and Scalability Analysis

Points de vigilance:
- disponibilité et latence IdP,
- charge de validation des tokens,
- propagation des changements de droits.

Réponse:
- cache maîtrisé, observabilité auth, HA IdP, tests de charge auth.

### 7. Security and Compliance Considerations

Exigences minimales:
- sessions HTTP-only côté BFF,
- scopes minimaux,
- séparation authn/authz,
- journalisation d'audit.

Règle opérationnelle:
- bénévoles sans accès Paheko par défaut,
- exceptions explicites et traçables.

### 8. Strategic Technical Recommendations

Décisions recommandées:
- Valider officiellement Paheko comme source de vérité membres.
- Démarrer immédiatement avec API Paheko disponible.
- Ouvrir un chantier plugin Paheko pour combler le gap RBAC.
- Conserver RecyClique comme surface principale, Paheko comme accès expert/secours.

### 9. Implementation Roadmap and Risk Assessment

Roadmap courte:
1. Cadrage rôles/groupes/cas d'exception.
2. POC IdP + BFF + mapping minimal.
3. Synchronisation membres via API Paheko.
4. Contrôle d'accès Paheko par rôle.
5. Spécification puis dev plugin Paheko (groupes/permissions avancées).

Risques critiques:
- dérive des droits inter-systèmes,
- panne IdP,
- incompletude API.

Mitigations:
- fail closed,
- monitoring auth,
- tests de panne,
- plugin ciblé.

### 10. Future Technical Outlook and Innovation Opportunities

Après stabilisation:
- automatisation provisioning plus poussée,
- amélioration UX de gestion des droits,
- extension de la gouvernance multi-structures.

### 11. Research Methodology and Source Verification

Sources principales:
- OpenID Foundation (OIDC),
- IETF RFC/drafts OAuth,
- NIST 800-63C-4,
- documentation officielle Paheko,
- documentation Keycloak/Authentik.

Niveau de confiance global: eleve sur architecture cible et standards; moyen sur profondeur fonctionnelle API Paheko groupes/permissions sans plugin dédié.

### 12. Appendices

#### Decision Log (Synthèse)

- D1: Un seul mécanisme cross-plateforme.
- D2: Paheko source de vérité membres.
- D3: RecyClique surface principale.
- D4: API Paheko d'abord, plugin Paheko ensuite.
- D5: Accès Paheko limité aux rôles autorisés.

#### Backlog Item à ajouter

- **Epic/Story**: "Plugin Paheko - Exposition API groupes/permissions pour gouvernance RBAC cross-plateforme"
- **But**: permettre gestion complète des groupes/permissions depuis RecyClique UI sans divergence avec Paheko.

---

## Technical Research Conclusion

Le démêlage est clarifié: votre besoin est cohérent, mais il nécessite une trajectoire technique progressive. La cible "un seul mécanisme cross-plateforme" est atteignable en combinant IdP central + Paheko source de vérité + extension locale RecyClique. Le blocage principal n'est pas conceptuel mais d'exposition API pour le RBAC avancé, d'où la nécessité planifiée d'un plugin Paheko.

La stratégie pragmatique est validée: avancer tout de suite avec ce qui est possible via API Paheko, et traiter le plugin comme chantier prioritaire de consolidation. Cela permet de livrer rapidement de la valeur tout en gardant une architecture saine.

**Technical Research Completion Date:** 2026-02-28
**Source Verification:** Web et documentation officielle croisées
**Technical Confidence Level:** High (architecture), Medium (couverture API RBAC Paheko sans plugin)
