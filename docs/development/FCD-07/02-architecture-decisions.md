# FCD-07 §02 — Architecture Decisions & Design Records

## 1. Context & Objectives

Phase FCD-07 establishes the formal API communication infrastructure for Menu-It. Prior phases (FCD-01 through FCD-06) established the modular monolith architecture, database persistence, multi-tenant isolation, identity/session management, and domain modeling. FCD-07 connects these foundations to external clients (`apps/web`, `apps/admin`) and cross-module boundaries via predictable, observable, and secure protocols.

---

## 2. Key Architectural Decisions (ADRs)

### ADR-01: Explicit URL Path Versioning (`/api/v1`)
- **Decision:** All public API endpoints are mounted under `/api/v1` prefix.
- **Rationale:** Path-based versioning enables clear caching policies, predictable reverse-proxy routing, and unambiguous client targeting across major platform revisions without relying on volatile custom HTTP headers.
- **Consequences:** Client libraries bind to `/api/v1`; future major breaks will introduce `/api/v2` cleanly side-by-side.

### ADR-02: Universal Envelope Contract (`APIResponse[T]`)
- **Decision:** Every successful and error response adheres to `{ "success": boolean, "data": T | null, "error": APIError | null, "meta": ResponseMeta }`.
- **Rationale:** Eliminates ambiguity on the client. Frontend applications can implement a single type guard (`if (!res.success)`) without defensive heuristic checks.
- **Consequences:** Endpoints wrap models or DTOs inside `success_response` or `error_response`.

### ADR-03: Sanitized Structured Validation Errors
- **Decision:** Pydantic validation errors are stripped of raw inputs and normalized into a stable `list[APIErrorDetail]` (`field`, `code`, `message`).
- **Rationale:** Prevents credential, secret, or internal memory reflection when clients submit malformed or malicious payloads.
- **Consequences:** Handlers do not reflect `input` fields in JSON responses.

### ADR-04: Non-Blocking In-Memory & Redis Rate Limiting
- **Decision:** Sliding window rate limiter with native Python `asyncio.Lock` and deque storage, plus Redis adapter for clustered execution.
- **Rationale:** Fast, zero-dependency local development with horizontal scalability in multi-instance production environments.
- **Consequences:** Endpoints enforce limits via standard `Depends(rate_limit(...))` injecting `Retry-After` and `X-RateLimit-*` headers upon exhaustion.

### ADR-05: Durable Database-Backed Idempotency
- **Decision:** Store idempotency keys, SHA-256 payload digests, and serialized responses in the `idempotency_records` table, protected by PostgreSQL Row-Level Security (RLS).
- **Rationale:** Guarantees state safety during network retries of mutating requests (`POST`).
- **Consequences:** Scoped by `(organization_id, actor_id, key)` to prevent cross-tenant key pollution. Payload mismatch triggers `409 Conflict` with `IDEMPOTENCY_CONFLICT`.
