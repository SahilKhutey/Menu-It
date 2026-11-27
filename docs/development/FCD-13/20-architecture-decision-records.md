# FCD-13 · Document 20 — Architecture Decision Records (ADRs)

This document formalizes the 12 Architecture Decision Records (`FCD13-ADR-001` through `FCD13-ADR-012`) established during FCD-13 foundational integration and baseline release validation.

---

### FCD13-ADR-001: Integrated Module Dependency Boundaries
- **Context:** The modular monolith must prevent architectural erosion where domain models couple to presentation or database frameworks.
- **Decision:** Enforce Clean Architecture via automated AST inspection (`test_architecture_boundaries.py`). Domain models MUST NOT import FastAPI, SQLAlchemy, Redis, or cloud SDKs.
- **Consequences:** Domain logic is 100% portable, unit-testable in milliseconds, and decoupled from infrastructure libraries.

---

### FCD13-ADR-002: Centralized Application Lifespan & Startup Root
- **Context:** Multiple subsystems (FastAPI, database, Redis cache, rate limiting, ARQ workers) require coordinated initialization and clean teardown.
- **Decision:** Use FastAPI's async `lifespan` context manager and a dedicated `PlatformServices` container (`menu_it.platform.container.build_platform_services`).
- **Consequences:** One authoritative composition root handles startup and graceful shutdown with zero resource leakage.

---

### FCD13-ADR-003: Multi-Tenant Security Chain & Fail-Closed Tenancy
- **Context:** In a multi-tenant SaaS platform, trusting client-provided tenant headers leads to critical security vulnerabilities (cross-tenant data leakage).
- **Decision:** Derive tenant scope strictly from validated user memberships. Store immutable `TenantContext` in Python `ContextVar`. Missing tenant context raises `RuntimeError` immediately (fail closed).
- **Consequences:** Zero client-side tenant spoofing; database connection-pool context leakage is mathematically eliminated.

---

### FCD13-ADR-004: Database-Domain Mapping & Outbox Atomicity
- **Context:** Business operations producing asynchronous side effects must not suffer from dual-write inconsistencies.
- **Decision:** Stage all durable domain events to `event_outbox` within the exact same database transaction via `OutboxEventPublisher`.
- **Consequences:** If the business write rolls back, the event is also rolled back; if committed, the event is guaranteed to be dispatched.

---

### FCD13-ADR-005: API Versioning & Shared TypeScript Contracts
- **Context:** Frontend applications and external clients require stable, typed API contracts that avoid drift.
- **Decision:** Standardize on `/api/v1` routes with OpenAPI 3.x schema generation and export shared TypeScript contracts in `@menu-it/shared-types`.
- **Consequences:** Any backend contract modification is caught at compile time by `tsc --noEmit` across all workspace apps.

---

### FCD13-ADR-006: Provider-Independent Platform Service Ports
- **Context:** Core platform utilities (file storage, email notifications, audit logging) must be usable without hard-coding external vendors.
- **Decision:** Define abstract protocols (`FileStorage`, `TemplateRenderer`, `AuditEventPublisher`) with local filesystem and console adapters as defaults for the baseline release.
- **Consequences:** Easy switching to S3, SES, or cloud providers in production without rewriting application services.

---

### FCD13-ADR-007: Redis Caching with In-Memory Safe Fallback
- **Context:** High-throughput caching and rate limiting must not turn Redis into a single point of total application failure.
- **Decision:** Wrap Redis calls in `CacheService` and `RateLimiter`; if Redis is unavailable, fall back gracefully to in-memory adapters.
- **Consequences:** Transient Redis outages degrade performance but do not crash application HTTP request flows.

---

### FCD13-ADR-008: Telemetry Instrumentation & Append-Only Security Audit
- **Context:** Observability must be standardized across API requests and background worker tasks.
- **Decision:** Expose Prometheus metrics at `/api/v1/metrics`, emit structured JSON logs, and persist immutable security audit records.
- **Consequences:** Full visibility into latency, throughput, error rates, and security operations without performance degradation.

---

### FCD13-ADR-009: Strict Environment Configuration & Secret Scoping
- **Context:** Environment variables must be validated and secrets prevented from leaking into frontend builds.
- **Decision:** Validate backend configuration via Pydantic `Settings`; restrict frontend exposed variables to `NEXT_PUBLIC_` prefixes.
- **Consequences:** Misconfigured ports or invalid environment names fail at boot; client bundles contain zero backend secrets.

---

### FCD13-ADR-010: Database Migration Sequencing in CI/CD
- **Context:** Production deployments must avoid schema divergence and downtime.
- **Decision:** Execute Alembic single-head validation in CI and apply `alembic upgrade head` before swapping application containers.
- **Consequences:** Zero migration conflicts in `develop`; backward-compatible schema changes ensure safe rollbacks.

---

### FCD13-ADR-011: Foundational Baseline Versioning (v0.1.0)
- **Context:** FCD-13 validates the technical platform foundation, but restaurant SaaS business modules remain to be implemented in subsequent phases.
- **Decision:** Tag the baseline release as `v0.1.0` rather than `v1.0.0`. Promote to `v1.0.0` only when initial commercial restaurant business features are complete.
- **Consequences:** Transparent, accurate semantic versioning reflecting foundational readiness versus commercial product readiness.

---

### FCD13-ADR-012: Environment-Protected Release Approval & Rollback Runbook
- **Context:** Production releases must be protected against accidental deployment and equipped with verified recovery procedures.
- **Decision:** Require GitHub Environment approval for production deployments and document step-by-step container and schema rollback runbooks.
- **Consequences:** Traceable, auditable release gates and tested disaster recovery drills.
