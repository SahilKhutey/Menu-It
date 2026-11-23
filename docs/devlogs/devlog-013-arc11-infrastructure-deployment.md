# Devlog 013 — ARC-11 Infrastructure & Deployment Architecture

**Date:** 2026-11-23  
**Author:** AI Architecture Team  
**Subject:** Implementation, Verification, and Release of ARC-11 Infrastructure & Deployment Architecture  
**Release Tag:** `v1.0.0-arc11`  
**Parent Documents:** ARC-01 through ARC-10  

---

## 1. Objectives & Context
ARC-11 establishes how ModularMenu is packaged, containerized, configured, deployed, operated, upgraded, monitored, backed up, and recovered across two distinct deployment models:
1. **Managed SaaS Edition (Multi-Tenant):** Shared PostgreSQL database with Row-Level Security (RLS), distributed S3/MinIO object storage, optional Redis caching and rate-limiting, and automated rolling migrations.
2. **Customer-Hosted Edition (Single-Tenant/Turnkey):** Turnkey appliance or private cloud installation utilizing hardened local filesystem storage (with HMAC signed URLs), optional Redis (with automatic graceful degradation), and self-contained backup routines.

Both deployment models share 100% identical application code, domain entities, database schemas, and API contracts.

---

## 2. Key Engineering Accomplishments

1. **Infrastructure Schemas & Manifests (`infrastructure/schemas/`, `infrastructure/manifests/`):**
   - Implemented JSON schemas: `deployment-profile.schema.json`, `release-manifest.schema.json`, `environment-config.schema.json`.
   - Engineered manifests: `deployment_profiles.yaml`, `environment_variables.yaml`, `service_dependencies.yaml`, `network_ports.yaml`, `image_compatibility.yaml`, `migration_compatibility.yaml`, `backup_policy.yaml`, `resource_requirements.yaml`, `security_requirements.yaml`.

2. **Container Packaging & Multi-Stage Dockerfiles (`infrastructure/docker/`):**
   - `frontend.Dockerfile`: Multi-stage Next.js 14 standalone build running as non-root user `nextjs:nodejs` (`UID 1001, GID 1001`) with curl health checks.
   - `backend.Dockerfile`: Multi-stage Python 3.12 slim Debian build running as non-root user `menuapp:menuapp` (`UID 10001, GID 10001`) with read-only root filesystem support.
   - `worker.Dockerfile`: Shared Python 3.12 runtime executing transactional outbox poller with graceful SIGTERM handling.
   - Root and module `.dockerignore` files created to eliminate secret leaks and artifact bloat.

3. **Docker Compose Profiles & Nginx Proxy (`infrastructure/compose/`, `infrastructure/proxy/`):**
   - Hardened `compose.production.yaml` with `read_only: true`, `cap_drop: [ALL]`, `no-new-privileges: true`, tmpfs `/tmp`, and isolated `data-net` bridge network.
   - Created `compose.customer-hosted.yaml` for offline-capable, single-node appliance deployment.
   - Configured `infrastructure/proxy/nginx.conf` providing TLS 1.2/1.3 termination, HTTP security headers (`nosniff`, `SAMEORIGIN`, `CSP`), API rate limiting (100 req/min), and media routing.

4. **Storage Abstraction & Background Worker (`backend/app/`):**
   - Implemented unified `ObjectStorage` protocol, `S3StorageAdapter`, and hardened `LocalStorageAdapter` (path traversal guard, SHA-256 HMAC-signed URLs).
   - Created `BackgroundWorker` with bounded exponential backoff (max 60s), dead-letter queue (DLQ) transitions, `TenantJobContext` envelope integration, and graceful signal handling.
   - Implemented triple health probes: `/health/live`, `/health/ready`, `/health/startup` in `backend/app/api/v1/health.py`, ensuring zero database credential disclosure on failure.

5. **Operational Tooling & Shell Scripts (`infrastructure/scripts/`):**
   - `preflight.sh`: Validates Docker, disk space (>= 20 GB), and required secrets.
   - `build-images.sh`: Builds and tags versioned, non-root OCI images.
   - `deploy.sh`: Orchestrates rolling container deployment.
   - `migrate.sh`: Executes zero-downtime expand-and-contract migrations with pre-migration backups.
   - `smoke-test.sh`: Automated post-deployment validation of health endpoints, API, and static assets.
   - `backup-postgres.sh` & `restore-postgres.sh`: Gzip-compressed, SHA-256 verified, point-in-time recovery tooling.
   - `verify-storage.sh`, `verify-release.sh`, and `install-customer-hosted.sh`.

6. **Documentation & Runbook Suite:**
   - Authored complete 34-document architectural specification suite in `docs/architecture/ARC-11-infrastructure-deployment/`.
   - Created 29 operational runbooks across `docs/deployment/`, `docs/operations/`, `docs/backup-recovery/`, and `docs/runbooks/`.
   - Registered 30 Architecture Decision Records (`ADR-0192` through `ADR-0221`) in `docs/decisions/decision-register.md`.

7. **Automated Verification:**
   - 120/120 automated test scenarios passing in `tests/infrastructure/test_arc11_infrastructure_catalogue.py`.
   - 738/738 total platform tests passing with 100% pass rate across ARC-01 through ARC-11.
