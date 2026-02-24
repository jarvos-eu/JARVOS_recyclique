# Nouvelles UI workflows Paheko

---

## 2026-02-24 — Mary (brainstorm migration)

Nouvelles interfaces Recyclic pour workflows terrain via Paheko (routines ressourcerie). Paheko natif accessible en mode super-admin. A concevoir en fonction des besoins terrain.

Intention : a-conceptualiser

---

## 2026-02-24 — Pattern technique pose (session modules/plugins — Mary)

Pattern retenu pour les UI de modules dans `references/artefacts/2026-02-24_07_design-systeme-modules.md` :
- Chaque module Paheko a ses propres routes React (`/modules/paheko/*`) avec lazy loading.
- Extension de l'UI existante via slots (`<ModuleSlot />`) — inspire des snippets Paheko (module.ini + snippets/).
- Paheko natif reste accessible en mode super-admin (URL directe), pas reimplemente cote Recyclic.

Les workflows terrain concrets (quelles routines, quelles interfaces) restent a definir selon les besoins metier reels. Garder en a-conceptualiser.
