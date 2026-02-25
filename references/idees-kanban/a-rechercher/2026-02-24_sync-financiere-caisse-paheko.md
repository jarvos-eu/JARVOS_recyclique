# Sync financiere caisse Paheko

---

## 2026-02-24 — Mary (brainstorm migration)

Comment les sessions de caisse Recyclic generent des ecritures dans Paheko. Source de verite, modele de sync, frequence. Prerequis critique avant tout developpement financier.

Intention : a-rechercher

---

## 2026-02-24 — Cartographie interne + decision Option B

### Ce qu'on sait — Recyclic 1.4.4

Modeles : `CashSession`, `CashSessionStep`, `Sale`, `SaleItem`, `PaymentTransaction`, `CashRegister`. Workflow session : ouverture (fond de caisse) -> saisie tickets (articles / categ / prix / poids) -> fermeture (montants, ecart, variance) -> rapport email. Donnees a la fermeture : total encaisse especes/cheques, detail tickets+lignes, `total_weight_out`, fond de caisse + ecart. Decision dec 2025 : cheques comptabilises a l'encaissement.

### Decision Option B confirmee (session max Paheko)

Caisse Paheko native utilisee. Recyclic = surcouche UX ; on se cale sur le workflow Paheko. Voir `references/artefacts/2026-02-24_08_decision-architecture-max-paheko.md`.

### Ecritures attendues (plan comptable associatif)

Vente especes : 53 / 707. Vente cheque : 511 / 707. Remise cheques : 512 / 511. Ecart positif : 53 / 758. Ecart negatif : 658 / 53.

### Questions ouvertes (bloquantes pour design BDD)

1. **Source de verite caisse** : Paheko seul (Recyclic n'a plus de tables caisse) vs miroir (Recyclic garde tables + sync). A decider apres recherche API Paheko.
2. Granularite des ecritures : par session ? par categorie ? par ticket ?
3. Timing push : fermeture session temps reel ou batch ?
4. Document correspondances : pas fourni par Germaine/Corinne ; acces aux dumps BDD prod Recyclic + Paheko prevu, montage en local pour analyser et deduire (2e passe).

Blocage actuel : recherche API Paheko caisse (endpoints, modeles) necessaire avant de trancher source de verite.

---

## 2026-02-25 — Decisions 2e passe

- **Source de verite** = Paheko seul. RecyClique gere la caisse en propre et envoie a la fermeture un payload vers un plugin PHP Paheko (ex. recyclique) qui ecrit dans plugin_caisse_* et appelle POS::syncAccounting().
- Pas d'ecriture directe RecyClique → BDD Paheko ; pas de modification du core Paheko.
- Tables caisse confirmees (plugin_caisse_sessions, tabs, tabs_items, tabs_payments, etc.) ; ecritures compta creees par syncAccounting, pas a la fermeture.
- Reference : [references/artefacts/2026-02-25_04_analyse-plugins-caisse-decisions-push.md](../../artefacts/2026-02-25_04_analyse-plugins-caisse-decisions-push.md).

---

## 2026-02-25 — Decisions granularite push et resilience

- **Push par ticket** (pas par session) ; clôture = syncAccounting + contrôle.
- **File d'attente** = Redis Streams (côté FastAPI), workers consommateurs, retry si Paheko down.
- References : [artefact 2026-02-25_07](../../artefacts/2026-02-25_07_decisions-push-redis-source-eee.md), [grille 05](../../artefacts/2026-02-25_05_grille-confrontation-recyclic-paheko.md).
