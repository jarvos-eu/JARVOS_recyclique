# Versioning — JARVOS Recyclique

Convention de versions et tags Git. Peut evoluer selon BMAD ou les besoins du projet.

---

## Contexte

- **Ancien repo (archive)** : Recyclique **v1.4.4** — une ressourcerie test, code a refactorer.
- **Ce repo** : JARVOS Recyclique — refonte complete, nouveau backend.

---

## Usage pour les agents et le developpement

**A lire en premier.** Les numéros de version (v0.1.0, v0.2.0, etc.) **ne pilotent pas** le développement : ils ne définissent pas l'ordre des epics ni des stories. La planification et la priorisation se font **uniquement** via les **epics et stories** (`_bmad-output/planning-artifacts/epics.md`). La **seule cible de livraison** à prendre en compte pour le travail courant est la **première version en production** (objectif « v1.0 » : parité 1.4.4 + sync, sans rupture). Le tableau « Convention de tags » ci-dessous est une **référence optionnelle** pour des tags Git / releases GitHub ; créer un tag est à la discrétion de Strophe et n'est pas requis pour avancer. Dans les documents (PRD, epics), les mentions « v0.1 », « v0.2+ », « v1 » dans les FR ou les stories désignent des **phases ou périmètres** (ex. phase initiale, phase ultérieure, première prod), **pas** des numéros de release à respecter à la lettre.

---

## Convention de tags (releases)

Le tableau ci-dessous peut servir de repère pour des tags optionnels ; il **ne constitue pas un plan de livraison** à suivre.

| Version   | Objectif |
|-----------|----------|
| **v0.1.0** | Socle Docker Paheko + API stub FastAPI |
| **v0.2.0** | Vertical slice caisse/ventes fonctionnel |
| **v0.3.0** | Reception fonctionnelle |
| **v0.4.0** | Auth + users + admin |
| **v0.5.0** | Eco-organismes |
| **v1.0.0** | Deploye en prod chez La Clique, stable |

Tags Git : `v0.1.0`, `v0.2.0`, etc. (semver). Ne pas creer de tag sans validation de Strophe.
