# PWA Recyclique — terrain (installable, non offline)

## Installable ne signifie pas hors ligne

Recyclique peut être **installée** comme application (PWA) pour une expérience plus stable sur poste partagé (fenêtre dédiée, icône, mode `standalone`).

Toute **action métier** (caisse, réception, admin, live, enrôlement poste, etc.) nécessite une **connexion réseau** vers l’API Recyclique. Il n’y a pas de mode déconnecté, pas de synchronisation différée des opérations métier, et aucune promesse de fonctionnement hors ligne.

## Navigateur et profil dédiés

Recommandations terrain (cadrage postes partagés) :

- Installer depuis un navigateur **dédié** au poste (ex. Edge sur le poste caisse si Chrome sert au quotidien ailleurs).
- Utiliser un **profil navigateur séparé** pour limiter les extensions qui purgent le stockage ou interceptent le trafic.
- Éviter les modes « navigation privée » permanents si l’enrôlement poste doit persister entre sessions.

## Identité poste locale (story 27.4)

L’identité d’appareil enregistré est stockée en **IndexedDB** (`device-identity-store`), pas en `localStorage`.

**Effacer les données du site**, désinstaller la PWA ou réinitialiser le navigateur peut **supprimer cette identité** : un SuperAdmin devra alors régénérer un code d’enrôlement (flux `/shared-workstation/enroll`).

L’installation PWA **ne remplace pas** l’enrôlement, le credential device ni l’authentification utilisateur.

## Manifests CREOS vs Web App Manifest

- `public/manifests/*.json` — manifests **CREOS** (navigation, pages, widgets). Ne pas les confondre avec le manifeste d’installation PWA.
- `public/manifest.webmanifest` — **Web App Manifest** W3C pour l’installation PWA.

## Checklist installation manuelle (QA)

1. Servir l’app en **HTTPS** (ou `localhost` en développement).
2. Ouvrir l’application, vérifier la présence du manifeste (`/manifest.webmanifest`) et des icônes.
3. Installer via le navigateur (Chrome/Edge : « Installer l’application » ; Safari iOS : Partager → Sur l’écran d’accueil).
4. Lancer l’app installée : vérifier le mode **standalone** (pas de barre d’URL complète selon OS).
5. Ouvrir les DevTools → onglet **Réseau** : effectuer une requête API authentifiée (`/api/...`). La réponse doit provenir du **réseau**, pas du **Service Worker** (colonne « Size » / type « from ServiceWorker » absent pour l’API métier).
6. Confirmer qu’aucun message UI ne suggère un « mode hors ligne » ou une « sync différée ».

## Service worker (périmètre)

Un service worker minimal peut mettre en cache **uniquement** les assets statiques du build (JS, CSS, HTML, icônes). Il **n’intercepte pas** les chemins `/api` ni les réponses métier authentifiées.

## Mise à jour

Le service worker est configuré en `autoUpdate` : une nouvelle version déployée remplace le SW au prochain chargement (rechargement conseillé après déploiement majeur).
