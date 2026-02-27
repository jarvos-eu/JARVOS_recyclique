# Story 8.6 — Accès et documentation pour l'administration compta via Paheko (v1)

- **Epic:** epic-8 (Administration, compta v1 et vie associative)
- **Story_key:** 8-6-acces-et-documentation-pour-l-administration-compta-via-paheko-v1
- **Références:** `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.6)
- **FR:** FR12 — Un responsable compta peut administrer la compta via l'interface Paheko (v1) en attendant les interfaces RecyClique.
- **Livrable:** Documentation (URL + rôle requis) + éventuel lien ou redirection depuis RecyClique.

---

## User story

En tant que responsable compta,
je veux savoir comment accéder à l'interface Paheko pour administrer la compta en v1,
afin de faire la compta pendant que les interfaces RecyClique ne sont pas encore disponibles.

---

## Critères d'acceptation

- **Étant donné** une instance avec RecyClique et Paheko déployés et la caisse synchronisée (Epic 5),
- **Quand** je consulte la documentation ou l'aide RecyClique,
- **Alors** l'accès à l'interface Paheko pour la compta est documenté : **URL** (ou méthode pour la construire selon l'environnement) et **rôle requis** côté Paheko (FR12).
- **Et** un lien ou une redirection depuis RecyClique vers cette interface peuvent être ajoutés si pertinent (décision produit : lien dans le menu admin, page Aide, ou doc seule).

### Détail attendu

- **Documentation :**
  - URL (ou base + chemin) de l'interface Paheko pour la compta (ex. section Comptabilité / Accounting).
  - Rôle ou niveau d'accès Paheko requis (ex. lecture/écriture compta selon `references/paheko/liste-endpoints-api-paheko.md` — Accounting).
  - Contexte v1 : compta administrée via Paheko ; RecyClique pousse les ventes et clôture (Epic 5) ; pas d'interface compta dans RecyClique en v1.
- **Lien ou redirection (optionnel) :**
  - Si pertinent : lien depuis l'interface RecyClique (ex. menu Admin ou Aide) vers l'URL Paheko compta, pour éviter de chercher l'URL manuellement.
  - Sinon : la doc suffit comme livrable.

---

## Livrable

1. **Document** : page ou section documentant l'accès compta Paheko (URL, rôle requis), intégrée à la doc projet (ex. `docs/` ou aide in-app selon convention du projet).
2. **Optionnel :** lien ou redirection depuis RecyClique vers l'interface Paheko compta (écran Admin ou Aide).

---

## Tasks

### Documentation

1. **Rédiger la documentation accès compta Paheko (v1)**
   - Définir l'URL (ou la règle de construction : base URL Paheko + chemin compta) selon l'instance (dev/prod).
   - Documenter le rôle ou le niveau d'accès Paheko requis pour la compta (référence : `references/paheko/liste-endpoints-api-paheko.md`, section Accounting).
   - Indiquer le contexte v1 : RecyClique envoie les ventes et clôture ; la compta est gérée dans Paheko.
   - Placer le document au bon endroit (ex. `docs/admin-compta-paheko-v1.md` ou section dédiée dans la doc existante).

### Frontend (optionnel)

2. **Lien ou redirection depuis RecyClique**
   - Si décision produit : ajouter un lien (menu Admin ou Aide) vers l'URL Paheko compta (ouverte dans un nouvel onglet ou redirection).
   - Afficher le lien uniquement pour les utilisateurs ayant un rôle adapté (ex. responsable compta / admin), si l'info est disponible côté RecyClique.

### Vérification

3. **Validation**
   - Un responsable compta peut suivre la doc pour accéder à Paheko et y faire l'administration compta.
   - FR12 couvert par la documentation (et éventuellement le lien).

---

## Références

- **Epic 8, Story 8.6 :** `_bmad-output/planning-artifacts/epics.md`
- **FR12 (FR Coverage Map) :** Epic 8 — Administrer compta via Paheko (v1)
- **API Paheko Accounting :** `references/paheko/liste-endpoints-api-paheko.md` (section Accounting)

---

## Review

- **2026-02-27** : Code review pass 2 — **approved**. Doc (URL, rôle), GET /v1/admin/paheko-compta-url, lien dashboard Admin vérifiés. FR12 couvert.
