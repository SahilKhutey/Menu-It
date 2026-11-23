# Development Deployment Guide
**ModularMenu Operational Documentation**

## 1. Scope
Covers continuous deployment of the `develop` branch to the persistent development cluster.

## 2. Automated Pipeline
Pushes to `develop` trigger `.github/workflows/quality-gates.yml`:
1. Ruff linting and formatting validation.
2. Architecture boundary validation (`tests/architecture/`).
3. Complete 738-test regression suite.
4. Next.js standalone build verification.

## 3. Manual Deployment Procedure
```bash
# Pull latest code
git checkout develop
git pull origin develop

# Execute preflight checks
bash infrastructure/scripts/preflight.sh

# Build updated images
docker compose -f compose.yaml -f compose.dev.yaml build

# Apply schema migrations
docker compose run --rm backend alembic upgrade head

# Restart containers
docker compose -f compose.yaml -f compose.dev.yaml up -d
```\n