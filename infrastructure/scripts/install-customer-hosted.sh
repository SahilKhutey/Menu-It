#!/usr/bin/env bash
# ModularMenu — Customer-Hosted Appliance Installer (ARC-11 §14.4)
set -euo pipefail

ROOT_DIR="${MODULARMENU_HOME:-/opt/modularmenu}"
echo "=== ModularMenu Customer-Hosted Installer ==="
echo "Target Directory: $ROOT_DIR"

mkdir -p "$ROOT_DIR"
mkdir -p "$ROOT_DIR/data"
mkdir -p "$ROOT_DIR/backups"
mkdir -p "$ROOT_DIR/certs"

if [[ ! -f "$ROOT_DIR/.env" ]]; then
    if [[ -f ".env.example" ]]; then
        cp ".env.example" "$ROOT_DIR/.env"
    else
        cat << 'EOF' > "$ROOT_DIR/.env"
APP_ENV=production
APP_NAME=ModularMenu
APP_VERSION=1.0.0
APP_DEBUG=false
FRONTEND_URL=https://menu.yourdomain.com
BACKEND_URL=https://menu.yourdomain.com/api
API_PREFIX=/api/v1
DATABASE_URL=postgresql+asyncpg://modularmenu:changeme_secure_pass@postgres:5432/modularmenu
SECRET_KEY=generate_a_random_32_char_secret_key_here
REDIS_ENABLED=false
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=/app/storage
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax
LOG_LEVEL=INFO
POSTGRES_USER=modularmenu
POSTGRES_PASSWORD=changeme_secure_pass
EOF
    fi
    chmod 600 "$ROOT_DIR/.env"

    echo "=========================================================="
    echo "Created configuration template at: $ROOT_DIR/.env"
    echo "ACTION REQUIRED: Edit secrets and domain before starting!"
    echo "=========================================================="
    exit 1
fi

echo "Configuration file detected at $ROOT_DIR/.env"

# Validate configuration
echo "Validating Docker Compose configuration..."
docker compose \
    -f infrastructure/compose/compose.customer-hosted.yaml \
    config --quiet

echo "Pulling latest immutable container images..."
docker compose \
    -f infrastructure/compose/compose.customer-hosted.yaml \
    pull

echo "✓ Images downloaded and configuration validated."
echo "To start your customer-hosted instance, run:"
echo "  docker compose -f infrastructure/compose/compose.customer-hosted.yaml up -d"
