# Exemples — skill interroger-eco-organismes

## Cas 1 — Ecologic T2 2026 DEC_REE (session 07–14/07/2026)

**Template :** 9 lignes DEC_REE · avril–juin 2026

| Code | Agent auto | Retour CLIC | Retenu final |
|------|------------|-------------|--------------|
| PAM | 0,270 t | OK | 0,270 t |
| ECR | 0,032 t | OK | 0,032 t |
| GHF | 0,060 t | OK | 0,060 t |
| GEF | 0,063 t | OK | 0,063 t |
| ASL-CAT1 | 0,100 t | **0,055 t** | 0,055 t |
| ASL-CAT2 | 0,036 t | **0,081 t** | 0,081 t |
| ABJ-TONA | 0 | OK | 0 |
| ABJ-TONM | 1 pc | OK **0,010 t** | 0,010 t |
| ABJ-AUT | 0 | — | 0 |

**Artefacts :** `references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/`

---

## Cas 2 — Golden test T1 PAM DEC_REE

Requête template :

```csv
id;partenaire;flux;code;date_debut;date_fin;unite;exclure_recyclage
GOLDEN-T1-PAM;ecologic;DEC_REE;PAM;2026-01-01;2026-03-31;t;non
```

**Attendu :** `0,184` t (pro forma T1). Écart si `exclure_recyclage=oui` → ~0,180 t (1 ligne recyclage 4 kg).

---

## Cas 3 — Dump insuffisant

Template avec `date_fin=2026-09-30` et dump du `2026-07-07` :

→ Statut `dump_insuffisant` · message : demander export frais dans `references/_depot/`

---

## Commande type

```bash
python .cursor/skills/interroger-eco-organismes/scripts/interroger_eco_org.py \
  --template references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/templates/interrogation-ecologic-T2-DEC_REE.csv \
  --output references/eco-organismes/partenaires/ecologic/declarations-la-clique/2026-T2/interrogation-ecologic-T2-DEC_REE_rempli.csv \
  --save-sql log/cursor-agent/eco-org-T2-queries.sql
```
