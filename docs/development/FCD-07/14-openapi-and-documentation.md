# FCD-07 §14 — OpenAPI 3.1 Specification & Interactive Documentation

## 1. Documentation Endpoints

The Menu-It API automatically publishes interactive OpenAPI documentation generated directly from FastAPI type signatures and Pydantic schemas:

| URL Path | Protocol | Purpose |
| :--- | :--- | :--- |
| `/api/v1/openapi.json` | OpenAPI 3.1 JSON | Raw schema definition consumed by SDK generators and test harnesses |
| `/api/v1/docs` | Swagger UI | Interactive web console for endpoint exploration |
| `/api/v1/redoc` | ReDoc | Reference documentation with three-panel layout |

---

## 2. Tag Organization & Operations Taxonomy

Endpoints are partitioned into logical tags for clear navigation:
- `Health`: System probes, liveness, readiness.
- `System`: Build and environment metadata.
- `Authentication`: Login, credential management, tokens.
- `Identity`: User profile and security settings.
- `Sessions`: Session lifecycle and token refresh.
- `Organizations`: Multi-tenant organization and membership administration.
- `Restaurants`: Multi-tenant restaurant locations and configurations.

---

## 3. Schema Conformance Verification

The automated contract test in `apps/api/tests/contract/test_openapi_specification.py` verifies on every CI build that:
- OpenAPI schema generates without runtime errors.
- Version matches `menu_it.core.metadata.API_VERSION`.
- Tag definitions are present and all core routes are declared.
