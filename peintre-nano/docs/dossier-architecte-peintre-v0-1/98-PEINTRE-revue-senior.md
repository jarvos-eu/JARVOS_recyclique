# 98-PEINTRE — Revue architecte senior (findings & modifications proposées)

> Revue à froid du pack PEINTRE (19 fichiers) **croisée avec l'écosystème doc Recyclique v2** (packs ARCH/MOD, conventions, BMAD). Classement : 🔴 à corriger · 🟡 à décider · 🟢 ajout à forte valeur.

## A. Cohérence interne du pack

1. 🔴 **Index périmé** : `12-PEINTRE-veille` et `qa2-rapport-final-run2` absents de la table de lecture et de la table des tours. → ajouter.
2. 🔴 **Collision de nom QA** : le pack ARCH possède déjà un `qa2-rapport-final.md`. Déposer le nôtre tel quel dans `references/` crée deux fichiers homonymes dans deux packs. → renommer `qa2-rapport-peintre-run1.md` / `-run2.md`.
3. 🟡 **Nom du dossier au dépôt** : viser `references/dossier-architecte-peintre-v0-1/` (déjà noté addendum, jamais acté). Le code `PEINTRE` devient officiellement le 3ᵉ pack (ARCH, MOD, PEINTRE) → à déclarer dans le prompt système Recyclique v2 (ordre de lecture global + tableau conventions).
4. 🟢 **Manque un `prompt-agent-chantier-peintre.md`** : le pack MOD a son prompt d'entrée agent (`prompt-agent-chantier-modules.md`). Même convention ici : 1 page qui dit à l'agent Cursor quoi lire, dans quel ordre, quelles règles (agnosticité, D-15, refs_first). C'est le fichier qui « allume » le chantier. **Ajout le plus rentable de cette revue.**

## B. Cohérence avec le pack MOD (le vrai trou)

5. 🔴 **Interaction modules ↔ composition non traitée**. Un module optionnel (slice CREOS type `kpi-live-banner`, activé par `site_id`+`module_key`, Story 9.6) **injecte des slots**. Questions non couvertes par le pack PEINTRE :
   - un slot injecté par module porte-t-il son profil `presentation` ? (réponse à acter : **oui, dans le manifest du module**, même grammaire) ;
   - que fait le LayoutResolver quand un module est désactivé ? (réponse : rien de spécial — `effectiveModuleKeys` du ContextEnvelope filtre en amont, AR39 ; mais **l'écrire**) ;
   - le schéma `kpi-live-banner` est **versionné 1.0.0** au registre MOD : ajouter `presentation` à un manifest de module = bump de version ? → règle de gouvernance à trancher avec `21-MOD`.
   → **Ajouter §« Modules optionnels » dans `04`** (3-5 lignes) + 1 ligne dans `10` (portage bandeau-live = module publié, attention au contrat versionné).
6. 🟡 **Gouvernance des nouveaux `creos_kind`** (`theme`, `layout_template`, `overlay`, `presentation-*`) : qui est writer, quel versioning, entrée au registre ? Le pack MOD a déjà ce régime (`21-MOD-gouvernance-contrats`). → 1 ligne dans `04` : « ces schémas entrent dans le régime `21-MOD` » (Q-03 l'effleure, pas acté).

## C. Cohérence avec le pack ARCH

7. 🟢 **AR39 tenu** : la hiérarchie OpenAPI > ContextEnvelope > CREOS > prefs UI est respectée partout (04A explicite). RAS.
8. 🟡 **Pistes A/B** : le chantier PEINTRE est de la **Piste A** (mocks OK). Non dit explicitement — 1 ligne dans l'index éviterait qu'un agent croie devoir attendre l'API (Piste B).
9. 🟡 **T-MOD-3 (OpenAPI module-config non fusionné)** : le portage `10` suppose l'activation modules ; si Story 9.6/T-MOD-3 traînent, seul le toggle bandeau existe. Non bloquant pour Épics A/B ; à noter comme dépendance externe dans `09`.

## D. Améliorations d'ensemble (fluidité/possibilités)

10. 🟢 **Schéma d'un écran « avant/après »** dans l'index ou `02` : 10 lignes ASCII montrant le même écran caisse nano vs v0.1 (surcouches→profil). Aide énorme pour humains non-tech et agents.
11. 🟢 **Glossaire 15 termes** (shell, région, rôle, template, overlay, profil, provenance, arbitre, prise inerte…) en annexe d'index — le pack invente du vocabulaire ; un agent froid gagnera 30 min.
12. 🟡 **Q-08 (barème défaut)** : seul point de fond ouvert. Proposer un défaut v0.1 ultra-simple (3 règles : viewport, volume, nature) dans `04B` pour débloquer sans attendre l'arbitrage fin.

## E. Verdict

Pack solide, doctrine cohérente, ancrage code complet. **Rien de contradictoire.** Les manques sont périphériques mais réels : (1) intégration à l'écosystème doc v2 (index, noms, prompt-agent, déclaration 3ᵉ pack), (2) le pont **modules↔composition** — seul vrai trou de fond, 15 lignes à écrire, forte valeur car le bandeau-live est à la fois ton pilote tokens ET un module publié versionné.

## Plan de modifications (ordre d'exécution)
| # | Action | Fichier | Effort |
|---|--------|---------|--------|
| 1 | MAJ index (12, run2, mention Piste A) | `index` | XS |
| 2 | Renommer rapports QA | `qa2-*` | XS |
| 3 | §Modules optionnels (composition, désactivation, versioning) | `04` + `10` + `09` | S |
| 4 | Gouvernance creos_kind → régime 21-MOD | `04` | XS |
| 5 | `prompt-agent-chantier-peintre.md` | nouveau | S |
| 6 | Glossaire + schéma avant/après | `index` | S |
| 7 | Défaut Q-08 simple (3 règles) | `04B` | XS |
| 8 | Déclarer pack PEINTRE dans le prompt système v2 | hors pack (toi) | XS |
