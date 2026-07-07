# Feedback La Clique — dashboard stats & déclarations éco-organismes

**Date :** 2026-07-05  
**Source :** message utilisatrice ressourcerie pilote **La Clique Qui Recycle** (transmis par Strophe)  
**Contexte :** préparation des déclarations aux éco-organismes ; module décla v2 (**story 9.1**) pas encore livré — besoin cible **prochain socle V2**.

**Volume :** **3** besoins indexés (préfixe addendum **LCQ-** = La Clique Qui Recycle / stats dashboard).

**Lecture :** retour terrain spontané, pas de décision gelée. Matière produit pour **Epic 5** (dashboard) et/ou **Epic 9** (éco-organismes).

**Fiche kanban :** [`docs/ideas/kanban/IDEA-2026-07-05-001.md`](../../docs/ideas/kanban/IDEA-2026-07-05-001.md)

---

## Verbatim

> Je suis en train de faire les déclarations aux éco-organismes et j'ai vraiment hâte qu'on puisse avoir sur le dashboard de Recyclique le détail des sous-catégories pour les réceptions et les sorties. Et que les sorties puissent distinguer les ventes/dons de ce qui part au recyclage… Ça changera ma vie!!!

---

## 1. Cartographie LCQ-001…003

| ID addendum | Énoncé court | Lien existant |
|-------------|--------------|---------------|
| **LCQ-001** | Dashboard réceptions : détail par **sous-catégorie** (pas seulement parent) | Story **5.2** done — agrégation parent uniquement ; legacy B50-P5 idem |
| **LCQ-002** | Dashboard sorties : détail par **sous-catégorie** | Idem ; export B50-P1 explicitement sans sous-catégories |
| **LCQ-003** | Sorties : distinguer **ventes / dons / recyclage** (matière sortante) | Réception : champs `destination`, `is_exit` en saisie — **absents** des graphiques dashboard ; presets Don/Recyclage post-v2 dans `references/todo.md` |

---

## 2. Par chantier produit

### Dashboard stats (Epic 5 — candidat stories post-5.2)

1. **LCQ-001 + LCQ-002** — endpoints et widgets drill-down sous-catégories (réceptions + sorties).
2. **LCQ-003** — segmentation des sorties par nature de flux (vente caisse vs don matière vs recyclage/déchèterie).

### Module éco-organismes (Epic 9 — story 9.1 backlog)

- Les agrégats **LCQ-001…003** alimentent la préparation des déclarations (mapping catégories boutique → catégories officielles par éco-organisme).
- Vision : [`references/vision-projet/vision-module-decla-eco-organismes.md`](../vision-projet/vision-module-decla-eco-organismes.md)
- Pack brownfield : `recyclique-1.4.4/docs/eco-organismes/`

---

## 3. Écart constaté (juillet 2026)

| Capacité | Saisie terrain | Dashboard v2 |
|----------|----------------|--------------|
| Catégorie / sous-catégorie | Oui | Parent uniquement |
| Destination recyclage / déchèterie | Oui (`destination`) | Non exposé |
| Sortie matière vs entrée | Oui (`is_exit`) | Sorties = ventes caisse (`/stats/sales/by-category`) |

---

## 4. Questions ouvertes

| Question | Note |
|----------|------|
| Dashboard seul ou aussi exports admin / décla ? | L'utilisatrice parle du **dashboard** ; exports décla pourraient réutiliser les mêmes agrégats |
| « Dons » = don caisse (gratuité) ou don matière en sortie réception ? | À clarifier en cadrage — les deux existent métier |
| Périmètre V2 minimal | Sous-catégories + 3-way split sorties semble le cœur du retour |

---

## 5. Suite recommandée

1. Conserver cette fiche + **IDEA-2026-07-05-001** jusqu'à cadrage PO.
2. Si validé en beta : item(s) **REV-*** dans `references/revision/` (domaine stats ou admin).
3. Promotion BMAD : story(s) Epic **5** et/ou enrichissement **9.1** — **sans modifier le PRD** hors process BMAD.
