#!/usr/bin/env bash
# ModularMenu — Production Deployment Coordinator (ARC-11 §13.3)
set -euo pipefail

PROFILE="${1:-profile_c_saas_production}"
COMPOSE_FILE="infrastructure/compose/compose.production.yaml"

if [ "$PROFILE" = "profile_b_customer_hosted" ]; then
    COMPOSE_FILE="infrastructure/compose/compose.customer-hosted.yaml"
fi

echo "=== Deploying ModularMenu Profile: $PROFILE ==="
echo "Using compose definition: $COMPOSE_FILE"

# 1. Validate Compose File
docker compose -f "$COMPOSE_FILE" config --quiet
echo "✓ Compose configuration verified."

# 2. Run Database Migrations before updating services
echo "--> Applying database migrations..."
infrastructure/scripts/migrate.sh

# 3. Pull / Refresh Containers
docker compose -f "$COMPOSE_FILE" pull --quiet || true

# 4. Start Services in proper order
docker compose -f "$COMPOSE_FILE" up -d postgres
echo "Waiting for postgres health..."
docker compose -f "$COMPOSE_FILE" up -d backend worker frontend reverse_proxy

# 5. Run Smoke Tests
echo "--> Running post-deployment smoke tests..."
infrastructure/scripts/smoke-test.sh

echo "=== Deployment Completed Successfully ==="
