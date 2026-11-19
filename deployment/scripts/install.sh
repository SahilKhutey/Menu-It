#!/usr/bin/env bash
set -e

echo "=== ModularMenu Customer-Hosted Installation ==="

if ! command -v docker &> /dev/null; then
    echo "Error: Docker is required but not installed. Please install Docker first."
    exit 1
fi

if [ ! -f .env ]; then
    echo "Creating .env configuration from .env.example..."
    cp .env.example .env
    # Generate high-entropy secret key
    SECRET=$(openssl rand -hex 32)
    sed -i "s/change_this_to_a_random_64_character_hex_string/$SECRET/" .env
    echo ".env generated with a secure random SECRET_KEY."
fi

echo "Starting ModularMenu Docker services..."
docker compose up -d

echo "Running database schema migrations..."
docker compose exec backend alembic upgrade head

echo "=== Installation Complete! ==="
echo "Access customer menu at: http://localhost:3000"
echo "API docs available at:   http://localhost:8000/docs"
