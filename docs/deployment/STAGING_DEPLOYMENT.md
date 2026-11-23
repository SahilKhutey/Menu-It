# Staging Deployment Guide
**ModularMenu Operational Documentation**

## 1. Scope
Pre-production staging cluster mirroring Managed SaaS production settings (Profile C).

## 2. Deployment Procedure
```bash
# 1. Verify release candidate tag
git checkout tags/v1.0.0-rc1

# 2. Run preflight environment checks
bash infrastructure/scripts/preflight.sh

# 3. Create pre-migration database snapshot
bash infrastructure/scripts/backup-postgres.sh

# 4. Execute database migrations
bash infrastructure/scripts/migrate.sh

# 5. Deploy production compose stack
docker compose -f compose.yaml -f infrastructure/compose/compose.production.yaml pull
docker compose -f compose.yaml -f infrastructure/compose/compose.production.yaml up -d

# 6. Run automated smoke tests
bash infrastructure/scripts/smoke-test.sh
```\n