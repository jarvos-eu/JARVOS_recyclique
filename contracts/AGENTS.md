# AGENTS — contracts

## Purpose

Artefacts **versionnés** partagés entre **recyclique/api** et **peintre-nano** : contrat HTTP OpenAPI (Piste B) et schémas **CREOS** (manifests, widgets). Point d’ancrage pour éviter la dérive front/back.

**Parents :** lire [`../AGENTS.md`](../AGENTS.md) puis ce fichier avant toute édition.

## Ownership

- **Strophe** — décisions HITL gouvernance (périmètre reviewable vs démo, renommages `operationId`, semver draft).
- **Agents** — maintenir YAML + `generated/` cohérents, refs CREOS `data_contract.operation_id` alignées.

## Local contracts

| Zone | Rôle |
|------|------|
| `openapi/recyclique-api.yaml` | Source reviewable API v2 — `operationId` **stables** ; writer Recyclique |
| `openapi/generated/recyclique-api.ts` | Types TS (`paths`, `components`) — **versionné**, régénéré après chaque évolution YAML |
| `creos/schemas/` | JSON Schema manifests / extensions widgets |
| `creos/manifests/` | Lots reviewables (navigation, pages, catalogues widgets) |

**Gouvernance normative :** [`references/artefacts/2026-04-02_04_gouvernance-contractuelle-openapi-creos-contextenvelope.md`](../references/artefacts/2026-04-02_04_gouvernance-contractuelle-openapi-creos-contextenvelope.md) (§0, §2.3 HITL, procédure B4 ruptures).

- **`info.version` draft (`0.x.y-draft`) :** patch = corrections doc ; minor = ajouts rétro-compatibles ; major / `1.0.0` ou rupture schéma → procédure B4 (refs CREOS, tests, doc).
- **Renommage `operationId` déjà référencé :** co-mettre à jour refs + tests + doc **ou** ligne dans le journal du [`README.md`](README.md).
- **Manifests démo Epic 3 :** restent sous `peintre-nano/public/manifests/` et `src/fixtures/manifests/` — ne pas confondre avec lots reviewables `creos/manifests/`.

## Work guidance

- Détail zones et bandeau live / Epic 4 : [`README.md`](README.md).
- Architecture boundaries : [`_bmad-output/planning-artifacts/architecture/project-structure-boundaries.md`](../_bmad-output/planning-artifacts/architecture/project-structure-boundaries.md).
- Flux typique évolution API :
  1. Modifier `openapi/recyclique-api.yaml`
  2. Régénérer TS (ci-dessous)
  3. Implémenter route côté `recyclique/api`
  4. Consommer types côté `peintre-nano`
  5. Mettre à jour manifests CREOS si `data_contract.operation_id` change
- Ne pas dupliquer le pivot gouvernance dans ce fichier — le citer.

## Verification

**Codegen TypeScript (obligatoire après changement YAML) :**

```bash
cd contracts/openapi
npm install          # première fois ou dépendances changées
npm run generate     # → openapi/generated/recyclique-api.ts
```

Contrôler le diff `generated/` dans la PR. Valider côté consommateurs :

```bash
cd peintre-nano && npm run lint && npm run test
cd recyclique/api && python -m pytest tests/test_infrastructure.py   # + tests ciblés route
```

Pas de push sans OK Strophe ([`references/procedure-git-cursor.md`](../references/procedure-git-cursor.md)).
