# FCD-11 · Document 01: Security Architecture & Principles

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Architectural Philosophy

Menu-It is an organization-centric multi-tenant restaurant SaaS platform. Its security architecture follows six foundational principles:

1. **Zero Trust Inside the Perimeter:** No network boundary, internal service, or process is implicitly trusted. Every inbound request must prove authentication, identity, tenant context, and explicit authorization.
2. **Deny-by-Default Authorization:** An action is forbidden unless an active, valid permission explicitly allows it. Wildcards and super-user overrides are strictly restricted.
3. **Tenant Data Boundary Invariant:** Tenant isolation is enforced at two distinct, non-bypassable layers:
   - Application Layer: Scoped repository queries and `assert_tenant_boundary` assertions.
   - Database Layer: PostgreSQL Row Level Security (RLS) driven by `app.current_organization_id`.
4. **Append-Only Forensic Immutability:** Security audit events are write-only. Once persisted, audit records cannot be altered, overwritten, or deleted by application users or tenant administrators.
5. **Fail-Secure & Fail-Safe Defaults:** If a security check or authorization rule fails, execution terminates with an error; access is never granted on failure.
6. **Defense in Depth:** Security controls exist across the entire stack: HTTP security headers, CORS restrictions, rate limiting, request validation, tenant assertions, database RLS, and continuous auditing.

---

## 2. Security Boundaries & Protection Rings

```
 [ Public Internet / Untrusted Clients ]
                    │
                    ▼
 [ Edge & Reverse Proxy / TLS Termination / WAF ]
                    │
                    ▼
 [ HTTP Security Headers Middleware & CORS Protection ]
                    │
                    ▼
 [ Rate Limiting Engine (Redis + InMemory Fallback) ]
                    │
                    ▼
 [ Request ID & Correlation Tracking Middleware ]
                    │
                    ▼
 [ Authentication Layer: JWT Validation & Session Verification ]
                    │
                    ▼
 [ Multi-Tenant Resolution: Organization Membership & TenantContext ]
                    │
                    ▼
 [ Authorization Layer: Role & Permission Enforcement ]
                    │
                    ▼
 [ Application Service & Repository: assert_tenant_boundary ]
                    │
                    ▼
 [ PostgreSQL Database Engine: Row Level Security (RLS) Policies ]
```

---

## 3. Cryptographic Standards

- **Password Hashing:** Argon2id with memory cost 64 MB, time cost 3 iterations, and parallelism 4 threads.
- **JWT Tokens:** Asymmetric RS256 (or cryptographically strong HS256 with minimum 256-bit entropy).
- **Transport Security:** TLS 1.3 preferred (TLS 1.2 minimum). HSTS enabled with `max-age=31536000; includeSubDomains`.
