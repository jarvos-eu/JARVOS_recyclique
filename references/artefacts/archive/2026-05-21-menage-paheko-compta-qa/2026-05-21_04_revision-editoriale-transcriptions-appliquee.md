# Révision éditoriale appliquée — transcripts terrain (mai 2026)

**Date** : 2026-05-21  
**Périmètre** : les **six** meetings sous `.transcription/meetings/<MEETING_ID>/working/draft/*.md`, puis régénération des **`final/<MEETING_ID>.md`** via les scripts du skill **transcription-pipeline-v1.1**.

## Principes appliqués

1. **Encadré méthode / STT** : encadré type blockquote en tête des drafts (index, fiches, vues, questions, orphelines) — distinguer tags éditoriaux, verbatim, structuration non lue mot pour mot à l’oral.  
2. **Reco QA2 intégrées** là où des rapports `qa2-draft-fusion.md` existaient (1245, 1246, 1301, 1333) : exemples — fusion des triples IDEA-001 en facettes (1245), omnicanal **IDEA-009** + vues + questions (1246), réserves maturité / modules (1301), scission IDEA-004 / 005 dans les vues + glossaire *agent* (1333).  
3. **1401 et Paheko** (sans rapport QA2 disque au moment de la passe) : notices de révision + rappels volume / distinction verbatim–structuration ; Paheko : renforcement de l’encadré méthode existant sur `fiches-d-idees.md`.

## Vérification mécanique

Commandes exécutées (depuis la racine du repo, `PYTHONUTF8=1`) pour chaque `meeting_id` :

- `validation_check.py --transcription-root …\.transcription --meeting-id <id> --skill-root …\transcription-pipeline-v1.1`  
- `assemble_final.py` (mêmes arguments)

**Résultat** : **exit 0** pour les six meetings ; rapports `working/validation-report.md` mis à jour.

## Fichiers régénérés (finaux)

Chemins absolus :

1. `…\meetings\2026-05-18-terrain-1245\final\2026-05-18-terrain-1245.md`  
2. `…\meetings\2026-05-21-terrain-1246\final\2026-05-21-terrain-1246.md`  
3. `…\meetings\2026-05-21-terrain-1301\final\2026-05-21-terrain-1301.md`  
4. `…\meetings\2026-05-21-terrain-1333\final\2026-05-21-terrain-1333.md`  
5. `…\meetings\2026-05-21-terrain-1401\final\2026-05-21-terrain-1401.md`  
6. `…\meetings\2026-05-21-recyclique-terrain-paheko\final\2026-05-21-recyclique-terrain-paheko.md`  

(Racine `…` = `d:\users\Strophe\Documents\1-IA\La Clique Qui Recycle\JARVOS_recyclique\.transcription`.)

## Suite recommandée

- Compléter les **QA2** manquants (draft + final) pour **1401** et **Paheko** si besoin de score / gate documenté — voir [2026-05-21_03_revision-transcriptions-terrain-qa2.md](2026-05-21_03_revision-transcriptions-terrain-qa2.md).  
- Atelier terrain pour trancher les **questions ouvertes** et les libellés marqués *hypothèse*.  
- Recap modules Réception / Paheko réaligné : [2026-05-21_02_recap-idees-paheko-reception-terrain.md](2026-05-21_02_recap-idees-paheko-reception-terrain.md) (section 0 + journal §10).
