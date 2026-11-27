# Menu-It Backend API (`apps/api`)

FastAPI backend application shell for the Menu-It multi-tenant restaurant SaaS platform.

## Features (FCD-02)

- Application factory pattern (`create_application()`)
- Explicit runtime lifespan startup/shutdown hooks (`lifecycle.py`)
- Standardized request ID correlation middleware (`X-Request-ID`)
- Centralized enveloped error handling with sanitized internal messages
- Operational health endpoints:
  - `/api/v1/health` — Basic health status
  - `/api/v1/health/live` — Liveness probe
  - `/api/v1/health/ready` — Readiness probe
  - `/api/v1/system/info` — Non-sensitive application metadata
- Strict Pydantic v2 configuration settings (`config.py`)

## Running Locally

```powershell
python -m uvicorn menu_it.main:app --app-dir apps/api/src --host 127.0.0.1 --port 8000 --reload
```

Interactive API docs: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
