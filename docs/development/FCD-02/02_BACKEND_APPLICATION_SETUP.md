# FCD-02 — Backend Application Setup & Directory Architecture

## 1. Overview
The backend application shell is located at `apps/api` and encapsulates the `menu_it` Python package.

## 2. Directory Architecture
```
apps/api/
├── src/
│   └── menu_it/
│       ├── __init__.py           # Package entry and factory re-export
│       ├── main.py               # Instantiated app object for Uvicorn ASGI
│       ├── application.py        # create_application() factory
│       ├── core/                 # Core configurations and metadata
│       │   ├── config.py         # Pydantic Settings and CORS origins
│       │   ├── lifecycle.py      # Runtime initialize and shutdown hooks
│       │   ├── logging.py        # Standardized application logging
│       │   └── metadata.py       # Title, description, version constants
│       ├── api/v1/               # Version 1 API endpoints and routers
│       │   ├── router.py         # Sub-router aggregation
│       │   └── endpoints/        # Health and system endpoints
│       ├── middleware/           # Request ID correlation middleware
│       ├── exceptions/           # RFC 7807/9457 centralized exception handlers
│       ├── schemas/              # Common response models and health schemas
│       └── shared/               # Shared domain placeholder
├── tests/                        # Unit and integration test suites
│   ├── conftest.py               # Shared TestClient fixtures
│   ├── unit/                     # Config, lifecycle, metadata tests
│   └── integration/              # Application, CORS, health, request ID tests
├── pyproject.toml                # Dependencies, Ruff, Pytest configuration
└── README.md                     # Backend developer guide
```

## 3. Application Factory Pattern
The application factory `create_application() -> FastAPI` in `menu_it/application.py` ensures:
1. Deterministic configuration loading and logging initialization.
2. Fresh application instances per test scenario without state contamination.
3. Decoupled ASGI entrypoint in `menu_it/main.py`.
