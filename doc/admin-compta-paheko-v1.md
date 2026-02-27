# Accès à l'administration compta via Paheko (v1)

**Story 8.6 — FR12.** En v1, la comptabilité est administrée dans Paheko ; RecyClique envoie les ventes et les clôtures (Epic 5) mais n'a pas d'interface compta propre.

---

## URL d'accès

L'interface d'administration Paheko (dont la section Comptabilité) s'ouvre à l'URL suivante.

### Règle de construction

À partir de l'URL du plugin RecyClique configurée côté serveur (`PAHEKO_PLUGIN_URL`, ex. `https://paheko.example/plugin/recyclic/push`) :

1. Prendre l'**origine** (schéma + hôte + port éventuel) : `https://paheko.example`
2. Ajouter le chemin d'administration : **`/admin/`**

**URL d'accès administration Paheko :**

```
{origine_paheko}/admin/
```

Exemple : si `PAHEKO_PLUGIN_URL=https://paheko.example/plugin/recyclic/push`, l'URL admin est **`https://paheko.example/admin/`**.

Une fois dans l'interface d'administration Paheko, aller dans la section **Comptabilité** (menu ou onglet selon la version).

---

## Rôle requis côté Paheko

- **Lecture compta** : niveau d'accès Paheko **read** (consulter plans comptables, exercices, journaux, exports).
- **Écriture compta** : niveau d'accès Paheko **write** (créer/modifier des écritures, lier des transactions, etc.).

En pratique, utiliser un **compte Paheko** (membre ou credentials API) ayant au moins le droit **write** sur le module Comptabilité. Les comptes avec accès **admin** ont tous les droits.

Référence technique : `references/paheko/liste-endpoints-api-paheko.md` (section Accounting).

---

## Contexte v1

- RecyClique pousse les **ventes** et les **clôtures de session** vers Paheko (Epic 5).
- La **compta** (écritures, rapprochement, exports) se fait dans l'interface Paheko.
- RecyClique ne propose pas d'écran compta en v1 ; ce document et, si configuré, le lien depuis le menu Admin permettent d'accéder rapidement à Paheko.

---

## Lien depuis RecyClique (optionnel)

Si l'instance est configurée avec une URL Paheko (`PAHEKO_PLUGIN_URL`), un lien **« Comptabilité (Paheko) »** peut apparaître sur le tableau de bord Admin (réservé aux utilisateurs avec permission admin). Ce lien ouvre l'interface d'administration Paheko dans un nouvel onglet.

En l'absence de configuration ou pour un utilisateur sans droit admin, seule cette documentation permet de retrouver l'URL.
