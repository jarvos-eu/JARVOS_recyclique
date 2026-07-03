# Signaux projet — jarmes-ecosystem

Projections synthétiques pour consolidation Mentor (`jarmes-cockpit/global-bmad/`).

| Fichier | Publisher | Amont |
|---------|-----------|-------|
| `project-program-signal.json` | Ariane | `docs/programme/JARMES_REPRISE.md` |
| `project-memory-signal.json` | Clio | `REPRISE.md` |

**Ne pas** traiter ces JSON comme source de vérité — lire les amont.

## Cascade signaux → global

1. **Projet** : Clio / Ariane maintiennent `REPRISE.md` et `docs/programme/JARMES_REPRISE.md`.
2. **Signaux** : mise à jour des JSON en fin de session utile (projection, pas SoT).
3. **Global** : Mentor consolide vers `jarmes-cockpit/global-bmad/` — **ne pas** écrire directement dans le sanctum global depuis le conteneur.

Schema : `schema.signal.v0.1.json` (copie pattern bridge)
