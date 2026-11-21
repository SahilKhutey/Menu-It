# 01. API Architecture Overview

## 1. High-Level Architecture
ModularMenu's API architecture converts the logical domains established in ARC-04 and the tenancy isolation rules in ARC-05 into an enforceable HTTP REST interface.

```
+-----------------------------------------------------------------------------------+
|                                 Clients Layer                                     |
|  [ Next.js Admin / Editor ]    [ Public Mobile Web ]    [ External API Consumers ]|
+------------------------------------------+----------------------------------------+
                                           | HTTPS / JSON
                                           v
+-----------------------------------------------------------------------------------+
|                             API Gateway / Reverse Proxy                           |
|  - TLS Termination    - CORS Verification    - Endpoint Rate Limiting (Token Bucket) |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                        FastAPI Core Middleware Pipeline                           |
|  1. RequestCorrelationIdMiddleware (UUIDv4)                                       |
|  2. Centralized RFC 7807 Exception Handlers                                       |
|  3. Authentication Dependency (Cookie session or Bearer JWT)                      |
|  4. Server-Derived TenantContext Resolver (Fail-closed)                           |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                         Versioned REST Routers (/api/v1)                          |
|  /auth  /organizations  /restaurants  /menus  /categories  /themes  /public ...  |
+------------------------------------------+----------------------------------------+
```

## 2. Core Architectural Objectives
- **Contract-First Design:** Single source of truth in FastAPI route type hints and Pydantic schemas, exported to OpenAPI 3.1 JSON/YAML and typed frontend contracts.
- **Tenant Isolation:** Enforced via server-derived `TenantContext`. No client header or parameter can bypass server-side membership validation.
- **Predictable Error Contracts:** Adherence to RFC 7807 Problem Details for all 4xx/5xx responses.
- **Zero Drift:** CI/CD pipeline verifies that OpenAPI schemas, TypeScript types, and tests remain synchronized.
