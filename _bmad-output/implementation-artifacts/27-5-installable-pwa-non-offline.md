# Story 27.5 : PWA installable non-offline

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

**Story key :** `27-5-installable-pwa-non-offline`  
**Epic :** 27 — Postes partagés enrôlés + PIN opérateur + PWA installable non-offline  
**Implementation artifact :** `_bmad-output/implementation-artifacts/27-5-installable-pwa-non-offline.md`  
**Date CS :** 2026-05-30

## Dépendances (prérequis)

- **Stories 27.1–27.4 done** : registre `RegisteredDevice`, contexte serveur + audit, panel SuperAdmin, enrôlement IndexedDB + credential device — fichiers `_bmad-output/implementation-artifacts/27-1-registered-device.md` … `27-4-enrollment-reconnect-replace.md`.
- **Epic 27 — cadrage gelé** : `_bmad-output/planning-artifacts/epics.md` (§ Epic 27, Story 27.5).
- **Mini-ADR Epic 27** : `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — § PWA installable (icône, standalone, **aucun** cache offline métier).
- **Cadrage produit** : `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.8 bis PWA, §3.8 ter navigateur dédié.
- **Runbook orchestration** : `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — ordre §4, invariants §7, gates PWA §8.
- **Contrat OpenAPI** : `contracts/openapi/recyclique-api.yaml` — **pas de modification attendue** pour cette story (périmètre front + doc terrain) ; les routes Epic 27 existantes exposent déjà `Cache-Control: no-store` (ex. `registered_devices`, `shared_workstation`).
- **Stories suivantes (ne pas implémenter ici)** : 27.6 (lock screen PIN + session opérateur), 27.7 (intersection modules serveur), 27.8 (brouillons Reception), 27.9 (timeout / passer la main), 27.10 (override SuperAdmin).

## Garde-fous ADR / runbook (obligatoires pour le DS)

| Invariant | Application story 27.5 |
|-----------|-------------------------|
| Installable ≠ offline | Aucune promesse UI ou doc du type « fonctionne hors ligne », « mode déconnecté », « sync différée ». |
| Pas de cache métier | Aucune mise en cache SW/fetch de réponses API authentifiées, brouillons, snapshots live, données caisse/réception, etc. |
| SW borné | Si un service worker est enregistré : **uniquement** precache / runtime cache des **assets statiques** du build Vite (JS/CSS/fonts/images/icônes). |
| Pas d’interception API | Le SW **ne doit pas** enregistrer de handler `fetch` qui matche `/api`, le préfixe `VITE_RECYCLIQUE_API_PREFIX`, ni les chemins proxy dev ; denylist explicite. |
| Network-only métier | Les clients API existants (`peintre-nano/src/api/*`) continuent d’appeler le réseau ; option recommandée : `cache: 'no-store'` sur les `fetch` métier (sans refactor massif — au minimum ne pas introduire de cache). |
| PWA ≠ autorisation | L’installation PWA ne remplace pas enrôlement, credential device, JWT, ni futur PIN (27.6). |
| IndexedDB identité (27.4) | L’identité poste reste dans `device-identity-store.ts` (IndexedDB) ; la PWA partage l’origine — documenter que « vider les données du site » peut effacer l’identité locale (renvoi flux 27.4). |
| Pas `localStorage` autoritaire | Ne pas déplacer identité poste vers `localStorage` pour « faciliter » la PWA. |
| Distinction manifests | `public/manifests/*.json` = **CREOS** (navigation/pages widgets) ; **ne pas** confondre avec le **Web App Manifest** (`manifest.webmanifest`). |
| Palier distinct PRD | Ne pas implémenter offline-first 1.4.4, file d’opérations, PIN kiosque PWA vision. |

## Story (BDD)

As a **field operator**,  
I want **Recyclique installable as a PWA** for a more stable workstation experience,  
So that **shared posts feel app-like without promising offline business operation**.

## Acceptance criteria

Source normative : `_bmad-output/planning-artifacts/epics.md` — **Story 27.5**.

**Given** Epic 27 is explicitly non-offline  
**When** this story is delivered  
**Then** the app provides a PWA manifest, name, icons and standalone launch behavior where supported  
**And** static assets may be cached if needed  
**And** no business data, business API response, draft content, or authenticated endpoint is cached for offline business use  
**And** authenticated business endpoints use `network-only` / `no-store` or an equivalent strategy  
**And** no service worker strategy intercepts authenticated business endpoints  
**And** if a service worker exists, it is limited to static asset caching  
**And** documentation states that installable does not mean offline and recommends a dedicated browser/profile where useful

### Interprétation exécutable

#### 1. Web App Manifest (obligatoire)

Créer un manifeste W3C servi en production et dev :

| Champ | Valeur proposée | Règles |
|-------|-----------------|--------|
| Fichier | `peintre-nano/public/manifest.webmanifest` (ou généré par plugin avec même sémantique) | Copié dans `dist/` au build ; MIME `application/manifest+json`. |
| `name` | `Recyclique` | Libellé installable terrain (pas « Peintre_nano — socle v2 »). |
| `short_name` | `Recyclique` | ≤ 12 caractères si possible. |
| `description` | Courte phrase : poste partagé **connecté** | Sans mot « offline » / « hors ligne ». |
| `start_url` | `/` | `scope` : `/` ; pas de start_url isolée qui contourne l’auth. |
| `display` | `standalone` | `display_override` optionnel : `window-controls-overlay` seulement si testé. |
| `orientation` | `any` | Compatible tablette paysage. |
| `theme_color` / `background_color` | Alignés tokens Mantine / marque existante | Cohérence barre statut installée. |
| `lang` | `fr` | |
| `icons` | Au minimum **192×192** et **512×512** PNG (maskable recommandé) | Fichiers sous `peintre-nano/public/icons/` ; déclarer `purpose: "any"` et `"maskable"` si fourni. |

Lier le manifeste dans `peintre-nano/index.html` :

```html
<link rel="manifest" href="/manifest.webmanifest" />
<meta name="theme-color" content="…" />
```

Mettre à jour le `<title>` et `apple-touch-icon` si icônes dédiées (iOS Safari « Ajouter à l’écran d’accueil »).

**Ne pas** renommer ni fusionner le dossier `public/manifests/` (CREOS).

#### 2. Service worker — stratégie (quasi obligatoire pour installabilité Chromium)

Chrome / Edge exigent en pratique un SW enregistré + manifest pour l’installation bureau. Livrer un SW **minimal** :

**Option recommandée (DS)** : `vite-plugin-pwa` (devDependency) avec configuration explicite :

- `registerType: 'autoUpdate'` (ou `prompt` si l’équipe préfère contrôler le reload — documenter le choix).
- Precache **uniquement** les assets émis par `vite build` (JS/CSS/HTML/icônes/favicon).
- `workbox.navigateFallback` = `index.html` pour le shell SPA **uniquement** sur navigations document ; **denylist** : `/api`, regex préfixe API configurable (`import.meta.env.VITE_RECYCLIQUE_API_PREFIX` par défaut `/api`).
- **Interdit** : `runtimeCaching` sur `https?` générique, `NetworkFirst`/`StaleWhileRevalidate` pour hosts API, cache des réponses `fetch` contenant `Authorization` ou `X-Recyclique-Device-Credential`.
- **Interdit** : precache de fichiers sous `public/manifests/` si cela fige des manifests CREOS obsolètes — si precache, limiter aux assets hashés du bundle ou exclure `manifests/**` du glob precache.

**Alternative** (si plugin rejeté en VS) : SW hand-written < 80 lignes, `install` + precache liste close, **aucun** `fetch` listener — acceptable si preuve installabilité Chrome/Edge.

Sans SW : **FAIL** gate installabilité sauf HITL documenté (navigateur ne supportant que manifest — rare).

#### 3. Politique réseau côté client (complément SW)

- Ne pas ajouter de couche « offline queue » ni de persistance de réponses API.
- Revue ciblée : les nouveaux appels ou wrappers ajoutés pour la PWA ne doivent pas passer par le SW.
- **Optionnel (nice-to-have, non bloquant MVP)** : helper `fetchRecycliqueApi` avec `cache: 'no-store'` par défaut — **ne pas** refactorer tous les clients dans cette story sauf si trivial (< 3 fichiers touchés).

Le backend Epic 27 pose déjà `Cache-Control: no-store` sur les endpoints sensibles ; **pas** de story backend obligatoire sauf régression détectée en QA.

#### 4. UX — message « installable ≠ offline »

Livrable doc **obligatoire** (fichier suggéré : `peintre-nano/docs/pwa-terrain.md` ou section README peintre-nano) couvrant :

1. **Installable ne signifie pas hors ligne** — l’app nécessite le réseau pour toute action métier.
2. **Navigateur / profil dédié** (cadrage §3.8 ter) : ex. installer depuis Edge si Chrome sert au quotidien ; profil séparé ; éviter extensions qui purgent le stockage.
3. **Perte d’identité locale** : effacer données du site / désinstaller PWA peut nécessiter reconnexion SuperAdmin (story 27.4).
4. **Checklist installation manuelle** : HTTPS (ou localhost dev), icône bureau, ouverture standalone, vérifier qu’une requête `/api/...` authentifiée part bien en réseau (DevTools → pas de réponse SW).

**Optionnel UI** (Story Runner tranche) : encart discret sur la page enrôlement `/shared-workstation/enroll` ou footer admin — **sans** bloquer le DS si doc seule suffit.

#### 5. Compatibilité navigateurs (matrice MVP)

| Cible | Attendu |
|-------|---------|
| Chrome / Edge desktop Windows | Install prompt ou menu « Installer » ; standalone. |
| Edge / Chrome Android tablette | Ajout écran d’accueil ; standalone. |
| Safari iOS | `apple-mobile-web-app-capable` ; pas d’exigence install prompt identique — doc « Partager → Sur l’écran d’accueil ». |
| Firefox desktop | Manifest + icône ; installabilité variable — pas bloquant. |

**HITL** si échec installabilité sur matériel terrain réel : remonter avec navigateur/OS/version — ne pas élargir le scope offline pour compenser.

#### 6. Build / déploiement

- `npm run build` produit `dist/manifest.webmanifest`, icônes, SW enregistré (fichier `sw.js` ou injecté).
- `npm run preview` permet test install local (localhost considéré sécurisé pour dev).
- Docker / prod : servir le manifeste et le SW avec les bons en-têtes ; pas de cache CDN agressif sur `sw.js` (invalidation à chaque release — `autoUpdate`).

### Hors scope explicite

- Lock screen PIN, endpoints PIN, session opérateur UI (**27.6**).
- Intersection modules, filtrage nav métier poste (**27.7**).
- Brouillons Reception masqués (**27.8**).
- Timeout inactivité, passer la main (**27.9**).
- Override SuperAdmin (**27.10**).
- Modifications OpenAPI / CREOS (sauf lien doc vers manifests CREOS inchangés).
- Push notifications, background sync, periodic sync, Web Share ciblé offline.
- Génération d’icônes brand finalisées par un designer — MVP = icônes propres dérivées du logo existant (`vite.svg` ou asset Recyclique si présent dans le dépôt).
- Tests E2E multi-navigateurs automatisés (Playwright install PWA) — optionnel ; revue manuelle + tests unitaires manifest suffisent MVP.

### Dépendances 27.1–27.4 (réutilisation, pas de rework)

| Story | Élément réutilisé par la PWA |
|-------|------------------------------|
| 27.1 | Aucun changement API ; le manifeste ne lit pas `device_id`. |
| 27.2 | Les appels métier restent soumis au garde serveur ; la PWA ne court-circuite pas `shared_workstation_guard`. |
| 27.3 | Panel admin inchangé ; doc peut mentionner l’install depuis poste enrôlé. |
| 27.4 | `device-identity-store.ts` (IndexedDB) fonctionne dans le contexte PWA installée (même origine) ; route `/shared-workstation/enroll` reste le point d’entrée enrôlement. |

**Note epics.md** : la 27.4 est utile pour un parcours terrain bout-en-bout, mais **l’installation PWA n’est pas un mécanisme d’autorisation**.

### Anti-patterns (interdits)

- Workbox `runtimeCaching` avec URL contenant `/api` ou le host backend.
- Precache des réponses JSON dynamiques (live snapshot, listes admin, etc.).
- Message marketing « mode hors ligne » ou badge « disponible offline ».
- Utiliser le SW pour servir une page métier en cache quand le réseau est down.
- Confondre `public/manifests/navigation.json` (CREOS) avec `manifest.webmanifest`.
- Stocker secret device ou JWT dans le cache SW / Cache API.
- Exiger JWT utilisateur pour afficher le manifeste ou le SW (fichiers publics statiques).
- Modifier `sprint-status.yaml` depuis DS.
- Étendre le scope vers sync différée ou file locale « pour améliorer la PWA ».

### Testing / gates (Story Runner)

| Gate | Commande / critère |
|------|-------------------|
| Lint / build front | `cd peintre-nano && npm run lint && npm run build` → exit 0 |
| Manifest présent | Après build : `dist/manifest.webmanifest` existe ; JSON valide ; champs `name`, `icons`, `display`, `start_url` |
| Lien HTML | `dist/index.html` contient `rel="manifest"` |
| Revue SW | Grep / revue : aucune règle Workbox sur `/api` ; pas de `fetch` handler catch-all sur requêtes authentifiées |
| Test unitaire manifest | Fichier suggéré : `peintre-nano/tests/unit/pwa-manifest.test.ts` — parse JSON, tailles icônes déclarées, `display === 'standalone'` |
| Test non-régression 27.4 | `npm run test -- --run tests/unit/device-identity-store.test.ts tests/unit/shared-workstation-enrollment*.test.tsx` |
| Doc terrain | Fichier doc §4 présent et mentionne installable ≠ offline + navigateur dédié |
| OpenAPI | **Aucune modification** attendue — gate = diff vide sur `contracts/openapi/recyclique-api.yaml` |
| Backend | **Aucun test backend obligatoire** sauf régression involontaire — gate = pas de changement `recyclique/api/` ou tests existants Epic 27 verts si touchés |
| Preuve QA manuelle | Checklist §4.4 : install locale, ouverture standalone, requête API visible « from network » (pas SW) dans DevTools |

`gates_skipped_with_hitl: false` — **interdit** de skip gates PWA / build / revue SW pour cette story.

### Project Structure Notes

| Zone | Fichiers / dossiers |
|------|---------------------|
| Manifest + icônes | `peintre-nano/public/manifest.webmanifest`, `peintre-nano/public/icons/*` |
| Entrée HTML | `peintre-nano/index.html` |
| Config Vite | `peintre-nano/vite.config.ts` (+ plugin PWA si retenu) |
| Doc terrain | `peintre-nano/docs/pwa-terrain.md` (créer) |
| Tests | `peintre-nano/tests/unit/pwa-manifest.test.ts` (suggéré) |
| Optionnel UI | `peintre-nano/src/domains/shared-workstation/` — encart doc seulement |

Ne pas déplacer les manifests CREOS hors de `public/manifests/`.

### References

- `_bmad-output/planning-artifacts/epics.md` — Epic 27, Story 27.5
- `_bmad-output/implementation-artifacts/27-4-enrollment-reconnect-replace.md` — IndexedDB, route enrôlement
- `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md` — § PWA installable
- `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md` — §3.8 bis, §3.8 ter
- `references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md` — §7–8
- `peintre-nano/vite.config.ts` — proxy `/api`
- `peintre-nano/src/domains/shared-workstation/device-identity-store.ts`
- `_bmad-output/project-context.md`

## Trace Epic 27 — ADR

| Élément | Valeur |
|--------|--------|
| Nouvelle ADR structurante requise ? | **ADR N/A pour 27.5** — application des décisions mini-ADR § PWA installable et runbook §7. |
| ADR applicables | Mini-ADR 2026-05-29 ; cadrage §3.8 bis / §3.8 ter. |

## Alignement sprint / YAML

- Clé **`27-5-installable-pwa-non-offline`** : **non modifiée** par ce worker CS (writer unique Epic Runner — pas de passage `ready-for-dev` dans `sprint-status.yaml` depuis CS).
- **`epic-27`** : inchangé par CS.
- Prochaine story après clôture 27.5 : **`27-6-pin-lock-operator-session`** (ordre runbook §4).

## Risques / HITL

| Sujet | Statut | Action |
|-------|--------|--------|
| Niveau support tablette / navigateur | Risque epics | Matrice §6 ; HITL Strophe seulement si matériel terrain incompatible après implémentation. |
| `vite-plugin-pwa` vs SW minimal | Proposition DS | Plugin recommandé avec denylist `/api` ; VS peut imposer SW minimal si config Workbox trop risquée. |
| Icônes brand définitives | Proposition | MVP dérivé asset existant ; HITL design si marketing exige charte stricte. |
| Encart UI vs doc seule | Proposition | Doc obligatoire ; encart optionnel sur `/shared-workstation/enroll`. |
| Safari install prompt | Connu | Documenter procédure manuelle ; pas d’exigence parity Chrome. |

**NEEDS_STROPHE_HITL** : non requis pour démarrer le DS si le dev suit les propositions ci-dessus (plugin PWA + denylist API + doc terrain).

## Checklist VS (validate-create-story)

- [x] AC BDD alignés `epics.md` §27.5 (manifest, icônes, standalone, pas cache métier, SW borné, doc installable ≠ offline).
- [x] Garde-fous mini-ADR § PWA + runbook §7 (pas SW sur API auth, pas offline métier).
- [x] Distinction `manifest.webmanifest` vs `public/manifests/` CREOS explicite.
- [x] Dépendances 27.1–27.4 référencées ; hors scope 27.6–27.10 explicite.
- [x] Gates § Testing (build, manifest, revue SW, doc, pas de changement OpenAPI attendu).
- [x] Anti-patterns couvrent Workbox API, messages offline, localStorage identité.
- [x] `sprint-status.yaml` non modifié par CS/VS (writer unique Epic Runner).

## Tasks / Subtasks (DS)

- [x] Web App Manifest `public/manifest.webmanifest` + icônes 192/512
- [x] `index.html` : lien manifest, theme-color, Apple meta, titre Recyclique
- [x] `vite-plugin-pwa` : precache assets statiques, denylist `/api`, `runtimeCaching: []`, exclusion `manifests/**`
- [x] Doc terrain `peintre-nano/docs/pwa-terrain.md`
- [x] Tests unitaires `pwa-manifest.test.ts`
- [x] Tests backend `test_story_27_5_pwa_non_offline.py` (headers `no-store` Epic 27)
- [x] Gates : pytest `-k story_27_5`, lint, vitest, build

## Change Log

- 2026-05-30 — Story 27.5 CS (create) : guide dev PWA non-offline ; garde-fous ADR/runbook §7 ; gates explicites ; Status `ready-for-dev` ; sprint-status non modifié (writer unique).
- 2026-05-30 — Story 27.5 VS (validate, vs_loop=0) : **PASS** — AC epics §27.5, mini-ADR § PWA installable, runbook §7–§8, invariants manifest/icône/standalone, SW statique uniquement, denylist `/api`, doc installable ≠ offline, checklist complète ; prêt DS.
- 2026-05-30 — Story 27.5 DS : PWA installable (manifest, icônes, SW minimal Workbox), doc terrain, tests front/back ; Status `review`.
- 2026-05-30 — Story 27.5 CR1 (cr_loop=0) : **APPROVE** — invariants runbook §7 / AC epics §27.5 satisfaits ; findings LOW documentés, aucun correctif bloquant.

## Code Review

### CR1 (cr_loop=0) — **APPROVE** (2026-05-30)

**Verdict :** PASS — livrable conforme aux AC story 27.5 et invariants runbook §7 (pas d’offline métier, SW borné aux assets statiques, denylist `/api`, `runtimeCaching: []`, doc installable ≠ offline, complément backend `no-store` Epic 27).

**Gates revus :** `pwa-manifest.test.ts` 6/6 ; `test_story_27_5_pwa_non_offline.py` 2/2 ; analyse `dist/sw.js` (precache sans `manifests/**` CREOS, denylist `/api`, pas NetworkFirst/SWR).

**Findings (non bloquants) :**

| Sévérité | Finding | Action |
|----------|---------|--------|
| LOW | Double source manifest (`public/manifest.webmanifest` + bloc `manifest` dans `vite.config.ts`) — risque de dérive | Garder les deux fichiers alignés ou unifier en follow-up |
| LOW | `navigateFallbackDenylist` duplique `/^\/api/` quand le préfixe par défaut est `/api` | Cosmétique |
| LOW | Double `<link rel="manifest">` dans `dist/index.html` (source + injection `vite-plugin-pwa`) | Cosmétique ; unifier en follow-up si souhaité |
| LOW | Proxy dev hardcodé `/api` alors que `recycliqueApiPrefix` est configurable au build | Documenter si changement de préfixe prévu |
| LOW | Icônes `maskable` réutilisent les mêmes PNG que `any` (safe zone non optimisée) | Acceptable MVP (story) |
| INFO | Hors ligne, le shell SPA peut s’afficher depuis le precache sans données métier | Couvert par `pwa-terrain.md` |

**Fichiers modifiés par CR :** aucun (pas de patch trivial requis).

### Review Findings

_(Aucun item `decision-needed` ou `patch` ouvert — revue clôturée APPROVE.)_

## Dev Agent Record

### Agent Model Used

Composer (DS worker bmad-dev-story)

### Debug Log References

- `vite-plugin-pwa@^0.21.1` — `registerType: autoUpdate`, `devOptions.enabled: false`
- Build : `dist/sw.js`, `dist/manifest.webmanifest`, `dist/icons/icon-{192,512}.png`

### Completion Notes List

- Manifest W3C distinct des manifests CREOS (`public/manifests/`).
- SW : precache bundle Vite uniquement ; `navigateFallbackDenylist` sur `/api` et préfixe configurable ; pas de `runtimeCaching` métier.
- Backend : 2 tests `story_27_5` vérifient `Cache-Control: no-store` sur list registered-devices et flux enrôlement shared-workstation.
- OpenAPI inchangé.

### File List

- `peintre-nano/package.json`
- `peintre-nano/package-lock.json`
- `peintre-nano/vite.config.ts`
- `peintre-nano/index.html`
- `peintre-nano/public/manifest.webmanifest`
- `peintre-nano/public/icons/icon-192.png`
- `peintre-nano/public/icons/icon-512.png`
- `peintre-nano/docs/pwa-terrain.md`
- `peintre-nano/tests/unit/pwa-manifest.test.ts`
- `recyclique/api/tests/test_story_27_5_pwa_non_offline.py`
- `recyclique/api/pyproject.toml` (marqueurs pytest `story_27_4`, `story_27_5`)
