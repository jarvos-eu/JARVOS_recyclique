# Cadrage — bot Discord pilote La Clique (CH-LACLIQUE-BOT-001)

**Date :** 2026-07-05  
**Demandeur :** Strophe  
**Statut :** spec · **P0** · **activation bloquée** (gate Ombre/CREOS)  
**Nature :** outil **local / temporaire / pilote** — **pas** vision produit Recyclique

**Spec canonique JARMES :** [`JARMES/docs/programme/CH-LACLIQUE-BOT-001-spec.md`](../../../../JARMES/docs/programme/CH-LACLIQUE-BOT-001-spec.md)

**Fiches kanban :**

- Projet : [`docs/ideas/kanban/IDEA-2026-07-05-002.md`](../../docs/ideas/kanban/IDEA-2026-07-05-002.md)
- Écosystème : [`JARMES/docs/ideas/kanban/IDEA-2026-07-05-002.md`](../../../../JARMES/docs/ideas/kanban/IDEA-2026-07-05-002.md)

---

## 0. Gate d'activation (Strophe · 2026-07-05)

> **Ne rien activer** tant que le système de **communications Ombre / CREOS** n'est pas **terminé** dans JARMES.

Le MVP specs CREOS/LANG est clos ([`CH-OMBRE-CREOS-LANG-001`](../../../../JARMES/cursor-sdk-ombre/_bmad-output/planning-artifacts/orchestration/CH-OMBRE-CREOS-LANG-001/00_SYNC_STATUS.md)), mais la **chaîne opérationnelle** Hermes ↔ Ombre ↔ Cursor + **verrous** reste à livrer avant le pilote La Clique.

---

## 1. Problème

L'utilisatrice pilote La Clique remonte besoins, bugs et questions **via Discord**. Aujourd'hui Strophe **transcrit à la main** → kanban / artefacts. Friction + risque de perte.

---

## 2. Schéma cible (architecture imposée)

```text
Salon Discord La Clique (#recyclique-pilote)
        │
        ▼
Agent Discord  ──►  Hermes (VPS)
                         │  verrous Hermes
                         ▼
                    L'Ombre (orchestrateur CREOS)
                         │  verrous Cursor
                         ▼
                    Agent Cursor (réponses)
```

**Pas de route directe** `cursor-discord-bridge` → Cursor pour ce pilote.

---

## 3. Trois modes autorisés (seuls)

| Mode | Exemple | Destination |
|------|---------|-------------|
| **TICKET** | plante, erreur, bug | **CH-TICKETS-001** |
| **PROPOSITION** | il faudrait, il manque | **IDEA** / DEPOT kanban Recyclique |
| **AIDE** | comment, je suis bloquée | Réponse **doc + code** read-only |

**Interdit** : coder, télécharger, exécuter, ou toute action hors ces 3 modes.

### Override exceptionnel

Aller plus loin (dev, actions sensibles) : **uniquement** via **ID Discord personnel Strophe** — overkill, **hors cadre normal** du pilote.

---

## 4. Verrous

### Hermes

- Whitelist salon + serveur La Clique.
- Types mission : `ticket` · `proposition` · `aide` seulement.
- Pas de dev généraliste, pas de push/téléchargement/exécution libre.

### Cursor (via Ombre)

- Profil pilote **read-only** · repo `jarvos-recyclique` + doc.
- Pas d'édition, commit, shell destructif.
- CREOS : capability set dédié `la_clique_pilot` (à cadrer).

---

## 5. Garde-fous produit

- **Un salon** autorisé · config figée La Clique.
- Accusé de réception (✅ + type + ID ticket/IDEA).
- Escalade humaine si confiance basse.

---

## 6. Dépendances JARMES

| Dépendance | Note |
|------------|------|
| **CH-OMBRE-CREOS-LANG-001** | Gate spec · MVP clos · intégration Hermes↔Ombre **requise** |
| **OMB-BACKLOG-04** (SPEC-006) | Parser multicanal · P0 post-MVP |
| **CH-TICKETS-001** | File tickets |
| **Hermes** | Gateway Discord + verrous |
| **K-Drive headless VPS** (chantier à part) | Clone local K-Drive La Clique sur le VPS — runbook [`2026-07-07_08_installation-kdrive-headless-vps.md`](2026-07-07_08_installation-kdrive-headless-vps.md) · accès fichiers pour mode **AIDE** (lecture doc, pas de téléchargement libre au pilote) · post-gate |

---

## 7. Owners trio

| Rôle | Agent / projet | Responsabilité |
|------|----------------|----------------|
| **Priorisation globale** | **Mentor** | GLOBAL_REPRISE · gate visible cross-projets |
| **Programme / todo** | **Ariane** | JARMES_TODO_STREAMS · spec programme |
| **Fil opérationnel** | **Clio** | REPRISE Hermes + Ombre |
| **Implémentation** | `Hermes` + `cursor-sdk-ombre` | Chaîne Discord → Hermes → Ombre → Cursor |
| **Contenu métier** | `jarvos-recyclique` | Doc assistance · kanban idées |

---

## 8. Ordre d'exécution (post-gate)

1. **G1** — Gate CREOS/Hermes/Ombre opérationnel.
2. **G2** — Verrous Hermes.
3. **G3** — Profil Cursor read-only Ombre.
4. **G4** — Bot Discord → Hermes (salon La Clique).
5. **G5** — Classification TICKET / PROPOSITION / AIDE.
6. **G6** — Raccord kanban + tickets Recyclique.
7. **G7** — HITL utilisatrice pilote.

---

## 9. Hors scope

- Produit Recyclique multi-ressourceries.
- Bridge Discord dev Strophe comme canal utilisatrice.
- Bot compta / Paheko / voix.

---

## 10. Questions ouvertes

| # | Question |
|---|----------|
| Q1 | Préfixes V0 (`!bug` / `!idée` / `?`) vs classification auto ? |
| Q2 | Assistance : thread public ou DM ? |
| Q3 | Définition exacte « CREOS terminé » pour lever la gate (checklist sign-off) ? |
