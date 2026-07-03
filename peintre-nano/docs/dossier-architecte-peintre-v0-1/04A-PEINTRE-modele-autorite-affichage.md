# 04A-PEINTRE — Modèle d'autorité d'affichage (défaut → app → user)

> **But** : définir *qui décide quoi* dans la composition d'un écran, **en une seule grammaire CREOS**. C'est la colonne vertébrale de l'agnosticité : Peintre ne décide pas le métier, il **résout une superposition** de couches d'intention exprimées dans le même langage.
> **Décision cadrante (HITL Strophe)** : grammaire unique CREOS — l'app déclare, le user surcharge dans la même grammaire ; hooks d'arbitrage agentique présents mais inertes ; prefs user sur deux niveaux (local + app/back).

## 1. Les trois couches d'autorité

Toutes émettent le **même type d'objet** : un *fragment de profil de composition CREOS* (voir `04`). Elles ne diffèrent que par leur **origine** et leur **précédence**.

```
┌─ COUCHE 0 — DÉFAUT MOTEUR ────────────────────────────────┐
│  Peintre fournit un profil de composition neutre et sûr   │
│  pour tout widget/slot non spécifié. Garantit "jamais     │
│  d'écran cassé". Agnostique : aucune couleur/识identité.    │
│  Précédence : la plus faible.                             │
├─ COUCHE 1 — CONTRAT APP (CREOS) ──────────────────────────┤
│  L'application (ex. Recyclique) déclare l'intention        │
│  métier : theme, priorités, emphase, layout cible par      │
│  support. C'est "l'affichage parfait par défaut" de l'app. │
│  Writer = l'app. Précédence : moyenne.                     │
├─ COUCHE 2 — PRÉFÉRENCE USER (CREOS) ──────────────────────┤
│  Le user surcharge via la MÊME grammaire : voix            │
│  (onboarding permanent JARVOS), poignées de redim,         │
│  déplacement, densité choisie. Précédence : la plus forte  │
│  (sauf invariants, voir §4).                              │
└───────────────────────────────────────────────────────────┘
              │  fusion à la résolution (LayoutResolver, 05)
              ▼
        profil de composition effectif → rendu
```

**Principe** : `effectif = merge(défaut, app, user)` où la précédence croît défaut < app < user, champ par champ (deep-merge sémantique, pas remplacement de bloc).

## 2. Pourquoi une grammaire unique (et pas un canal user séparé)

- **Cohérence** : un override user de densité et une déclaration app de densité sont *le même champ* → fusion triviale, pas de pont à maintenir.
- **Préparation de l'âme** : le futur agent « final cut » émettra exactement le même type de fragment CREOS. Si le user passait par un canal distinct, l'agent aurait un 4ᵉ format à réconcilier. Une grammaire = l'agent se branche sans refonte.
- **Traçabilité** : chaque champ du profil effectif sait *de quelle couche il vient* (provenance), ce qui rend l'arbitrage futur explicable.

## 3. Provenance et merge

Chaque fragment porte sa provenance ; le résultat fusionné conserve, par champ, la couche gagnante.

```jsonc
// Exemple de profil effectif après merge, avec provenance (debug/inspection)
{
  "density":  { "value": "compact",     "from": "user"    },   // user a dit "compact"
  "emphasis": { "value": "primary",     "from": "app"     },   // app l'a déclaré, user muet
  "region":   { "value": "body",        "from": "default" }    // personne n'a parlé
}
```

Règle de merge (deep-merge par champ) :
1. partir du **défaut moteur** ;
2. écraser champ par champ avec le **contrat app** présent ;
3. écraser champ par champ avec la **préférence user** présente ;
4. journaliser la provenance (mode dev) pour inspection.

## 4. Invariants : ce que le user ne peut PAS surcharger

La précédence user est forte mais **bornée par AR39 et la sécurité métier**. **Ancrage code réel** : `runtime/resolve-page-access.ts` est l'autorité d'accès, pure, et documente déjà *« Aucun paramètre UserRuntimePrefs : les prefs UI ne participent pas à la garde page »*. Le modèle ci-dessous ne fait que **prolonger cette frontière existante** à la composition :

- Le user ne peut **pas** faire afficher un widget/slot que le `ContextEnvelope` n'autorise pas (permissions, contexte). La préférence agit sur la *mise en présentation*, jamais sur le *droit d'accès*.
- Le user ne peut **pas** supprimer un slot marqué `required` par le contrat app (ex. un total de caisse réglementaire).
- Le user ne peut **pas** émettre une valeur hors vocabulaire du schéma (`04` est `additionalProperties:false`).

Ces invariants sont **dans le moteur** (agnostiques : « respecter ce que l'app a marqué required/autorisé »), pas des règles Recyclique.

**Ancrage code réel (confirmé)** : `types/context-envelope.ts` fournit déjà tout le nécessaire — `permissions.permissionKeys` (droits effectifs, à croiser avec `requiredPermissionKeys` du PageManifest), `contextMarkers` (*« consommation déclarative uniquement, ne pas inférer de permissions »*), `effectiveModuleKeys` (intersection modules poste partagé), et `runtimeStatus` (`degraded`/`forbidden`). Surtout : `presentationLabels` est documenté *« Présentation uniquement — ne participe pas aux décisions d'accès »*. → **la frontière présentation/accès que ce modèle formalise est déjà tracée dans les types du runtime** ; l'invariant ne fait que la rendre explicite à la résolution du profil.

## 5. Champ `override_policy` (déclaré par l'app, appliqué par le moteur)

L'app déclare, par slot/widget, **jusqu'où** le user peut surcharger. Le moteur applique sans rien savoir du métier.

```jsonc
{
  "slot_id": "caisse-total",
  "presentation": { "emphasis": "primary", "region": "hero" },
  "override_policy": {
    "user_can": ["density", "position"],       // déplacement/densité OK
    "user_cannot": ["visibility", "emphasis"], // ne peut pas masquer ni déprioriser
    "required": true                            // slot non supprimable
  }
}
```

→ C'est ainsi que « l'app porte la priorité d'affichage » (réponse HITL) **sans** que le moteur connaisse la sémantique : il lit `override_policy`, point.

## 6. Hooks d'arbitrage inertes (place réservée à l'âme)

v0.1 pose un point d'extension **présent mais pass-through**, pour le futur « final cut » agentique (incarné dans son code/mémoire, plus tard).

```ts
// Interface stable dès v0.1 ; implémentation v0.1 = identité
interface CompositionArbiter {
  // reçoit le profil mergé + le contexte, peut le réécrire ; v0.1 ne change rien
  arbitrate(effective: CompositionProfile, ctx: ArbitrationContext): CompositionProfile;
}

// v0.1 : arbitre inerte (pass-through), branché dans le pipeline LayoutResolver
const passthroughArbiter: CompositionArbiter = { arbitrate: (p) => p };
```

**Garanties v0.1** :
- l'arbitre est **appelé** dans le pipeline (point d'injection réel, testé) mais **ne modifie rien** ;
- aucune autre partie du moteur ne court-circuite ce point → quand l'âme arrivera, elle s'y branche *seule* ;
- l'arbitre reçoit la **provenance** (§3) → l'agent futur saura ce que l'app voulait vs ce que le user a imposé, pour arbitrer finement.

C'est le sens de *« poser les fondations qui ne rendront jamais l'agentique impossible »* sans coder l'agent maintenant.

## 7. Persistance des préférences user (deux niveaux)

Décision HITL : **deux niveaux, précédence à arbitrer** (→ `09` Q-07).

**Ancrage code réel** : `types/user-runtime-prefs.ts` existe déjà et est **explicitement non-métier** (commentaire : *« ne doit jamais devenir une seconde source de vérité pour permissions ou navigation »*). Il porte `uiDensity`, `sidebarPanelOpen`, `onboardingCompleted` + `normalizeUserRuntimePrefs` (merge tolérant, ignore l'inconnu). → On **étend** ce type avec un champ `composition?` (overrides user du profil), **sans** y mettre de métier, et on réutilise le pattern `normalize*` pour le merge couche 2.

| Niveau | Portée | Exemple | Persistance |
|--------|--------|---------|-------------|
| **Local** | device / poste | densité sur ce poste de caisse | store device (comme `UserRuntimePrefs` aujourd'hui) |
| **App/back** | user multi-device | disposition préférée qui suit l'utilisateur | API app (Recyclique back) |

Précédence proposée (à valider) : **local > app/back** pour les réglages éphémères de poste, **app/back > local** pour les préférences personnelles identitaires. → champ `pref_scope: "device" | "identity"` sur chaque préférence pour trancher au cas par cas plutôt qu'une règle globale.

## 8. Pipeline de résolution (vue d'ensemble — détaillé en `05`)

```
NavigationManifest + PageManifest (couche app)
        + profil défaut moteur (couche 0)
        + prefs user local + app/back (couche 2)
        + ContextEnvelope (AR39 : autorisations)
        + viewport / support (→ 04B)
   │
   ▼  merge par champ avec provenance (§3) + invariants (§4) + override_policy (§5)
   ▼  CompositionArbiter.arbitrate()  ← inerte en v0.1 (§6)
   ▼
 profil de composition effectif → adaptation support (04B) → rendu
```

## 9. Definition of Done (modèle d'autorité)

- [ ] Type `CompositionProfile` + fragments à provenance définis dans le moteur.
- [ ] `merge(défaut, app, user)` deep-merge par champ, testé (tables de cas).
- [ ] Invariants AR39/required appliqués et testés (user ne peut pas franchir).
- [ ] `override_policy` lu et respecté par le moteur, sans connaissance métier.
- [ ] `CompositionArbiter` pass-through branché dans le pipeline + test prouvant qu'il est appelé et neutre.
- [ ] `pref_scope` device/identity posé ; précédence documentée (Q-07 tranchée ou marquée ouverte).
- [ ] Provenance inspectable en mode dev.
