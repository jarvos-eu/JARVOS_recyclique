# Runbook orchestration — Epic 27 postes partages + PIN

Date : 2026-05-29  
Statut : prompt / instructions pour orchestrateur global Epic 27  
But : lancer et piloter l'Epic 27 avec autonomie maximale, sans invention produit ni execution parallele risquee.

## 1. Role de ce document

Ce runbook decrit **comment executer** l'Epic 27 avec les agents BMAD dans Cursor.

Il ne remplace pas :

- `epics.md` ;
- `sprint-status.yaml` ;
- les fichiers story ;
- les skills BMAD ;
- la spec `references/automatisation-bmad/epic-story-runner-spec.md`.

Il sert de contrat d'orchestration pour l'agent global qui pilote l'epic.

## 2. Documents obligatoires

L'orchestrateur global doit lire, dans cet ordre :

1. `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`
2. `references/artefacts/2026-05-29_03_brief-pm-epic-stories-postes-partages-pin.md`
3. `references/automatisation-bmad/epic-story-runner-spec.md`
4. `references/automatisation-bmad/2026-04-02_recueil-technique-orchestration-bmad.md` §15
5. `.cursor/agents/bmad-epic-runner.md`
6. `.cursor/agents/bmad-story-runner.md`
7. `_bmad-output/planning-artifacts/epics.md`
8. `_bmad-output/implementation-artifacts/sprint-status.yaml`
9. `_bmad/bmm/config.yaml`

Selon la story, il charge ensuite uniquement les documents metier / techniques necessaires.

### 2.1 Pre-vol avant delegation 27.1

Avant de lancer la premiere story, l'Epic Runner verifie que les references `module_key` et configuration modules par `site_id` sont presentes et lisibles :

- `references/config-modules-site-id/index.md` ;
- `contracts/openapi/recyclique-api.yaml` si les contrats API sont touches ;
- `references/protocole-modules-recyclique/18-MOD-config-modules-crosswalk.md` si un doute d'alignement `module_key` apparait.

Si ces references sont absentes, incoherentes ou illisibles, stopper avant delegation story avec `BLOCKED_ENVIRONMENT` si c'est un probleme d'acces fichier / environnement, ou `NEEDS_EPIC_DECISION` si c'est une incoherence documentaire a arbitrer. Ne pas inventer un vocabulaire module local.

## 3. Principe d'execution

Mode d'execution retenu :

- execution supervisee dans Cursor / LLM, sans daemon, cron local, ou promesse headless ;
- un **Epic Runner unique** ;
- une **seule story active a la fois** ;
- un **Story Runner parent** par story ;
- un sous-agent / Task par etape BMAD quand la plateforme le permet ;
- pas de dev avant stories validees et QA2 du livrable PM ;
- pas de parallelisation de stories sur le meme depot.

Graphe story :

```text
CS_create -> VS_validate -> DS_dev -> GATE -> QA_tests -> CR_review -> YAML_update
```

Apres correction QA ou CR :

```text
DS_dev -> GATE -> QA_tests -> CR_review
```

Ne jamais sauter QA ou CR apres un correctif significatif.

## 4. Ordre Epic 27

Ordre attendu pour l'Epic 27, a verifier avant lancement contre `epics.md` et `sprint-status.yaml` :

1. `27.1` — Contrat `RegisteredDevice` et registre minimal
2. `27.2` — Contexte serveur poste partage et audit transversal
3. `27.3` — Panel SuperAdmin Gestion des postes
4. `27.4` — Enrolement, reconnexion et remplacement
5. `27.5` — PWA installable non-offline
6. `27.6` — Lock screen PIN et session operateur active
7. `27.7` — Intersection serveur modules / poste / operateur
8. `27.8` — Pilote Reception : brouillons masques et reprise autorisee
9. `27.9` — Timeout, verrouillage et passage de main
10. `27.10` — Override SuperAdmin explicite et audite

Cet ordre devient la discipline d'execution lorsque `epics.md` et `sprint-status.yaml` sont alignes. Si `epics.md`, `sprint-status.yaml` ou les stories finales divergent, l'Epic Runner stoppe avant delegation, documente la divergence et demande l'arbitrage parent / Strophe selon l'impact.

L'Epic Runner ne saute pas une story sauf decision documentee par l'Epic Runner et tracee dans son resume.

## 5. Regles de parallelisation

Interdit par defaut :

- deux Story Runners actifs en parallele sur le meme depot ;
- deux writers sur `sprint-status.yaml` ;
- deux agents modifiant les memes contrats OpenAPI / schemas / runtime authz ;
- un worker qui elargit une story a un autre module sans autorisation.

Autorise :

- QA par axes en readonly, ou sur le perimetre deja modifie par une story stabilisee ;
- code review en contexte frais ;
- exploration readonly ;
- generation de tests ciblee sur une story deja stabilisee ;
- sous-agents specialises a l'interieur du Story Runner si le parent garde la decision.

## 6. Politique HITL en cascade

Objectif : maximiser l'autonomie sans demander a Strophe des arbitrages deja couverts par les documents.

### 6.1 Types de blocage

Utiliser ces statuts internes avant de remonter a l'humain :

- `NEEDS_PARENT_DECISION` : le worker demande au Story Runner.
- `NEEDS_EPIC_DECISION` : le Story Runner demande a l'Epic Runner.
- `BLOCKED_ENVIRONMENT` : probleme d'outil, test, service, credential, port, reseau, ou plateforme Cursor.
- `NEEDS_STROPHE_HITL` : decision produit / securite / scope impossible a trancher avec les documents.

### 6.2 Cascade obligatoire

Un worker ne doit pas s'arreter directement vers Strophe sauf risque destructif immediat.

Cascade normale :

```text
Worker -> Story Runner -> Epic Runner -> Strophe
```

Exemples :

- Nom d'un bouton, formulation UI, choix mineur de test : Story Runner tranche.
- Test timer flaky : Story Runner tranche, de preference mocks / injection.
- Ambiguite de scope entre deux stories : Epic Runner tranche si le runbook ou les stories couvrent le cas.
- Extension de 27.8 a la caisse : refusee par les decisions gelees.
- Changement de module pilote : `NEEDS_STROPHE_HITL`.
- Stocker un secret en clair ou contourner l'ADR : `NEEDS_STROPHE_HITL`.
- Operation destructive Git / DB non demandee : `NEEDS_STROPHE_HITL`.

### 6.3 Pouvoir d'arbitrage du parent

Le Story Runner ou Epic Runner peut arbitrer uniquement si :

- la reponse est deja impliquee par ADR / brief / story ;
- la decision est locale, reversible et ne change pas le produit ;
- la decision n'elargit pas le scope ;
- la decision ne degrade pas les invariants de securite.

Si l'agent rencontre une regle produit non deja impliquee par ADR / brief / story, il doit la consigner comme **decision proposee** et la remonter a Strophe via l'Epic Runner avant application. Le parent peut proposer une option locale et reversible, mais ne l'applique pas comme nouvelle regle produit pendant l'absence de Strophe.

## 7. Regles produit non negociables

Les runners doivent proteger ces invariants :

- pas d'offline metier ;
- pas de file locale d'operations ;
- pas de service worker interceptant les endpoints metier authentifies ;
- pas d'autorisation decidee cote front ;
- pas de `localStorage` comme source de verite ; pour l'identite poste, suivre la nuance Epic 27.4 : ne pas utiliser `localStorage` si une alternative raisonnable existe, et ne jamais en faire une autorite autonome ;
- pas de confusion `device_id` / `workstation_id` avec `cash_register_id` ;
- `device_id` est l'identifiant canonique Epic 27 ; `workstation_id` peut rester un libelle produit ou alias documentaire, pas un second identifiant concurrent ;
- `reception_post_id`, si introduit plus tard, ne remplace pas `device_id` pour l'identite du poste partage Epic 27 ;
- le palier Epic 27 reste distinct du chantier PIN kiosque / PWA offline du PRD ;
- un appareil personnel admin reste hors lock screen PIN terrain par defaut ;
- pas de generalisation hors module pilote explicitement valide dans `27.8` ;
- pas d'override SuperAdmin implicite ;
- PIN verifie cote serveur, avec limitation d'essais / verrouillage / rate-limit selon ADR ;
- pas de PIN ou derive de PIN dans logs / audit ;
- pas de nouveau role local non stabilise.

Toute violation potentielle remonte au minimum a l'Epic Runner.

## 8. Gates et tests

Chaque story doit avoir des gates non vides. `gates_skipped_with_hitl: true` est autorise uniquement pour un blocage d'environnement documente, jamais pour authz, PIN, audit, PWA non-offline, migrations ou contrats API.

Gates transverses :

- backend : tests unitaires, API, authz, audit, migrations selon fichiers touches ;
- frontend : lint / build TypeScript, tests UI pertinents ;
- PWA : manifest, absence de cache metier offline, endpoints authentifies no-store / network-only ;
- contrats : OpenAPI / CREOS si modifies ;
- securite : refus API hors contexte, PIN verifie cote serveur, limitation d'essais / verrouillage / rate-limit, aucun PIN en log, audit minimal.

Echec reproductible local :

- corriger via DS ;
- relancer gates ;
- relancer QA ;
- relancer CR.

Blocage environnement :

- produire diagnostic court ;
- proposer action ;
- remonter `BLOCKED_ENVIRONMENT` au parent.

## 9. Ecritures BMAD et YAML

Regle : un seul writer operationnel.

Avant toute modification de :

- `_bmad-output/planning-artifacts/epics.md` ;
- `_bmad-output/implementation-artifacts/sprint-status.yaml` ;
- fichiers story ;

l'Epic Runner doit confirmer que :

- QA2 du livrable PM est GO ;
- Strophe a valide l'ecriture BMAD ;
- aucune autre session ne modifie le meme epic ;
- l'ordre des stories est stable.

Writer unique :

- l'Epic Runner designe explicitement le writer `YAML_update` pour la story courante ;
- le Story Runner peut preparer le patch, mais ne pousse pas une ecriture concurrente ;
- l'Epic Runner confirme ensuite l'etat de `sprint-status.yaml` ;
- si le writer designe, le brief ou les compteurs sont ambigus : produire un patch / instructions, pas une ecriture directe.

## 10. Strategie modeles

Strophe configure le contexte parent avec un modele type GPT 5.5 Medium. Politique cible : les sous-agents utilisent **inherit** par defaut.

Recommandation :

- Epic Runner : inherit.
- Story Runner parent : inherit.
- Dev cible borne : Composer 2.5 possible si disponible et si la story est simple.
- QA / code review authz, audit, PWA, securite : inherit / modele robuste.

Ne pas forcer un modele indisponible. Ne pas bloquer un run parce que le modele exact n'existe pas dans la liste Cursor ; utiliser `inherit` si le parent est correctement configure.

Avant lancement, verifier le modele effectif declare par les agents Cursor. Si un frontmatter agent force un modele different de `inherit`, l'orchestrateur le note dans le resume de lancement et choisit explicitement : conserver le frontmatter si acceptable pour la passe, ou relancer avec un agent / mode qui herite du parent. Ne jamais supposer que `inherit` est actif si le fichier agent dit autre chose.

## 11. Gestion du contexte

L'Epic Runner garde une fenetre courte :

- epic cible ;
- story courante ;
- statut dernier run : `PASS` / `FAIL` / `NEEDS_*` ;
- compteurs `vs_loop`, `qa_loop`, `cr_loop` ;
- fichiers touches ;
- prochaine action.

Il ne colle pas tout le contenu des stories dans son resume.

Le Story Runner transmet aux workers :

- chemin absolu du `SKILL.md` a suivre ;
- brief YAML complet ;
- chemins absolus ;
- etat courant ;
- sortie attendue.

Brief minimal `story_run` attendu :

- conforme a `references/automatisation-bmad/epic-story-runner-spec.md` §6.2 ;
- `story_key`, `epic_id` et `project_root` explicites ;
- `resume_at` explicite (`CS`, `VS`, `DS`, `GATE`, `QA` ou `CR`) ;
- `paths.epics_md`, `paths.sprint_status` et `paths.story_file` explicites ;
- `paths.story_file` renseigne des que le fichier story existe, ou chemin cible attendu au moment CS ;
- `skill_paths` absolus et lisibles ;
- cles `skill_paths.create_story`, `skill_paths.dev_story`, `skill_paths.qa_e2e`, `skill_paths.code_review` presentes quand la passe les utilise ;
- pour `bmad-create-story`, `mode_create_story` explicite : `create` ou `validate` ; les autres etapes utilisent `resume_at` + le skill appele, pas un champ `mode` ambigu ;
- gates non vides, ou `gates_skipped_with_hitl` limite au blocage d'environnement documente ;
- compteurs `vs_loop`, `qa_loop`, `cr_loop` coherents avec les plafonds ;
- `policy.retry_chain: "DS -> gates -> QA -> CR"` ;
- `fresh_context_for_cr: true` sauf HITL documente ;
- `if_cr_task_unavailable: NEEDS_HITL` ;
- politique CR si Task indisponible : stopper ou produire HITL, pas auto-valider ;
- chemins story / epics / sprint-status absolus.

## 12. Format de brief Epic Runner

Le run commence avec un brief de ce type, a adapter avec les chemins absolus reels :

```yaml
epic_run:
  epic_id: epic-27
  epic_label: "Epic 27 — Postes partages enroles + PIN operateur + PWA installable non-offline"
  project_root: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique"
  paths:
    runbook: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md"
    adr: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md"
    pm_brief: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/references/artefacts/2026-05-29_03_brief-pm-epic-stories-postes-partages-pin.md"
    sprint_status: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/_bmad-output/implementation-artifacts/sprint-status.yaml"
    epics_md: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/_bmad-output/planning-artifacts/epics.md"
    runner_spec: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/references/automatisation-bmad/epic-story-runner-spec.md"
    orchestration_recueil: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/references/automatisation-bmad/2026-04-02_recueil-technique-orchestration-bmad.md"
    bmad_config: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/_bmad/bmm/config.yaml"
    epic_runner_agent: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/.cursor/agents/bmad-epic-runner.md"
    story_runner_agent: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/.cursor/agents/bmad-story-runner.md"
  story_order_is_hint: true
  story_order_hint: "ordre epics.md / sprint-status.yaml pour epic-27"
  current_story_key: null
  story_order:
    - "27-1-registered-device"
    - "27-2-server-context-audit"
    - "27-3-superadmin-device-management"
    - "27-4-enrollment-reconnect-replace"
    - "27-5-installable-pwa-non-offline"
    - "27-6-pin-lock-operator-session"
    - "27-7-server-module-intersection"
    - "27-8-reception-pilot-drafts"
    - "27-9-timeout-lock-handoff"
    - "27-10-superadmin-override"
  max_vs_loop: 3
  max_qa_loop: 3
  max_cr_loop: 3
  writer_policy: "single_writer"
  hitl_policy: "cascade_to_parent_before_strophe"
  model_policy: "inherit_by_default"
  story_runner_final_report_required: true
```

### 12.1 Exemple minimal `story_run` pour 27.1

Exemple a adapter avant delegation au Story Runner ; le fichier story n'existe pas encore tant que la story reste `backlog`.

```yaml
story_run:
  story_key: "27-1-registered-device"
  epic_id: epic-27
  project_root: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique"
  resume_at: CS
  paths:
    sprint_status: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/_bmad-output/implementation-artifacts/sprint-status.yaml"
    epics_md: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/_bmad-output/planning-artifacts/epics.md"
    story_file: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/_bmad-output/implementation-artifacts/27-1-registered-device.md"
  skill_paths:
    create_story: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/.cursor/skills/bmad-create-story/SKILL.md"
    dev_story: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/.cursor/skills/bmad-dev-story/SKILL.md"
    qa_e2e: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/.cursor/skills/bmad-qa-generate-e2e-tests/SKILL.md"
    code_review: "d:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/.cursor/skills/bmad-code-review/SKILL.md"
  mode_create_story: create
  gates:
    - cmd: "python -c \"import yaml, pathlib; yaml.safe_load(pathlib.Path(r'd:/users/Strophe/Documents/1-IA/La Clique Qui Recycle/JARVOS_recyclique/_bmad-output/implementation-artifacts/sprint-status.yaml').read_text(encoding='utf-8'))\""
      timeout_sec: 60
  gates_skipped_with_hitl: false
  max_vs_loop: 3
  max_qa_loop: 3
  max_cr_loop: 3
  vs_loop: 0
  qa_loop: 0
  cr_loop: 0
  policy:
    retry_chain: "DS -> gates -> QA -> CR"
    fresh_context_for_cr: true
    if_cr_task_unavailable: NEEDS_HITL
```

## 13. Prompt de lancement orchestrateur

```text
Tu es l'orchestrateur global de l'Epic 27 pour JARVOS Recyclique.

Colle et adapte le bloc `epic_run` de la section 12 avant de lancer l'Epic Runner.

Lis d'abord :
1. references/artefacts/2026-05-29_04_runbook-orchestration-epic-27-postes-partages-pin.md
2. references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md
3. references/artefacts/2026-05-29_03_brief-pm-epic-stories-postes-partages-pin.md
4. references/automatisation-bmad/epic-story-runner-spec.md
5. references/automatisation-bmad/2026-04-02_recueil-technique-orchestration-bmad.md §15
6. .cursor/agents/bmad-epic-runner.md
7. .cursor/agents/bmad-story-runner.md
8. _bmad-output/planning-artifacts/epics.md
9. _bmad-output/implementation-artifacts/sprint-status.yaml
10. _bmad/bmm/config.yaml

Mission :
- piloter Epic 27 story par story ;
- utiliser un Epic Runner unique ;
- lancer un Story Runner par story ;
- demander aux workers de remonter les questions au parent avant Strophe ;
- respecter la politique HITL en cascade ;
- ne pas paralleliser plusieurs stories ;
- avant chaque delegation Story Runner, construire un `story_run` complet conforme a la spec §6.2 : `story_key`, `epic_id`, `project_root`, `skill_paths.*`, compteurs, gates, `policy.retry_chain`, `fresh_context_for_cr`, `if_cr_task_unavailable` ;
- ne pas devier du perimetre non-offline ;
- rester dans Cursor / LLM supervise, sans daemon ni execution headless autonome ;
- ne pas modifier epics.md / sprint-status.yaml sans validation Strophe et sans verifier qu'il n'y a qu'un writer.

Avant de lancer, verifie que l'ordre story de ce runbook est coherent avec epics.md et sprint-status.yaml. S'il diverge, stoppe et demande arbitrage.

Utilise inherit pour les sous-agents sauf raison explicite, mais verifie le modele effectif des agents Cursor avant de supposer que l'heritage fonctionne.
Si une decision produit non couverte apparait, consigne-la comme decision proposee et remonte a l'Epic Runner ; si elle cree une nouvelle regle produit ou change le scope, demande Strophe avant application.
```

## 14. Conditions de stop

Stopper le run et produire un rapport court si :

- compteur VS / QA / CR atteint le plafond ;
- brief YAML mal forme, `skill_paths` manquants, chemins absolus illisibles ou compteurs incoherents ;
- gates vides sans `gates_skipped_with_hitl` limite a un blocage environnement documente ;
- conflit d'ecriture YAML ;
- incertitude produit non couverte ;
- risque securite critique ;
- echec de spawn Task requis par une etape BMAD, notamment CS / VS / DS / QA / CR en contexte frais ;
- environnement local non fiable apres diagnostic ;
- demande de modification destructive non explicitement validee.

Rapport de stop :

- story courante ;
- statut ;
- cause ;
- fichiers touches ;
- options de reprise ;
- question precise a poser au parent ou a Strophe.
