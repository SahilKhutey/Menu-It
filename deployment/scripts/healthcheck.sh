#!/usr/bin/env bash
set -e

echo "=== ModularMenu System Health Inspection ==="

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "DOWN")

if [ "$HTTP_STATUS" == "200" ]; then
    echo "Backend API: Healthy (HTTP 200)"
    curl -s http://localhost:8000/health
    echo ""
else
    echo "Backend API: Failed or unreachable (Status: $HTTP_STATUS)"
    exit 1
fi

WEB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "DOWN")
if [ "$WEB_STATUS" == "200" ]; then
    echo "Frontend Web: Healthy (HTTP 200)"
else
    echo "Frontend Web: Status $WEB_STATUS"
fi
