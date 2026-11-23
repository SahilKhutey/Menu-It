# Runbook: Redis Cache Failure & Degradation
**ModularMenu Emergency Runbook**

## 1. Symptoms
- Redis container crashed or unreachable.
- Warning logs: `Redis unavailable, falling back to in-memory bypass`.

## 2. Diagnostic Steps
```bash
docker compose ps redis
docker compose logs --tail=50 redis
```

## 3. Remediation
- ModularMenu is architected for safe degradation (ARC11-I03). Core flows continue without Redis.
- Restart Redis: `docker compose restart redis`.\n