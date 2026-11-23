# 11 — Observability & Health Probing
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Triple Health Probe Model (ARC11-I12)
- `/health/live`: Liveness probe indicating process responsiveness (returns 200 OK).
- `/health/ready`: Readiness probe verifying downstream connectivity (PostgreSQL query, optional Redis ping).
- `/health/startup`: Startup probe validating environment preflight and schema readiness.

## 2. Error Sanitization (ARC11-I07, ADR-0216)
Health check responses never return raw SQL exception strings, connection URLs, or internal topology details. Failed checks return generic sanitized status: `{"status": "degraded", "database": "unavailable"}` with HTTP 503.\n