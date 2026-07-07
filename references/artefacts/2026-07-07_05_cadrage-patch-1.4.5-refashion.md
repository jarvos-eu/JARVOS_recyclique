# Cadrage patch 1.4.5 — Refashion (TLC / DPAV)

**Date :** 2026-07-07  
**Demandeur :** Strophe (via orchestration patch éco-organismes La Clique)  
**Statut :** cadrage · **P2** · **activation conditionnelle** (conventionnement DPAV)  
**Périmètre :** préparation déclaration trimestrielle Refashion — **pas** saisie portail ni AMI RNRR

**Contexte :** 3ᵉ filière REP pour La Clique (après Ecomaison P0, Ecologic P1). Aucune grille trimestrielle remplie au dépôt ; conventionnement en cours. Patch code **préparatoire** : stats, mapping, export brouillon — utilisable dès convention signée.

**Sources :** [grilles décla finale](../eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md) § Refashion · [analyse mapping Refashion](../eco-organismes/partenaires/refashion/2026-07-07_analyse-declarations-mapping.md) · [calendrier](../eco-organismes/2026-07-07_calendrier-declarations-partenaires.md) · [feedback LCQ](../artefacts/2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md) · [vision module](../vision-projet/vision-module-decla-eco-organismes.md) · [inventaire dépôt éco-organismes](2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md) · dépôt `partenaires/refashion/referentiels-officiels/` (contrat DPAV ESS 2024, formulaire conventionnement 2025, matrice PAV).

---

## 1. Résumé

| Élément | Valeur |
|---------|--------|
| **Partenaire** | Refashion — REP **Textiles, Linge de maison, Chaussures (TLC)** |
| **Rôle La Clique** | **DPAV** (détenteur point d'apport volontaire) — structure ESS (loi 2014-856) |
| **Plateforme** | Portail `https://refashion.fr` (extranet DPAV) |
| **Périodicité** | Trimestre civil |
| **Délai légal** | **J+40** après fin de trimestre (art. 12.3 / 15.3 contrat-type DPAV ESS 2024) |
| **Granularité** | **Par PAV** (point d'apport volontaire) |
| **Champs volume minimum** | **≥ 4 cases par PAV** × nombre de PAV actifs |
| **Urgence patch Recyclique** | **P2** — conditionnelle au **conventionnement** |
| **Prochaine échéance calendaire** | T2 2026 → **09/08/2026** *(si convention active au 07/07/2026 : non)* |
| **Exemple chiffré dépôt** | **Aucun** — pas de déclaration validée ; proxies export pollués (voir §8 scénario test) |
| **Soutien financier collecte** | **0 €** actuellement (art. 15.2 — Observatoire non réactualisé) ; décla reste **obligatoire** pour traçabilité |

### Les 4 cases minimum par PAV (1 boutique = 4 cases)

| # | Case portail (libellé métier) | Flux | Unité |
|---|------------------------------|------|-------|
| 1 | **TLC Usagés collectés** | Gisement / collecte REP | **t** |
| 2 | **Réemploi local** (utilisation locale, ventes, dons structures) | Réemploi | **t** |
| 3 | **Remise opérateur de tri / repreneur** — nature **Original** | Sortie tri | **t** |
| 4 | **Remise opérateur de tri / repreneur** — nature **Écrémé** | Sortie tri / surplus | **t** |

> Variante : si tout le réemploi reste en structure sans export tri, la case 3–4 peut être à **0** mais le **partenariat repreneur SIRET** reste un prérequis convention (formulaire : *« Sans cette information, le dossier ne pourra être traité »*).

### Priorité relative patch 1.4.5

```text
P0 Ecomaison  →  P1 Ecologic  →  P2 Refashion (ce document)
```

Le patch Refashion **réutilise** les livrables transverses LCQ-001…003 (stats sous-catégories + split ventes/dons/recyclage) déjà cadrés pour Ecomaison.

---

## 2. Déclaration finale DPAV — cases par PAV

D'après contrat-type DPAV ESS 2024 (art. 12.1–12.3, 15.3), formulaire conventionnement 2025 et grille [§ Refashion](../eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md).

### 2.1 Tableau opérationnel (1 PAV = boutique La Clique)

| Libellé officiel / obligation | Flux | Unité | Période | Source Recyclique cible | État dépôt |
|-------------------------------|------|-------|---------|-------------------------|------------|
| **Quantités de TLC Usagés collectés** — **par PAV** (art. 12.1.b) | Gisement | **t** | Trimestre | `SUM(poids_kg)` entrées textile REP, ventilé `pav_id` | *Non rempli* |
| **Liste PAV** — adresse, type, horaires, GPS | Référentiel | — | Continu | Entité `pav_refashion` | Matrice xls = header seul |
| **Réemploi local** — justificatifs cession (art. 12.2) | Réemploi | **t** | Trimestre | Ventes caisse textile + dons structures (LCQ-003) ; exclure TLC d'Occasion | *Non rempli* |
| **Remise opérateur de tri** — SIRET, quantités **Original** | Sortie tri | **t** | Trimestre | Sorties surplus vers OT conventionné | *Non tracé* |
| **Remise repreneur** — SIRET, quantités **Écrémé** | Sortie tri / recyclage | **t** | Trimestre | Idem ; distinction Original vs Écrémé selon annexe 6 | *Non tracé* |
| **Collectes ponctuelles** (annexe 4) | Gisement ponctuel | **t** | ≤ 3 mois | Événements / camion TLC | N/A si boutique seule |

### 2.2 Distinction Original vs Écrémé

| Nature | Définition terrain La Clique | Comptage Recyclique |
|--------|------------------------------|---------------------|
| **Original** | TLC usagés remis **tout venant** à un opérateur de tri / repreneur (flux brut export structure) | Sorties `destination` = tri/repreneur, sans passage écrémage local |
| **Écrémé** | Surplus après tri « bon état » conservé en boutique (écrémage local) | Sorties surplus post-écrémage vers SIRET repreneur |

### 2.3 Méthodologie sans balance homologuée

Cases formulaire conventionnement (une seule méthode à documenter) :

| Méthode | Adéquation La Clique |
|---------|---------------------|
| **Enregistrement des ventes et dons** | **Alignée** — tickets réception + caisse + dons −18 ans (kg) |
| Reconstitution par borne de collecte | Non documentée |
| Reconstitution par sacs collectés | Non documentée |

**Conséquence patch :** l'export Recyclique doit produire une **reconstitution kg** cohérente avec la méthode « ventes et dons » (entrées − exclusions occasion − exclusions hors REP).

### 2.4 Pièces jointes portail (hors scope calcul auto)

- Tickets pesée balance homologuée **ou** justification méthodologie alternative
- Photocopie registres art. 11.1
- Mise à jour quotidienne adresses PAV sur cartographie Refashion

---

## 3. Spec exports Recyclique

### 3.1 Filtre textile usagé (gisement / collecte)

```text
INCLUS  → catégories mappées refashion_code IN {TLC_USAGE, TLC_LINGE, TLC_CHAUSSURES}
EXCLU   → refashion_code = EXCLUDE | TLC_OCCASION | NULL (autre REP)
EXCLU   → articles mouillés/souillés (flag métier si existant ; sinon procédure terrain)
EXCLU   → décoration textile ameublement (→ Ecomaison DEA_DECO_TEXTILE)
```

**Période (règle canonique patch 1.4.5) :** `TicketDepot.created_at` ∈ trimestre civil `[T_start, T_end]` — alignée Ecomaison/Ecologic ; test AC bordure trimestre (ticket à cheval T1/T2).

**Unité export :** kg en base → **tonnes** à l'export (`value_t = ROUND(SUM(poids_kg) / 1000, 3)`).

### 3.2 Agrégation par PAV

```yaml
# Structure cible export — non implémenté
declaration:
  partner: refashion
  period: 2026-T2
  methodology: ventes_et_dons  # sans balance homologuée
  pavs:
    - pav_id: PAV-LCQ-001
      label: "Boutique L'ÉCO de LA CLIQUE"
      typologie: boutique  # matrice Refashion
      lines:
        - code: TLC_COLLECTE
          flux: gisement
          unit: t
          value: null  # calculé
        - code: TLC_REEMPLOI_LOCAL
          flux: reemploi
          unit: t
        - code: TLC_TRI_ORIGINAL
          flux: sortie_tri
          unit: t
        - code: TLC_TRI_ECREME
          flux: sortie_tri
          unit: t
```

**Règle PAV unique (phase 1) :** si une seule boutique, tous les tickets du site pilote → `pav_id` par défaut ; extension future : conteneurs, collectes ponctuelles.

### 3.3 Méthodologie ventes + dons (sans balance)

Formule de reconstitution collecte TLC Usagés (méthode alternative contractuelle) :

```text
COLLECTE_TLC_kg (trimestre, PAV) =
    SUM_entrées_tickets( textile_REP, pav_id, période )
  + SUM_dons_matière_kg( textile, période )          # LCQ-003 type=don, y.c. −18 ans
  − SUM_exclusions_TLC_OCCASION( période )           # pièces non-déchet au dépôt
```

**Anti-double-comptage dons :** un kg don matière (−18 ans) est compté **une seule fois** — soit en entrée ticket réception, soit en ligne caisse `don` kg, **pas les deux** (cf. G9, AC 9.RF-04).

**Cohérence ventes :** les ventes boutique textile comptent en **réemploi local** (sortie), pas en double dans la collecte si la collecte est définie comme « entrées brutes » — variante **figée en convention** via paramètre config `collecte_variant: A|B` ; export production bloqué tant que non renseigné :

| Variante | Collecte | Réemploi local |
|----------|----------|----------------|
| **A — Entrées brutes** (défaut dev / pré-convention) | Toutes entrées TLC usagés | Ventes + dons sortants |
| B — Net collecte | Entrées − réemploi immédiat | Ventes + dons |

**Proxy pollution (ne pas déclarer tel quel) :**

| Source export | Catégorie | Masse brute | Commentaire |
|---------------|-----------|-------------|-------------|
| T4 sorties Ecomaison `SORTIES RECYCLIC Ameublement.xlsx` | `👕 Textiles` | **834 kg** | Dump non filtré — hors DEA |
| T1 entrées Ecologic dump | `A -Textile Divers` | **~2 867 kg** | Pollution filière — périmètre magasin entier |

### 3.4 Endpoints cibles (brouillon)

| Endpoint | Rôle |
|----------|------|
| `GET /v1/stats/eco-organismes/{partner}/by-subcategory?period=&partner=refashion` | Drill-down LCQ sous-catégories (transverse Ecomaison/Ecologic/Refashion) |
| `GET /v1/stats/eco-organismes/{partner}/by-exit-type?period=&partner=refashion` | Split vente \| don \| recyclage \| tri (LCQ-001…003) |
| `GET /v1/stats/eco-organismes/refashion?period=2026-T2&pav_id=` | Agrégats DPAV 4 cases/PAV (consomme mapping + stats LCQ filtrées) |
| `GET /v1/admin/declarations/refashion/export?period=2026-T2&format=csv` | Fichier pré-rempli portail |
| `GET/POST /v1/admin/pavs/refashion` | CRUD référentiel PAV |

> **Relation LCQ ↔ DPAV :** les endpoints `by-subcategory` / `by-exit-type` alimentent dashboard et pré-décla ; `eco-organismes/refashion` agrège les 4 lignes portail pour un `period` + `pav_id` donné. AC 9.RF-04 : sommes Refashion = filtre partner=refashion des stats LCQ sur même période/PAV.

---

## 4. Mapping — catégories boutique → TLC

### 4.1 Principes

- **Une catégorie boutique** → **un** `refashion_code` + flag `flux` (entree | sortie_vente | sortie_don | sortie_tri | exclude).
- Chevauchements **Ecomaison DEA** : décoration textile ameublement ≠ habillement Refashion.
- **Vente boutique** d'articles encore « occasion » (non-déchet) → `TLC_OCCASION` — **exclu** du soutien collecte ch. II.C (art. 13).

### 4.2 Tableau mapping brouillon (La Clique)

| Catégorie / libellé Recyclique (exemples dépôt) | `refashion_code` | Flux | Note |
|-------------------------------------------------|------------------|------|------|
| `👕 Textiles` | `TLC_USAGE` | entree, sortie_vente, sortie_don | Cœur filière |
| `A -Textile Divers` | `TLC_USAGE` | entree | Alias tickets |
| Sous-cat. chaussures (si ventilée) | `TLC_CHAUSSURES` | entree, sortie_* | Agrégat TLC portail |
| Sous-cat. linge de maison (si ventilée) | `TLC_LINGE` | entree, sortie_* | Idem |
| Dons textile −18 ans (caisse, kg sans €) | `TLC_USAGE` | entree (don) | LCQ-003 — inclure kg |
| Vente fripe « état neuf dépôt » qualifiée occasion | `TLC_OCCASION` | sortie_vente | **Exclure** collecte soutenue |
| `4- Eléments de décoration textile` / `* Décoration textile` | `EXCLUDE` → Ecomaison | — | Autre REP |
| `Cintres` | `EXCLUDE` | — | Ambigu EA / hors TLC |
| Accessoires non-TLC (bijoux, maroquinerie…) | `EXCLUDE` | — | Hors Refashion |

### 4.3 Arbre de décision (agent / opérateur)

```text
Objet textile en entrée
  ├─ Mouillé / souillé ? ──────────────► EXCLURE (hors collecte)
  ├─ Décoration ameublement (rideau, tapis…) ? ► Ecomaison DEA — EXCLURE Refashion
  ├─ Encore qualifié « occasion » non-déchet ? ► TLC_OCCASION — hors collecte II.C
  ├─ Chaussures ? ──────────────────────► TLC_CHAUSSURES
  ├─ Linge de maison ? ─────────────────► TLC_LINGE
  └─ Sinon habillement / textile divers ► TLC_USAGE
```

### 4.4 YAML cible (extrait)

```yaml
# config/eco-organismes/refashion-mapping.yaml — à créer
partner: refashion
version: 1
mappings:
  - recyclique_category_pattern: "^👕 Textiles$"
    refashion_code: TLC_USAGE
    flux: [RECEIVED, REUSED_SALE, REUSED_DON]
  - recyclique_category_pattern: "^A -Textile Divers$"
    refashion_code: TLC_USAGE
    flux: [RECEIVED]
  - recyclique_category_pattern: ".*[Dd]écoration textile.*"
    refashion_code: EXCLUDE
    redirect_partner: ecomaison
    ecomaison_code: DEA_DECO_TEXTILE
```

---

## 5. Règles calcul kg par trimestre

### 5.1 Paramètres

```text
Période décla     = trimestre civil (T1 jan–mar … T4 oct–déc)
Champ date        = TicketDepot.created_at (canonique patch 1.4.5)
Filtre partenaire = mapping YAML → refashion_code ≠ EXCLUDE
Unité canonique   = kg en base ; conversion t à l'export (÷ 1000)
Granularité       = par pav_id
collecte_variant  = A | B (config site ; obligatoire avant export production)
```

### 5.2 Formules par flux

| Flux décla | Formule | Champs source |
|------------|---------|---------------|
| **Collecte TLC Usagés** | **Variante A :** `SUM(poids_kg)` entrées tickets mappés `TLC_*` (hors `TLC_OCCASION`), `pav_id`, période ; + dons matière kg **sans double** (cf. §3.3). **Variante B :** variante A **−** `SUM(poids_kg)` réemploi local du même trimestre/PAV (entrées nettes après réemploi sortant) | Tickets réception ; dons matière kg (LCQ-003) |
| **Réemploi local** | `SUM(poids_kg)` sorties vente + don structure, catégories `TLC_*` | Caisse `Détails Tickets` ; dons sortants |
| **Tri Original** | `SUM(poids_kg)` sorties `destination` = repreneur, `tri_nature=original` | Migration enum/colonne `tri_nature` (9.RF-04) |
| **Tri Écrémé** | `SUM(poids_kg)` sorties `destination` = repreneur, `tri_nature=ecreme` | Idem + liaison `repreneur_id` (9.RF-05) |
| **Collecte ponctuelle** | Idem collecte, filtre `event_id` / type PAV `ponctuel` | Extension phase 2 |

### 5.3 Contrôles qualité (pré-soumission)

| Contrôle | Règle |
|----------|-------|
| Cohérence masse | `réemploi + tri_original + tri_ecreme ≤ collecte + stock_delta` (tolérance configurable) |
| `stock_delta` | Variation stock TLC usagés en boutique sur le trimestre : `stock_fin − stock_debut` (kg) ; **0** par défaut en phase 1 si pas de module stock textile |
| PAV obligatoire | Aucune ligne sans `pav_id` si convention multi-PAV |
| Exclusion double REP | Aucun kg `DEA_*` ou `ECOLOGIC_*` dans agrégat Refashion |
| Unité | Pas de mélange `poids_Tn` / `poids_kg` (leçon Ecomaison T4/T1) |
| Variante collecte | `collecte_variant` renseigné avant export production |
| Gate convention | Export **production** retourne **409** si `convention_active=false` ou aucun repreneur actif ; `?draft=true` exempté (brouillon interne) |
| Cohérence LCQ | Agrégats Refashion = filtre `partner=refashion` des stats LCQ (même `period`, `pav_id`) |

### 5.4 Calendrier 2026 (J+40)

| Trimestre | Fin activité | Date limite | Applicable La Clique (07/07/2026) |
|-----------|--------------|-------------|-----------------------------------|
| T1 2026 | 31/03/2026 | 10/05/2026 | Non — pas de convention |
| **T2 2026** | 30/06/2026 | **09/08/2026** | Conditionnel |
| T3 2026 | 30/09/2026 | 09/11/2026 | — |
| T4 2026 | 31/12/2026 | 09/02/2027 | — |

---

## 6. Prérequis conventionnement — statut La Clique

### 6.1 Checklist administrative (hors code)

| # | Prérequis | Statut dépôt 07/07/2026 | Bloquant |
|---|-----------|-------------------------|----------|
| 1 | Formulaire `demande_conventionnement_DPAV_refashion_2025_vdef.pdf` **complété** | **Vierge** | Oui |
| 2 | Envoi à `collecte@refashion.fr` | **Inconnu** | Oui |
| 3 | **Liste repreneurs + SIRET** (annexe 6 / formulaire) | **Absente** | **Oui** — *« Sans cette information, le dossier ne pourra être traité »* |
| 4 | Matrice `Matrice point d'apport.xls` — PAV renseignés | **Header seul** | Oui |
| 5 | Contrat-type signé | **Absent** | Oui |
| 6 | Méthodologie pesée : case **« Enregistrement ventes et dons »** | À cocher à la convention | Oui (audit) |
| 7 | Membre réseau **RNRR** (case formulaire) | Cohérent parcours La Clique | Non bloquant décla |
| 8 | Signalétique logo **Repère** sur PAV (annexe 1) | Non tracé | Oui (contractuel) |
| 9 | Accord occupation domaine public (si PAV voirie) | N/A boutique ? | À confirmer |
| 10 | Balance homologuée | **Non documentée** — méthodo alternative | Contourné par ventes/dons |
| 11 | **Variante collecte A vs B** figée et documentée (§3.3) | **À décider** (action §6.3 #4) | **Oui** (impact mass-balance portail) |

### 6.2 Blocages opérationnels actuels

1. **Convention non confirmée** → échéance T2 09/08/2026 **non engageante** tant que pas signée.
2. **Repreneur SIRET inconnu** → impossible de finaliser dossier ni de renseigner cases tri Original/Écrémé.
3. **Format portail exact** inconnu (pas de capture extranet au dépôt).
4. **Soutien financier = 0 €** — motivation décla = conformité / traçabilité, pas facturation.

### 6.3 Actions terrain immédiates (Strophe / La Clique)

1. Confirmer statut envoi convention avec `collecte@refashion.fr` / 07 87 17 47 33.
2. Identifier repreneur(s) surplus TLC actuel(s) + SIRET.
3. Compléter matrice PAV (1 ligne boutique minimum : type, adresse, GPS, horaires).
4. Décider variante collecte A vs B (§3.3) et la figer dans la convention.

### 6.4 Hypothèses calendaires et plan B

| Hypothèse | Échéance cible | Statut 07/07/2026 | Plan B |
|-----------|----------------|-------------------|--------|
| Convention signée | **15/07/2026** (jalon interne) | Non atteint | Décla T2 manuelle portail ou report focus T3 |
| Repreneur SIRET renseigné | Avant envoi convention | Absent | Cases tri Original/Écrémé à 0 ; **stats** via `GET /eco-organismes/refashion` ; export admin `?draft=true` autorisé sans repreneur |
| Décla T2 J+40 | **09/08/2026** | Conditionnel | Saisie manuelle portail si convention tardive ; brouillon interne `draft=true` |

> Le patch code reste **P2 préparatoire** : feature flags `convention_active` et `repreneurs_configured`. **Export admin :** `?draft=true` → brouillon interne (200, sans repreneur) ; sans `draft` → production (409 si convention inactive ou repreneur absent).

---

## 7. Gaps code

| # | Gap | Impact | Dépendance |
|---|-----|--------|------------|
| G1 | Pas de partenaire `refashion` dans config éco-organismes | Aucun filtre export | YAML mapping |
| G2 | Pas d'entité **`pav_refashion`** | Ventilation par PAV impossible | Migration DB + admin |
| G3 | Stats textile sans split vente / don / tri (**LCQ-001…003**) | Méthodo « ventes et dons » incomplète | Epic 5 + 9 |
| G4 | Dons textile −18 ans : **kg sans €** non agrégés en sortie décla | Sous-déclaration collecte | LCQ-003 |
| G5 | Pas de référentiel **repreneurs SIRET** (annexe 6) | Cases tri non renseignables | Admin + saisie terrain |
| G6 | Pas de distinction **Original / Écrémé** sur sorties | Cases 3–4 portail vides | Modèle flux sortie |
| G7 | Pas de déclaration type ni parse portail | Format colonnes inconnu | Accès extranet post-convention |
| G8 | Catégories `NE PLUS UTILISER…` dans exports | Bruit agrégats | Nettoyage config boutique |
| G9 | Tickets mixtes (don −18 + ligne payante) | Double comptage risque | Règle split ligne ticket — **AC 9.RF-03/04** |
| G10 | Module décla REP vs **suivi AMI TLC 2025** (RNRR) | Confusion périmètre | Routes séparées — **AC 9.RF-03** (pas de route AMI sous `/declarations/`) |

---

## 8. Backlog stories + critères d'acceptation

**Nombre de stories proposées : 6** (préfixe `9.RF-` — Epic 9 extension Refashion).

**Prérequis transverse (hors 9.RF-*) :** story **LCQ transverse** (LCQ-001…003) partagée Ecomaison/Ecologic/Refashion — **bloquante** pour 9.RF-03 et 9.RF-04 (cf. feedback LCQ, Epic 5).

### 9.RF-01 — Entité PAV Refashion

**Objectif :** CRUD `pav_refashion` (id, libellé, typologie matrice, adresse, GPS, horaires, `site_id`, actif).

**Critères d'acceptation :**

- [ ] Migration DB + modèle API Pydantic
- [ ] Au moins 1 PAV seed « Boutique La Clique » aligné matrice Refashion
- [ ] FK `pav_id` sur **`ticket_depot`** (granularité ticket ; défaut PAV par `site_id` via poste) + résolution documentée
- [ ] Routes admin : `GET/POST /v1/admin/pavs/refashion` (liste, création, désactivation)
- [ ] Tests : création, liste, désactivation PAV

---

### 9.RF-02 — Mapping YAML catégories → Refashion

**Objectif :** Fichier `refashion-mapping.yaml` + service résolution catégorie → `refashion_code`.

**Critères d'acceptation :**

- [ ] Codes : `TLC_USAGE`, `TLC_LINGE`, `TLC_CHAUSSURES`, `TLC_OCCASION`, `EXCLUDE`
- [ ] Exclusion explicite décoration textile → redirect `ecomaison:DEA_DECO_TEXTILE`
- [ ] Tests unitaires : 10 libellés dépôt (`👕 Textiles`, `A -Textile Divers`, `* Décoration textile`, …)
- [ ] Documentation opérateur : arbre §4.3

---

### 9.RF-03 — Stats textile LCQ (sous-catégories + split sorties)

**Objectif :** Endpoints stats textile transverses pour dashboard et pré-décla (réutilise LCQ-001…003).

**Critères d'acceptation :**

- [ ] `GET /v1/stats/eco-organismes/{partner}/by-subcategory?period=&partner=refashion` — drill-down sous-catégories
- [ ] `GET /v1/stats/eco-organismes/{partner}/by-exit-type?period=&partner=refashion` — vente | don | recyclage | tri
- [ ] Inclusion dons −18 ans en **kg** dans agrégat `don`
- [ ] Règle split ligne ticket mixte (don −18 + ligne payante) documentée + test unitaire
- [ ] Aucune route AMI/RNRR sous le préfixe décla REP (`/declarations/`, `/eco-organismes/`)
- [ ] Widget Peintre ou export JSON consommable par admin décla

---

### 9.RF-04 — Agrégats trimestriels DPAV par PAV

**Objectif :** Calcul collecte + réemploi + tri (Original/Écrémé) par trimestre et `pav_id`.

**Critères d'acceptation :**

- [ ] `GET /v1/stats/eco-organismes/refashion?period=2026-T2&pav_id=`
- [ ] Réponse JSON conforme structure §3.2 (4 lignes minimum par PAV)
- [ ] Formules §5.2 implémentées ; `collecte_variant` A par défaut, B configurable
- [ ] Migration `tri_nature` (`original` \| `ecreme`) sur sorties tri + tests seed
- [ ] Anti-double-comptage dons (§3.3) + test intégration ticket mixte
- [ ] Cohérence : agrégats = filtre `partner=refashion` stats LCQ (même `period`, `pav_id`)
- [ ] Test filtre `pav_id` obligatoire en multi-PAV
- [ ] Tests intégration avec jeu seed textile (voir scénario ci-dessous)

**Scénario test (sans chiffre officiel dépôt) :**

```text
Seed T2 2026 — PAV-LCQ-001
  Hypothèse : entrées et sorties disjointes sur le trimestre (pas de réemploi immédiat du lot entré)
  Entrées :  120 kg 👕 Textiles + 15 kg chaussures + 8 kg don −18 ans (compté une fois)
  Exclu :    5 kg décoration textile (→ Ecomaison)
  Exclu :    10 kg TLC occasion (vente état neuf dépôt)
  Sorties :  45 kg ventes textile + 12 kg don structure + 30 kg tri Original (SIRET mock)
  Attendu collecte (variante A) : (120+15+8) = 143 kg = 0,143 t
  Attendu réemploi local : (45+12) = 57 kg = 0,057 t
  Attendu tri Original : 30 kg = 0,030 t ; Écrémé : 0 t
  Contrôle §5.3 : 57+30+0 ≤ 143 + stock_delta (stock_delta = 0 en seed)

Seed variante B (même jeu, collecte_variant=B) :
  Attendu collecte : 143 − 57 = 86 kg = 0,086 t
  Attendu réemploi local : 57 kg = 0,057 t (inchangé)
```

---

### 9.RF-05 — Référentiel repreneurs / opérateurs de tri

**Objectif :** Table `refashion_repreneur` (raison sociale, SIRET, type OT|repreneur, actif).

**Critères d'acceptation :**

- [ ] CRUD admin protégé `require_admin`
- [ ] Liaison sortie tri → `repreneur_id` + champ `tri_nature` (Original/Écrémé)
- [ ] Export annexe 6 (liste SIRET) pour dossier convention
- [ ] Validation format SIRET (14 chiffres)

---

### 9.RF-06 — Export brouillon décla portail Refashion

**Objectif :** CSV/xlsx téléchargeable pré-rempli pour saisie manuelle portail.

**Critères d'acceptation :**

- [ ] `GET /v1/admin/declarations/refashion/export?period=&format=csv`
- [ ] Colonnes : `pav_id`, `pav_label`, `flux`, `nature_original_ecreme`, `tonnes`, `methodology`, `period`, `collecte_variant`
- [ ] Bannière « brouillon — vérifier avant soumission portail »
- [ ] `GET /v1/admin/declarations/refashion/export?period=&format=csv&draft=true` — brouillon interne (200 même sans repreneur)
- [ ] Export **production** (sans `draft`) : retour **409** si `convention_active=false` ou aucun repreneur actif
- [ ] Retour **409** si `collecte_variant` non figé (production uniquement)
- [ ] Test e2e : export T2 seed → sommes cohérentes avec 9.RF-04

---

### Ordre d'implémentation suggéré

```text
9.RF-02 (mapping)
  → 9.RF-01 (PAV)
  → [LCQ transverse — prérequis Epic 5]
  → 9.RF-03 (stats LCQ)
  → 9.RF-05 (repreneurs) — parallélisable avec RF-03
  → 9.RF-04 (agrégats DPAV)
  → 9.RF-06 (export)
```

**Synergies patch Ecomaison/Ecologic :** 9.RF-02 partage l'infrastructure YAML ; 9.RF-03 utilise le contrat API unifié `eco-organismes/{partner}/…` pour les trois filières.

---

## 9. Hors scope

| Élément | Raison |
|---------|--------|
| **TLC neuf** (textile neuf invendu producteur) | Autre filière / producteur — hors DPAV collecte usagés |
| **Non conventionné** | Pas de décla portail tant que convention inactive |
| Saisie automatique API portail Refashion | Pas d'API partenaire documentée |
| **AMI TLC 2025** RNRR (cofinancement projet) | Hors décla REP — module suivi projet distinct |
| Facturation / soutien financier collecte | Montant **nul** art. 15.2 — pas de calcul facture |
| Signalétique physique logo Repère | Terrain / convention — pas code Recyclique |
| Balance homologuée / tickets pesée | Matériel terrain ; AMI peut financer plus tard |
| Mobilier textile décoration (rideaux…) | **Ecomaison DEA** — pas Refashion |
| Conteneurs voirie / collecte ponctuelle camion | Phase 2 — après PAV boutique stabilisé |
| Intégration Paheko clôture dons textile | Epic 8 / correspondance — post patch 1.4.5 |

---

## 10. Liens

| Ressource | Chemin |
|-----------|--------|
| Grilles décla finale § Refashion | [`references/eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md`](../eco-organismes/2026-07-07_grilles-declaration-finale-champs-a-remplir.md) |
| Analyse mapping Refashion | [`references/eco-organismes/partenaires/refashion/2026-07-07_analyse-declarations-mapping.md`](../eco-organismes/partenaires/refashion/2026-07-07_analyse-declarations-mapping.md) |
| Calendrier partenaires | [`references/eco-organismes/2026-07-07_calendrier-declarations-partenaires.md`](../eco-organismes/2026-07-07_calendrier-declarations-partenaires.md) |
| Contrat-type DPAV ESS 2024 | [`references/eco-organismes/partenaires/refashion/referentiels-officiels/Contrat_Type_DPAV_ESS_version_2024.pdf`](../eco-organismes/partenaires/refashion/referentiels-officiels/Contrat_Type_DPAV_ESS_version_2024.pdf) |
| Formulaire conventionnement 2025 | [`references/eco-organismes/partenaires/refashion/referentiels-officiels/demande_conventionnement_DPAV_refashion_2025_vdef.pdf`](../eco-organismes/partenaires/refashion/referentiels-officiels/demande_conventionnement_DPAV_refashion_2025_vdef.pdf) |
| Matrice PAV | [`references/eco-organismes/partenaires/refashion/referentiels-officiels/Matrice point d'apport.xls`](../eco-organismes/partenaires/refashion/referentiels-officiels/Matrice%20point%20d'apport.xls) |
| Feedback LCQ-001…003 | [`references/artefacts/2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md`](2026-07-05_01_feedback-la-clique-dashboard-stats-eco-organismes.md) |
| Vision module décla | [`references/vision-projet/vision-module-decla-eco-organismes.md`](../vision-projet/vision-module-decla-eco-organismes.md) |
| Inventaire dépôt éco-organismes | [`references/artefacts/2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md`](2026-07-07_01_inventaire-depot-eco-organismes-la-clique.md) |
| Guide mapping brownfield | [`recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md`](../../recyclique-1.4.4/docs/eco-organismes/04-guide-mapping-categories.md) |
| Index éco-organismes | [`references/eco-organismes/index.md`](../eco-organismes/index.md) |
| Kanban LCQ stats | [`docs/ideas/kanban/IDEA-2026-07-05-001.md`](../../docs/ideas/kanban/IDEA-2026-07-05-001.md) |

---

## Retour orchestrateur (synthèse)

| Champ | Valeur |
|-------|--------|
| **Chemin artefact** | `references/artefacts/2026-07-07_05_cadrage-patch-1.4.5-refashion.md` |
| **Nb stories** | **6** (`9.RF-01` … `9.RF-06`) |
| **Prérequis convention** | Formulaire complété + envoi `collecte@refashion.fr` · **liste repreneurs SIRET** (bloquant) · matrice PAV · contrat signé · méthodo « ventes et dons » · signalétique Repère |
| **Urgence** | **P2 conditionnelle** — J+40 (prochaine : **09/08/2026** T2 si convention active) |
| **Cases / PAV** | **≥ 4** (collecte, réemploi local, tri Original, tri Écrémé) |
