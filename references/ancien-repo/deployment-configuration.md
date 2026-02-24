# Configuration déploiement — RecyClique 1.4.4 (référence migration)

---

## Stack actuelle (README + docs/architecture)

- **Runtime :** Docker Compose sur VPS.
- **Services :** API (port 4433), Frontend (4444), Bot (polling). PostgreSQL et Redis en conteneurs.
- **Reverse proxy :** Nginx (mentionné).
- **Environnements :** Dev local (ports ci-dessus), staging/prod à configurer.

---

## Stratégie (docs/architecture/9)

- Déploiement : rolling deployment avec feature flags.
- Rollback : feature flags + rollback migrations BDD. Procédures dans `docs/runbooks/`, `docs/rollback-test-guide.md`.
- Sauvegarde : scripts PostgreSQL (backup, compression, chiffrement), cron/Docker. Détails dans `docs/architecture/9-infrastructure-et-dploiement.md`.

---

## CI/CD

- `.github/workflows/` (ex. `alembic-check.yml`). Scripts dans `scripts/` : deploy-staging, deploy-prod, deploy-local, pre-deployment-check, rollback, etc.

Pour la v0.1.0 : reprendre les besoins (sauvegarde, rollback, feature flags) et les réimplémenter dans le nouveau pipeline et infra.
