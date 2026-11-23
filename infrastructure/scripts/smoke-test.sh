#!/usr/bin/env bash
# ModularMenu — Post-Deployment Smoke Test (ARC-11 §13.3)
set -euo pipefail

TARGET_URL="${1:-http://localhost:8000}"
FRONTEND_URL="${2:-http://localhost:3000}"

echo "=== Running ModularMenu Smoke Tests ==="

# 1. Check Backend Liveness
LIVE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET_URL/api/v1/health/live" || echo "000")
if [ "$LIVE_STATUS" != "200" ]; then
    echo "ERROR: Backend liveness probe failed (HTTP $LIVE_STATUS)"
    exit 1
fi
echo "✓ Backend /health/live returned 200 OK"

# 2. Check Backend Readiness
READY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET_URL/api/v1/health/ready" || echo "000")
if [ "$READY_STATUS" != "200" ]; then
    echo "ERROR: Backend readiness probe failed (HTTP $READY_STATUS)"
    exit 1
fi
echo "✓ Backend /health/ready returned 200 OK"

# 3. Check Frontend Home or Health
FE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/" || echo "000")
if [ "$FE_STATUS" != "200" ] && [ "$FE_STATUS" != "304" ]; then
    echo "WARNING: Frontend returned HTTP $FE_STATUS"
else
    echo "✓ Frontend root returned HTTP $FE_STATUS"
fi

echo "=== All Smoke Tests Passed ==="
exit 0
