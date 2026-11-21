# 16. OpenAPI and Contract Generation

## 1. OpenAPI 3.1 Pipeline
- FastAPI auto-generates schema at `/openapi.json`.
- Export scripts write `backend/openapi/openapi.json` and `openapi.yaml`.
- Schema validated via `backend/app/scripts/validate_openapi.py`.
