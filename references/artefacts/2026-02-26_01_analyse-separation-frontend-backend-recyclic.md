# Analyse : garder ou non la separation frontend / backend dans RecyClique

**Date :** 2026-02-26  
**Contexte :** Question de Strophe sur l'utilite de la separation frontend/backend *cote RecyClique*, sachant que Paheko est deja le backend et qu'une surcouche cognitive (JARVOS Nano/Mini) arrivera plus tard. Proposition : tout rassembler dans un seul container (frontend + middleware).  
**Usage :** Aide a la decision architecture ; reference pour PRD / Brief / architecture. Contient aussi les **preconisations migration v1** (communication front-serveur, API, ce qu'il faut eviter).

---

## 1. Ce dont on parle

- **Paheko** = backend (compta, caisse native, Saisie au poids). Deja acte.
- **RecyClique** aujourd'hui dans les docs = **frontend** (React PWA) + **middleware/API** (FastAPI) qui orchestre, pousse vers Paheko, gere Redis Streams, etc.
- La question : garder **deux containers** RecyClique (un pour le front, un pour l'API) ou **un seul container** qui sert a la fois le front (statics) et l'API (middleware) ?

On ne parle pas de fusionner RecyClique et Paheko dans un seul container — Paheko reste un service a part. On parle uniquement de la frontiere *au sein de* RecyClique : front vs back.

---

## 2. Pourquoi un seul container RecyClique a du sens

### 2.1 Semantique claire

- **Paheko = le backend** (donnees, compta, regles metier caisse).
- **RecyClique = une application** : UX terrain + orchestration + push vers Paheko. Donc un seul « binaire » applicatif (front + middleware) est coherent : une seule chose a deployer pour « l'app RecyClique ».

### 2.2 Simplicite deploiement et exploitation

- Un seul container RecyClique a builder, deployer, monitorer, logger.
- Pas de CORS ni de gestion auth entre deux origines (front container vs api container) : tout est meme origine si FastAPI sert les statics du build React.
- Pour une instance par ressourcerie (deploiement cible), aucun besoin de scaler front et API independamment.

### 2.3 Surcouche cognitive

- La surcouche cognitive (JARVOS Nano/Mini, RAG, appels LLM) sera forcement **cote orchestration** : le front enverra des requetes (ex. « classer cet item », « rechercher dans la doc »), et c'est le **meme service** qui appellera Nano/Mini ou un placeholder LLM.
- Si RecyClique = 1 container (front + middleware) : un seul endroit ou ajouter les routes `/api/...` et les appels vers Nano/Mini. Pas de « qui appelle qui » entre un container front et un container api.
- Si on gardait 2 containers : la logique cognitive serait de toute facon dans le container « API ». Le container « front » ne ferait qu'appeler cette API. Donc la complexite cognitive est dans l'API ; mettre le front dans le meme container que l'API **ne complique pas** la surcouche cognitive, au contraire elle reste concentree dans un seul service.

Conclusion : **un seul container RecyClique simplifie l'arrivee de la surcouche cognitive**, au lieu de la compliquer.

### 2.4 Offline-first

- Le PWA tourne dans le navigateur ; en ligne il parle a l'API. Que l'API soit dans le meme container ou non ne change pas le protocole (HTTP/JSON). Le sync reste : front → API (meme processus ou meme container) → Redis / Paheko. Un seul container ne casse pas l'offline-first.

---

## 3. Arguments parfois avances pour garder deux containers

- **Scale independant** : peu pertinent pour une ressourcerie (une instance, peu de connexions simultanees).
- **Equipes differentes** : pas le cas (solo dev).
- **Technos differentes** : le front React est compile en statics ; les servir depuis FastAPI (Starlette) est standard. Aucune obligation d'avoir un serveur Node ou nginx dedie pour le front.

Rien de ces points ne milite fortement pour garder deux containers RecyClique dans ton contexte.

---

## 4. Avis et recommandation

**Avis :** Garder la separation **frontend / backend** *en deploiement* (deux containers RecyClique) n'apporte pas de benefice clair dans ton contexte et peut effectivement compliquer plus tard (deux services a faire evoluer, CORS, auth inter-services). L'argument « Paheko est deja le backend, donc RecyClique = une seule app (front + middleware) » est coherent.

**Recommandation :**

- **Decider** : **un seul container RecyClique** = build React servi en statics par FastAPI + routes API (middleware). Un seul process (ex. Gunicorn + FastAPI) par container.
- **Paheko** reste un container/service externe (backend).
- **Dans le code** : garder une separation **logique** claire (dossiers type `frontend/` et `backend/` ou `api/`, contrat API bien defini) pour la maintenabilite, sans dupliquer cette frontiere en **deploiement** (un seul image Docker « recyclic »).
- **Surcouche cognitive** : s'integre dans ce meme container (nouvelles routes FastAPI, appels Nano/Mini ou placeholder) sans ajouter de service RecyClique supplementaire.

Tu peux faire figurer cette decision dans le PRD / l'architecture (ex. « RecyClique deploye en un seul container ; Paheko en separate ») et eventuellement une phrase du type « pas de separation front/back en deploiement cote RecyClique » pour eviter les malentendus plus tard.

---

## 5. Preconisations pour la migration v1 (complement)

Suite a la question « faut-il toujours communiquer en API ? » et « quelles preconisations pour la migration ? », ce qui suit complete la section 4 pour la **refonte concrete** (import 1.4.4, stack cible, PRD).

### 5.1 Communication front ↔ serveur : garder SPA + API en v1

- Le **navigateur** execute le React ; le **serveur** execute FastAPI. Ils sont dans deux environnements — il faut donc un **canal** (HTTP, WebSocket, etc.). On ne peut pas « appeler une fonction Python depuis React » sans passer par le reseau.
- Pour la **migration v1** : garder le modele **SPA + API REST** (comme en 1.4.4). Memes ecrans, copy + consolidate + security ; le design modules (slots React, routes par module) suppose deja des appels depuis le client vers l'API.
- **Ne pas** introduire en v1 du rendu serveur (SSR) ou du full-page (formulaires POST + redirection) pour la meme app : cela ferait coexister deux facons de faire (SPA + SSR), plus de complexite pour un solo dev. Si plus tard certains ecrans (rapports, parametres) justifient du SSR, le faire de maniere ciblee apres v1.

### 5.2 Forme de l'API et organisation du code

- **Contrat clair** : schemas partages (Pydantic cote FastAPI, types TypeScript derives ou partages en monorepo) pour requetes/reponses. Une seule source de verite pour les definitions.
- **Routes par domaine / module** : comme prevu (register_routes par module), pas une mega-API centralisee.
- **EventBus / Redis Streams** : reserves au **serveur** (inter-modules, workers, push Paheko). Le front n'y accede pas ; il appelle l'API, l'API emet/consomme les evenements.
- **Pas de GraphQL** pour v1 : REST suffit, moins de couches.

### 5.3 Import 1.4.4 et structure du repo

- Suivre la **checklist** existante (copy + consolidate + security) a chaque pioche dans le code 1.4.4.
- Garder une **separation logique** nette dans le code : dossiers `frontend/` et `api/` (ou `backend/`), domaines identifiables. Meme avec un seul container, cela aide la maintenabilite.
- La frontiere reste « le front appelle l'API » ; on ne fusionne pas les runtimes (React dans le navigateur, FastAPI sur le serveur).

### 5.4 Synthese preconisations migration

| Sujet | Preconisation |
|--------|----------------|
| **Containers** | Un seul container RecyClique (front + middleware), Paheko a part. |
| **Front ↔ serveur en v1** | Garder **SPA + API REST** ; pas de bascule SSR/full-page pour v1. |
| **Forme de l'API** | REST structure, contrat et types partages (monorepo), routes par module. |
| **Evenements** | EventBus / Redis Streams cote serveur uniquement ; le front passe par l'API. |
| **Import 1.4.4** | Checklist copy + consolidate + security ; separation logique front/back dans le code. |
| **Surcouche cognitive** | Routes et logique dans le meme FastAPI (meme container). |
| **A eviter en v1** | GraphQL, melange SSR + SPA, deuxieme stack de rendu. |

---

## 6. Suite possible

- Figer la decision (sections 4 et 5) dans le PRD ou le document d'architecture quand tu les ecris.
- Si tu veux tracer l'idee et la decision : idee Kanban « un container RecyClique (front + middleware) » avec une note pointant vers cet artefact, puis passage en « a-faire » ou archive une fois acte dans le PRD.
