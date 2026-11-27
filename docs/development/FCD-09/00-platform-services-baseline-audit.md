# FCD-09 §00 — Platform Services Baseline & Compatibility Audit

## 1. Executive Summary

Phase **FCD-09 — Core Platform Services & Shared Utilities** establishes the reusable backend services and cross-cutting utilities required by all future Menu-It business modules (restaurants, menus, orders, tables, reservations, billing, analytics).

The central mission of FCD-09 is to create a centralized platform-services layer while preserving the existing modular-monolith architecture:
- **Platform services provide capabilities; business modules own business decisions.**
- Shared utilities and services must be reusable without turning the codebase into a sprawling collection of globally accessible functions with hidden dependencies.
- Infrastructure and execution responsibilities belong to explicit phases:
  - **FCD-09:** Service interfaces, local file storage, email adapter, in-app notification persistence, structured logging, audit contracts, common utilities.
  - **FCD-10:** Distributed queues, Redis/cache, workers, retries, dead letters, background execution.
  - **FCD-11:** Centralized observability, metrics, OpenTelemetry tracing, centralized secret stores.

---

## 2. Monorepo & Technology Stack Inventory

### 2.1 Workspace Structure
- **Package Manager:** `pnpm@11.11.0`
- **Monorepo Packages:**
  - `apps/web`: Next.js 14 customer-facing web application.
  - `apps/admin`: Next.js 14 platform administration application.
  - `apps/api`: FastAPI backend application (`src/menu_it`).
  - `packages/shared-types`: Canonical TypeScript contracts (FCD-06 / FCD-07).
  - `packages/design-tokens`: Visual tokens and CSS variables (FCD-08).
  - `packages/theme-engine`: Multi-tenant theme resolver and WCAG AA contrast validator (FCD-08).
  - `packages/ui`: Accessible React component library (FCD-08).

### 2.2 Backend Environment & Dependencies
- **Python Version:** Python `>= 3.12` (running Python 3.12.9)
- **Web Framework:** FastAPI `>= 0.110.0`
- **Database ORM:** SQLAlchemy `2.x` (asynchronous engine with `asyncpg`)
- **Database Migrations:** Alembic `1.13.x`
- **Configuration & Validation:** Pydantic `2.x` and `pydantic-settings`
- **Template Engine:** Jinja2 `3.1.6` (available in environment; to be pinned in `pyproject.toml`)
- **Current Database Migration Head:** `0005_idempotency_records` (FCD-07)

---

## 3. Existing Foundations & Interoperability Audit

### 3.1 Configuration (`apps/api/src/menu_it/core/config.py`)
- **Current State:** Single `Settings` class using `pydantic_settings.BaseSettings` reading from `.env`.
- **Identified Gaps for FCD-09:**
  - Missing file storage configuration (`FILE_STORAGE_BACKEND`, `FILE_STORAGE_ROOT`, `FILE_MAX_UPLOAD_BYTES`, `FILE_ALLOWED_MIME_TYPES`).
  - Missing notification configuration (`NOTIFICATION_EMAIL_ENABLED`, `NOTIFICATION_EMAIL_PROVIDER`, `NOTIFICATION_DEFAULT_FROM`).
  - Missing default localization settings (`DEFAULT_LOCALE`, `DEFAULT_TIMEZONE`, `DEFAULT_CURRENCY`).
  - Settings class needs freezing (`frozen=True`) and strict validation for port ranges, CORS wildcard restrictions, and upload size bounds.

### 3.2 Logging & Observability (`apps/api/src/menu_it/core/logging.py`)
- **Current State:** Basic `logging.basicConfig()` outputting single-line formatted logs.
- **Identified Gaps for FCD-09:**
  - Lacks structured JSON output option for production.
  - Lacks context logger adapter binding `request_id`, `correlation_id`, and `organization_id`.
  - Lacks recursive sensitive-data redaction for credentials, tokens, cookies, and secret headers.

### 3.3 Database & Tenancy Architecture (FCD-03, FCD-04)
- **Current State:** PostgreSQL database with Row-Level Security (RLS) enabled on tenant tables (`app.current_organization_id`).
- **Target Schema Additions for FCD-09:**
  - `files` table: Tenant-aware file metadata table with RLS applied to `organization_id`.
  - `notifications` table: In-app user notifications with optional `organization_id` scoping and RLS.
  - `notification_deliveries` table: Outbound delivery tracking records with provider references and idempotency keys.
- **Migration Sequence:** Next migration will be `0006_create_files_and_notifications.py` branching from `0005_idempotency_records`.

### 3.4 API & Transport Layer (FCD-07)
- **Current State:** Modular router under `/api/v1` with universal envelope `APIResponse[T]`, `ResponseMeta`, and `APIError`.
- **Integration for FCD-09:**
  - File management endpoints (`POST /api/v1/files`, `GET /api/v1/files/{file_id}`, `GET /api/v1/files/{file_id}/content`, `DELETE /api/v1/files/{file_id}`) must strictly use `APIResponse[T]` and derive tenant context from authenticated server state (`TenantContext`).
  - Notification management endpoints (`GET /api/v1/notifications`, `PATCH /api/v1/notifications/{id}/read`) must expose unread/read state without leaking recipient context.

---

## 4. Scope Boundaries & Anti-Patterns to Prevent

| Invariant | Requirement |
| :--- | :--- |
| **No Tenant Leakage** | Tenant identity is never resolved from a file upload body or notification request payload; it is strictly derived from the validated `TenantContext`. |
| **No Predictable Storage Paths** | Files are stored under generated, non-sequential hashed keys (`organizations/{org_id}/files/{file_id}/{hash}.ext`). Filesystem paths and storage keys are never exposed in public API responses. |
| **Safe File Content Verification** | MIME types reported by the browser and raw extensions are untrusted. Verification must sniff magic bytes and inspect signatures. |
| **No Background Broker in FCD-09** | FCD-09 implements synchronous notification adapters and contracts. Redis, Celery/Arq, and asynchronous worker queues belong strictly to FCD-10. |
| **No Secret Spillage** | Password, token, and authorization headers must be redacted before serialization in logs. Settings must not expose credentials in `__repr__`. |
