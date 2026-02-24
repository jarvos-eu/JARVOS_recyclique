# Inventaire des composants UI — RecyClique 1.4.4 (part: frontend)

**Stack :** React 18, TypeScript, Mantine, Zustand, React Query. **Build :** Vite.

---

## Structure des composants (référence migration)

- **`components/ui/`** — Composants génériques : Button, Input, Modal, Numpad, NumericKeypad, StepIndicator, SessionStatusBanner.
- **`components/layout/`** — PageLayout, Heading.
- **`components/tickets/`** — TicketScroller, TicketHighlighter (réception / dépôts).
- **`components/presets/`** — PresetButtonGrid, PriceCalculator (caisse).
- **`components/categories/`** — EnhancedCategorySelector, CategoryDisplayManager (catégories EEE).
- **`components/business/`** — Logique métier : CashRegister, SaleWizard, FinalizationScreen, UserListTable, UserDetailView, UserProfileTab, UserHistoryTab, PendingUsersTable, SiteForm, RoleSelector, ReceptionKPIBanner, CashKPIBanner, TicketDisplay, AdminLayout, etc.

---

## State (Zustand) et données

- Stores par domaine (à identifier dans `frontend/src` : stores/ ou équivalent).
- React Query pour les appels API (cache, mutations).

---

## Utile pour la migration

- Réutiliser les **patterns** (wizard caisse, réception, admin) et la **structure** (ui vs business).
- Les **composants Mantine** peuvent être conservés ou remplacés selon la stack cible v0.1.0.
- Tester les composants listés dans `frontend/src/test` et `*.test.tsx` pour repérer les contrats et comportements à préserver.
