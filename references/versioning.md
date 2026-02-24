# Versioning — JARVOS Recyclique

Convention de versions et tags Git. Peut evoluer selon BMAD ou les besoins du projet.

---

## Contexte

- **Ancien repo (archive)** : Recyclique **v1.4.4** — une ressourcerie test, code a refactorer.
- **Ce repo** : JARVOS Recyclique — demarre en **v0.1.0**, refonte complete, nouveau backend.

---

## Convention de tags (releases)

| Version   | Objectif |
|-----------|----------|
| **v0.1.0** | Socle Docker Paheko + API stub FastAPI |
| **v0.2.0** | Vertical slice caisse/ventes fonctionnel |
| **v0.3.0** | Reception fonctionnelle |
| **v0.4.0** | Auth + users + admin |
| **v0.5.0** | Eco-organismes |
| **v1.0.0** | Deploye en prod chez La Clique, stable |

Tags Git : `v0.1.0`, `v0.2.0`, etc. (semver). Ne pas creer de tag sans validation de Strophe.
