# 07 — Configuration & Secrets Management
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Configuration Validation Model
All application configuration is validated at process startup using Pydantic Settings (`backend/app/core/config.py`). Startup fails immediately if:
- Production environment (`ENVIRONMENT=production`) has `DEBUG=True`.
- Production environment uses insecure session cookies (`SESSION_COOKIE_SECURE=False`).
- Secret keys (`SECRET_KEY`, `JWT_SECRET`) use default/insecure sample values.
- `STORAGE_BACKEND` is not one of `local` or `s3`.
- `REDIS_ENABLED=True` but `REDIS_URL` is empty.

## 2. Secret Redaction Policy (ARC11-I07)
Sensitive attributes (database passwords, JWT secrets, S3 secret access keys) implement custom `__repr__` and `__str__` masking, emitting `***` to guarantee credentials are never exposed in log aggregators or tracebacks.\n