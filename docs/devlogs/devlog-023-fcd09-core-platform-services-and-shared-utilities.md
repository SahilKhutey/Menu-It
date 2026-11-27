# Devlog 023 — FCD-09 Core Platform Services & Shared Utilities

**Date:** 2026-11-25  
**Author:** AI Architecture & Core Engineering Team  
**Subject:** Implementation, Verification, and Release of FCD-09 Core Platform Services & Shared Utilities  
**Milestone:** `v1.0.0-fcd09`  
**Phase:** Foundational Core Development (FCD-09)  
**Parent Documents:** FCD-01 through FCD-08, ARC-05 (Multi-Tenancy), ARC-06 (Persistence), ARC-07 (API Infrastructure)  

---

## 1. Objectives & Architectural Context

Phase **FCD-09** establishes the reusable backend platform services and shared utilities that all future business modules (restaurant/branch management, menus, QR ordering, reservations, billing, analytics, and platform administration) depend on.

The governing architecture principle is:
> **Platform services provide capabilities; business modules own business decisions.**

Shared services are strictly encapsulated, dependency-injected via FastAPI composition roots, and tenant-isolated at both the repository and database (PostgreSQL Row-Level Security) layers.

---

## 2. Completed Work Packages & Deliverables

### WP-01: Centralized Configuration Management
- Refactored `apps/api/src/menu_it/core/config.py` to leverage `pydantic-settings` with `frozen=True` to guarantee runtime immutability.
- Added typed, validated configurations for storage backend (`storage_backend`, `storage_local_root`, `storage_max_file_size_bytes`, `storage_allowed_mime_types`), notifications (`notifications_email_provider`, `smtp_*`), logging (`log_level`, `log_format`), and platform defaults.
- Implemented field validators for port ranges, ISO 4217 currencies, and storage limits.
- Implemented `_mask_secret()` in `Settings.__repr__()` ensuring passwords, secret keys, and tokens are never exposed in log outputs or console dumps.
- Created `apps/api/.env.example` documenting all environment variables and default values.
- Verified with 9 dedicated unit tests in `apps/api/tests/unit/core/test_platform_config.py`.

### WP-02: File Handling & Storage Abstraction
- Defined provider-agnostic storage protocol `FileStorage` in `menu_it.platform.files.domain.storage` with `save()`, `get()`, `delete()`, and `exists()`.
- Implemented `LocalFileStorage` adapter in `menu_it.platform.files.infrastructure.local_storage` providing directory path sandboxing, atomic file writes (`.tmp` write followed by `replace`), and mime-type preservation.
- Implemented rigorous upload validation in `menu_it.platform.files.application.validation`:
  - Enforced file extension validation against an allowed whitelist (`.jpg`, `.jpeg`, `.png`, `.webp`, `.pdf`).
  - Implemented magic-byte sniffing (verifying genuine binary signatures for JPEG, PNG, WEBP, and PDF) to prevent content spoofing.
  - Implemented strict RFC 3986 filename sanitization (stripping traversal characters `..`, slashes, and control characters).
- Implemented non-predictable internal storage keys: `organizations/{organization_id}/files/{file_id}/{hash}.{ext}`.
- Added `files` database model and Alembic migration `0006_create_files_and_notifications.py` with PostgreSQL Row-Level Security policies enforcing organization isolation.
- Implemented `FileRepository` with async SQLAlchemy 2.x and `FileService` handling transactional upload, retrieval, and soft deletion.
- Implemented REST API endpoints in `menu_it.api.v1.endpoints.files`:
  - `POST /api/v1/files`: Multipart upload returning `APIResponse[FileResponse]`.
  - `GET /api/v1/files/{file_id}`: Metadata retrieval with tenant ownership verification.
  - `GET /api/v1/files/{file_id}/content`: Binary streaming download with Content-Disposition headers.
  - `DELETE /api/v1/files/{file_id}`: Soft deletion marking file inactive.

### WP-03: Notification Infrastructure & Multi-Channel Adapters
- Defined notification contracts in `menu_it.platform.notifications.domain.contracts`: `NotificationChannel` (email, in-app), `NotificationStatus`, `NotificationMessage`, and `NotificationResult`.
- Implemented Jinja2-based template rendering engine in `menu_it.platform.notifications.application.renderer`:
  - Autoescaping enabled strictly for HTML templates to protect against XSS injection.
  - Locale resolution supporting Indian multilingual context (`en`, `hi`) with automatic English fallback.
  - Created templates for `account-welcome` and `order-status`.
- Implemented email delivery adapters in `menu_it.platform.notifications.infrastructure.email_adapter`:
  - `InMemoryEmailProvider` for deterministic test assertions.
  - `ConsoleEmailProvider` for local developer observability.
  - `EmailNotificationAdapter` fulfilling `NotificationChannelAdapter`.
- Added `notifications` and `notification_deliveries` database tables with PostgreSQL RLS enforcing tenant boundaries.
- Implemented `NotificationRepository` and `NotificationService` handling multi-channel dispatches, retry counts, error message capture, and in-app feed operations.
- Implemented REST API endpoints in `menu_it.api.v1.endpoints.notifications`:
  - `GET /api/v1/notifications`: Paginated in-app notifications feed.
  - `PATCH /api/v1/notifications/{id}/read`: Mark notification as read.

### WP-04: Structured Application Logging & Sensitive Data Redaction
- Implemented `menu_it.platform.common.redaction.redact_mapping` recursively masking sensitive fields (passwords, tokens, secrets, API keys, CVVs, credit cards).
- Implemented `JsonFormatter` in `menu_it.core.logging` standardizing structured JSON logs with UTC timestamps, log level, message, module, request ID, correlation ID, and tenant context.
- Implemented `ContextLoggerAdapter` and `get_context_logger()` enabling contextual logging with automatic tenant/request correlation.

### WP-05: Audit Event Contracts & Publishers
- Defined `AuditEvent` domain model in `menu_it.platform.audit.contracts` capturing event type, timestamp, tenant ID, actor identity, client IP, action, resource, status, and payload.
- Implemented `AuditEventPublisher` protocol with `InMemoryAuditEventPublisher` (for unit testing) and `LoggingAuditEventPublisher` (for audit trail stream logging).

### WP-06: Common Platform Utilities
- **Clock:** `Clock` protocol with `SystemClock` (strict UTC) and `FrozenClock` (for deterministic time-travel testing).
- **Identifiers:** `new_uuid()` and `parse_uuid()` with validation error handling.
- **Timezones:** `get_timezone()`, `to_local_time()`, and `now_in_timezone()` supporting `Asia/Kolkata` and IANA timezone offsets.
- **Serialization:** `serialize_value()` safely serializing UUIDs, Datetimes, Decimals, and Pydantic models.
- **Pagination:** Universal `PageRequest` supporting standard cursor and limit/offset pagination.
- **Localization:** `resolve_locale()` resolving `en`, `hi` with fallback handling.

### WP-07: Service Registration & Composition Root
- Implemented `PlatformServices` container in `menu_it.platform.container` aggregating file storage, audit publishing, template rendering, and notification adapters.
- Wired platform container initialization and teardown into the FastAPI application lifespan in `menu_it.core.lifecycle`.
- Exposed FastAPI dependency injectors for `FileService`, `NotificationService`, and `PlatformServices`.

### WP-08: Health Check & Probes Integration
- Added `/health/platform` probe validating file storage and notification engine availability.
- Enhanced `/health/ready` probe with bounded database connectivity checks.

### WP-10: Frontend Integration Contracts
- Created `packages/shared-types/src/platform/files.ts` and `notifications.ts`.
- Exported platform contracts in `packages/shared-types/src/index.ts`.
- Verified zero TypeScript compilation errors across the monorepo.

### WP-11: Technical Documentation Suite
- Authored 26 comprehensive technical documents in `docs/development/FCD-09/` (`00-platform-services-baseline-audit.md` through `25-acceptance-report.md`).

---

## 3. Verification & Metrics

```
pnpm format:check           -> PASS (All matched files use Prettier code style)
pnpm -r typecheck           -> PASS (6 workspace projects, 0 errors)
pnpm -r lint                -> PASS (Zero ESLint warnings or errors)
pytest apps/api/tests -q    -> PASS (296 passed in 25.45s, 0 failures, 0 errors)
```

---

## 4. Next Steps

With FCD-09 complete, the platform possesses enterprise-grade foundation services for configuration, storage, notifications, logging, audit trails, and multi-tenant isolation. The next development phase (FCD-10) will build upon these services to introduce background processing, Redis queues, and asynchronous event workers.
