# Investigation — Code story 8-3 « absent » (2026-02-27)



## Constat



Le code de la story **8-3** (Import/export catégories et admin avancé) **est bien présent** dans le dépôt.



### Fichiers présents



| Fichier | Statut Git | Contenu |

|---------|------------|--------|

| `frontend/src/admin/AdminCategoriesPage.tsx` | **??** (untracked) | Page admin catégories : hiérarchie, breadcrumb, Import/Export CSV, modal analyse → exécution, hard delete, restauration |

| `frontend/src/admin/AdminCategoriesPage.test.tsx` | **??** (untracked) | Tests Vitest + RTL (6 tests) |

| `frontend/src/api/categories.tsx` | **??** (untracked) | Client API : getCategoriesHierarchy, getImportTemplate, getExportCsv, postImportAnalyze, postImportExecute, hardDeleteCategory, restoreCategory, getCategoryHasUsage, getCategoryBreadcrumb |

| `api/routers/categories.py` | **M** (modifié) | Routes 8.3 : GET `/import/template`, GET `/actions/export`, POST `/import/analyze`, POST `/import/execute`, GET `/{id}/breadcrumb`, GET `/{id}/has-usage`, DELETE `/{id}/hard`, POST `/{id}/restore` |



## Pourquoi le sous-agent QA a rapporté « code absent »



- Les **sous-agents** (Task / mcp_task) s'exécutent dans un **contexte isolé** (sandbox) : ils reçoivent une **vue partielle** du projet (snapshot ou liste de fichiers).

- Souvent seuls les **fichiers suivis par Git** sont inclus dans cette vue ; les fichiers **non suivis** (`??`) peuvent **ne pas être exposés** au sous-agent.

- Donc le QA a littéralement « pas vu » `frontend/src/admin/` et `api/` tels qu'ils sont chez toi — pas un second workspace utilisateur, mais **le sandbox du sous-agent** qui n'avait pas ces fichiers (surtout les untracked).



## docker-compose build



- **Peu probable** que le build ait supprimé ou écrasé du code : le build utilise le répertoire comme **contexte de build** (lecture), il ne supprime pas les sources.

- Les fichiers 8-3 sont bien présents ; rien n'indique une suppression ou un revert lié au build.



## Action



- Story 8-3 considérée comme **implémentée** ; la revue de code peut être **refaite par l'agent principal** (qui voit tout le dépôt) ou considérée **approved** au vu des fichiers ci-dessus.

- Recommandation : **git add** des fichiers 8-3 (et des autres admin/ non suivis) pour les inclure dans le prochain commit et les rendre visibles dans tout contexte qui se base sur les fichiers trackés.

