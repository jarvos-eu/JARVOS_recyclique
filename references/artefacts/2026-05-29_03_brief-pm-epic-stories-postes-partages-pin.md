# Brief PM — Creer epic/stories postes partages + PIN

Date : 2026-05-29  
Statut : brief de transmission pour nouveau contexte PM / BMAD  
Objectif : produire un epic BMAD et des stories executables, puis les faire QA avant tout dev.

## 1. Mission du prochain agent PM

Creer un epic BMAD dedie au chantier :

**Postes partages enroles + PIN operateur + PWA installable non-offline**

Le prochain agent doit produire :

- un epic clairement borne ;
- une liste de stories ordonnees ;
- des criteres d'acceptation testables ;
- les dependances et gates ;
- les exclusions explicites ;
- un plan d'enchainement compatible Epic Runner / Story Runner.

Ne pas lancer le dev dans le meme contexte. Le livrable PM devra etre QA2 avant execution.

Avant de figer les stories, le prochain agent PM doit faire trancher ou proposer explicitement deux choix courts :

- le nom canonique du modele : `Device`, `Workstation`, `RegisteredDevice`, autre ;
- le ou les modules pilotes initiaux : par defaut un seul module pilote, sauf choix explicite de Strophe.

Decision PM/Strophe du 2026-05-30 : modele canonique **`RegisteredDevice`**, identifiant technique **`device_id`**, type MVP **`shared_workstation`**, module pilote initial **Reception**.

## 2. Fichiers a charger en premier

Ordre de lecture recommande :

1. `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`
2. `references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md`
3. `references/automatisation-bmad/epic-story-runner-spec.md`
4. `references/automatisation-bmad/2026-04-02_recueil-technique-orchestration-bmad.md` §15
5. `_bmad-output/planning-artifacts/prd.md` uniquement pour verifier la coherence globale et les exclusions PWA/offline.
6. `references/config-modules-site-id/index.md` puis docs ciblees si le sujet `module_key` doit etre precise.
7. `references/artefacts/2026-04-02_03_spec-multi-contextes-invariants-autorisation-v2.md` pour les invariants authz / ContextEnvelope.

Ne pas recharger tout `references/`.

## 3. Decisions gelees

Le prochain agent ne doit pas rouvrir ces decisions sauf contradiction majeure :

- Le chantier est un palier **non-offline**.
- La PWA du MVP est **installable**, pas offline metier.
- Le poste est **enrole**, pas devine.
- Le backend reste l'autorite d'autorisation.
- Sans operateur PIN actif : refus par defaut.
- Apres PIN, les modules accessibles sont calcules cote serveur par intersection :

```text
configuration module par site x allowlist poste x permissions operateur
```

- Le vocabulaire `module_key` doit etre reutilise, pas duplique.
- Le Panel SuperAdmin "Gestion des postes" fait partie du MVP.
- Le flux de reconnexion / remplacement apres perte d'identite locale fait partie du MVP.
- L'audit reutilise le socle `audit_logs` existant.
- `device_id` est l'identifiant technique canonique valide ; `workstation_id` peut rester un libelle produit / alias documentaire, mais ne doit pas etre confondu avec `cash_register_id` ni devenir un second identifiant concurrent.
- L'override SuperAdmin est inclus, mais explicite, audite, et jamais automatique apres PIN.

## 4. Hors perimetre a rappeler dans l'epic

Exclure explicitement :

- offline metier ;
- file locale d'operations ;
- sync differee ;
- agent local ;
- decouverte reseau automatique ;
- cartographie complete des peripheriques ;
- supervision temps reel du parc ;
- reporting audit avance ;
- nouveaux roles locaux non stabilises ;
- developpement simultane de tous les modules.

Le futur registre materiel doit rester ouvert, mais ne pas entrer dans le MVP au-dela des champs necessaires aux postes partages.

## 5. Decoupage PM recommande

Proposition d'ordre de stories. Note 2026-05-30 : l'ordre executable final est celui de `epics.md`, `sprint-status.yaml` et du runbook Epic 27 ; il scinde explicitement **27.8 Reception / brouillons**, **27.9 timeout / passage de main** et **27.10 override SuperAdmin**.

1. **Contrat et modele poste partage**  
   Definir modele minimal `device_id` / poste enrole, statuts, site, emplacement, allowlist `module_key`, dernier contact, revocation. Inclure migrations/API/OpenAPI si le flux BMAD le demande.

2. **Contrat `ContextEnvelope` poste partage + audit minimal**  
   Specifier comment `site_id`, `device_id`, `operator_user_id`, `module_key` et override SuperAdmin entrent dans le contexte serveur. `workstation_id` reste un libelle produit / alias documentaire si rencontre, pas un second identifiant concurrent. Prevoir l'enrichissement minimal de l'audit sans creer un second journal.

3. **Panel SuperAdmin Gestion des postes**  
   Lister, nommer, configurer, revoquer, voir statut, definir modules autorises et timeout.

4. **Enrolement + reconnexion/remplacement**  
   Enroler un poste, stocker secret/cle locale, revoquer ancien secret, gerer cache vide et conflit de machine.

5. **PWA installable non-offline**  
   Manifest, icone, standalone, consignes navigateur dedie. Aucun cache metier offline.

6. **Lock screen PIN + session operateur**  
   Ecran verrouille, PIN serveur, operateur actif, aucun module sans PIN. Le timeout et le passage de main sont bornes dans la story dediee.

7. **Intersection serveur modules / poste / permissions**  
   Calcul effectif des modules visibles/actionnables avec `module_key`, site, poste, operateur. Le front n'est pas autoritaire.

8. **Module pilote Reception et brouillons bornes**  
   Appliquer le flux au module pilote Reception. Ne pas elargir a caisse / atelier / inventaire dans la story pilote. Brouillons masques sans PIN, reprise explicite par operateur autorise, endpoints authentifies en `network-only` / `no-store` ou equivalent.

9. **Timeout et passage de main**  
   Timeout configurable, avertissement, verrouillage propre, sortie de l'operateur actif.

10. **Override SuperAdmin**  
   Override SuperAdmin explicite avec sortie claire et audit.

Note historique : le PM pouvait fusionner ou scinder avant figage. Depuis la validation Strophe du 2026-05-30, l'Epic 27 conserve la scission `27.8 Reception / brouillons`, `27.9 timeout / passage de main`, `27.10 override SuperAdmin` ; toute fusion, scission ou extension de scope doit remonter `NEEDS_STROPHE_HITL`.

## 6. Gates et QA attendus

Avant dev :

- QA2 sur epic/stories, gate 95.
- Verification anti-derive : pas d'offline cache, pas de securite front, pas de confusion device/caisse/reception.
- Validation que les stories sont executables par Story Runner.

Pendant dev :

- Une seule story active a la fois.
- Gates tests/lint/build adaptees a la story.
- QA/code review en contexte frais.
- Pas de passage `done` sans gates + QA + CR.

## 7. Strategie runners

Runner recommande :

- **Epic Runner unique** pour garder le contexte global leger.
- **Story Runner sequentiel** : une story a la fois.
- Le Story Runner agit comme parent orchestrateur et delegue chaque etape a des sous-agents : create story, validate story, dev, gates, QA, code review.

Ne pas lancer plusieurs Story Runners en parallele sur le meme depot pour l'Epic 27. Les seules parallelisations raisonnables, hors execution de stories concurrentes, sont :

- QA par axes en readonly ;
- code review ;
- exploration readonly ;
- generation de tests sur une story deja stabilisee.

## 8. Strategie modeles

Strophe prevoit de lancer les agents avec un modele global type GPT 5.5 Medium ; les sous-agents peuvent donc utiliser **inherit**.

Recommandation :

- PM / architecture / securite : inherit depuis le modele du chat agent.
- Dev cible et correctifs : Composer 2.5 si disponible et si la story est bornee.
- QA / code review authz-audit : preferer inherit / modele robuste.

Ne pas forcer un modele indisponible dans les briefs ; preferer `inherit` quand Strophe configure le contexte parent.

## 9. Prompt de depart pour le prochain PM agent

```text
Tu es le PM BMAD pour JARVOS Recyclique.

Mission : creer un epic et des stories BMAD pour le chantier "postes partages enroles + PIN operateur + PWA installable non-offline".

Lis d'abord :
1. references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md
2. references/artefacts/2026-05-29_01_cadrage-postes-partages-pin-operateur.md
3. references/artefacts/2026-05-29_03_brief-pm-epic-stories-postes-partages-pin.md

Puis produis un epic dedie et des stories ordonnees, avec criteres d'acceptation testables, exclusions explicites, gates, dependances et plan compatible Epic Runner / Story Runner.

Ne lance pas le dev. Le livrable devra passer QA2 avant execution.
```

## 10. Decision de fonctionnement

Fonctionnement recommande :

1. Ouvrir un nouveau contexte PM avec ce brief.
2. Produire epic + stories.
3. Lancer QA2 sur le livrable PM.
4. Corriger les P0/P1.
5. Valider avec Strophe.
6. Lancer ensuite Epic Runner, story par story.
