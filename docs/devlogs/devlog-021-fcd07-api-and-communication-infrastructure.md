# Devlog 021 — FCD-07 API & Communication Infrastructure

**Date:** 2026-11-24  
**Author:** AI Architecture & Core Engineering Team  
**Subject:** Implementation, Verification, and Release of FCD-07 API & Communication Infrastructure  
**Milestone:** `v1.0.0-fcd07`  
**Phase:** Foundational Core Development (FCD-07)  
**Parent Documents:** FCD-01 through FCD-06, ARC-01 through ARC-12  

---

## 1. Objectives & Context

Phase **FCD-07** establishes the formal communication standards and runtime infrastructure through which the Menu-It backend exposes functionality to its frontend applications (`apps/web`, `apps/admin`), external integrations, and internal application modules.

Building upon FCD-01 through FCD-06, FCD-07 delivers:
1. **API Standards & Path Versioning:** Universal `/api/v1` URL path versioning, strict HTTP semantics, kebab-case URL paths, and camelCase/snake_case JSON consistency.
2. **Modular Router Tree:** Transitioned from a monolithic router to a domain-oriented modular tree (`v1/endpoints/` and `v1/modules/restaurants/`).
3. **Universal Envelope & Serialized Schemas:** Reusable `APIResponse[T]` wrapping `{success, data, error, meta}` with UTC timestamp and UUID `request_id`.
4. **Sanitized Validation Error Normalization:** Transformed raw Pydantic errors into structured `APIErrorDetail` while strictly stripping sensitive input values.
5. **Centralized Domain Exception Mapping:** Seamless translation of pure domain exceptions (`EntityNotFoundError` -> 404, `InvalidStateTransitionError` -> 409, `BusinessRuleViolationError` -> 409, `ConcurrencyConflictError` -> 409, `ValidationDomainError` -> 422) into standard public error envelopes.
6. **Defense-in-Depth Middleware Stack:**
   - `RequestIDMiddleware`: UUID validation, replacement of invalid strings, header propagation.
   - `RequestTimingMiddleware`: High-precision monotonic execution timing injecting `X-Response-Time-MS`.
   - `SecurityHeadersMiddleware`: Enforcing `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`.
   - `RequestLoggingMiddleware`: Access logging with automatic redaction of sensitive credentials and headers.
7. **Unified Dependency Injection Facade:** Clean `api/dependencies/` subsystem for authentication, tenant context, RBAC permissions, and pagination.
8. **Rate Limiting Infrastructure:** Sliding window rate limiter supporting thread-safe in-memory execution and Redis adapter with IP, tenant, and user key resolution strategies, generating `Retry-After` and `X-RateLimit-*` headers upon 429 throttling.
9. **Durable Idempotency Infrastructure:** Database-backed `idempotency_records` table with SHA-256 payload digest matching, PostgreSQL Row-Level Security, and cache replay (`Idempotent-Replay: true`, `X-Cache-Lookup: HIT`).
10. **Internal Application Communication:** `ApplicationResult[T]` container and cross-module structural protocol `RestaurantQueryService`.
11. **Frontend HTTP Client & Shared Contracts:** Enhanced `apiRequest<T>` client in `apps/web` and `apps/admin` handling 204 No Content, error mapping, and token/idempotency propagation, powered by `@menu-it/shared-types`.
12. **OpenAPI 3.1 Documentation:** Automated interactive documentation generated with structured tags and contract tests.
13. **Full Automated Verification:** 251 tests passing 100% with 90% codebase coverage.

---

## 2. Completed Work Packages

- **WP-01: Baseline & Compatibility Audit:** Completed in `docs/development/FCD-07/00-baseline-audit.md`.
- **WP-02: API Standards & Design Guidelines:** Completed in `docs/development/FCD-07/01-api-standards.md`.
- **WP-03: Modular Router Architecture:** Modular router hierarchy mounted under `/api/v1`.
- **WP-04: Request & Response Envelopes:** Enveloped response models and sanitized validation handling.
- **WP-05: Request Lifecycle & Middleware:** Standardized pipeline in `menu_it.api.middleware`.
- **WP-06: Dependency Injection Facade:** Unified dependencies in `menu_it.api.dependencies`.
- **WP-07: Pagination, Filtering & Sorting:** `PaginationParams` and `PaginationMeta` standards.
- **WP-08: Security Headers & Telemetry:** Security headers and response timing telemetry.
- **WP-09: Restaurant API Endpoints:** Multi-tenant restaurant location management endpoints.
- **WP-10: Rate Limiting Infrastructure:** In-memory and Redis sliding window limiters.
- **WP-11: Durable Idempotency Support:** Database persistence and Alembic migration `0005_idempotency_records`.
- **WP-12: Internal Service Communication:** `ApplicationResult[T]` and `RestaurantQueryService`.
- **WP-13: Frontend Client & Shared Types:** TypeScript client and contracts in `@menu-it/shared-types`.
- **WP-14: OpenAPI 3.1 Documentation:** Interactive docs, metadata, tags, and schema validation.
- **WP-15: Automated Verification & Testing:** Unit, integration, security, and contract test suites.
- **WP-16: Technical Documentation & Sign-Off:** 21 technical documents, Devlog 021, and Tasklog.

---

## 3. Test Verification Metrics

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
collected 251 items

251 passed in 24.99s (100% pass rate)
Total Coverage: 90% (3281 / 3656 statements)
```

- **Static Analysis:**
  - `ruff check`: All checks passed!
  - `ruff format`: 255 files formatted!
  - `pnpm typecheck`: Clean across all workspaces!
  - `pnpm lint`: 0 ESLint warnings or errors!
  - `prettier`: 100% compliant!

---

## 4. Next Milestone

Proceed to **FCD-08 (Data Pipeline & Event Streaming)** or business module development (Menu Management & Restaurant Operations) building on top of this standardized API foundation.
