# FCD-02 — Backend Runtime Lifecycle

## 1. Lifecycle Overview
The backend application runtime lifecycle manages deterministic startup, resource provisioning, state tracking, and graceful shutdown via FastAPI's `lifespan` context manager.

## 2. Startup Sequence
1. **Module Import:** Uvicorn imports `menu_it.main:app`.
2. **Factory Invocation:** `create_application()` loads cached `Settings` from `core/config.py`.
3. **Logging Setup:** `configure_logging(settings.log_level)` sets unified formatting.
4. **Middleware Registration:** Middlewares are registered (`RequestIDMiddleware`, `CORSMiddleware`).
5. **Exception Handler Attachment:** Centralized handlers for `HTTPException`, `RequestValidationError`, and `Exception` are registered.
6. **API Route Inclusion:** `api_router` mounted under `settings.api_prefix` (`/api/v1`).
7. **ASGI Lifespan Startup:** `initialize_runtime(application)` executes.
8. **Readiness State:** `application.state.runtime_ready = True`.
9. **Traffic Acceptance:** Server accepts external HTTP requests on port 8000.

## 3. Shutdown Sequence
1. **Signal Reception:** Uvicorn captures `SIGINT` or `SIGTERM`.
2. **Traffic Drain:** Server halts receiving new connections while processing in-flight requests.
3. **ASGI Lifespan Teardown:** `shutdown_runtime(application)` executes.
4. **Readiness State Reset:** `application.state.runtime_ready = False`.
5. **Resource Teardown:** Database connections and background queues (introduced in FCD-03+) are safely terminated.
6. **Process Exit:** Clean process termination.

## 4. Invariant Protection
- Readiness probes (`/api/v1/health/ready`) return `HTTP 503` if called prior to lifespan completion.
- Startup failures cleanly prevent the process from falsely reporting ready status.
