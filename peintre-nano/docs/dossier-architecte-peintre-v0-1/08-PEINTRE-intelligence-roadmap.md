# 08-PEINTRE — Roadmap de la brique d'intelligence

> **Invariant absolu** (D-05) : l'intelligence **produit un profil de composition CREOS** (`04`/`04A`/`04B`), validé par schéma, **via le hook `CompositionArbiter`** (`04A` §6 — inerte en v0.1, vivant plus tard). Elle parle la **même grammaire** que l'app et le user (D-09). Elle ne génère ni React, ni CSS, ni `operation_id` ; elle ne contourne jamais AR39 ; le mode dégradé la borne.
> **Point d'injection unique** : l'intelligence ne s'ajoute nulle part ailleurs que dans `arbiter.arbitrate(effective, ctx)`. v0.1 a déjà câblé ce point (pass-through) → l'allumer = remplacer l'implémentation inerte, sans toucher au reste du moteur.

## 1. Pourquoi l'intelligence vient en dernier (et pourquoi c'est une force)

Sans langage de présentation déclaratif, « adapter les écrans à la volée » obligerait l'IA à générer du code — ingouvernable. **Avec** le profil présentation (Phase 1), adapter un écran = produire un petit JSON d'intentions dans un vocabulaire fermé. L'IA devient un **sélecteur d'intentions**, pas un générateur d'interface. C'est ce qui transforme un fantasme en feature livrable.

```
Contexte (viewport, volume données, rôle, device, historique)
        │
        ▼
  [ Intelligence ]  →  profil presentation CREOS (JSON validé)
        │                 { emphasis, density, region, reflow, … }
        ▼
  [ Schéma valide ? ] ──non──▶ rejet → profil par défaut (jamais d'écran cassé)
        │ oui
        ▼
  [ LayoutResolver ] → rendu
```

## 2. Palier 3a — Intelligence par règles (le « semblant d'intelligence » demandé en premier)

**Déterministe, sans LLM, testable, zéro coût.** Des heuristiques qui émettent un profil présentation.

Exemples de règles :
- **Densité auto** : `viewport < md` OU `slot.itemCount > seuil` → `density: compact`. Sinon `comfortable`. Override `UserRuntimePrefs` prioritaire.
- **Emphase contextuelle** : si le ContextEnvelope signale une action prioritaire (ex. session caisse à clôturer) → le slot concerné passe `emphasis: primary`.
- **Reflow responsive** : `viewport < sm` → `aside` collapse en drawer, `main` passe `reflow: stack`.
- **State style adaptatif** : liste longue en chargement → `loading: skeleton` ; liste vide → `empty: illustration`.

**Propriétés** : pur, idempotent, unit-testable (table entrée→profil attendu). C'est le livrable le plus rentable de la Phase 3 et il suffit probablement à rendre les écrans « intelligents » au sens où tu l'entends d'abord.

## 3. Palier 3b — Intelligence générative (le « vrai début de quelque chose »)

Un agent (LLM) qui **propose** un profil présentation pour un contexte donné, quand les règles ne suffisent pas (écrans nouveaux, dispositions inhabituelles, optimisation fine).

Architecture sûre :
1. **Entrée** : description structurée du contexte (slots disponibles, contraintes, intentions métier) — **pas** les données métier brutes.
2. **Sortie contrainte** : le LLM ne peut émettre que du JSON conforme à `presentation-profile.schema.json` (sortie structurée / validation stricte). Tout écart → rejet → profil par défaut.
3. **Garde-fous** :
   - validation schéma **avant** rendu (jamais de profil non validé) ;
   - le profil ne peut référencer que des slots/widgets **déjà autorisés** par le ContextEnvelope (AR39 inviolable) ;
   - mode dégradé : échec/latence/timeout → profil règles (3a) → profil manifest par défaut ;
   - **cache** : un profil généré pour (contexte signature) est mémorisé → coût d'inférence amorti, déterminisme retrouvé.
4. **Boucle d'amélioration** (option v1.x) : les profils générés validés et « bons » peuvent être **promus en règles** (3a) — l'IA défriche, les règles stabilisent.

**Ce que 3b ne fait jamais** : générer un composant, inventer une opération, afficher une donnée non autorisée, écrire dans les contrats. Il choisit une mise en présentation parmi le possible déclaré.

## 4. Réutilisabilité écosystème (lien Peintre v0.1 → JARVOS)

Parce que l'intelligence ne produit que du profil présentation **standard**, elle est **agnostique de l'application** : la même brique sert Recyclique aujourd'hui et une autre app de l'écosystème demain, du moment qu'elles parlent CREOS + tokens `--pn-*`. C'est la promesse « moteur réutilisable » concrétisée par le haut de la pile autant que par le bas.

## 5. Séquençage intelligence

| Sous-phase | Contenu | Prérequis | Risque |
|-----------|---------|-----------|--------|
| 3a-1 | Densité auto par règles | Épic A+B livrés | très faible |
| 3a-2 | Emphase/reflow contextuels | 3a-1 | faible |
| 3b-1 | Générateur contraint (sortie schéma) + validation + fallback | 3a stable, profil strict (D-07) | moyen (gouvernance LLM) |
| 3b-2 | Cache + promotion profils→règles | 3b-1 | moyen |

**Ne pas démarrer 3b avant que 3a soit stable et que le profil présentation soit figé.** Sinon on génère vers une cible mouvante.

## 6. Definition of Done (intelligence)

- [ ] 3a : règles densité + emphase + reflow, déterministes, testées (tables entrée→profil).
- [ ] 3a : override UserRuntimePrefs toujours prioritaire (l'humain garde la main).
- [ ] 3b : générateur à sortie strictement validée ; 100% des profils non conformes rejetés sans rendu.
- [ ] 3b : AR39 prouvé inviolable (test : profil tentant un slot non autorisé → rejeté).
- [ ] 3b : mode dégradé prouvé (échec LLM → 3a → défaut, jamais d'écran cassé).
- [ ] Doc : la même brique consommée par une 2ᵉ app fictive (preuve d'agnosticité).
