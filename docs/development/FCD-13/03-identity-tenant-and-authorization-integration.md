# FCD-13 · Document 03 — Identity, Tenant & Authorization Integration

## 1. Objective
Demonstrates that user authentication, organization membership, tenant resolution, role-based authorization, and PostgreSQL Row-Level Security (RLS) operate as a single, tamper-proof security chain.

---

## 2. End-to-End Security Chain

```
HTTP Bearer Token (JWT)
  │
  ▼
JWT Validation & Principal Resolution (User UUID)
  │
  ▼
Authoritative Membership Lookup (Active status, Organization UUID)
  │
  ▼
Immutable TenantContext Established (in Python ContextVar)
  │
  ▼
Transaction Local Context Set (SET LOCAL app.current_organization_id = ...)
  │
  ▼
PostgreSQL Row-Level Security (RLS) Filter Applied Automatically
  │
  ▼
Authorized Business Result (Cross-tenant access rejected fail-closed)
```

---

## 3. Inviolable Tenancy Invariants
1. **Never Trust Client Tenant Header:** Organization and restaurant scope are derived solely from validated database membership records, not client-supplied request parameters.
2. **Fail Closed:** When no active `TenantContext` is present in `ContextVar`, calls to `get_current_tenant()` raise a `RuntimeError`, immediately aborting unauthorized execution.
3. **Connection Pool Safety:** Tenant context is transaction-scoped (`SET LOCAL`); when a pooled database connection returns to the pool, tenant variables are cleared, preventing cross-request data leaks.
4. **Worker Context Propagation:** Asynchronous jobs carry an explicit `SystemTenantContext(organization_id, system_actor, job_id)` injected into the worker task frame.

---

## 4. Security Integration Test Matrix

| Test ID | Security Scenario | Expected Result | Verification Status |
| :--- | :--- | :--- | :---: |
| `SECINT-T01` | Valid user & membership | Authoritative `TenantContext` created & resolved | **PASSED** |
| `SECINT-T02` | Unauthenticated request | Rejected immediately with HTTP 401 | **PASSED** |
| `SECINT-T03` | User not in organization | Rejected with HTTP 404 (anti-enumeration) | **PASSED** |
| `SECINT-T04` | Cross-tenant access attempt | Denied; Org A cannot resolve or touch Org B records | **PASSED** |
| `SECINT-T05` | Missing tenant context | `get_current_tenant()` fails closed with RuntimeError | **PASSED** |
| `SECINT-T06` | Worker context isolation | Worker task executes with explicit system context | **PASSED** |
| `SECINT-T07` | ContextVar cleanup | `reset_current_tenant()` clears token; no leakage | **PASSED** |

---

## 5. Verification Evidence
Verified by test suites:
- `apps/api/tests/integration/test_identity_tenant_security_chain.py`
- `apps/api/tests/security/test_tenant_isolation_assurance.py`
- `apps/api/tests/security/test_api_tenant_security.py`
