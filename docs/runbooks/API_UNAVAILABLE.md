# Runbook: API Unavailable (HTTP 502/503/504)
**ModularMenu Emergency Runbook**

## 1. Symptoms
- Web frontend displays "Unable to reach server".
- Health probes return HTTP 502 Bad Gateway or 503 Service Unavailable.

## 2. Diagnostic Steps
```bash
# 1. Check if backend container is running
docker compose ps backend

# 2. Inspect backend logs for crash stack traces
docker compose logs --tail=100 backend

# 3. Test backend liveness directly
docker compose exec backend curl -s http://127.0.0.1:8000/health/live
```

## 3. Remediation
```bash
# Restart backend container gracefully
docker compose restart backend

# If memory exhausted, scale resources or restart compose stack
docker compose down && docker compose up -d
```\n