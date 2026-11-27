# Menu-It v0.1.0 — Deployment Reference & Operating Guide

## Overview

This document specifies the operational configuration, environment variable contracts, container execution models, and health probe definitions for deploying the Menu-It foundational platform (`v0.1.0`).

---

## Topology

The baseline deployment consists of the following containerized workloads:

1. **API Service (`menu-it-api`):** FastAPI asynchronous service running on port `8000`.
2. **Customer Web (`menu-it-web`):** Next.js application running on port `3000`.
3. **Admin Web (`menu-it-admin`):** Next.js application running on port `3001`.
4. **Background Worker (`menu-it-worker`):** ARQ async worker executing background jobs from Redis queues.
5. **PostgreSQL 16:** Primary multi-tenant relational persistence with RLS enabled.
6. **Redis 7:** In-memory caching, rate limiting, and distributed job broker.

---

## Environment Configuration

### Backend API & Worker (`apps/api`)

| Variable            | Required | Default                    | Purpose                                                         |
| :------------------ | :------: | :------------------------- | :-------------------------------------------------------------- |
| `APP_ENV`           |   Yes    | `production`               | Environment tier (`development`, `staging`, `production`)       |
| `DATABASE_URL`      |   Yes    | -                          | Async PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `REDIS_URL`         |   Yes    | `redis://localhost:6379/0` | Redis connection URL                                            |
| `JWT_SECRET_KEY`    |   Yes    | -                          | Cryptographic secret for signing bearer tokens (min 32 chars)   |
| `CORS_ORIGINS`      |   Yes    | -                          | Comma-separated allowlist of origins (no `*` in prod)           |
| `FILE_STORAGE_ROOT` |    No    | `./storage`                | Filesystem path for local storage adapter                       |
| `LOG_LEVEL`         |    No    | `INFO`                     | Structured logging verbosity                                    |

### Frontend Applications (`apps/web` & `apps/admin`)

| Variable              | Required | Purpose                                                                  |
| :-------------------- | :------: | :----------------------------------------------------------------------- |
| `NEXT_PUBLIC_API_URL` |   Yes    | Base URL for backend API endpoint (e.g., `https://api.menu-it.internal`) |
| `NODE_ENV`            |   Yes    | Set to `production` in container builds                                  |

---

## Health & Liveness Probes

- **Liveness Probe:** `GET /api/v1/health` (HTTP 200 OK)
- **Database Readiness Probe:** `GET /api/v1/database/health` (HTTP 200 OK or 503 Service Unavailable)
- **System Information:** `GET /api/v1/system/info` (HTTP 200 OK)
- **Telemetry Metrics:** `GET /api/v1/metrics` (Prometheus text format)

---

## Container Security Model

- All containers execute as dedicated unprivileged users (`appuser` UID 10001 for API/worker, `nextjs` UID 1001 for web/admin).
- Read-only root filesystem supported; temp files and storage mounted to designated persistent volumes.
