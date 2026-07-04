# Préparation chantier Peintre v0.1 — peintre-nano → moteur agnostique

**Date :** 2026-07-04  
**Statut :** annoncé par Strophe — **pas d'exécution ce soir** ; cadrage Mentor + mémoire projet.  
**Décision :** le chantier est un **nouveau programme BMAD** (Piste A — mocks OK), distinct du fil Epic 28 / parité beta, mais à **séquencer** après arbitrage charge (C2b, retests HITL).

---

## En une phrase

Passer de **Peintre nano** (placement correct, composition absente, shell pollué Recyclique) à **Peintre v0.1** : moteur UI **agnostique** piloté par CREOS (tokens, composition, autorité défaut→app→user, adaptation support, LayoutResolver, overlays, micro-workflows), puis portage Recyclique comme **consommateur**.

---

## Source d'autorité documentaire

| Élément | Emplacement actuel | Emplacement cible (à acter) |
|---------|-------------------|----------------------------|
| Pack **PEINTRE** (3ᵉ pack doc v2, après ARCH / MOD) | `peintre-nano/docs/dossier-architecte-peintre-v0-1/` | `references/dossier-architecte-peintre-v0-1/` |
| PRD chantier + épics A/B/C/E | `06-PEINTRE-prd-chantier.md` | idem (déplacé avec le pack) |
| Prompt agent d'entrée | `prompt-agent-chantier-peintre.md` | idem |
| Prompt système Recyclique v2 | `prompt-systeme-recyclique-v2.md` | idem — chemins à réaligner après move |
| Dépôt zip micro-workflows | `references/_depot/2026-07-04_01_pack-architecte-micro-workflows-navigation-raccourcis.zip` | fusionner / ventiler via @depot-specialist si doublon avec `04D` |

**Revue senior** (`98-PEINTRE-revue-senior.md`) : le move vers `references/` est **déjà recommandé**, jamais acté. **Gate avant promotion BMAD** : ventilation + index `references/index.md` + lien depuis `references/peintre/index.md`.

---

## Liens kanban / idées

| ID | Lien |
|----|------|
| `IDEA-2026-07-04-001` | Chantier macro Peintre v0.1 (capture 2026-07-04) |
| `IDEA-2026-03-31-001` | Micro-workflows / raccourcis / navigation — matière intégrée dans `04D`, `04C`, épic B-5 |
| `IDEA-2026-05-20-001` | Gardien du seuil — **Phase 3** intelligence (`08`, épic E), pas le noyau v0.1 |

---

## Process BMAD proposé (skills disponibles)

Ordre **non négociable** côté moteur (cf. index PEINTRE) : tokens → composition → autorité → support → LayoutResolver → dé-pollution shell → portage Recyclique → intelligence.

### Phase 0 — Pré-vol (prochaine session, avant code)

| # | Action | Skill / agent | Livrable |
|---|--------|---------------|----------|
| 0.1 | Ventiler pack PEINTRE + zip `_depot` | @depot-specialist · skill traiter-depot | `references/dossier-architecte-peintre-v0-1/` |
| 0.2 | HITL questions ouvertes | Strophe + `09-PEINTRE-risques-et-questions-hitl.md` | décisions dans `07-PEINTRE-adr-decisions.md` |
| 0.3 | Confirmer audit sur repo vivant | skill bmad-investigate ou lecture `01` + `0A` | note courte artefact ou MAJ `01` |
| 0.4 | **Promotion PRD → BMAD** | bmad-create-epics-and-stories · bmad-create-prd (si besoin epic dédié) | nouvel epic(s) dans `epics.md` + stories dans `implementation-artifacts/` |
| 0.5 | QA documentaire pack | @qa2-orchestrator (gate 98 déjà visé dans le pack) | rapport si écart |
| 0.6 | Arbitrage **charge vs Epic 28 / C2b** | Mentor → Ariane (programme) | date de GO exécution |

### Phase 1 — Exécution Piste A (moteur)

| # | Action | Skill / agent | Notes |
|---|--------|---------------|-------|
| 1.1 | Epic **A** (noyau langage) story par story | @bmad-epic-runner → @bmad-story-runner | séquence A-1…A-6 |
| 1.2 | Epic **B** (LayoutResolver, templates, overlays) | idem | B-1…B-6 ; pilote raccourcis = lien `IDEA-2026-03-31-001` |
| 1.3 | Gates QA par story / epic | @qa2-orchestrator · bmad-qa-generate-e2e-tests | smoke `peintre-nano` : lint + test + build |
| 1.4 | Multi-vagues si contexte long | long-run-orchestrator | runbook type Epic 27 |

### Phase 2 — Portage Recyclique (Tour 2)

| # | Action | Réf |
|---|--------|-----|
| 2.1 | Epic **C** stories C-1… | `10-PEINTRE-portage-recyclique.md` + `06` |
| 2.2 | Parité observable caisse / transverses | revision + checklist parité si overlap beta |

### Phase 3 — Intelligence (différable)

Epic **E** (`08-PEINTRE-intelligence-roadmap.md`) — hooks inertes déjà posées en A-5 ; gardien du seuil (`IDEA-2026-05-20-001`) **après** noyau stable.

### Mémoire & reprise session

| Besoin | Où |
|--------|-----|
| Fil court | `REPRISE.md` (Clio) — une ligne « chantier Peintre v0.1 annoncé » |
| Programme | `sprint-status.yaml` (Ariane) — après promotion epic |
| Session agentique | `references/jarvos-agentique/sessions/2026-07-04_chantier-peintre-v0-1-annonce.md` |
| Porte d'entrée type session | skill **jarvos-session-memory** · type `mixte` posture **Archi** |

### Modèles / tiers

Conseil modèle par vague : skill **user-llm-tier-advisor** (stories layout/CREOS = tier élevé ; doc/index = tier léger).

---

## Épics PRD (rappel — détail dans `06`)

| Epic | Thème | Stories clés |
|------|-------|--------------|
| **A** | Noyau langage agnostique | tokens, composition CREOS, autorité, support, PresentationSurface |
| **B** | LayoutResolver & dé-pollution | resolver, routage déclaratif, rapatriement surcouches, templates, overlays, micro-workflows |
| **C** | Portage Recyclique | theme CREOS, manifests, parité écrans |
| **E** | Intelligence (palier règles puis génératif) | post-v0.1 |

---

## Définition de « prêt à démarrer »

- [ ] Pack PEINTRE sous `references/dossier-architecte-peintre-v0-1/` + index projet à jour
- [ ] HITL Strophe sur questions bloquantes (`09`) — au minimum Q liées modules (`98` §B) et promotion epic
- [ ] Epic(s) BMAD créés et ordonnés dans `sprint-status.yaml`
- [ ] GO explicite Strophe sur **quand** enchaîner vs Epic 28 / C2b
- [ ] Branche Git dédiée (convention à choisir : `feat/peintre-v0-1` ou epic number)

---

## Prompt de reprise (coller en tête de session)

```
Chantier Peintre v0.1 — Piste A.
Charger : references/artefacts/2026-07-04_01_preparation-chantier-peintre-v0-1.md
puis references/dossier-architecte-peintre-v0-1/index.md (ou peintre-nano/docs/… si move pas fait)
puis prompt-agent-chantier-peintre.md.
Règles : agnosticité moteur, AR39, refs_first, pas de décision Recyclique dans le moteur.
Exécution : @bmad-epic-runner après promotion BMAD.
```

---

## Suite immédiate (hors scope ce soir)

1. Strophe valide le plan et le **timing** vs parité beta.
2. Session ventilation @depot-specialist (move PEINTRE + zip).
3. Session HITL + promotion BMAD (create-epics-and-stories).
4. GO exécution → Epic Runner sur premier epic.
