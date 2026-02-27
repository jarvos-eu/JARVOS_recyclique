# Story 8.7 — Écrans ou placeholders « vie associative » dans RecyClique

- **Epic:** epic-8 (Administration, compta v1 et vie associative)
- **Story_key:** 8-7-ecrans-ou-placeholders-vie-associative-dans-recyclique
- **FR:** FR21

---

## User story

En tant qu'utilisateur (ex. bénévole),
je veux accéder à des écrans ou placeholders « vie associative » depuis RecyClique,
afin d'avoir un point d'entrée unique sans ouvrir Paheko.

---

## Critères d'acceptation

- **Étant donné** un utilisateur connecté avec accès vie asso,
- **Quand** je navigue vers la section vie associative,
- **Alors** des écrans ou placeholders sont affichés (FR21) ; le parcours complet sera déroulé en growth.

### Détails

- **Accès vie associative :** l'entrée de menu / navigation « Vie associative » est visible pour les utilisateurs ayant le droit d'accès (permission ou rôle à définir selon le modèle existant ; alignement avec les autres sections admin ou bénévole).
- **Section affichée :** au moins une route dédiée (ex. `/vie-associative` ou `/admin/vie-associative`) avec un écran ou un placeholder (texte explicatif, liens futurs, ou structure de page vide prête pour le growth).
- **FR21 :** « Un utilisateur peut accéder à des écrans ou placeholders « vie associative » depuis RecyClique. »

---

## Tasks

### Frontend

1. **Navigation et entrée « Vie associative »**
   - Ajouter une entrée « Vie associative » dans le menu / la navigation (sidebar ou header) pour les utilisateurs autorisés.
   - Contrôle d'accès : afficher l'entrée uniquement si l'utilisateur a le droit « accès vie asso » (permission ou groupe à aligner avec le RBAC existant — Epic 3).

2. **Route et écran / placeholder**
   - Créer la route (ex. `/vie-associative` ou `/admin/vie-associative`) et le composant associé.
   - Afficher un écran ou un placeholder (titre « Vie associative », court texte explicatif, éventuellement liens ou zones prévues pour le growth ; pas de fonctionnalité complète requise en v1).

### Backend (si nécessaire)

3. **Permission / accès**
   - Si une permission dédiée « vie_associative » ou « accès vie asso » est requise : l'ajouter au seed des permissions (alembic) et l'associer aux groupes appropriés (ex. bénévoles, admin). Sinon, réutiliser une permission existante et la documenter ici.

---

## Références

- **Epic 8, Story 8.7 :** `_bmad-output/planning-artifacts/epics.md`
- **FR21 :** `_bmad-output/planning-artifacts/epics.md` ; `_bmad-output/planning-artifacts/prd.md` (§ Vie associative v1 placeholders)
- **Architecture et conventions :** `_bmad-output/planning-artifacts/architecture.md` ; `references/artefacts/2026-02-26_03_checklist-v0.1-architecture.md`
- **Sprint status :** `_bmad-output/implementation-artifacts/sprint-status.yaml`

---

## Conventions d'implémentation

- **UI / styling :** Mantine (alignement 1.4.4).
- **Layout :** intégrer la section dans le layout existant (navigation cohérente avec admin ou app selon le choix produit).
- **Tests frontend :** Vitest + React Testing Library + jsdom ; tests co-locés `*.test.tsx` pour la route et la visibilité conditionnelle de l'entrée menu.
- **Backend :** si permission dédiée, respecter les conventions alembic seed et RBAC (Epic 3).

---

## Dev Agent Record

### Status

done

### Completion Notes

Story créée depuis epics.md (Story 8.7). Périmètre v1 : accès et affichage section vie associative + placeholders ; parcours complet reporté en growth.

Implémentation 2026-02-27 : entrée menu « Vie associative » (permission admin ou vie_asso.access), route /admin/vie-associative, page placeholder Mantine, VieAssociativeGuard (admin ou vie_asso.access), tests co-locés VieAssociativeGuard.test.tsx, AdminVieAssociativePage.test.tsx, AppNav.test.tsx. Permission backend : vie_asso.access déjà présente dans le seed (groupe benevole).

Code review 2026-02-27 : approved. Vérifié entrée menu (permissionCodes), route /admin/vie-associative, page Mantine, garde, tests. review.json : 8-7-ecrans-ou-placeholders-vie-associative-dans-recyclique.review.json.
