# Addendum transcripts 23/05/2026 — visions, workflows org, pont REC/PKO

**Date meeting :** 2026-05-23 · **Révision STT/QA2 :** 2026-05-26  
**Complète :** [2026-05-21_02_recap-idees-paheko-reception-terrain.md](2026-05-21_02_recap-idees-paheko-reception-terrain.md) (gate QA2 **96 %**, 42 cartes REC/PKO)  
**Sources :**

| Meeting | Final | Idées |
|---------|-------|-------|
| `2026-05-23-terrain-1423` | `.transcription/meetings/…/final/2026-05-23-terrain-1423.md` | **4** |
| `2026-05-23-recyclique-bilans-audit-visions` | `.transcription/meetings/…/final/2026-05-23-recyclique-bilans-audit-visions.md` | **20** |

**Volume cumulé pipeline (in-scope brainstorm modules) :** **49** (18–21 mai) **+ 24** (23 mai) = **73** idées indexées ; **42 + 24 = 66** cartes addendum (dont recoupements REC/PKO).

**Lecture :** addendum **post-terrain** — ne remplace pas les specs/décisions mai ; valider sur audio les lignes *hypothèse* / *inférence*.

---

## 1. Positionnement vs session en cours

| Chantier | Apport 23/05 |
|----------|----------------|
| **Brainstorm Réception** | **VIS-010, 017, 019, 020, 004, 007, 008, 011, 016** — upgrades REC-001, 005, 006, 007, 008 |
| **Brainstorm Compta / Paheko** | Peu de direct (**PKO-001…025** inchangés en substance) ; **VIS-018** (modèle données), **VIS-019** (journal → SAV **REC-015** / **PKO-017**), **VIS-015** HelloAsso adjacent **PKO-005** |
| **Workflows / org (transversal)** | **1423** (ORG/WFL/GOV/AGT) + **VIS-009, 010, 019, 020** — upgrade **REC-008** |

---

## 2. Meeting court `terrain-1423` (4 IDEA → domaines WFL/ORG)

| ID addendum | Source | Énoncé | Lien REC/PKO |
|-------------|--------|--------|--------------|
| **ORG-001** | 1423 IDEA-001 | Workflows par cercle / org / atelier ; jonction secteur (admin / « superadmin secteur » — STT ambigu) | **Enrichit REC-008** |
| **WFL-001** | 1423 IDEA-002 | Ports entrée/sortie : info, matière, outils ? | Sous-jacent **REC-002**, **REC-008** ; tangente **PKO-000** (matière) |
| **WFL-002** | 1423 IDEA-003 | Couche interprétation workflows → langage humain, exploration | **Enrichit REC-008** ; complète **1245** MCP (Peintre) |
| **GOV-001** | 1423 IDEA-004 | Agentique + mode d’emploi ; matière règlements intérieurs / statuts | **Nouveau** ; lien **VIS-009** (cercles) |

**Questions 1423 :** ports outils ? · superadmin secteur vs admin global RecyClique ?

**Ne pas fusionner dans §3 Réception seul** — gouvernance + agentique documentaire.

---

## 3. Meeting `bilans-audit-visions` (VIS-001…020)

| VIS | Titre court | Domaine | Lien REC/PKO |
|-----|-------------|---------|--------------|
| VIS-001 | Addendum post-enquêtes terrain | Transverse | Cadre — « ressourcerie source de vérité » |
| VIS-002 | Réseau local entité + enrôlement machines | Réseau | **Nouveau** |
| VIS-003 | IoT / Home Assistant (différé) | Réseau | **Nouveau** |
| VIS-004 | Lecteurs RPi/ESP32 + écran statut objet | Réseau / réception | **REC-001**, **REC-005** |
| VIS-005 | Personnalisation extrême UI | Transverse | **Nouveau** |
| VIS-006 | Module interfaces personnalisées RecyClique/Jarvos | Jarvos | **Nouveau** |
| VIS-007 | Emplacements multi-sites, contenance | Lieux | **REC-006**, **REC-007** |
| VIS-008 | Carte interactive + onboarding permanent | Lieux | **REC-007** (Peintre ? — STT) |
| VIS-009 | Cercles echo-eco (admin, agenda, passations) | Org | **Nouveau** ; lien **ORG-001** |
| VIS-010 | Éditeur workflows graph + chatbot | Workflows | **Upgrade REC-008** ; complète **WFL-002** (lecture vs édition) |
| VIS-011 | Auth opérateur (PIN, RFID, QR, ludique) | Réception | **Nouveau** — prérequis **VIS-020** |
| VIS-012 | Module documentaire K-Drive | Documents | **Nouveau** ; adjacent **PKO-005** |
| VIS-013 | Jarvos nano reclassement docs | Jarvos | **Nouveau** |
| VIS-014 | Audio cercles → transcription / tâches | Org | **Nouveau** |
| VIS-015 | HelloAsso cotisations / campagnes | Org / finance | **Nouveau** ; ≠ caisse Paheko |
| VIS-016 | Topologie réseau, cross-post, rôles | Réseau | **REC-001** (imprimante, webcam) |
| VIS-017 | Postes métiers, rayonnages, balance quadrillée IA | Réception | **Upgrade REC-001** |
| VIS-018 | Schéma BDD pour toute la vision | Données | Fondation **REC-*** + **PKO-000** |
| VIS-019 | Run rétrocompat + journal déplacements | Workflows | **REC-008**, **REC-002**, **REC-015** |
| VIS-020 | Session transhumance (scan rafale, pause 3 min) | Workflows | **REC-005**, **REC-006** |

---

## 4. Top intégrations pour les 2 brainstorms

### Réception (prioriser)

1. **VIS-010** → configurateur concret (**REC-008**)  
2. **VIS-017** → poste pesée + IA balance (**REC-001**)  
3. **VIS-019** → objets en vol + logs (**REC-008**, retours **REC-015**)  
4. **VIS-020** → déplacements / zones (**REC-005**, **REC-006**)  
5. **VIS-007/008** → stock spatial (**REC-006**, **REC-007**)  
6. **VIS-004/011/016** → matériel réseau + auth postes  

### Compta / Paheko (prioriser)

1. **VIS-018** — entités compta/matière/ticket dans le modèle dès v1  
2. **VIS-019** — journal = preuve remboursements (**PKO-017**)  
3. **VIS-015** — HelloAsso ≠ PKO ; cadrer avec **PKO-005** cockpit  
4. Pas de nouvelle écriture Paheko dans visions — **PKO-001…025** restent la base compta  

---

## 5. Upgrades explicites (pas doublons)

| Existant | Apport 23/05 |
|----------|--------------|
| **REC-008** | ORG-001, WFL-001/002, **VIS-010**, **VIS-019** |
| **REC-001** | **VIS-017**, 004, 016 |
| **REC-005/006** | **VIS-020** (transhumance) |
| **REC-007** | **VIS-007**, **VIS-008** |
| **1245 MCP Peintre** | **WFL-002**, **GOV-001** (repérage agentique métier) |

---

## 6. Questions transverses (registre)

**1423 :** ports outils · superadmin secteur  

**Visions :** stack IoT différée · Home Assistant vs module UI · nom module workflows · Graphset = produit ou métaphore · balance vs bascule · liste postes/rayonnages par site · STT « traitements par l'eau » (**VIS-020**)  

**Croisement recap :**

1. Périmètre v1 Réception : VIS-010/017/019/020 in or parking ?  
2. **VIS-018** : entités minimum v1 sans sur-modéliser  
3. **VIS-011** + **VIS-002** : PIN seul v1 ou multi-modal dès la conception ?  
4. **VIS-019** : politique modification workflow (bloquer / migrer / fork) ?  
5. **WFL-002** vs **VIS-010** : même module ou deux couches ?  
6. Frontière RecyClique / Jarvos / echo-eco (VIS-009, 012, 015)  

---

## 7. Suite recommandée

1. **Ne pas** regonfler le recap 21/05 — garder **REC/PKO** pour caisse + réception v1.  
2. Brainstorm Réception : charger **ce addendum** §4 + recap §3.  
3. Brainstorm Compta : recap §4 PKO + **VIS-018**, **VIS-019** ici.  
4. Chantier **workflows/org** : **1423** + **VIS-009/010/019/020** + **ORG/WFL** (session dédiée).  
5. Option : QA2 sur les 2 finaux 23/05 si registre contractuel (1423 a déjà `qa2-draft-fusion.md`).

---

*Synthèse agents explore 2026-05-26 — croisement factuel avec finaux STT post-QA2.*
