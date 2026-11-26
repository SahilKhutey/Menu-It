# FCD-13 · Document 02 — Application Startup & Lifecycle Validation

## 1. Objective
Validates that the API backend, frontend applications, and background worker systems start, operate, and shut down as coordinated platform services without resource leaks or unhandled startup crashes.

---

## 2. Startup Lifecycle & Composition Root

### 2.1 FastAPI Lifespan Protocol
Application startup is managed centrally via `menu_it.application.create_application` using FastAPI's async lifespan context manager:

```python
@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    await initialize_runtime(application)
    try:
        yield
    finally:
        await shutdown_runtime(application)
```

1. **`initialize_runtime(app)`:**
   - Reads immutable, validated `Settings` from `get_settings()`.
   - Configures structured JSON logging with correlation IDs.
   - Builds singleton `PlatformServices` container (`LocalFileStorage`, `NotificationService`, `CacheService`, `RateLimiter`).
   - Marks `app.state.runtime_ready = True`.
2. **`shutdown_runtime(app)`:**
   - Marks `app.state.runtime_ready = False`.
   - Gracefully disposes the SQLAlchemy async database engine (`await engine.dispose()`).
   - Closes background connections.

### 2.2 Background Worker Lifecycle
ARQ background worker lifecycle is managed via `menu_it.platform.jobs.worker.WorkerSettings`:
- `on_startup(ctx)`: Initializes platform services and database connection pools inside worker execution context.
- `on_shutdown(ctx)`: Disposes worker connections and drains in-flight job tasks gracefully.

---

## 3. Lifecycle Validation Matrix

| Test ID | Test Scenario | Expected Outcome | Verification Status |
| :--- | :--- | :--- | :---: |
| `LIFE-T01` | API normal startup | `runtime_ready` set to True, all routes mounted | **PASSED** |
| `LIFE-T02` | Invalid environment config | Pydantic `ValidationError` raised, safe fail-closed | **PASSED** |
| `LIFE-T03` | API graceful shutdown | Engine connection pool disposed, no dangling sockets | **PASSED** |
| `LIFE-T04` | Worker startup hook | Services container injected into ARQ worker context | **PASSED** |
| `LIFE-T05` | Worker shutdown hook | Clean resource drain, zero job starvation | **PASSED** |
| `LIFE-T06` | Database health probe | Returns 200 on healthy connection, 503 on offline | **PASSED** |
| `LIFE-T07` | Liveness & Metrics | `/api/v1/health` and `/api/v1/metrics` respond immediately | **PASSED** |

---

## 4. Verification Evidence
Verified by automated integration test: `apps/api/tests/integration/test_lifecycle_integration.py` (all tests passing).
