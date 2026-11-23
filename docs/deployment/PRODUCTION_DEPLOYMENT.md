# Production Deployment Guide (Managed SaaS)
**ModularMenu Operational Documentation**

## 1. Prerequisites & Approvals
- Release branch approved by Technical Lead.
- CI/CD quality gates passing (738/738 tests).
- Change Advisory Board (CAB) ticket logged for scheduled maintenance window.

## 2. Execution Procedure
```bash
# Step 1: Preflight Verification
export RELEASE_TAG="v1.0.0"
bash infrastructure/scripts/preflight.sh

# Step 2: Full Database & Media Backup
bash infrastructure/scripts/backup-postgres.sh
bash infrastructure/scripts/verify-storage.sh

# Step 3: Expand Database Schema (Zero Downtime)
bash infrastructure/scripts/migrate.sh

# Step 4: Rolling Container Deployment
docker compose -f compose.yaml -f infrastructure/compose/compose.production.yaml pull
docker compose -f compose.yaml -f infrastructure/compose/compose.production.yaml up -d --no-deps backend worker frontend

# Step 5: Smoke Testing
bash infrastructure/scripts/smoke-test.sh

# Step 6: Post-Deployment Verification
bash infrastructure/scripts/verify-release.sh
```\n