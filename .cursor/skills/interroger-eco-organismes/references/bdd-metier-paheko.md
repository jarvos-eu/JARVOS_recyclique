# Paheko — frontière (pas une source de volumes éco-organismes)

> **Décision 2026-08-18 (Strophe) :** Paheko = **compta en euros** uniquement.  
> Poids, caisse métier, dépôts, DEC_REE / LIV / RECYCLAGE = **Recyclique**.  
> Voir [bdd-metier.md](bdd-metier.md).

Les extensions Paheko **Saisie au poids** (`saisie_poids`) et **Caisse** (`plugin_pos_*`) sont **hors périmètre** et vont être **désinstallées**. Ne pas les activer, ne pas les interroger pour une déclaration.

---

## Qui interroge quoi

| Question | Où |
|----------|----|
| Volumes filière, tickets, ventes au poids, benne | Recyclique — skill `interroger-eco-organismes` |
| Écritures, exercices, bilan, compte de résultat, notes de frais | Dump Paheko SQLite (`acc_*`, `module_data_expenses_claims`) |
| Factures éco-organismes scannées (PDF) | Fichiers joints Paheko (`files`) — pièces comptables, **pas** des agrégats kg/t |

`--source paheko` et `--compare` dans `interroger_eco_org.py` sont **refusés** (statut `hors_perimetre`).

---

## Dump 2026-08-18 (L'Eco de la Clique)

| | |
|--|--|
| Fichier | `references/_depot/L'Eco de la Clique - Sauvegarde données - PAHEKO - 2026-08-18.sqlite` |
| Taille | ~54 Mo |
| Paheko | 1.3.22.1 |
| Exercices | 2025 (clos, 2025-07-04 → 2025-12-31) · 2026 (ouvert) |
| Écritures | 216 · 2025-07-22 → 2026-05-31 |

| Extension | État | Attendu |
|-----------|------|---------|
| Module `saisie_poids` | présent, **désactivé**, pas de table `module_data_saisie_poids` | **à désinstaller** |
| Plugin Caisse | **absent** (0 plugin) | **ne pas installer** |
| Notes de frais | `module_data_expenses_claims` (21 docs) | OK (compta) |

Ce dump est **cohérent** avec le périmètre euros : pas de volumes à extraire ici.

Vérif lisibilité (pas pour décla) :

```bash
python .cursor/skills/interroger-eco-organismes/scripts/check_paheko_dump.py
```

Si Saisie au poids ou Caisse réapparaissent : **alerte** (désinstallation incomplète), pas une invitation à agréger.

---

## Audits historiques (ne plus suivre pour les décla)

Les audits `references/migration-paheko/audits/audit-saisie-au-poids-paheko.md` et `audit-caisse-paheko.md` décrivent le **module Paheko générique** (2026-02). Ils ne justifient plus d'importer des poids depuis Paheko pour La Clique.

Schéma compta Paheko : `references/dumps/schema-paheko-dev.md` (§ `acc_*`).
