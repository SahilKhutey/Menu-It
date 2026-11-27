# FCD-11 · Document 27: Architecture Decision Records (FCD11-ADR-001 to FCD11-ADR-012)

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## FCD11-ADR-001: Automated Startup Production Security Validation
- **Context:** Deploying insecure default credentials, debug flags, or HTTP cookies in production undermines multi-tenant isolation.
- **Decision:** Implement `ensure_production_config` and `SecurityConfigValidator` to prevent application startup if security invariants are violated in production.
- **Status:** Approved & Implemented.

## FCD11-ADR-002: Dual-Layer Tenant Isolation Model
- **Context:** Multi-tenancy must be resilient to application logic errors.
- **Decision:** Combine application-level `assert_tenant_boundary` checks with PostgreSQL Row Level Security (RLS) driven by `app.current_organization_id`.
- **Status:** Approved & Implemented.

## FCD11-ADR-003: Dedicated Append-Only Security Audit Table
- **Context:** Business audit logs (`organization_audit_events`) lack security-specific fields and tamper resistance.
- **Decision:** Create `security_audit_events` with dedicated PostgreSQL RLS, unique event IDs, and forbid UPDATE/DELETE operations.
- **Status:** Approved & Implemented.

## FCD11-ADR-004: Fail-Safe Security Audit Writer Fallback
- **Context:** If the database transaction fails during a security incident, the audit record must not be lost.
- **Decision:** Implement `SecurityAuditWriter` with automatic structured log fallback when database writes fail.
- **Status:** Approved & Implemented.

## FCD11-ADR-005: Comprehensive Browser Isolation Response Headers
- **Context:** Modern browsers require hardened defense against clickjacking, cross-origin reads, and MIME sniffing.
- **Decision:** Inject `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`, `COOP`, `CORP`, and `CSP` via `SecurityHeadersMiddleware`.
- **Status:** Approved & Implemented.

## FCD11-ADR-006: Distributed Sliding-Window Rate Limiting with In-Memory Fallback
- **Context:** Rate limiting must scale across pods while degrading gracefully during Redis disruptions.
- **Decision:** Implement `RedisRateLimiter` using Redis sorted sets, falling back to `InMemoryRateLimiter` if Redis is unreachable.
- **Status:** Approved & Implemented.

## FCD11-ADR-007: Universal Recursive Sensitive Data Redaction
- **Context:** Credentials, tokens, and PANs must never appear in logs or trace spans.
- **Decision:** Provide centralized `redact_data`, `redact_authorization_header`, and `mask_card_number` across all logging and telemetry paths.
- **Status:** Approved & Implemented.

## FCD11-ADR-008: Native Prometheus Metrics Instrumentation
- **Context:** Operational monitoring requires standardized, high-performance telemetry.
- **Decision:** Instrument `http_requests_total`, `http_request_duration_seconds`, connection gauges, and expose via `GET /api/v1/metrics`.
- **Status:** Approved & Implemented.

## FCD11-ADR-009: OpenTelemetry Distributed Tracing & W3C Context Propagation
- **Context:** Distributed requests across API pods, background workers, and databases must be traceable.
- **Decision:** Adopt OpenTelemetry SDK with W3C `traceparent` propagation across HTTP headers and background jobs.
- **Status:** Approved & Implemented.

## FCD11-ADR-010: Process-Local Circuit Breakers for External Integrations
- **Context:** Remote dependency failures (SMTP, payment, storage) can cascade and exhaust thread pools.
- **Decision:** Implement `CircuitBreaker` with Closed/Open/Half-Open state machine to fast-fail degraded third parties.
- **Status:** Approved & Implemented.

## FCD11-ADR-011: Point-in-Time Recovery (PITR) for Database Protection
- **Context:** Backups must meet strict RPO and RTO objectives.
- **Decision:** Continuous PostgreSQL WAL streaming to object storage providing 15-minute RPO and 4-hour RTO.
- **Status:** Approved & Implemented.

## FCD11-ADR-012: Deny-by-Default Authorization Verification
- **Context:** Ad-hoc permission queries can result in accidental access grants.
- **Decision:** Enforce `require_permission` across all protected routes with strict wildcard rules.
- **Status:** Approved & Implemented.
