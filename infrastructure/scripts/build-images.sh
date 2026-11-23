#!/usr/bin/env bash
# ModularMenu — Immutable Container Image Builder (ARC-11 §6.1, §12.4)
set -euo pipefail

RELEASE="${1:-1.0.0}"
GIT_COMMIT="${2:-$(git rev-parse HEAD 2>/dev/null || echo 'unknown')}"
REGISTRY="${REGISTRY:-ghcr.io/modularmenu}"

echo "=== Building Immutable Images for Release: $RELEASE (Commit: $GIT_COMMIT) ==="

# Build Frontend
echo "--> Building Frontend Image..."
docker build \
    --file infrastructure/docker/frontend.Dockerfile \
    --tag "$REGISTRY/modularmenu-frontend:$RELEASE" \
    --tag "$REGISTRY/modularmenu-frontend:$GIT_COMMIT" \
    frontend/

# Build Backend
echo "--> Building Backend Image..."
docker build \
    --file infrastructure/docker/backend.Dockerfile \
    --tag "$REGISTRY/modularmenu-backend:$RELEASE" \
    --tag "$REGISTRY/modularmenu-backend:$GIT_COMMIT" \
    backend/

# Build Worker
echo "--> Building Worker Image..."
docker build \
    --file infrastructure/docker/worker.Dockerfile \
    --tag "$REGISTRY/modularmenu-worker:$RELEASE" \
    --tag "$REGISTRY/modularmenu-worker:$GIT_COMMIT" \
    backend/

echo "=== Images Built Successfully ==="
docker images | grep "$REGISTRY" || true
