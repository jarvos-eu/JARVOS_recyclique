# Synthèse — recherche Liaison Paheko (brainstorm, pas spec dev)

**Date :** 2026-05-21  
**Pour :** Strophe — phase idées avant BMAD  
**Entrées :** [réponse Perplexity](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md), [décisions figées](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md), [répertoire comptes](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md), recap terrain `02`.

---

## En 10 lignes

1. Tu peux **boucler la caisse → Paheko** sans attendre toute la réception.  
2. **Une fermeture par jour** + tickets détaillés gardés dans Recyclique = OK.  
3. **Comptage pièces obligatoire** = module à part, branché sur la fermeture.  
4. Dans Paheko : **plusieurs lignes** (ventes / dons / espèces / chèques), pas un total fourre-tout.  
5. **7070** ventes réemploi, **7541** dons caisse — direction claire.  
6. **Ticket mixte** (habits donnés + payant) : seule la partie **€** part en clôture.  
7. **-18 / kg** : trace dans Recyclique ; **pas** d’écriture Paheko tant que l’EC n’a pas tranché la classe 8.  
8. Le bug « don par défaut » : la v2 caisse suffit — pas un chantier brainstorm.  
9. Prochaine étape pour toi : **synthèse** après tes consultations, puis **atelier parcours fermeture**.  
10. Liste complète des comptes audio/CR : fichier **répertoire comptes** (section 8 = checklist EC).

---

## Ce qui est figé (ne plus rediscuter en brainstorm)

Voir [décisions figées](../migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md) §1–3.

---

## Questions qui restent (pour toi puis EC)

### Après tes consultations (synthèse ½ page)

| # | Question en langage simple |
|---|----------------------------|
| Q1 | On valide **7070** pour toutes les ventes réemploi ? |
| Q2 | Dons caisse : un seul compte **7541** ou on sépare espèces / chèques (**754.11 / 754.115**) ? |
| Q3 | Écart de caisse : quels numéros de compte (**658/758** ou ceux de Paheko **678/778**) ? |
| Q4 | Dans Paheko aujourd’hui : **511 205/210**, **530**, **512** — qu’est-ce qui est déjà créé (avec Carole) ? |
| Q5 | Textiles -18 : on reste **sans écriture Paheko** pour l’instant ? |

### Brainstorm suivant (quand tu veux)

| Atelier | Sujet |
|---------|--------|
| **Fermeture** | Étapes écran : récap → module comptage → écart → envoi Paheko → preuve PDF |
| **Ticket** | Ligne payante / ligne don -18 / gratuité ; ce qui entre dans le récap du soir |

### Pour l’expert-comptable (reprise recherche §8)

Les 8 questions du fichier [réponse Perplexity](../recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md) (fin de document) + checklist [répertoire §8](../migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md).

---

## Où c’est rangé dans le dépôt

| Besoin | Fichier |
|--------|---------|
| Décisions produit figées | `references/migration-paheko/2026-05-21_decisions-compta-liaison-paheko-recherche-terrain.md` |
| Tous les comptes + workflows | `references/migration-paheko/2026-05-21_repertoire-comptes-terrain-audio-recyclique.md` |
| Recherche brute | `references/recherche/2026-05-21_liaison-paheko-caisse-compta-terrain_perplexity_reponse.md` |
| Idées terrain d’origine | `references/artefacts/2026-05-21_02_recap-idees-paheko-reception-terrain.md` |
| Spec technique dev (inchangée) | `references/migration-paheko/2026-04-15_prd-recyclique-caisse-compta-paheko.md` |

---

## Suite BMAD (plus tard)

Quand Q1–Q5 + EC sont répondues : epic « Liaison Paheko v1 » = fermeture + module comptage + paramétrage comptes + outbox Paheko (déjà décrit dans le PRD avril).
