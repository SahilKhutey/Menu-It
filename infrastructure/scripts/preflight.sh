#!/usr/bin/env bash
# ModularMenu — Infrastructure Preflight Verification (ARC-11 §14.4)
set -euo pipefail

echo "=== ModularMenu Preflight Check ==="

# 1. Docker Engine verification
if ! command -v docker &> /dev/null; then
    echo "ERROR: docker command not found. Please install Docker Engine 24.0+."
    exit 1
fi
DOCKER_VERSION=$(docker --version)
echo "✓ Docker: $DOCKER_VERSION"

# 2. Docker Compose verification
if ! docker compose version &> /dev/null; then
    echo "ERROR: docker compose plugin not found."
    exit 1
fi
COMPOSE_VERSION=$(docker compose version)
echo "✓ Docker Compose: $COMPOSE_VERSION"

# 3. Available disk space (min 10 GB)
FREE_DISK_KB=$(df -k . | awk 'NR==2 {print $4}')
FREE_DISK_GB=$((FREE_DISK_KB / 1024 / 1024))
if [ "$FREE_DISK_GB" -lt 10 ]; then
    echo "WARNING: Less than 10GB free disk space available ($FREE_DISK_GB GB detected)."
else
    echo "✓ Disk space: $FREE_DISK_GB GB available"
fi

# 4. Port availability check (80, 443)
for PORT in 80 443; do
    if command -v nc &> /dev/null; then
        if nc -z 127.0.0.1 "$PORT" 2>/dev/null; then
            echo "WARNING: Port $PORT is already in use on localhost."
        fi
    fi
done

echo "✓ Preflight checks completed successfully."
exit 0
