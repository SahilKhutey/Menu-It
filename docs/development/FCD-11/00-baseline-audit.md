# FCD-11 · Document 00: Baseline Security & Operational Audit

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Executive Summary

Prior to establishing the formal operational assurance layer in FCD-11, an end-to-end baseline audit was conducted across the Menu-It repository covering codebase security, tenant isolation, authentication, error envelopes, logging, database configurations, and background infrastructure.

### Key Audit Findings
1. **Multi-Tenancy Foundation (FCD-04):** Verified that `TenantContext`, `TenantResolver`, and `set_database_tenant_context` correctly populate PostgreSQL session variable `app.current_organization_id`. Database RLS policies are active on all tenant-bound tables.
2. **Identity & Authorization (FCD-05):** Verified Argon2id password hashing, RS256/HS256 JWT validation, and session lifecycle controls. Identified the need for explicit boundary assertion utilities to prevent ad-hoc tenant comparisons in service layers.
3. **Application & API Infrastructure (FCD-02, FCD-07):** Standard error envelopes (`/api/v1`) and request ID middleware were present. Hardened HTTP headers required additional browser isolation headers (CSP, Permissions-Policy, COOP, CORP, and conditional HSTS).
4. **Platform Services & Async Execution (FCD-09, FCD-10):** Redis cache, outbox event dispatch, and ARQ background execution operate predictably. Bounded timeouts and distributed rate-limiting required centralized implementation.
5. **Durable Security Audit Trail:** Previously, organization audit records captured business modifications (`organization_audit_events`), but security-critical events (authentication failures, permission denials, boundary breach attempts) lacked an append-only, tamper-resistant persistence table with dedicated RLS.

---

## 2. Baseline Inventory & Technical State

| Component | State Pre-FCD-11 | Assessment | Action Taken in FCD-11 |
| :--- | :--- | :--- | :--- |
| **Config Validation** | Pydantic model validation only | Insecure dev settings could reach production | Implemented `SecurityConfigValidator` & `ensure_production_config` |
| **Security Headers** | Basic X-Frame-Options & nosniff | Incomplete defense against modern browser attacks | Injected CSP, Permissions-Policy, COOP, CORP, and conditional HSTS |
| **Rate Limiting** | None | Vulnerable to brute force & DoS | Created `RedisRateLimiter` with in-memory fallback |
| **Security Auditing** | Business events only | Security incident forensics gap | Added `SecurityAuditEventModel`, migration `0008`, and `SecurityAuditWriter` |
| **Metrics** | None | No system or operational telemetry | Integrated `prometheus-client` with `/metrics` endpoint |
| **Tracing** | None | No distributed context propagation | Integrated OpenTelemetry with W3C traceparent propagation |
| **Circuit Breakers**| None | Cascade failure risk on remote service outages | Implemented `CircuitBreaker` with Closed/Open/Half-Open state machine |

---

## 3. Baseline Audit Sign-off

The baseline audit confirmed architectural integrity and paved the way for the security, reliability, and observability implementations detailed in subsequent documents.
