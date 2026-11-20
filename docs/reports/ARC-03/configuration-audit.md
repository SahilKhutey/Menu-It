# ARC-03 Configuration & Environment Audit

**Document ID:** REP-ARC03-CFG  
**Project:** ModularMenu / Menu-It  
**Governing Specification:** ARC-03 §9 (Configuration Architecture) & §11 (Infrastructure Adapters)  
**Status:** Approved & Formally Verified  
**Audit Date:** 2026-11-20  

---

## 1. Overview & Objectives

In accordance with **P-08 (Deployment Portability)** and **ADR-0026 (ARC03-D14)**, ModularMenu must support two distinct deployment editions from a single binary codebase:
1. **Edition A (Managed SaaS Multi-Tenant):** Multi-tenant cloud hosting with PostgreSQL 16, Redis caching, and automated subdomain/path routing.
2. **Edition B (Customer-Hosted Appliance):** Single-server deployment running on local hardware or private VM, with optional Redis and local or managed PostgreSQL.

---

## 2. Configuration Architecture

Configuration is managed centrally via Pydantic Settings (`backend/app/core/config.py`), reading from environment variables with strong type validation and fail-fast startup behavior.

### Configuration Variables Matrix:

| Variable Name | Type | SaaS Default | Customer-Hosted Default | Validation / Constraint |
| :--- | :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | string | `"production"` | `"production"` | `"development"`, `"test"`, `"production"` |
| `DEPLOYMENT_PROFILE`| string | `"saas-multitenant"` | `"customer-hosted"` | Controls feature flags and licensing checks |
| `PROJECT_NAME` | string | `"ModularMenu"` | `"ModularMenu"` | 1–100 chars |
| `API_V1_STR` | string | `"/api/v1"` | `"/api/v1"` | Immutable version prefix |
| `SECRET_KEY` | string | Secure Secret | Secure Secret | Min 32 characters; rejected if default in prod |
| `DATABASE_URL` | string | `postgresql+asyncpg://...` | `postgresql+asyncpg://...` (or sqlite test) | Valid async connection URI |
| `REDIS_URL` | string? | `redis://...` | `None` (Optional) | If omitted, in-memory cache is used |
| `CORS_ORIGINS` | list | `["https://app.modularmenu.com"]` | `["http://localhost:3000"]` | Valid URL list |

---

## 3. Deployment Profile Resolution

The deployment profile (`DEPLOYMENT_PROFILE`) determines runtime adapter selection:
- **Managed SaaS Profile:**
  - Enforces database multi-tenant isolation with tenant ID context.
  - Connects to distributed Redis for rate-limiting and cache invalidation.
  - Requires valid JWT secret and TLS-terminated origins.
- **Customer-Hosted Profile:**
  - Permits single-tenant configuration overrides.
  - Operates seamlessly with or without Redis (`ADR-0025`).
  - Allows local network CORS origins.

---

## 4. Startup Validation & Fail-Fast Behavior

Startup validation is executed during FastAPI initialization (`backend/app/bootstrap.py`):
1. **Schema Validation:** If any required environment variable is missing or malformed (e.g. invalid URI or short secret key in production), Pydantic raises `ValidationError` immediately during module load, preventing the server from starting with an invalid configuration.
2. **Database Connectivity:** The lifespan context manager executes `initialize_database()` on startup, verifying table structures and database accessibility.
3. **Graceful Probes:** The `/health/ready` probe reports `503 Service Unavailable` if database connectivity is lost at runtime, signaling container orchestrators to avoid routing traffic to degraded pods.

---

## 5. Audit Conclusion

The configuration architecture is robust, type-safe, and enforces complete deployment portability without requiring code divergence or separate build artifacts.
