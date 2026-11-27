# FCD-07 §15 — Security Architecture & Threat Isolation

## 1. Threat Model & Mitigations

| Threat Vector | Attack Scenario | Menu-It Mitigation |
| :--- | :--- | :--- |
| **Cross-Tenant Data Leakage** | Tenant A attempts to fetch or modify Tenant B's restaurant | Dual layer: Scoped repository filters + PostgreSQL RLS. Returns 404 to avoid probing. |
| **Information Disclosure** | Validation errors or 500 exceptions reveal database connection or passwords | `normalize_validation_error` strips inputs. `unhandled_exception_handler` sanitizes messages. |
| **Denial of Service (DoS)** | Script floods API endpoints with requests | Sliding window rate limiting (`InMemoryRateLimiter` / `RedisRateLimiter`) with 429 throttling. |
| **Double Mutate / Replay** | Network interruption causes duplicated create request | Durable `IdempotencyRecord` table with hash comparison and response cache replay. |
| **MIME Sniffing & Clickjacking**| Browser misinterprets content type or frames application | `SecurityHeadersMiddleware` sets `nosniff`, `DENY`, and `strict-origin-when-cross-origin`. |
| **Credential Reflection** | Sensitive auth tokens logged in access logs | `RequestLoggingMiddleware` redacts `Authorization`, `Cookie`, `X-Refresh-Token` headers. |

---

## 2. Automated Security Verification

The automated security test suite under `apps/api/tests/security/` validates:
- `test_api_sanitization_and_isolation.py`: Verifies sensitive parameters are never reflected in error payloads.
- `test_api_tenant_security.py`: Verifies cross-tenant organization isolation.
- `test_rls_isolation.py`: Verifies database-level RLS policies reject foreign tenant queries.
- `test_platform_boundary.py`: Verifies platform admin roles cannot be assumed by tenant users.
