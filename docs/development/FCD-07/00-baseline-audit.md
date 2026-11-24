# FCD-07 §00 — Baseline & Compatibility Audit

## 1. Executive Summary

Phase **FCD-07 — API & Communication Infrastructure** standardizes the communication mechanisms through which the Menu-It backend exposes functionality to its frontend applications, external systems, and internal modules.

This audit evaluates the existing architecture from FCD-01 through FCD-06 to ensure zero regression and seamless backward compatibility.

---

## 2. Inventory of Existing Foundations

| Concern | Existing Implementation Path | Current Behavior | FCD-07 Action |
| :--- | :--- | :--- | :--- |
| **API Base Path** | `/api/v1` via `apps/api/src/menu_it/core/config.py` | Authoritative base prefix configured in settings | Retain `/api/v1` URL path versioning |
| **App Factory** | `apps/api/src/menu_it/application.py` (`create_application()`) | Manages lifespan, state, middleware, CORS, routers | Extend with security headers, timing, and modular routers |
| **Request ID** | `apps/api/src/menu_it/middleware/request_id.py` | Reads/generates UUID for `request.state.request_id` and sets `X-Request-ID` header | Retain and enhance with bounded validation and logging |
| **Error Envelope** | `apps/api/src/menu_it/exceptions/handlers.py` | Enveloped `{success, data, error, meta}` format | Extend to map FCD-06 domain errors and standardized validation |
| **Router Composition** | `apps/api/src/menu_it/api/v1/router.py` | Flat router importing health, system, auth, identity, sessions, orgs | Modernize into modular, domain-oriented routing tree |
| **CORS Policy** | `CORSMiddleware` in `application.py` | Configurable `CORS_ORIGINS` with credentials | Retain explicit allowed origins and add exposed headers |
| **Auth Pipeline** | FCD-05 (`menu_it.authentication`, `menu_it.sessions`, `menu_it.authorization`) | Bearer token validation, session checks, permission checks | Integrate cleanly via FastAPI dependencies in `api/dependencies/` |
| **Tenant Context** | FCD-04 (`menu_it.tenancy.context`, `TenantResolver`) | Server-derived immutable `TenantContext` | Integrate as standard dependency for tenant endpoints |
| **Domain Models** | FCD-06 (`menu_it.domain`, `menu_it.contracts`) | Pure entities, value objects, domain error hierarchy | Map domain exceptions to standardized HTTP responses |
| **Frontend Client** | `apps/web/src/services/api-client.ts` & `admin` | Basic fetch wrapper with envelope parsing | Standardize into robust client in `@menu-it/shared-types` / apps |

---

## 3. Audit Checklist Results

- **AUD-01 (API prefix):** PASS. `/api/v1` is authoritative and configured centrally.
- **AUD-02 (Application factory):** PASS. Single authoritative factory in `application.py`.
- **AUD-03 (Request ID):** PASS. `X-Request-ID` is assigned on every request and response.
- **AUD-04 (Error envelope):** PASS. `{success: false, data: null, error: {...}, meta: {...}}` contract preserved.
- **AUD-05 (Validation errors):** EXTENSION REQUIRED. Normalize Pydantic validation errors into structured `APIErrorDetail` list without exposing internal python paths or sensitive data.
- **AUD-06 (Router structure):** EXTENSION REQUIRED. Modularize routers into domain module packages (`v1/endpoints/` and `v1/modules/`).
- **AUD-07 (CORS):** PASS. Explicit allowed origins configured.
- **AUD-08 (Auth integration):** PASS. FCD-05 provides bearer token, principal, and permission dependencies.
- **AUD-09 (Tenant integration):** PASS. FCD-04 provides server-derived `TenantContext` and PostgreSQL RLS.
- **AUD-10 (Frontend client):** EXTENSION REQUIRED. Reusable client with 204 support, request ID preservation, and shared TypeScript contracts.
- **AUD-11 (OpenAPI):** PASS. Generated OpenAPI documents versioned endpoints.
- **AUD-12 (Tests):** PASS. 219 tests currently passing across unit, contract, and integration suites.
