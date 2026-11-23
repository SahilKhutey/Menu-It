# 22 — Migration & Upgrade Strategy
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Customer-Hosted Upgrade Lifecycle
1. Pull new container release images: `docker compose pull`.
2. Execute automated preflight checks: `bash infrastructure/scripts/preflight.sh`.
3. Create pre-migration database snapshot: `bash infrastructure/scripts/backup-postgres.sh`.
4. Apply database migrations: `bash infrastructure/scripts/migrate.sh`.
5. Restart services with rolling zero downtime: `docker compose up -d --remove-orphans`.
6. Run smoke verification suite: `bash infrastructure/scripts/smoke-test.sh`.\n