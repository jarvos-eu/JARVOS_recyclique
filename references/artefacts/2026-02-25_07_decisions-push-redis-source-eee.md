# Décisions confrontation (push, Redis, source EEE, réception, interfaces compta)

**Date :** 2026-02-25  
**Contexte :** Suite au point global et à la grille confrontation ; décisions prises pour push caisse, résilience, source EEE, réception/poids, interfaces compta.

**Références :** [grille 05](2026-02-25_05_grille-confrontation-recyclic-paheko.md), [point global 06](2026-02-25_06_point-global-avant-prd.md), [artefact 04](2026-02-25_04_analyse-plugins-caisse-decisions-push.md), [vision module décla](../vision-projet/vision-module-decla-eco-organismes.md).

---

## 1. Synthèse des décisions

| Décision | Contenu |
|----------|----------|
| **Push caisse** | Par **ticket** au fil de l'eau (pas par session ni micro-lot). **Clôture** = déclenchement syncAccounting + contrôle (totaux). Tranché avec l'analyste. |
| **Résilience** | **Redis Streams** comme file d'attente des push RecyClique → Paheko (même stack que EventBus) ; workers consommateurs, retry sans perte si Paheko down. |
| **Source officielle EEE** | **RecyClique** : liste open data (niveau ministériel / REP), mapping catégories boutique → officielles, module décla éco-organismes dans RecyClique. Liste interrogable par JARVOS Nano / tiers si besoin. |
| **Réception matière / poids** | Réception + tickets de réception **dans RecyClique** (comme en 1.4.4). **Aucune sync manuelle**. Compta matière / poids / catégories peut rester **uniquement dans RecyClique** ; rôle du module Saisie au poids Paheko à trancher (fusion plugin ? plugin custom unique ?). |
| **Interfaces compta** | **Objectif** : ne plus avoir à entrer dans l'admin Paheko. **RecyClique** expose vues et workflows compta (bilan, traçabilité entrées/sorties, factures, rapprochement bancaire). Paheko = backend compta ; plus tard pilotage via JARVOS Nano / Mini. |

---

## 2. Questions encore à trancher

- ~~**Catégories caisse Paheko**~~ → **Tranché** : plugin recyclique crée/matche à la volée. Voir [artefact 08](2026-02-25_08_session-confrontation-recyclic-paheko.md).
- ~~**Module Saisie au poids Paheko**~~ → **Tranché** : garder module Brindille ; plugin peut alimenter module_data_saisie_poids après push. Voir [artefact 08](2026-02-25_08_session-confrontation-recyclic-paheko.md).
- ~~**Sécurité endpoint plugin**~~ → **Tranché** : secret partagé + HTTPS ; à figer en PRD v0.2. Voir [artefact 08](2026-02-25_08_session-confrontation-recyclic-paheko.md).
- **Périmètre module correspondance** : champs et règles de mapping exacts - **à trancher lors de la confrontation BDD + instance dev + analyste** (prérequis : dumps BDD, correspondances cartographiées). Recommandation : documenter en PRD comme prérequis v0.2.
- ~~**Auth v0.1 / SSO v0.2**~~ → **Tranché** : figer en PRD (auth séparée v0.1, SSO v0.2). Voir [artefact 08](2026-02-25_08_session-confrontation-recyclic-paheko.md).
- ~~**Montants / devises**~~ → **Tranché** : alignement centimes ; à valider en BDD Recyclic. Voir [artefact 08](2026-02-25_08_session-confrontation-recyclic-paheko.md).
- **Politique fichiers / chantier documents** : frontière RecyClique ↔ Paheko - **à trancher dans le chantier fichiers** (artefact 02), scope versions futures.
- **Stratégie LLM/IA** : reportée après brief (v0.1 = placeholder).
