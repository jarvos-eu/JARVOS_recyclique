# Cadrage postes partages + PIN operateur

Date : 2026-05-29  
Session : discussion PM avec Strophe  
Statut : artefact de decisions, avant creation d'epic/stories

## 1. Point de depart

La discussion part du constat suivant :

- Le chantier en cours reste le plancher v2.0 : parite robuste caisse / reception / compta, avec C2b encore a valider avant tag v2.0.
- La vision "poste enregistre + PIN + PWA/offline" existe dans les documents de vision, mais n'est pas encore decoupee en stories BMAD pretes a coder.
- Le besoin a cadrer maintenant n'est pas de reproduire les habitudes 1.4.4 pour elles-memes.
- Les motivations prioritaires sont : tracabilite, fluidite terrain, securite d'acces.

Decision de cadrage : travailler sur un palier "postes partages + PIN operateur + modules autorises par poste", sans lancer immediatement le chantier PWA/offline complet.

Desambiguïsation PRD : ce cadrage etend la prise de main operateur sur poste partage multi-modules. Il n'active pas le chantier "PIN kiosque PWA/offline" ni un mode secret de poste offline ; si ce palier devient un epic, il devra etre presente comme un "PIN poste partage non-offline" et non comme la realisation complete de la cible kiosque/PWA.

## 2. But produit

Permettre a un poste partage de rester connecte techniquement, tout en n'exposant aucune donnee metier tant qu'un operateur n'a pas pris la main par PIN.

Apres saisie PIN, l'operateur actif voit et utilise uniquement les modules autorises par l'intersection :

```text
configuration module par site x modules autorises par le poste x droits / permissions de l'operateur
```

Le PIN n'est donc pas seulement un confort UX : c'est le mecanisme d'attribution d'action et de limitation d'acces sur poste partage.

### 2.1 Invariant de securite

Le backend reste l'autorite d'autorisation. L'interface, le registre de modules, le stockage local du poste et les manifests ne doivent jamais devenir la verite de securite.

Le poste enregistre contribue au contexte d'autorisation calcule serveur, idealement via le contrat existant de type `ContextEnvelope` : `site_id`, `device_id`, `operator_user_id`, `module_key` et etat d'override SuperAdmin doivent etre valides cote API, sans source d'autorite autonome cote navigateur. `workstation_id` peut rester un libelle produit / alias documentaire, mais `device_id` est l'identifiant technique canonique retenu pour l'Epic 27.

Regle produit :

- sans operateur PIN actif : refus par defaut ;
- avec operateur PIN actif : le serveur calcule les permissions effectives ;
- module visible cote UI ne vaut pas autorisation d'action ;
- toute action metier doit etre refusee cote API si le contexte poste / operateur / site / module n'est pas valide ;
- les changements de droits, poste, site, session ou override SuperAdmin doivent provoquer un recalcul explicite du contexte.

## 3. Decisions actees

### 3.1 Vocabulaire produit

Ne pas reduire le chantier au terme "kiosque caisse".

Concept retenu :

- poste partage ;
- appareil / device enregistre ;
- modules autorises par poste ;
- operateur actif par PIN ;
- session technique de poste.

Le langage "kiosque" peut rester utile pour certains cas d'usage plein ecran, mais ne doit pas devenir le modele general.

### 3.2 Modele de session

Decision : le poste reste connecte avec une session technique de poste.

Le PIN operateur ne remplace pas forcement l'authentification technique du poste. Il ajoute une identite metier active, utilisee pour :

- droits effectifs ;
- affichage des modules ;
- audit ;
- attribution des actions ;
- validations sensibles.

Le modele "PIN comme simple step-up" est insuffisant pour ce besoin.

### 3.3 Acces sans PIN

Sans operateur actif :

- ecran verrouille plein ecran ;
- aucune navigation metier ;
- aucune donnee metier exploitable visible ;
- aucun module accessible.

Le poste revient a cet etat apres :

- action manuelle "passer la main" / "verrouiller" ;
- timeout d'inactivite ;
- expiration ou invalidation de la session technique.

### 3.4 Acces apres PIN

Apres PIN valide :

- l'operateur devient l'acteur metier actif ;
- l'accueil post-PIN montre les modules disponibles ;
- les modules visibles sont l'intersection entre configuration du poste et permissions de l'operateur ;
- l'operateur ne peut naviguer que vers ce que ses droits et le poste autorisent.

Cette logique doit eviter deux erreurs :

- donner trop de pouvoir a un poste public parce qu'un operateur est habilite ;
- bloquer l'evolution multi-modules en codant seulement "caisse".

### 3.5 Modules autorises par poste

Decision : implementer directement un modele generique de modules autorises par poste, pas seulement un poste polyvalent caisse + reception code en dur.

Le modele doit s'aligner avec la direction deja prise sur les `module_key` : liste blanche serveur, activation/configuration persistée serveur, et matrice role x module x site. Les modules autorises par poste ne doivent pas creer un second vocabulaire concurrent aux modules Recyclique.

Norme de cadrage : la configuration du poste est une allowlist serveur de `module_key`. Elle restreint le contexte effectif, mais ne remplace ni la configuration modules par `site_id`, ni les permissions de l'operateur, ni le recalcul backend. Les permissions restent additives cote operateur ; le profil du poste agit comme contrainte contextuelle, pas comme systeme de droits parallele.

Le premier perimetre peut rester limite a quelques modules disponibles, mais le modele doit etre extensible pour :

- caisse ;
- reception ;
- atelier ;
- inventaire ;
- admin leger ;
- futurs modules Recyclique.

### 3.6 Configuration SuperAdmin

Decision : pour le premier chantier, seul le SuperAdmin configure les postes.

Justification :

- les roles "responsable de site", "admin local", etc. ne sont pas encore stabilises ;
- ne pas inventer une gouvernance locale avant que le modele de roles soit tranche ;
- garder un premier rail simple et securise.

### 3.7 Ecran SuperAdmin "Gestion des postes"

Decision : inclure des le chantier un vrai ecran SuperAdmin de gestion des postes / appareils.

Fonctions souhaitees pour le MVP :

MVP obligatoire :

- lister les postes / appareils ;
- nommer un poste ;
- renseigner site et emplacement ;
- definir type d'appareil ;
- definir modules autorises ;
- regler le timeout ;
- voir un statut administratif simple ;
- generer ou valider un enrôlement ;
- revoquer un poste ;
- modifier la configuration a distance.

MVP si simple :

- afficher le dernier contact connu ;
- distinguer configuration active et configuration a rafraichir.

Post-MVP :

- sante des peripheriques ;
- supervision temps reel ;
- metriques de parc ;
- carte materielle complete.

Cet ecran prepare le futur registre materiel et la future carte du parc local.

Limite PM pour le premier chantier : l'ecran couvre les postes partages enroles et peut reserver une categorie "appareil personnel admin" en cadrage, mais il ne doit pas embarquer la cartographie complete des peripheriques, la decouverte reseau, ni la supervision du parc materiel.

Statuts MVP admis : `enrole`, `revoque`, `bloque`, `configuration active`, `configuration a rafraichir`, `dernier contact` simple. Ces statuts ne doivent pas devenir une supervision de sante temps reel.

### 3.8 Enrolement et identification du poste

Forte proposition retenue : ne pas chercher a deviner le poste, mais l'enroler.

Modele MVP :

- un SuperAdmin cree ou valide un poste ;
- depuis le poste physique, on lance l'enregistrement ;
- un code court ou QR code d'appairage permet l'association ;
- le navigateur / la PWA stocke localement une identite de poste sans que `localStorage` devienne source de verite si une alternative raisonnable existe ;
- le serveur associe cette identite au registre des appareils ;
- le poste recupere sa configuration a chaque chargement ;
- si le stockage navigateur est efface, le poste doit etre re-enrole ;
- le SuperAdmin peut revoquer le poste a distance.

Risque accepte pour le MVP : si le cache / stockage navigateur est vide, le poste perd son identite locale et doit etre re-enrole. Ce n'est pas considere comme bloquant pour le premier palier, tant que la procedure de re-enrolement est simple et que la revocation serveur existe.

Decision complementaire : la perte d'identite locale ne supprime pas le poste du Panel SuperAdmin. Le poste reste une entite serveur, avec un statut visible et un flux de reconnexion / remplacement.

Statuts a prevoir pour ce cas :

- `enrole` / actif ;
- `hors ligne` ou dernier contact ancien ;
- `identite locale perdue` / a reconnecter ;
- `conflit d'identite` ;
- `revoque` ;
- `bloque`.

Flux de reconnexion recommande :

1. Depuis un poste non reconnu, afficher "reconnecter ce poste".
2. Le poste demande un code de rattachement, un QR code ou une validation SuperAdmin.
3. Le SuperAdmin choisit le poste serveur existant a reconnecter.
4. Si validation : le serveur genere une nouvelle identite locale et revoque l'ancienne cle / secret.
5. Si l'ancien ordinateur revient ensuite avec l'ancienne identite, il est bloque et remonte en conflit.
6. Le SuperAdmin arbitre : refuser, remplacer definitivement l'ancien, ou creer un nouveau poste distinct (ex. `ordinateur caisse 2`).

Ce flux doit eviter qu'un accident d'enrolement connecte silencieusement deux machines au meme poste logique.

Option technique cible :

- device_id cote serveur ;
- secret local revocable au MVP ;
- idealement cle locale WebCrypto non exportable + challenge signe si l'effort technique reste raisonnable.

Critere produit pour le premier chantier : l'enrolement doit permettre d'identifier et de revoquer un poste cote serveur. WebCrypto reste une option d'architecture si elle tient dans l'effort, pas une exigence PM obligatoire pour demarrer le cadrage.

Ce qui est ecarte pour le MVP :

- lecture de l'adresse MAC depuis navigateur, non disponible en web standard ;
- fingerprinting navigateur, juge fragile et intrusif ;
- agent local, juge puissant mais trop lourd pour tablettes et maintenance ;
- decouverte reseau automatique.

### 3.8 bis PWA installable sans offline metier

Decision : inclure un premier jet de PWA installable dans ce chantier, mais ne pas inclure le mode offline metier.

Clarification vocabulaire : PWA signifie "Progressive Web App". Dans ce cadrage, le besoin vise surtout l'installation en un clic : icone sur bureau / barre des taches / ecran d'accueil tablette, ouverture en mode application, et experience de poste plus stable qu'un onglet navigateur ordinaire.

Ce que le MVP PWA doit couvrir :

- manifest PWA minimal ;
- icone et nom d'application ;
- lancement en mode standalone si supporte ;
- compatibilite PC / tablette autant que raisonnable ;
- ecran verrouille PIN propre en mode installe ;
- conservation du mecanisme d'enrolement serveur (`device_id` + secret / cle locale).

Ce que le MVP PWA ne promet pas :

- offline metier ;
- synchronisation differee ;
- file locale d'operations ;
- resolution automatique des pertes d'identite ;
- robustesse equivalente a un agent local.

Point important : la PWA ne resout pas magiquement l'identification du poste. Elle repose toujours sur du stockage local navigateur / application, mais ce stockage ne doit pas devenir une source de verite autonome ni s'appuyer sur `localStorage` si une alternative raisonnable existe. Si les donnees du site ou de l'application installee sont effacees, l'identite locale peut etre perdue. Le registre serveur et le flux de reconnexion restent donc necessaires.

### 3.8 ter Navigateur dedie recommande

Recommandation operationnelle : installer la PWA Recyclique depuis un navigateur dedie au poste, idealement peu ou pas utilise pour la navigation quotidienne.

Exemple terrain : si Chrome sert aux recherches et usages courants, installer Recyclique depuis Edge ou un profil navigateur dedie, puis epingler l'application installee.

Objectif :

- reduire le risque de vidage de cache accidentel ;
- separer l'usage Recyclique des usages web ordinaires ;
- limiter les extensions, cookies et manipulations non liees au poste ;
- rendre l'exploitation plus stable pour des benevoles.

Cette recommandation n'est pas une garantie de securite ni un substitut au registre serveur. Elle doit etre documentee comme bonne pratique d'installation terrain, pas comme mecanisme d'autorisation.

### 3.9 Audit

Constat : le socle audit existe deja cote API (`audit_logs`, `AuditLog`, `AuditActionType`, `log_audit`, `merge_critical_audit_fields`).

Decision : ne pas creer un nouveau "gros journal d'audit" dans ce chantier. Reutiliser et enrichir le journal existant.

Evenements a auditer :

MVP obligatoires :

- succes / echec de PIN operateur ;
- changement d'operateur actif ;
- verrouillage manuel ;
- verrouillage par timeout ;
- enrolement de poste ;
- modification de configuration de poste ;
- revocation de poste ;
- refus d'acces ;
- reprise ou abandon de brouillon ;
- actions sensibles avec `operator_user_id`.

Evenements utiles a enrichir ensuite, sans creer un reporting audit lourd :

- choix de module ;
- consultations d'etat de poste ;
- changements de timeout ;
- tentatives d'override SuperAdmin refusees ou annulees.

L'audit doit distinguer autant que possible :

- `operator_user_id` : humain actif ;
- `device_id` : identifiant canonique MVP pour l'ancrage poste / appareil enregistre ;
- `cash_register_id` seulement si l'action concerne vraiment une caisse ;
- `site_id` ;
- `session_id` ;
- `operation` ;
- `outcome`.

Les evenements PIN ne doivent jamais stocker le PIN ni ses derives dans `details_json`. L'etat doit passer par `operation`, `outcome`, `operator_user_id`, `device_id` (avec `workstation_id` seulement comme alias documentaire si rencontre), et les champs critiques existants du socle audit.

Point a specifier en story technique : mapper `operator_user_id` avec le `user_id` deja present dans le socle audit, ou etendre explicitement le helper d'audit si les deux notions doivent coexister. Meme logique pour `device_id` : l'ajout minimal attendu est un enrichissement de `details_json` / `merge_critical_audit_fields`, sans nouvelle table d'audit ni reporting lourd.

Note de vocabulaire : `workstation` peut rester le nom produit du poste partage, mais les traces MVP utilisent `device_id` tant qu'une ADR ne choisit pas un autre identifiant canonique.

### 3.10 Timeout

Decision : timeout configurable par poste / module, avec un defaut global.

Regles :

- activite clavier / souris / tactile repousse le timeout ;
- le timeout doit representer une inactivite reelle ;
- ne pas verrouiller brutalement au milieu d'une saisie active ;
- afficher un avertissement avant verrouillage si un ecran metier est ouvert ;
- "continuer" garde l'operateur actif ;
- "verrouiller maintenant" efface l'operateur actif ;
- le verrouillage par timeout produit le meme etat de securite que "passer la main".

Defaut propose pendant la discussion : 15 minutes, a confirmer.

### 3.11 Brouillons

Decision : les brouillons restent sur le poste, mais deviennent invisibles sans PIN.

Clarification : "sur le poste" designe le contexte de reprise rattache au poste et au serveur, pas une promesse de mode offline. Si un stockage local temporaire existe, il doit rester masque, revocable, borne au contexte autorise, et ne jamais exposer de donnee metier ou de metadonnee sensible hors `ContextEnvelope` valide.

Regles :

- timeout ou passer la main verrouille l'ecran ;
- le contenu du brouillon n'est pas visible sur l'ecran PIN ;
- apres nouveau PIN, un operateur autorise sur le site, le poste et le module concernes peut voir qu'un brouillon existe ;
- si l'operateur n'a pas les droits, il ne voit pas le contenu ;
- l'existence et les metadonnees sensibles du brouillon ne doivent pas fuiter hors contexte serveur autorise ;
- l'identite de l'operateur initial et l'heure de creation ne sont affichees qu'apres autorisation effective et selon une politique de minimisation ;
- l'audit trace brouillon masque, repris, abandonne ou valide.

### 3.12 Reprise par un autre operateur

Decision : un autre operateur autorise peut reprendre un brouillon avec confirmation explicite.

Exemple :

- Alice commence une vente ou une reception ;
- le poste se verrouille ;
- Bob tape son PIN ;
- si Bob a les droits, il voit "Brouillon commence par Alice a telle heure" ;
- Bob peut reprendre ou abandonner ;
- l'action est auditee.

### 3.13 Override SuperAdmin sur poste partage

Decision : inclure un override SuperAdmin sur poste partage.

Garde-fous requis :

- visible seulement pour un SuperAdmin identifie ;
- action explicite, jamais automatique apres PIN ;
- confirmation forte ou revalidation PIN ;
- audit complet ;
- sortie claire du mode override : verrouillage, timeout, bouton de sortie.

Important : distinguer deux cas.

Session personnelle SuperAdmin :

- login classique depuis ordinateur personnel ;
- acces complet selon droits SuperAdmin ;
- pas un poste partage terrain.

Poste partage terrain :

- soumis au profil du poste par defaut ;
- override SuperAdmin possible mais explicite et audite.

### 3.14 Ordinateurs personnels SuperAdmin

Decision provisoire : les ordinateurs personnels SuperAdmin peuvent etre geres comme une autre categorie d'appareils de confiance, pas comme des postes partages terrain.

Pistes :

- appareil personnel admin ;
- historique de connexion ;
- revocation ;
- MFA / PIN renforce selon future politique ;
- pas de limitation par modules du poste sauf decision specifique.

### 3.15 Postes, appareils et peripheriques

Decision de vocabulaire a stabiliser : ne pas confondre le poste partage qui porte une session operateur avec les peripheriques qu'il utilise.

Distinction produit recommandee :

- **poste partage / workstation** : appareil depuis lequel un humain agit dans Recyclique ;
- **appareil personnel admin** : appareil de confiance rattache a un SuperAdmin ou administrateur ;
- **peripherique** : imprimante, balance, webcam, lecteur code-barres, autre equipement associe a un poste ou a un site ;
- **device registry** : registre commun qui peut contenir ces categories, avec des champs differents selon le type.

Les webcams peuvent servir a la lecture code-barres ou a la photo d'objets ; ce point appartient a la future carte materielle / flux reception, pas au coeur du premier palier PIN.

### 3.16 Invalidation et revocation

La revocation d'un poste par SuperAdmin doit etre effective des que possible :

- au prochain chargement / rafraichissement de configuration ;
- idealement via polling court ou mecanisme temps reel plus tard ;
- en cas de revocation, l'operateur actif est efface et le poste revient a un etat non enrole ou bloque ;
- l'evenement est audite.

## 4. Registre materiel futur

Vision cible : un registre / map du parc local Recyclique.

Types d'equipements envisages :

- ordinateurs de caisse ;
- postes reception ;
- tablettes ;
- imprimantes ;
- webcams ou lecteurs code-barres ;
- balances connectees ;
- ordinateurs personnels SuperAdmin ;
- autres peripheriques reseau.

Champs envisages :

- nom lisible ;
- type ;
- site ;
- emplacement ;
- modules autorises ;
- statut ;
- dernier contact ;
- peripheriques associes ;
- configuration ;
- historique d'audit.

Le MVP doit preparer cette direction, sans inclure encore :

- decouverte reseau automatique ;
- association intelligente poste -> imprimante / balance / camera ;
- supervision temps reel complete ;
- agent local.

Le premier chantier doit toutefois eviter de fermer la porte a ces evolutions : les noms de modele et les champs doivent rester compatibles avec un registre materiel plus large.

## 5. Non-decisions et points a continuer

Questions encore ouvertes a la date du cadrage initial. Pour l'Epic 27, les points suivants ont ete tranches le 2026-05-30 : modele `RegisteredDevice`, identifiant `device_id`, type MVP `shared_workstation`, module pilote Reception, creation d'un epic dedie **Epic 27**.

- schema exact et endpoints pour articuler registre `module_key`, configuration modules par `site_id` et allowlist poste ; l'invariant d'intersection serveur est, lui, acte ;
- distinction schema donnees entre poste partage, appareil personnel admin et peripherique ;
- niveau d'effort acceptable pour WebCrypto des le premier chantier ;
- format exact de l'enrolement : code court, QR code, lien d'invitation, combinaison ;
- format exact du flux de reconnexion / remplacement de poste apres perte d'identite locale ;
- politique de conflit si deux machines revendiquent le meme poste logique ;
- niveau de support PWA minimal attendu selon OS / navigateur / tablette ;
- granularite des modules autorises par poste ;
- definition exacte des modules initiaux au-dela du pilote Reception ;
- politique de timeout par module ;
- comportement precis des brouillons au-dela du module pilote Reception ;
- place exacte de l'override SuperAdmin dans l'UX ;
- statut des ordinateurs personnels SuperAdmin ;
- articulation future avec une vraie carte reseau / parc materiel ;
- version cible : v2.0.1, v2.1 ou autre.

## 6. Recommandation PM actuelle

Créer un nouveau chantier BMAD dedie, probablement un nouvel epic, avec un perimetre coherent :

Avant create-epics-and-stories, fournir ce pre-brief PM :

- vocabulaire gele : "poste partage enrole", "PIN operateur", "device_id", "allowlist poste", "configuration module par site" ;
- in MVP : poste partage enrole, PIN, intersection serveur, timeout, passer la main, audit leger, ecran SuperAdmin administratif, reconnexion/remplacement de poste, PWA installable sans offline metier ;
- hors MVP : PWA offline, agent local, decouverte reseau, cartographie complete des peripheriques, supervision temps reel, reporting audit avance ;
- module pilote retenu pour Epic 27 : Reception uniquement ; ne pas elargir a caisse / atelier / inventaire dans la story pilote.

Perimetre coherent propose. Note 2026-05-30 : l'ordre executable final est celui de `epics.md`, `sprint-status.yaml` et du runbook Epic 27 ; la liste ci-dessous est une decomposition de perimetre historique, pas la file d'execution si elle diverge.

1. Registre SuperAdmin administratif des postes / appareils.
2. Enrolement controle d'un poste partage.
3. Reconnexion / remplacement d'un poste apres perte d'identite locale, avec arbitrage SuperAdmin en cas de conflit.
4. PWA installable pour usage poste, sans offline metier.
5. Configuration des modules autorises par poste, croisee avec la configuration module par site.
6. Ecran verrouille PIN operateur.
7. Session operateur active et modules visibles par intersection configuration site x poste x permissions.
8. Brouillons Reception masques et reprise explicite par operateur autorise.
9. Passer la main + timeout.
10. Audit integre au socle existant, avec `device_id` et mapping `operator_user_id` / `user_id` a specifier.
11. Override SuperAdmin explicite et audite.

Livrable de decision produit livre avant stories code : mini-ADR `references/artefacts/2026-05-29_02_mini-adr-postes-partages-pin-non-offline.md`, validee PM / Strophe pour l'ecriture BMAD documentaire Epic 27 le 2026-05-30. Elle explique la difference avec la cible PWA/kiosque offline du PRD et fixe les invariants repris ici.

Le chantier ne doit pas embarquer maintenant :

- PWA offline ;
- agent local ;
- decouverte reseau automatique ;
- cartographie complete des peripheriques ;
- roles locaux non stabilises ;
- reporting audit avance.

## 7. Phrase de synthese

Le produit vise n'est pas "un kiosque caisse", mais un systeme de postes partages enroles, verrouilles par PIN operateur, configures par modules, auditables, et extensibles vers un futur registre materiel Recyclique.
