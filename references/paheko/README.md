# Paheko — Référence pour JARVOS Recyclique

Ce dossier sert de **guide et référence** pour Paheko (gestion d'association : compta, membres, site web, bénévolat), futur backend / intégration envisagée pour RecyClique (voir migration-paeco).

---

## Source officielle et miroir

- **Forge officielle** : [Fossil](https://fossil.kd2.org/paheko) — `https://fossil.kd2.org/paheko` (développement principal, PHP, SQLite).
- **Miroir Git** : [GitHub paheko/paheko](https://github.com/paheko/paheko) — pour cloner en Git sans installer Fossil.

---

## Récupérer le code (clone local)

Le dossier `repo/` contient un clone du code source (pour analyse, doc, intégration). Il est **gitignore** — le clone reste local.

**Avec Git (recommandé, miroir à jour) :**

```bash
# Depuis la racine du projet JARVOS Recyclique
git clone https://github.com/paheko/paheko.git references/paheko/repo/
```

**Avec Fossil (source officielle) :**

Si Fossil est installé : `fossil clone https://fossil.kd2.org/paheko paheko.fossil` puis `fossil open paheko.fossil` dans un répertoire de travail. Pour rester cohérent avec le reste du projet, le clone Git dans `repo/` suffit.

---

## Documentation Paheko

- **Site / doc** : [fossil.kd2.org/paheko](https://fossil.kd2.org/paheko) → Wiki → Documentation (installation, configuration, extensions, doc développeur).
- **Aide utilisateur** : [paheko.cloud/aide](https://paheko.cloud/aide).
- **Essai gratuit** : [Paheko.cloud](https://paheko.cloud/).

---

## Utilisation pour JARVOS Recyclique

- Analyser l’API, les extensions et le modèle de données pour l’intégration RecyClique / Paheko.
- Croiser avec les documents dans **references/migration-paeco/** (guides, TODO, CR réunions).
