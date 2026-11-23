# Customer-Hosted Upgrade Guide
**ModularMenu Operational Documentation**

## 1. Upgrade Preflight
Ensure >= 10 GB disk space is free for pre-upgrade snapshots.

## 2. Upgrade Workflow
```bash
cd /opt/modularmenu

# 1. Create safety backup
bash infrastructure/scripts/backup-postgres.sh

# 2. Pull updated release images
docker compose -f compose.customer-hosted.yaml pull

# 3. Apply database migrations
docker compose -f compose.customer-hosted.yaml run --rm backend alembic upgrade head

# 4. Restart containers with zero downtime
docker compose -f compose.customer-hosted.yaml up -d --remove-orphans

# 5. Run smoke verification
bash infrastructure/scripts/smoke-test.sh
```\n