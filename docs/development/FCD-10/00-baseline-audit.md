# FCD-10 — Baseline Audit & Repository Readiness

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Date:** 2026-11-25  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Completed  

---

## 1. Executive Summary

This audit establishes the baseline state of the **Menu-It** repository prior to implementing **FCD-10 (Caching, Background Jobs & Event Infrastructure)**. It inventories existing architectural layers, database models, migration revisions, service composition roots, tenant isolation mechanisms, and dependencies.

The objective is to ensure that FCD-10 builds seamlessly on the foundation of **FCD-03** (Database & Repositories), **FCD-04** (Multi-Tenancy & RLS), **FCD-05** (Identity & RBAC), **FCD-06** (Domain Models & Operating Schedules), **FCD-07** (API Infrastructure), **FCD-08** (Frontend Design System), and **FCD-09** (Platform Services & Shared Utilities) without introducing duplicate abstractions or violating architectural invariants.

---

## 2. Repository & Monorepo State

```
Branch: develop
Commit: 2404648 ("feat(platform): establish FCD-09 core platform services and shared utilities")
Working Tree: Clean (0 uncommitted changes)
```

### Directory Structure & Workspace Layout
- `apps/api`: FastAPI backend service with SQLAlchemy 2.x async, Alembic migrations, Pydantic settings.
- `apps/web`: Next.js 14 customer/restaurant web application.
- `apps/admin`: Next.js 14 administrative application.
- `packages/shared-types`: Canonical TypeScript contracts synchronized with backend domain schemas.
- `packages/design-tokens`: UI primitive and semantic tokens.
- `packages/theme-engine`: Multi-tenant theme engine with WCAG 2.2 AA contrast calculation.
- `packages/ui`: Accessible React UI component library.

---

## 3. Architecture Foundation Review

### 3.1 Database & Migrations (FCD-03, FCD-04, FCD-05, FCD-06, FCD-09)
The current Alembic migration history shows 6 linear revisions:
- `0001_initial_schema`: Initial organization, restaurant, and user tables.
- `0002_multi_tenant_core`: Multi-tenant memberships, roles, and RLS policies.
- `0003_identity_and_auth`: Credentials, sessions, verification tokens.
- `0004_domain_foundation`: Restaurant profiles, schedules, operating hours.
- `0005_api_idempotency`: Durable idempotency keys table with RLS.
- `0006_create_files_and_notifications`: Files metadata, in-app notifications, and notification deliveries with RLS (`head`).

**Current Migration Head:** `0006_files_and_notifications`

### 3.2 Tenant Isolation & Context (FCD-04)
- **Model:** Primary tenant is `Organization`; subordinate entities are `Restaurant`.
- **Context:** `TenantContext` in `menu_it.tenancy.context` is immutable and request-scoped, carrying `organization_id`, `user_id`, `organization_role`, `restaurant_id`, `restaurant_role`, and `correlation_id`.
- **System Context:** `SystemTenantContext` provides explicit attribution for asynchronous workers.
- **Database Context:** `set_database_tenant_context(session, context)` in `menu_it.database.tenant_scope` executes `SELECT set_config('app.current_organization_id', :org_id, true)`. The third argument (`true`) ensures PostgreSQL settings are strictly transaction-local and are automatically cleared on commit or rollback.

### 3.3 Platform Services & Composition Root (FCD-09)
- **Container:** `PlatformServices` in `menu_it.platform.container` manages singleton application services (`Settings`, `Clock`, `FileStorage`, `NotificationService`, `AuditEventPublisher`).
- **Lifespan:** `initialize_runtime()` and `shutdown_runtime()` in `menu_it.core.lifecycle` manage runtime resources.
- **Settings:** `Settings` in `menu_it.core.config` is frozen (`frozen=True`) with secret masking in `__repr__`.
- **Logging:** `JsonFormatter` and `ContextLoggerAdapter` in `menu_it.core.logging` format structured JSON logs with correlation IDs and sensitive data redaction (`redact_mapping`).

---

## 4. Dependencies & Runtime Environment

### 4.1 Python Package Inventory
- Python version: `3.12.x`
- Fast API: `0.110.0+`
- SQLAlchemy: `2.0.x` (Async engine with `asyncpg` and `aiosqlite`)
- Pydantic: `2.6.x` & `pydantic-settings: 2.2.x`
- Jinja2: `3.1.x`
- Installed in site-packages:
  - `redis`: Version `5.3.1`
  - `arq`: Version `0.28.0`

### 4.2 Action Needed for pyproject.toml
Declare `redis>=5.0.0` and `arq>=0.25.0` explicitly under `dependencies` in `apps/api/pyproject.toml` to guarantee deterministic environment recreation.

---

## 5. Infrastructure Compatibility Analysis

### 5.1 Redis Infrastructure
- Redis will serve two distinct roles:
  1. Cache storage (`CacheBackend`, `RedisCacheBackend`).
  2. Asynchronous job broker (`ARQ`).
- In accordance with ARC-05 and FCD-10 guidelines:
  - Cache and broker must use isolated namespaces or prefixes (`menu-it:cache:`, `menu-it:jobs:`).
  - Cache failure must never block database writes or bypass authorization checks.
  - The cache layer will support an `InMemoryCacheBackend` for test environments where a live Redis server is not provisioned.

### 5.2 Persistence & Database Tables Required for FCD-10
FCD-10 will introduce 6 persistent tables via Alembic revision `0007_create_fcd10_jobs_events_and_schedules`:
1. `event_outbox`: Transactional outbox for guaranteed event publishing with lease locking (`locked_until`, `locked_by`).
2. `processed_events`: Consumer inbox deduplication ensuring idempotent event consumption.
3. `dead_letter_jobs`: Persistent record of exhausted or permanently failed background jobs with replay tracking.
4. `scheduled_jobs`: Persistent schedule definitions supporting cron/intervals and IANA timezones.
5. `scheduled_job_runs`: Execution occurrence history preventing duplicate scheduled runs.
6. `background_jobs`: Job status tracking and attempt metadata for asynchronous API tasks.

---

## 6. Identified Risks & Mitigations

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Redis Outage blocks API writes** | High | Outbox events are committed directly to PostgreSQL in the primary transaction. Redis is only queried during dispatch. |
| **Worker Context Leakage** | Critical | Workers must never retain tenant context across tasks. Each task creates a fresh DB session and sets transaction-local RLS. |
| **Stale Cache Authorization** | High | Tenant-private cache keys enforce server-resolved `organization_id`. Authorization decisions are never cached statically. |
| **Duplicate Event Processing** | Medium | `processed_events` inbox table enforces unique `(consumer_name, event_id)` within the consuming database transaction. |
| **Schedule Over-execution** | Medium | `scheduled_job_runs` table records unique run occurrences with pessimistic concurrency or atomic insert checks. |

---

## 7. Baseline Audit Sign-off

- [x] Repository state audited and clean.
- [x] Prior FCD milestones (01–09) confirmed active and intact.
- [x] Dependency versions verified (`redis 5.3.1`, `arq 0.28.0`).
- [x] Schema migration head confirmed (`0006_files_and_notifications`).
- [x] Ready to proceed with Stage 1 (WP-01: Redis dependencies and configuration).
