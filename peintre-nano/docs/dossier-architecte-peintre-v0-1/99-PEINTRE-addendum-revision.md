# 99-PEINTRE — Addendum de révision finale

> **But** : passe de revue après les 3 tours. Consigne les trous comblés, les incohérences restantes, les points qui attendent encore un arbitrage Strophe, et fait le bilan de complétude pour Cursor. À lire **après** le reste du dossier.

## 1. Trous comblés dans cette passe

- **04C non tissé** : les fichiers cœur (`02`, `04B`, `05`) ne référençaient pas les templates/overlays alors qu'ils en dépendent. Liens ajoutés (régions = template courant, `ResolvedLayout` porte `overlays`, trajectoire cite `04C`).
- **Arbitrage « 5 zones figées »** : corrigé (D-13/D-14, `04C`, `0A` §2.4 révisé). Le moteur n'a plus de constante de régions.
- **Validation des nouveaux objets CREOS** : point de greffe identifié (chaîne `validation/`, `0A` §3) — plus une zone grise.

## 2. Incohérences mineures restantes (à nettoyer en implémentation, non bloquantes)

- **Nom de fichier `02`** : ~~garde le suffixe `-v1`~~ **corrigé** → `02-PEINTRE-vision-cible-v0-1.md` (post-QA2). Les liens internes pointent par numéro, non cassés.
- **Dossier nommé `dossier-peintre-v1/`** : idem, viser `dossier-peintre-v0-1/` au dépôt.
- **Régions `toolbar`/`footer`** : `04B` parle parfois de `toolbar` comme rôle ; cohérent avec `04C` (rôle, pas région) mais à garder à l'œil lors du codage du schéma `presentation.region` (enum de rôles vs ids de régions du template — bien séparer les deux énumérations).

## 3. Points tranchés par Strophe (clôturés) + reste ouvert

**Tranchés (HITL) — à appliquer :**
- **Q-02** : pilote **caisse d'abord**, généralisation ensuite.
- **Q-04** : **règles (3a) en v0.1**, génératif (3b) plus tard (préparé via hook inerte, D-15).
- **Q-05** : mode sombre **préparé, pas livré** (architecture 2-niveaux + theme CREOS le permet ; prise inerte D-15).
- **Q-06** : extraction repo **reportée** ; durcir frontières seulement.
- **Q-07** : prefs user à **deux niveaux** via `pref_scope` device/identity ; le champ existe en v0.1 même si un seul niveau est câblé (D-15).
- **Q-08** : « affichage parfait par défaut » = **règles basiques** en v0.1, barème affinable plus tard.
- **Q-09** : **chaque template porte SA liste d'étiquettes (rôles)** ; `standard-5` a la sienne (fermée), les autres templates sont libres d'avoir les leurs. Pas de liste globale fixe. *(corrige la proposition initiale)*
- **Q-10** : **un seul theme actif** en v0.1, mais le résolveur accepte une **pile** et un **mock à 2 themes** prouve l'empilage futur (D-15).

**Principe transversal acté — D-15** : tout « plus tard » est une **prise inerte concrète dans le code** (interface/hook/mock), jamais une simple note. Chaque story réservée porte un AC « prise posée + test de réservation ».

**Encore à définir (non bloquant pour démarrer A-1) :**
- Q-08 barème précis (critères + pondération) — quand on attaquera le défaut moteur.
- Confirmation chaîne validation (voir §5, **le dossier `validation/` n'était pas dans le zip fourni**).

## 4. Risques nouveaux apparus avec templates/overlays

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Le passage région-constante → template **casse des manifests/tests existants** | élevé | template `standard-5` strictement iso-actuel ; tests de parité avant tout autre template |
| `OverlayHost` introduit des bugs de **focus/clavier** (piège classique) | moyen | réutiliser une primitive éprouvée (focus-trap) ; pilote unique avant d'ouvrir la vanne |
| Le **debounce** de réévaluation support (`04B` §7) provoque un flicker au resize | faible | recalcul idempotent + transition CSS ; tester rotation tablette |
| Sur-déclaration CREOS (trop de champs par slot) **alourdit les manifests** | moyen | défauts moteur généreux ; ne déclarer que ce qui dévie du défaut |

## 5. Confirmation de la greffe du « videur » (chaîne de validation) — **CONFIRMÉE**

Le dossier `src/validation/` a été lu (`page-manifest-ingest`, `validate-bundle-rules`, `allowed-widget-types`, `navigation-ingest`, `key-normalize`, `manifest-validation-types`). **La greffe est non seulement possible, elle est facile et à moitié préparée.** Preuves :

- **Champ `presentation` optionnel sur le slot** : `parsePageManifestJson` lit déjà `widgetProps`, `requiredPermissionKeys`, `requiresSite` selon le pattern *« si défini → valider, sinon ignorer »*. Ajouter `presentation` = **dupliquer le bloc `widgetProps`**. Trivial.
- **Rétrocompatibilité prouvée** : le parser **ignore silencieusement les champs inconnus** et reconstruit un objet propre → un manifest Story 3.x avec un futur `presentation` ne casse pas, même avant greffe ; après greffe, il est lu.
- **CREOS snake_case géré** : `deepMapKeysToCamelCase` normalise → `presentation_surface` (CREOS) → `presentationSurface` automatiquement.
- **Allowlist overlay = gratuite** : `allowed-widget-types` dérive directement du registre (`getRegisteredWidgetTypeSet`). L'overlay `keyboard-shortcuts-panel` n'a qu'à être **enregistré comme widget normal** → automatiquement autorisé. Zéro modif de l'allowlist. *(valide « overlay = widget registry standard », `04C`.)*
- **Règles de bundle additives** : `validateManifestBundle` est une suite de règles indépendantes (collisions routeKey/path/shortcut/pageKey). Ajouter une règle `layout_template`/`overlay` = bloc en fin, **sans toucher l'ordre existant**. L'inquiétude initiale tombe.
- **Bonus** : `NavigationEntry.shortcutId` **existe déjà** avec détection de collision → socle de données du pilote raccourcis clavier déjà présent.

**Verdict** : greffe **confirmée**, plus légère que prévu. Reste à confirmer un seul point sur le repo vivant : les marqueurs de `types/context-envelope.ts` pour l'invariant AR39 du profil (`04A` §4) — quel champ dit « ce slot est autorisé ».

## 6. Bilan de complétude (ce que Cursor a / n'a pas)

**A — couvert, prêt à coder :**
- contrat de tokens + résolveur de theme (`03`)
- langage de composition + autorité + support + templates/overlays (`04`/`04A`/`04B`/`04C`)
- pipeline LayoutResolver avec points d'injection réels (`05` + `0A`)
- PRD avec épics/stories/AC (`06`), ADR (`07`), portage (`10`), doc agents (`11`)

**B — confirmé sur le code (plus rien en suspens de bloquant) :**
- chaîne `validation/` : greffe confirmée (§5)
- marqueurs `ContextEnvelope` pour l'invariant AR39 : confirmés — `permissions.permissionKeys`, `contextMarkers`, `effectiveModuleKeys`, `runtimeStatus`, et `presentationLabels` (« présentation uniquement, pas d'accès »). La frontière présentation/accès est **déjà dans les types**.

**B' — confirmé (post-QA2) :**
- `templates/transverse` lu : embryon valide **et** cible de rapatriement (cascade `pageKey` + géométrie en dur à déclarer en données). Voir `0A`, `01` §4bis, `05`. **Plus aucune référence code non vérifiée dans le dossier.**

**C — volontairement hors v0.1 (réservé, pas codé) :**
- intelligence générative 3b (`08`)
- agent-âme + sous-équipes + mémoire (`11`)
- remapping live des raccourcis (`04C` §6)
- templates additionnels (plein écran, dashboard…) au-delà de `standard-5`
- édition par drag-and-drop des régions par l'utilisateur

## 7. Première action concrète recommandée pour Cursor

1. Lire `index` → `01` → `0A` → `02`, puis le noyau `03`/`04`/`04A`/`04B`/`04C` → `05`.
2. Confirmer §5 (chaîne validation + ContextEnvelope) sur le repo vivant.
3. Démarrer **Épic A-1** (contrat de tokens + resolveTheme) : levier le plus rentable, sans dépendance, débloque immédiatement le rendu convaincant.
4. Remonter à Strophe Q-07/Q-08/Q-09/Q-10 avant d'attaquer le portage caisse (Tour 2) et l'intelligence (Phase 3).

## 8. Ce qui fait que ce dossier tient

Un seul fil, du premier fichier au dernier : **tout ce qui touche l'affichage entre par CREOS, s'exprime en intentions, et est résolu par un moteur qui ne sait rien d'aucune application.** App, user et agent parlent la même grammaire ; le moteur ne fige ni les couleurs, ni les routes, ni le nombre de zones ; et la place de l'âme est réservée partout sans jamais être codée. Si une décision future contredit ce fil, c'est le fil qui a raison — ou alors c'est une vraie rupture à acter par un nouvel ADR.