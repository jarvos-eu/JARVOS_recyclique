# Révision — transcriptions terrain (draft, final, QA2)

**Date** : 2026-05-21  
**Contexte** : lot mai 2026 — six enregistrements traités par le pipeline **transcription-pipeline-v1.1** (brainstorming-organique), puis passes **QA2 adversariales** demandées sur les drafts puis sur les finaux.

**Objectif de ce document** : inventaire des **fichiers nécessaires** au chantier, état constaté après QA2, synthèse transversale des findings, **lacunes** (fichiers QA2 absents) et **ordre de travail** recommandé pour la suite (corrections draft / final, re-QA2).

---

## 1. Inventaire canonique des fichiers par meeting

Racine : `JARVOS_recyclique/.transcription/meetings/<MEETING_ID>/`

| Rôle | Chemins (relatifs à chaque meeting) | Statut révision |
|------|-------------------------------------|-----------------|
| Source vérité | `transcriptions/full-transcript.json` | Présent pour les six ; base de tout QA fidélité. |
| Segments (mécanique) | `working/segments/segment-*.md`, `working/index.json` | Présents selon pipeline ; cités dans certains QA (provenance segment vs JSON). |
| Draft brainstorming (5) | `working/draft/index-des-idees.md`, `fiches-d-idees.md`, `vues-par-theme.md`, `questions-ouvertes-consolidees.md`, `idees-orphelines.md` | Présents pour les six ; **contenu** révisé via QA2 pour **quatre** meetings (voir §2). |
| Final assemblé | `final/<MEETING_ID>.md` | Présent pour les six. |
| Rapport QA2 draft (fusion) | `qa2-draft-fusion.md` | **Présent** : `2026-05-18-terrain-1245`, `2026-05-21-terrain-1246`, `2026-05-21-terrain-1301`, `2026-05-21-terrain-1333`. **Absent** : `2026-05-21-terrain-1401`, `2026-05-21-recyclique-terrain-paheko`. |
| Rapport QA2 final (fusion) | `qa2-final-fusion.md` | **Absent pour les six** — la phase « création du Final » n’a pas laissé de livrable `qa2-final-fusion.md` sur disque. |

**Meetings** (six identifiants) :

1. `2026-05-18-terrain-1245`  
2. `2026-05-21-terrain-1246`  
3. `2026-05-21-terrain-1301`  
4. `2026-05-21-terrain-1333`  
5. `2026-05-21-terrain-1401`  
6. `2026-05-21-recyclique-terrain-paheko`  

**Fichiers transverses (hors `meetings/`)** — à garder alignés avec le chantier :

| Fichier | Rôle |
|---------|------|
| `.transcription/transcription-profile.json` | Profil (template, speakers, langue, diarisation). |
| `.transcription/README.md` | Point d’entrée humain (inbox, clés, sorties). |
| `.transcription/_queue/` | Originaux audio après traitement (non versionné si ignoré). |
| `.transcription/_queue_run_pipeline.py` | Script utilitaire batch (si conservé). |
| `.gitignore` | Règles `inbox/`, `meetings/`, `.transcription/.env`. |

**Matière déjà agrégée ailleurs** (recoupement utile, pas doublon obligatoire) : [2026-05-21_02_recap-idees-paheko-reception-terrain.md](2026-05-21_02_recap-idees-paheko-reception-terrain.md) — recap idées modules Réception / Paheko à partir des transcripts.

---

## 2. Synthèse des QA2 draft (fusion) — quatre meetings documentés

Les rapports détaillés sont dans chaque dossier meeting (`qa2-draft-fusion.md`). Ci-dessous : **verdicts** et **thèmes transverses** pour la révision des drafts (sans refaire l’audit ligne à ligne ici).

| Meeting | Score fusionné (rapport) | Gate ≥ 95 % | Thèmes principaux à corriger dans les drafts |
|---------|-------------------------|-------------|-----------------------------------------------|
| `2026-05-18-terrain-1245` | 89 | Non | Étiqueter le non-verbatim (mécanisme, friction, industrialisation, tag « orchestration ») ; éviter triple comptage IDEA-001 dans `vues-par-theme.md` ; clarifier « hors transcription » vs contenu réellement présent ; transcript JSON très court dans le rapport — vérifier cohérence avec l’audio réel si besoin terrain. |
| `2026-05-21-terrain-1246` | 79 | Non | **Omission** piste omnicanal / vente en ligne dans index et fiches ; projections non sourcées (ticket de caisse, canaux) ; cohérences index ↔ fiches ↔ questions ↔ vues (IDEA-003, IDEA-007, Q2) ; provenance `segment-002` vs JSON. |
| `2026-05-21-terrain-1301` | 81 | Non | Surfacturation de certitude (IDEA-005, maturité IDEA-008) vs réserves orales ; colonne « Modules » / lecture Paheko implicite sans nom dans l’audio ; ambiguïté « caisse » ; harmoniser fiches ↔ questions (IDEA-006/007) ; ajouter question ou justification pour IDEA-004. |
| `2026-05-21-terrain-1333` | 86 | Non | Regroupement IDEA-004 / 005 dans `vues-par-theme.md` ; colonne Modules pour IDEA-003 ; `idees-orphelines.md` peu relié à l’index ; glossaire « agent » ; nuancer IDEA-005 (argent vs trace don). |

**Constat transversal** : **aucun P0** consolidé dans ces quatre rapports ; les gates 95 % échouent surtout sur **score de confiance** et sur **exhaustivité / surfacturation** rédactionnelle. Aucun des quatre rapports ne remet en cause la nécessité de garder les **cinq** fichiers draft + le **final** : la révision porte sur **qualité, étiquetage et alignement transcript**.

---

## 3. Lacunes QA2 et actions correctives immédiates

### 3.1 Meetings sans `qa2-draft-fusion.md`

- **`2026-05-21-terrain-1401`**  
- **`2026-05-21-recyclique-terrain-paheko`**  

**Action** : relancer une passe **QA2** (orchestrateur + workers) avec le même brief que pour les autres meetings : `scope_paths` = les cinq `working/draft/*.md` + `transcriptions/full-transcript.json`, mode **adversarial**, criticité **high** ; écrire `qa2-draft-fusion.md` dans chaque dossier meeting.

### 3.2 Absence totale de `qa2-final-fusion.md`

Pour les **six** meetings, aucun rapport `qa2-final-fusion.md` n’a été trouvé sous `.transcription/meetings/`.

**Action** : enchaîner **six** QA2 ciblés sur **`final/<MEETING_ID>.md`**, idéalement avec `scope_paths` incluant le même meeting : **final** + **cinq drafts** (pour détecter régressions à l’assemblage) + optionnellement un extrait ou index du transcript si la taille du JSON impose une stratégie par segments.

### 3.3 Après corrections des markdown

Pour tout fichier `working/draft/*.md` ou `final/*.md` modifié : **re-lancer** `validation_check.py` et `assemble_final.py` (skill) sur le `meeting_id` concerné, puis **option** re-QA2 ciblé sur les sections modifiées.

---

## 4. Ordre de travail recommandé (révision éditoriale)

1. **Compléter les QA2 manquants** (§3.1 et §3.2) pour avoir une couverture **symétrique** sur les six meetings.  
2. **Appliquer par meeting** les recommandations en tête des `qa2-draft-fusion.md` (prioriser omissions type **omnicanal** 1246, étiquetage non-verbatim 1245, colonnes Modules / périmètre Paheko 1301, scission thèmes 1333).  
3. **Repasser les finaux** après assemble : lecture ciblée cohérence titres / doublons / renvois aux idées P1 signalées.  
4. **Tracer** dans `references/artefacts/` ou dans une note de meeting toute **décision terrain** qui infirme une question ou une fiche (éviter que les drafts « figent » une hypothèse non validée).

---

## 5. Charger si

- Reprise du chantier **transcriptions terrain** après interruption.  
- Brief pour un **éditeur** ou un **atelier** de correction des drafts / finaux.  
- Décision de **re-lancer** uniquement les QA2 manquants (1401, Paheko, finaux).

---

*Document de révision consolidé ; il ne remplace pas la lecture des `qa2-draft-fusion.md` existants ni des livrables sous `.transcription/meetings/`.*
