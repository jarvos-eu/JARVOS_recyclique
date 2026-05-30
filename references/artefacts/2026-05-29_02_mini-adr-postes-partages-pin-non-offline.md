# Mini-ADR — Postes partages, PIN operateur et PWA non-offline

Date : 2026-05-29  
Statut : validee PM / Strophe pour ecriture BMAD documentaire Epic 27 le 2026-05-30  
Source : cadrage `2026-05-29_01_cadrage-postes-partages-pin-operateur.md`

## Decision

Recyclique doit introduire un palier dedie aux **postes partages enroles** :

- un poste reste connecte techniquement ;
- aucune donnee metier n'est visible sans operateur actif ;
- un operateur prend la main par PIN ;
- les modules accessibles sont calcules cote serveur par intersection :

```text
configuration module par site x allowlist poste x permissions operateur
```

Ce palier inclut une **PWA installable** pour l'usage terrain, mais **n'inclut pas l'offline metier**.

## Contexte

Le besoin prioritaire n'est pas de reproduire la 1.4.4 pour elle-meme, mais de couvrir :

- tracabilite des actions ;
- fluidite de prise de poste par benevoles / operateurs ;
- securite d'acces sur postes partages ;
- preparation d'un futur registre materiel Recyclique.

Le PRD vision mentionne des cibles plus lourdes : kiosque, poste enregistre, PWA/offline, secret de poste, sync differee. Cette ADR ne livre pas cette cible complete. Elle fixe un premier palier non-offline, compatible avec elle.

## Portee MVP

Le MVP inclut :

- registre SuperAdmin administratif des postes / appareils ;
- enrôlement controle d'un poste partage ;
- reconnexion / remplacement apres perte d'identite locale ;
- arbitrage SuperAdmin si deux machines revendiquent le meme poste logique ;
- PWA installable sans offline metier ;
- recommandation terrain d'utiliser un navigateur ou profil dedie pour l'installation PWA ;
- configuration des modules autorises par poste, pour un module pilote initial valide PM : Reception ;
- ecran verrouille PIN ;
- session operateur active ;
- passer la main et timeout d'inactivite ;
- brouillons Reception masques sans PIN, repris uniquement sur le module pilote par operateur autorise ;
- audit integre au socle existant ;
- override SuperAdmin explicite et audite.

Le MVP exclut :

- offline metier ;
- file locale d'operations ;
- sync differee ;
- decouverte reseau automatique ;
- agent local ;
- cartographie complete des peripheriques ;
- supervision temps reel de parc ;
- reporting audit avance ;
- nouveaux roles locaux non stabilises.

## Invariants

### Autorite serveur

Le backend Recyclique reste la seule autorite d'autorisation.

- Le front, le stockage local, le manifest PWA, les manifests CREOS et l'allowlist poste ne decident jamais seuls.
- Toute action metier doit etre refusee cote API si le contexte poste / operateur / site / module n'est pas valide.
- Ce contexte s'aligne sur `ContextEnvelope` ou son evolution : `site_id`, `device_id`, `operator_user_id`, `module_key`, et etat d'override. `workstation_id` peut rester un libelle produit ou alias documentaire, pas un second identifiant technique concurrent dans l'Epic 27.
- La revocation d'un poste, d'un secret, d'un droit, d'un module ou d'un override s'applique a la frontiere API des que le backend la connait ; le rafraichissement UI ne fait que refléter l'etat.
- Sans operateur PIN actif : refus par defaut.
- Tout changement de poste, operateur, site, module, droits ou override impose un recalcul du contexte.
- Le PIN est verifie cote serveur, n'est pas stocke localement, et doit avoir une limitation d'essais / verrouillage ou rate-limit.

### Vocabulaire MVP

- `device_id` identifie le poste partage enrole dans l'Epic 27 ; `workstation_id`, si rencontre dans les docs, ne doit pas creer un second identifiant concurrent.
- `cash_register_id` reste reserve aux actions caisse.
- `reception_post_id`, si introduit plus tard, ne remplace pas l'identifiant du poste partage MVP.
- Un appareil personnel admin reste sous authentification classique et ne releve pas du lock screen PIN terrain.
- Les peripheriques futurs sont hors autorisation metier MVP.

### Identite du poste

Le poste n'est pas devine, il est enrole.

- Le serveur conserve un `device_id` ou identifiant equivalent.
- Le poste stocke localement un secret ou une cle locale associee.
- WebCrypto avec cle non exportable est la cible saine si l'effort reste raisonnable.
- Le MVP peut accepter un secret local revocable, mais pas dans `localStorage` si une alternative raisonnable existe.
- Le secret local doit etre rotatif, revocable cote serveur, et inutilisable sans contexte serveur valide.

La perte du stockage navigateur / PWA est un risque accepte, mais elle doit etre traitee :

- le poste serveur reste visible dans le Panel SuperAdmin ;
- le poste passe en statut a reconnecter / identite locale perdue ;
- le SuperAdmin peut reconnecter, remplacer ou refuser ;
- l'ancien secret / ancienne cle est revoque ;
- si l'ancien ordinateur revient, il est bloque et remonte en conflit.

### PWA installable

La PWA du MVP sert a l'installation et a l'ergonomie terrain :

- icone ;
- nom d'application ;
- lancement standalone si supporte ;
- experience de poste plus stable qu'un onglet ordinaire.

Elle ne garantit pas l'identification permanente du poste et ne remplace pas le registre serveur.

Elle ne leve pas le gate PWA / kiosque complet du PRD : le MVP couvre seulement manifest, icone, lancement standalone connecte et ergonomie terrain.

Aucun cache offline de donnees ou d'API metier n'est autorise. Les assets statiques peuvent etre caches ; les endpoints authentifies restent en network-only / no-store.

Bonne pratique terrain : installer la PWA depuis un navigateur ou profil dedie, par exemple Edge si Chrome sert aux usages quotidiens, afin de reduire les risques de vidage de cache accidentel.

### Modules

Les modules autorises par poste doivent s'aligner avec le vocabulaire `module_key`.

- L'intersection serveur utilise un `module_key` actif dans le registre serveur, la configuration `site_id` / `module_key`, l'allowlist poste et les permissions operateur.
- L'allowlist poste restreint le contexte.
- Elle ne remplace pas la configuration module par `site_id`.
- Elle ne remplace pas les permissions de l'operateur.
- Elle ne cree pas un second systeme de droits.

### Audit

Le chantier reutilise le socle audit existant (`audit_logs`, `log_audit`, `merge_critical_audit_fields`) au lieu de creer un second journal.

L'audit est transversal : chaque slice sensible du chantier doit tracer ses evenements critiques des la story concernee.

Evenements MVP a tracer :

- enrôlement ;
- reconnexion / remplacement ;
- conflit d'identite ;
- revocation ;
- succes / echec PIN ;
- changement d'operateur actif ;
- verrouillage manuel ;
- verrouillage par timeout ;
- refus d'acces ;
- override SuperAdmin ;
- reprise / abandon de brouillon ;
- actions sensibles avec `operator_user_id` et `device_id` quand pertinent.

`device_id` doit rester distinct de `cash_register_id` et de tout futur `reception_post_id`. `workstation_id` ne doit etre utilise que comme alias documentaire / libelle produit si rencontre. La story technique devra etendre `merge_critical_audit_fields` ou documenter le stockage explicite dans `details_json`.

Aucun PIN ni derive de PIN ne doit etre stocke dans l'audit.

## Consequences positives

- Le chantier est compatible avec le futur registre materiel sans l'embarquer entierement.
- Le risque de poste public trop ouvert est reduit par l'intersection serveur.
- La PWA installable ameliore l'usage terrain sans promettre l'offline.
- Le flux de reconnexion evite qu'un vidage de cache bloque durablement l'exploitation.
- La separation poste partage / appareil personnel admin / peripherique est bornee pour le MVP sans fermer le futur registre materiel.

## Consequences et risques

- Le MVP ajoute un vrai ecran SuperAdmin, donc le chantier est plus gros qu'un simple lock screen.
- La PWA peut donner une impression d'application native ; il faudra documenter clairement l'absence d'offline metier.
- Les pertes d'identite locale resteront possibles.
- Les brouillons doivent rester serveur-autoritatifs ; tout cache local eventuel doit etre borne, non autoritaire, revalide par API et limite au module pilote Reception. Les endpoints et payloads brouillons authentifies restent `network-only` / `no-store` ou equivalent.
- L'override SuperAdmin doit etre un etat serveur explicite du contexte, a TTL ou sortie claire, audite, jamais implicite apres PIN.

## Questions a trancher avant stories

Tranche avant ecriture BMAD documentaire (2026-05-30) :

- Nom canonique du modele : `RegisteredDevice`.
- Identifiant technique stable : `device_id`.
- Module pilote initial : Reception.

Dans la premiere story ou un spike technique :

- Format exact de l'enrôlement : code court, QR code, lien, validation SuperAdmin.
- Format exact de la reconnexion / remplacement.
- Politique de conflit si deux machines revendiquent le meme poste.
- Niveau WebCrypto attendu en premiere implementation.

En criteres d'acceptation de stories :

- Politique de timeout par defaut.
- UX exacte de l'override SuperAdmin.

## Decision de suite

Avant implementation, creer un epic BMAD dedie ou une tranche clairement isolee. Ne pas lancer ce chantier comme simple extension opportuniste d'une story caisse ou reception.

Ordre recommande. Note 2026-05-30 : l'ordre executable final est celui de `epics.md`, `sprint-status.yaml` et du runbook Epic 27 ; la liste ci-dessous est une synthese historique si elle diverge.

1. Modele / API registre de postes.
2. Contrat `ContextEnvelope` poste partage et audit transversal minimal.
3. Ecran SuperAdmin de gestion des postes.
4. Enrôlement + reconnexion / remplacement.
5. PWA installable minimale.
6. Lock screen PIN + session operateur.
7. Intersection serveur modules / poste / permissions.
8. Module pilote Reception / brouillons.
9. Timeout / passer la main.
10. Override SuperAdmin.
