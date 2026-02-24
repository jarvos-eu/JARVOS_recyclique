# UI modulaire configurable

---

## 2026-02-24 — Mary (brainstorm migration)

Contrainte d'architecture : UI configurable/modulaire des la conception. Future integration JARVOS Peintre. Pas une feature, un principe a honorer dans tout le front.

Intention : a-conceptualiser

---

## 2026-02-24 — Design arbitre (session modules/plugins — Mary)

Pattern retenu dans `references/artefacts/2026-02-24_07_design-systeme-modules.md` :
- Monorepo React, un seul `vite build`. Pas de Module Federation ni de builds separes.
- Lazy loading par route : `React.lazy(() => import('@/modules/paheko/PahekoApp'))`, charge le module seulement a la navigation.
- Slots UI (`<ModuleSlot name="sale_details" />`) pour injection de composants dans l'app existante — inspire des snippets Paheko.
- `register_ui_extensions()` dans `ModuleBase` : chaque module declare ses slots.

A creuser : implementation concrete du hook React `useModuleExtensions`, registre des slots cote frontend.

Passage a a-creuser.
