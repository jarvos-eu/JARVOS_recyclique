# Procédure d'activation — module comptage pièces/billets (pilote La Clique)

**Date :** 2026-06-06  
**Stories :** 9.11 (backend) · 9.12 (wizard) · **9.13** (activation admin)  
**Décisions :** [`2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md`](../artefacts/2026-06-06_01_decisions-hitl-comptage-pieces-billets-pilote.md)

---

## Prérequis

1. Stories **9.11** et **9.12** déployées (API + Peintre).
2. Migration **`s9_13_comptage_pilot_site_module_config`** appliquée **ou** activation manuelle ci-dessous.
3. Compte admin avec permission **`transverse.admin.view`** sur le site pilote.

---

## Identifier le site pilote

1. Ouvrir **Admin → Sites** (ou consulter l'enveloppe de contexte sur un poste pilote).
2. Noter le **`site_id`** du site « La Clique » (prod ou préprod désigné par Strophe).
3. Option ops : variable d'environnement **`PILOT_SITE_ID=<uuid>`** lors de la migration Alembic (sinon lookup automatique par nom `%La Clique%`).

---

## Activation via `/admin/modules`

1. Se connecter avec un profil admin du site pilote.
2. Naviguer vers **`/admin/modules`**.
3. Ouvrir l'accordéon **« Comptage pièces / billets (clôture) »**.
4. Vérifier / régler les interrupteurs :

| Champ | Valeur pilote (D-CPT-07) |
|-------|--------------------------|
| Module activé | **Oui** |
| Autoriser le passage sans comptage | **Non** |
| Grille complète obligatoire | **Oui** |
| Afficher les pictos | **Oui** (D-CPT-06) |

5. Saisir un **motif** (ex. « Activation pilote v2.0.2 ») et cliquer **Enregistrer le module comptage**.
6. Recharger la page : les valeurs doivent refléter le serveur (badge « Synchronisé avec le serveur » sur le bandeau KPI si applicable).

---

## Check-list recette — module **off** (Q-HITL-09)

| # | Étape | Résultat attendu |
|---|-------|------------------|
| R09.1 | `GET module-config/comptage-pieces-billets` → `enabled: false` | Defaults safe (legacy) |
| R09.2 | Wizard clôture caisse | Pas de panel « Comptage pièces » |
| R09.3 | Saisir `actual_amount`, clôturer sous seuil D33 | **200**, session fermée |
| R09.4 | Snapshot session | Pas de bloc `denomination_count_v1` |
| R09.5 | Outbox Paheko | T1–T3 inchangés (story 9.10) |

---

## Check-list recette — module **on** (Q-HITL-11)

| # | Étape | Résultat attendu |
|---|-------|------------------|
| R11.1 | Config pilote active | `enabled: true`, `skip_allowed: false`, `require_denomination_grid: true` |
| R11.2 | Clôture sans `PUT denomination-count` | **400** `COMPTAGE_REQUIRED` |
| R11.3 | Grille 15 lignes + relecture (9.12) | Close **200** |
| R11.4 | UI wizard | Pas de bouton « Passer » |
| R11.5 | `show_images: false` puis `true` | Pictos masqués puis visibles |

---

## Flux complet module on (Q-HITL-09 / Q-HITL-10)

1. Ouvrir wizard clôture caisse.
2. Saisir la grille (15 lignes, y compris quantités 0).
3. Valider la **relecture** obligatoire.
4. Saisir le **PIN** opérateur.
5. Vérifier snapshot : présence `denomination_count_v1`.
6. Vérifier chaîne Paheko T1–T3 : **aucune régression** vs story 9.10.

---

## Rollback

1. `/admin/modules` → désactiver **Module activé** (`enabled: false`).
2. Enregistrer.
3. Prochaine clôture : flux legacy R09.x (sans grille).

Aucune migration BDD métier requise pour le rollback — seule la ligne `site_module_configs` change.

---

## Validation Strophe

- Recette Q-HITL-09 et Q-HITL-11 cochées sur le site pilote.
- Contact équipe dev si `GET module-config` renvoie **404** (registre non déployé) ou **422** (payload invalide).
