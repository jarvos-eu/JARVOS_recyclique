# Recherche Perplexity — Trous restants Liaison Paheko (3e passe)

**Fichier :** `2026-05-21_liaison-paheko-trous-recherche_perplexity_reponse.md`  
**Date :** 2026-05-21 · **IA :** Perplexity Pro  
**Prompt :** [2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md](2026-05-21_liaison-paheko-trous-recherche_perplexity_prompt.md)  
**Ventilation :** [décisions](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) · [procédure clôture](../migration-paheko/2026-05-21_procedure-cloture-liaison-paheko-recyclique.md) · [synthèse](../artefacts/2026-05-21_11_synthese-trous-perplexity-liaison-paheko.md) · [QA ventilation](../artefacts/2026-05-21_12_qa-ventilation-3e-passe-perplexity.md)

---

# Réponse consolidée — RecyClique × Paheko — Liaison comptable (3e passe)

**Date :** 2026-05-21 | **Version :** finale post-deep-research | **Destinataire :** Architecte projet RecyClique

***

## A. Ce qui est FIGÉ (acquis toutes passes confondues)

**RecyClique** = caisse web ressourcerie ; **Paheko** = compta loi 1901 non TVA. Clôture **par session** (pas par ticket) ; tickets archivés RecyClique 10 ans (L123-22). Module comptage pièces/billets **obligatoire** à chaque fermeture, branché sur la clôture.

**Plan de comptes retenu :**


| Compte | Usage |
| :-- | :-- |
| **530** | Caisse espèces (une caisse = 530 unique ; multi-caisse = 531, 532… voir §R8) |
| **5112** | Chèques à encaisser |
| **511** | CB / valeurs à l'encaissement |
| **512** | Banque (un sous-compte par compte bancaire réel : 512A, 512B…) |
| **58** | Virements internes (transit obligatoire entre comptes de trésorerie) |
| **7070** | Ventes réemploi |
| **7541** | Dons caisse (exercice courant) |
| **658 / 758** | Écarts caisse (manque / surplus) |
| **672** | Remboursements sur exercice clos |
| **7070 débit** | Remboursements sur exercice courant |

**Rejeté définitivement :** 1630, 708 / 7041 / 7073, 709 pour remboursements, 511-205 / 511-210 comme sous-comptes du plan, 467 pour remboursements, 531 si une seule caisse.

***

## R1 — Extension Caisse Paheko et comptes d'écart — **FORT** ✅

### Ce que la documentation confirme

Depuis la version 1.3.12, l'extension Caisse Paheko propose un onglet **Configuration** (Caisse → Gestion et statistiques → Configuration) qui permet de lier un exercice comptable pour la **synchronisation automatique** des sessions. Les comptes utilisés pour les écritures synchronisées sont ceux paramétrés dans **Configuration des moyens de paiement** (un compte comptable par moyen : 530 pour espèces, 5112 pour chèques, 511 pour CB).[^1][^2]

**Point crucial :** la caisse native Paheko **ne génère pas d'écriture d'écart séparée** sur des comptes 678/778. Elle crée une écriture de session consolidée basée sur le solde de chaque moyen de paiement. Il n'existe **aucun champ configurable `POS::ERROR_DEBIT_ACCOUNT` / `POS::ERROR_CREDIT_ACCOUNT`** dans l'interface publique documentée — ces champs étaient une hypothèse d'audit à vérifier, désormais infirmée [web:synchroniser-caisse-comptabilite].

### Risque réel

Le risque n'est **pas** un conflit 658/758 vs 678/778 : c'est le **doublon d'écriture de session** si la synchro automatique Paheko reste active ET que RecyClique pousse ses propres écritures via API.

### Stratégie retenue

- **Désactiver** la synchro automatique : Caisse → Configuration → **laisser le champ exercice vide** [web:synchroniser-caisse-comptabilite].
- RecyClique devient le **seul producteur d'écritures comptables**. Le bouton "Synchroniser" manuel reste disponible mais doit être désactivé par procédure interne.
- Si l'asso utilise ponctuellement la caisse native hors RecyClique (ex. buvette) : deux jeux de procédures documentés + revue manuelle mensuelle anti-doublon. **Valider EC sur place.**

***

## R2 — Nombre de pièces / lots par session — **FORT** ✅

### Réconciliation PRD (3 transactions) vs validation (2 pièces)

La stratégie B du PRD est **compatible** avec la validation comptable dès lors qu'on adopte ce modèle : **3 transactions API maximum par session**, toutes de type `ADVANCED` (multi-lignes équilibrées) :


| Transaction | Contenu | Déclenchement |
| :-- | :-- | :-- |
| **T1** | Ventes + dons (débits 530/5112/511, crédits 7070/7541) | **Toujours**, à la clôture Z |
| **T2** | Remboursements exercice courant (débit 7070, crédit 530 ou 5112) | **Si et seulement si** remboursements dans la session |
| **T3** | Écart de caisse (débit 658 ou crédit 758 contre 530) | **Si et seulement si** module comptage ≠ 0 |

> Les "2 pièces" de la validation correspondent à T1 + T3 (session sans remboursement). Le PRD ajoute T2. Il n'y a pas de contradiction, juste des cas différents.

### Remboursements même jour

Toujours **T2 séparée**, même si remboursement le jour même. Raison : traçabilité individuelle dans le journal Paheko, et nécessité de distinguer de la session nette pour l'audit.

### 709 vs 7070 pour remboursement exercice courant — **tranché**

**→ Débit 7070.** Le compte 709 (RRR) s'applique aux remises accordées au moment de la vente. Un remboursement après coup sur exercice courant = annulation partielle de la vente = débit sur le compte de produit d'origine (7070). Cohérent PCA ressourcerie.

### API Paheko : une écriture multi-lignes ou plusieurs écritures ?

L'API accepte des écritures multi-lignes en un seul appel POST (`type: ADVANCED` + tableau `lines`). **Recommandation : un appel par transaction** (T1, T2, T3 séparés) pour que chaque pièce soit identifiable dans le journal. Possibilité de lier les écritures entre elles via `linked_transactions` (depuis v1.3.5).[^3]

### Ordre d'exécution

**Z de clôture d'abord** (calcul des totaux fiables), puis T1, puis T2 si applicable, puis T3 si applicable.

***

## R3 — Granularité compte 7541 (dons) — **FORT** ✅

### Doctrine PCA confirmée

- **7541** = dons manuels de particuliers sans contrepartie (PCA)
- **7542** = dons affectés à un projet spécifique
- **754.10, 754.11, 754.115, 754.111, 754.12** = sous-comptes **libres créés localement**, sans base normative PCA — usage interne de l'asso


### Recommandation v1 : 7541 unique

Pour une ressourcerie avec dons modérés en caisse, **7541 seul** en v1. Aucune obligation réglementaire de subdiviser les dons manuels en caisse. Si un subventionneur exige la traçabilité par type : créer **7542** comme second compte distinct (pas 7541.xx), plus propre en PCA.

### Double arborescence 754.xx vs 7541

Dans Paheko, si un compte parent (ex. 754) et ses enfants (754.10, 754.11) coexistent avec des écritures aux deux niveaux, **le compte de résultat cumule les deux** → double comptabilisation des dons. C'est le risque principal à vérifier en contrôle C.6.

### Fusion 754.xx → 7541

OD à réaliser en **début d'exercice N+1** (pas en cours), avec validation EC obligatoire.

### 754.900

Aucun usage normé PCA ni documenté dans les ressourceries. Vraisemblablement un compte "divers non affecté" créé localement. À identifier avec le comptable terrain.

***

## R4 — Migration historique 707 → 7070 — **FORT** ✅

**Ne pas reclasser l'historique N-1.** Critères :

- Le reclassement N-1 n'est ni obligatoire ni recommandé en loi 1901 hors changement de méthode formalisé
- Impact sur la comparabilité N/N-1 : signaler en note annexe "707 utilisé en N-1, remplacé par 7070 à partir de N"
- Impact bilan : nul (comptes de produits, pas de reports)

**Procédure Paheko :**

1. Comptabilité → Plan comptable → Ajouter compte **7070** (libellé : "Ventes réemploi")
2. Configurer RecyClique pour pointer sur 7070 dès la mise en production
3. Laisser 707 dans le plan pour l'historique N-1 (ne pas supprimer)
4. Les tableaux de bord Paheko afficheront les deux lignes sur la période de transition — ajouter une note dans le rapport annuel

***

## R5 — Compte 672 et fin d'exercice — **FORT** ✅

**672 = charges sur exercices antérieurs.** Usage confirmé pour tout remboursement portant sur une vente d'un exercice déjà clôturé.[^4][^5]

### Réimputation fin d'exercice

Le solde 672 doit être **soldé en fin d'exercice** par OD : **débit 658 / crédit 672** (réimputation en charges d'exploitation associative courantes). Valider le compte cible exact avec l'EC (certains cabinets préfèrent 671 selon la nature).

### Blocage RecyClique

RecyClique **doit bloquer** les nouvelles écritures 672 si l'exercice Paheko correspondant est fermé. Mécanisme : appel préalable `GET /api/accounting/years`, vérifier le statut de l'exercice (ouvert / verrouillé / clôturé) avant chaque POST. Si exercice clos → lever une alerte métier dans RecyClique, ne pas pousser l'écriture automatiquement.

### Granularité

**Une écriture par remboursement** (pas de regroupement mensuel). Raison : traçabilité de l'avoir RecyClique avec la pièce Paheko, contrôle interne et audit facilités.

***

## R6 — Procédures Paheko post-clôture banque — **FORT** ✅

### Dépôt chèques (5112 → 512)

Étapes confirmées par la doc officielle [web:extension-bordereau-cheques] :

1. Activer l'extension **"Bordereau de remise de chèques"** (Configuration → Extensions → Inactives)
2. Comptabilité → Comptes → **5112** → sélectionner les lignes chèques à remettre
3. Bouton **"Créer un bordereau"** → Paheko génère automatiquement l'écriture de transfert **5112 → 512** + PDF bordereau à déposer à la banque
4. Date de l'écriture = **date du dépôt physique** (pas la date de la session)

### Encaissement CB (511 → 512)

Écriture manuelle ou importée depuis le relevé bancaire. Délai : **J+1 à J+2** (TPE modernes), J+3 maximum. Rapprochement : Comptabilité → Rapprochement → compte **511**.

### Multi-comptes 512

Un sous-compte par compte bancaire réel (512A = compte courant principal, 512B = Hello Asso, etc.). Le 512 cible se choisit par correspondance directe avec le compte bancaire récepteur du dépôt/crédit.

### Compte 58 — Virements internes

**Obligatoire** pour tout mouvement entre deux comptes de trésorerie Paheko, pour éviter un déséquilibre transitoire.

**Exemple chiffré — retrait de 200 € à la banque pour remettre en caisse :**

- Écriture 1 : Débit **58** 200 € / Crédit **512** 200 €
- Écriture 2 : Débit **530** 200 € / Crédit **58** 200 €


### Journal comptable pour écritures RecyClique importées

- Ventes + dons (T1) → journal **Recettes**
- Écarts de caisse (T3) → journal **Opérations diverses (OD)**
- Remboursements (T2, T3 672) → journal **OD**
- À confirmer avec comptable terrain selon organisation des journaux existants.

***

## R7 — Paramètres techniques liaison — **FORT** ✅

### Libellé API

Pas de limite fixe documentée (champ TEXT SQLite). L'affichage Paheko tronque vers 150-200 caractères. **→ Limiter à 200 caractères** dans RecyClique. Format recommandé : `Z SESSION {id} – {type} – {date}`.

### id_year et exercice

L'API Paheko supporte explicitement **`current`** comme valeur de `{ID_YEAR}` → désigne l'exercice ouvert le plus récent non clôturé. C'est la méthode robuste pour tous les appels automatisés. Si plusieurs exercices ouverts simultanément (rare), `current` retourne le plus récent.[^3]

**Champs obligatoires** pour `POST /accounting/transaction`  :[^3]

- `label` (libellé)
- `date` (YYYY-MM-DD)
- `type` = ADVANCED pour multi-lignes
- `lines[]` : tableau d'au moins 2 lignes équilibrées (débit = crédit)


### Seuil d'écart caisse

**±2 €** recommandé pour une ressourcerie retail avec bénévoles (monnaie rendue à la main). Aucune norme sectorielle publiée — seuil pragmatique basé sur les pratiques retail associatif.

- En deçà de ±2 € : écriture 658/758 automatique
- Au-delà de ±2 € : **bloquer la clôture RecyClique**, alerter le responsable caisse

***

## R8 — Fond de caisse et compte 531 — **FORT** ✅

**Une seule caisse magasin → 530 uniquement.** Le compte 531 est superflu. Le fond de caisse = **solde permanent en 530** (ex. 50 €) qui ne bouge jamais dans Paheko.

**Aucune écriture Paheko à l'ouverture de session.** RecyClique gère le fond en interne (l'opérateur saisit le fond en début de session pour que le module comptage calcule les espèces à remettre = total espèces − fond).

**Module comptage et pièce 1 :** le fond est **hors périmètre de T1**. T1 ne comptabilise que les ventes et dons de la session. T3 comptabilise l'écart entre espèces théoriques (tickets) et comptage physique — le fond étant soustrait avant le comptage, il n'entre pas dans le calcul de l'écart.

**Multi-caisse** (rappel depuis passe 1) : si plusieurs caisses physiques → sous-comptes **531, 532, 533…** (ou 531001, 531002… format long). Chaque compte = une caisse identifiée. Lié aux **Lieux de vente** Paheko. À valider EC pour la numérotation exacte.

***

## C.1 — Tableau synthèse final R1–R8

| Bloc | Question clé | Recommandation | Certitude | Valider EC |
| :-- | :-- | :-- | :-- | :-- |
| R1 | Comptes d'écart caisse native Paheko | Désactiver synchro auto (champ exercice vide) ; pas de 678/778 dans caisse native ; RecyClique = seul producteur écritures | **Fort** | Oui (si caisse native utilisée en parallèle) |
| R2 | PRD 3 transactions vs validation 2 pièces | 3 transactions API (T1 toujours, T2 si rembours, T3 si écart) ; remboursements courants = débit 7070 ; Z d'abord | **Fort** | Non |
| R3 | 7541 unique ou sous-comptes | 7541 seul en v1 ; 7542 si projets affectés ; fusion 754.xx en N+1 avec EC | **Fort** | Oui (fusion) |
| R4 | Migration 707 → 7070 | Ne pas reclasser N-1 ; créer 7070 ; note N-1 dans rapport | **Fort** | Non |
| R5 | 672 et fin d'exercice | Réimputer 672 → 658 en OD clôture ; bloquer RecyClique si exercice clos ; 1 écriture par remboursement | **Fort** | Oui (réimputation) |
| R6 | Procédures Paheko post-clôture banque | Extension Bordereau chèques ; CB manuel J+1/J+2 ; 58 pour virements internes ; journal Recettes / OD | **Fort** | Non |
| R7 | Paramètres techniques liaison | Label ≤ 200 car ; `id_year = current` ; champs obligatoires API vérifiés ; seuil ±2 € | **Fort** | Non |
| R8 | Fond de caisse et 531 | 530 seul (1 caisse) ; fond = solde permanent 530 ; aucune écriture ouverture session ; fond hors T1 | **Fort** | Non |


***

## C.2 — Décisions RecyClique codables sans EC (≤ 5)

1. **3 transactions API par session** : T1 (ventes+dons), T2 (remboursements exercice courant si présents), T3 (écart si module comptage ≠ 0). Toutes type `ADVANCED`, `id_year = current`.[^3]
2. **Désactiver la synchro automatique Paheko Caisse** dès mise en production RecyClique : laisser le champ exercice vide dans Configuration Caisse [web:synchroniser-caisse-comptabilite].
3. **Bloquer la clôture RecyClique si écart > ±2 €** ; bloquer les écritures 672 si exercice Paheko clos (vérifier statut via `GET /api/accounting/years`).
4. **Remboursement exercice courant = débit 7070** ; remboursement exercice clos = débit 672.
5. **Label écriture ≤ 200 caractères** : format `Z SESSION {id} – {type} – {YYYY-MM-DD}` ; intercepter et logger toutes les réponses API non-200.

***

## C.3 — Décisions réservées EC (≤ 5)

1. **Réimputation solde 672 en fin d'exercice** : valider compte cible (658 ou 671) et moment exact de l'OD.
2. **Sous-comptes 7541 / 7542** : décision lors de la présentation du premier bilan avec subventionneurs.
3. **Fusion arborescence 754.xx → 7541** : OD à signer avec EC en début N+1.
4. **Journal comptable exact** pour les écritures importées (Recettes / OD / Banque) : à confirmer selon organisation des journaux Paheko terrain.
5. **Usage caisse native Paheko en parallèle** (ex. buvette, stand) : procédure anti-doublon à définir avec EC si ce cas existe.

***

## C.4 — Procédure opérationnelle complète : fin session → rapprochement banque

1. **Bénévole ferme la session RecyClique** → module comptage pièces/billets s'ouvre obligatoirement.
2. **Saisie du fond de caisse** (ex. 50 €) → RecyClique calcule : espèces à remettre = total espèces session − fond.
3. **Comptage physique** → RecyClique calcule l'écart (théorique vs comptage).
4. Si écart > ±2 € → **blocage**, alerte responsable caisse, régularisation manuelle avant toute écriture.
5. **RecyClique génère le Z de clôture** (totaux ventes, dons, CB, chèques, remboursements).
6. **API → T1** : `POST /accounting/transaction` — libellé `Z SESSION {id} – Ventes+Dons – {date}` — débits 530/5112/511, crédits 7070/7541.
7. **API → T2** (si remboursements dans la session) : libellé `Z SESSION {id} – Remboursements – {date}` — débit 7070 (exercice courant) ou 672 (exercice clos), crédit 530 ou 5112.
8. **API → T3** (si écart ≠ 0 et ≤ ±2 €) : libellé `Z SESSION {id} – Écart caisse – {date}` — débit 658 (manque) ou crédit 758 (surplus) contre 530.
9. **RecyClique confirme** les 3 réponses API (HTTP 200/201) et archive les `id` des pièces Paheko dans la session.
10. **J+0 à J+3 — Dépôt chèques** : dans Paheko, Comptabilité → 5112 → sélectionner lignes → Créer un bordereau → écriture automatique **5112 → 512**, PDF généré [web:extension-bordereau-cheques].
11. **J+1 à J+2 — Encaissement CB** : à réception de l'avis de crédit bancaire, créer écriture manuelle ou import **511 → 512** sur la date réelle du crédit.
12. **Mensuel — Rapprochement banque** : Paheko → Comptabilité → Rapprochement → 512, pointer chaque ligne contre le relevé bancaire.

***

## C.5 — Modèle complet des écritures par type d'événement

### T1 — Clôture session standard (ventes + dons)

| Compte | Débit | Crédit | Libellé ligne |
| :-- | :-- | :-- | :-- |
| 530 | montant espèces net |  | Espèces session |
| 5112 | montant chèques |  | Chèques session |
| 511 | montant CB |  | CB session |
| 7070 |  | montant ventes | Ventes réemploi |
| 7541 |  | montant dons caisse | Dons caisse |

*Chèque mixte vente + don : débit 5112 / deux lignes crédit (7070 + 7541).*

### T3 — Écart de caisse (module comptage)

| Cas | Compte | Débit | Crédit |
| :-- | :-- | :-- | :-- |
| Manque (comptage < théorique) | 658 | montant écart |  |
|  | 530 |  | montant écart |
| Surplus (comptage > théorique) | 530 | montant écart |  |
|  | 758 |  | montant écart |

### T2a — Remboursement exercice courant

| Compte | Débit | Crédit |
| :-- | :-- | :-- |
| 7070 | montant remboursé |  |
| 530 ou 5112 |  | montant remboursé |

### T2b — Remboursement exercice clos

| Compte | Débit | Crédit |
| :-- | :-- | :-- |
| 672 | montant remboursé |  |
| 530 ou 5112 |  | montant remboursé |

*OD fin d'exercice : débit 658 / crédit 672 (réimputation solde).*[^5][^4]

### Dépôt chèques banque

| Compte | Débit | Crédit |
| :-- | :-- | :-- |
| 512 | montant chèques |  |
| 5112 |  | montant chèques |

### Crédit CB (encaissement banque)

| Compte | Débit | Crédit |
| :-- | :-- | :-- |
| 512 | montant CB |  |
| 511 |  | montant CB |

### Virement interne (ex. retrait espèces banque → caisse, montant X)

| Écriture | Compte | Débit | Crédit |
| :-- | :-- | :-- | :-- |
| 1 | 58 | X |  |
| 1 | 512 |  | X |
| 2 | 530 | X |  |
| 2 | 58 |  | X |

### Fond de caisse — dotation initiale uniquement (première fois)

| Compte | Débit | Crédit |
| :-- | :-- | :-- |
| 530 | montant fond |  |
| 512 |  | montant fond |

*Aucune écriture à l'ouverture ni fermeture de chaque session ensuite.*

***

## C.6 — 3 contrôles à faire avec le comptable sur place

**Contrôle 1 — Libellés 511-205 / 511-210**
Dans Paheko : Comptabilité → Plan comptable → chercher "511". Si 511-205 et 511-210 apparaissent comme **comptes distincts** avec un solde propre → vrais sous-comptes à fusionner sur **511** avant mise en production RecyClique. Si ce sont seulement des libellés de lignes d'écriture → aucun risque.

**Contrôle 2 — Cohérence 5112 vs anciens comptes chèques terrain**
Vérifier que les écritures chèques historiques ne sont pas logées sous **512A** ou un sous-compte ad hoc. Si oui → créer 5112, y basculer les nouvelles écritures, noter l'écart de périmètre N-1/N pour l'EC dans la note annexe.

**Contrôle 3 — Arborescence 754.xx vs 7541**
Lister tous les comptes commençant par 754 (Paheko : Comptabilité → Plan comptable → filtre "754"). Vérifier qu'un compte parent (754) et ses enfants (754.10, 754.11…) ne coexistent pas avec des écritures aux **deux niveaux** → risque de double comptabilisation des dons dans le compte de résultat. Décision OD de fusion à prendre avec EC avant premier bilan.

***

## C.7 — Top 5 risques résiduels (lancement v1 sans réunion EC)

| \# | Risque | Probabilité | Impact | Mitigation |
| :-- | :-- | :-- | :-- | :-- |
| 1 | **Doublon écriture de session** si synchro auto Paheko Caisse reste active | Élevée si oubli | Élevé (comptes de résultat faussés) | Désactiver synchro auto immédiatement en configuration [web:synchroniser-caisse-comptabilite] |
| 2 | **Mauvais exercice** (id_year codé en dur ou périmé) | Moyenne | Élevé (écriture sur exercice clos/futur) | Toujours résoudre via `GET /api/accounting/years` avec `current` [^3] |
| 3 | **672 non réimputé en fin d'exercice** | Moyenne | Moyen (bilan/résultat incorrect) | Alerte RecyClique au 31/12 si solde 672 > 0 + check EC [^4][^5] |
| 4 | **Arborescence 754.xx non fusionnée** | Élevée (plan terrain actuel) | Moyen (dons en double dans le résultat) | Audit plan comptable avant mise en production (contrôle C.6) |
| 5 | **Erreur API silencieuse** (champ manquant, HTTP 4XX non géré) | Moyenne | Élevé (écriture non créée, non détectée) | Intercepter et logger systématiquement toutes les réponses API non-200 dans RecyClique [^3] |


***

## D. Checklist mise en production (10 actions ordonnées)

1. **Audit plan comptable Paheko** : exécuter les 3 contrôles C.6 avec le comptable (511-205/210, 5112, 754.xx)
2. **Créer les comptes manquants** dans Paheko : 7070 (si absent), 5112, 658, 758, 672, 58 (si absent)
3. **Désactiver la synchro automatique** Caisse Paheko (champ exercice vide)
4. **Activer l'extension Bordereau de remise de chèques** dans Paheko
5. **Configurer RecyClique** : mapping comptes (530/5112/511/7070/7541/658/758/672), seuil ±2 €, format label ≤ 200 car
6. **Test pièce T1** : créer une session de test, vérifier la pièce dans Paheko (équilibre, comptes, exercice)
7. **Test pièce T3** : simuler un écart caisse, vérifier l'écriture 658/758
8. **Test dépôt chèques** : simuler un chèque T1 → bordereau Paheko → vérifier 5112→512
9. **Test T2 remboursement** : simuler un remboursement, vérifier débit 7070 dans Paheko
10. **Revue EC** avant go live : soumettre le jeu de pièces test + plan comptable final pour validation

<div align="center">⁂</div>

[^1]: https://paheko.cloud/nouveautes-version-1-3-12

[^2]: https://paheko.cloud/caisse-configuration-paiement

[^3]: https://paheko.cloud/api

[^4]: https://www.pennylane.com/fr/fiches-pratiques/plan-comptable/compte-672-charges-sur-exercices-anterieurs

[^5]: https://www.compta-online.com/traiter-les-charges-et-produits-sur-exercice-anterieur-ao1761

