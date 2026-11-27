# FCD-03 — Verification & Test Evidence Report

## 1. Test Execution Summary

- **Total Backend Pytest Suite:** 40 passed in 1.17s (100% pass rate)
- **Total Code Coverage:** 95% across `menu_it` backend package
- **Frontend Typecheck:** 0 errors across 4 workspace projects
- **Frontend ESLint:** 0 warnings, 0 errors
- **Ruff Linter:** 100% compliant (`All checks passed!`)
- **Ruff Formatter:** 100% compliant (`57 files already formatted`)

---

## 2. Test Execution Details

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\ASUS\Documents\Menu-it\apps\api
configfile: pyproject.toml
plugins: anyio-4.12.1, hypothesis-6.156.6, asyncio-1.4.0, cov-7.1.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function
collected 40 items

apps\api\tests\integration\test_application.py::test_application_factory PASSED [  2%]
apps\api\tests\integration\test_application.py::test_application_metadata PASSED [  5%]
apps\api\tests\integration\test_application.py::test_application_routes_registered PASSED [  7%]
apps\api\tests\integration\test_cors.py::test_allowed_frontend_origin PASSED [ 10%]
apps\api\tests\integration\test_cors.py::test_unapproved_origin_not_authorized PASSED [ 12%]
apps\api\tests\integration\test_database_connection.py::test_database_connection PASSED [ 15%]
apps\api\tests\integration\test_database_health.py::test_database_health_endpoint_healthy PASSED [ 17%]
apps\api\tests\integration\test_database_health.py::test_database_health_endpoint_unreachable PASSED [ 20%]
apps\api\tests\integration\test_database_health.py::test_readiness_with_database_dependency PASSED [ 22%]
apps\api\tests\integration\test_exceptions.py::test_http_exception_format PASSED [ 25%]
apps\api\tests\integration\test_exceptions.py::test_unexpected_exception_is_sanitized PASSED [ 27%]
apps\api\tests\integration\test_health.py::test_health_endpoint PASSED   [ 30%]
apps\api\tests\integration\test_health.py::test_liveness_endpoint PASSED [ 32%]
apps\api\tests\integration\test_health.py::test_readiness_after_startup PASSED [ 35%]
apps\api\tests\integration\test_health.py::test_readiness_before_startup PASSED [ 37%]
apps\api\tests\integration\test_migrations.py::test_alembic_migration_lifecycle PASSED [ 40%]
apps\api\tests\integration\test_models.py::test_create_tenant PASSED     [ 42%]
apps\api\tests\integration\test_models.py::test_restaurant_requires_valid_tenant PASSED [ 45%]
apps\api\tests\integration\test_models.py::test_tenant_slug_uniqueness PASSED [ 47%]
apps\api\tests\integration\test_models.py::test_restaurant_slug_unique_per_tenant PASSED [ 50%]
apps\api\tests\integration\test_models.py::test_tenant_deletion_restricted_when_restaurant_exists PASSED [ 52%]
apps\api\tests\integration\test_repositories.py::test_get_tenant_by_slug PASSED [ 55%]
apps\api\tests\integration\test_repositories.py::test_missing_tenant_returns_none PASSED [ 57%]
apps\api\tests\integration\test_repositories.py::test_tenant_slug_exists PASSED [ 60%]
apps\api\tests\integration\test_repositories.py::test_restaurant_repository_crud_and_filtering PASSED [ 62%]
apps\api\tests\integration\test_request_id.py::test_request_id_is_generated PASSED [ 65%]
apps\api\tests\integration\test_request_id.py::test_valid_request_id_is_preserved PASSED [ 67%]
apps\api\tests\integration\test_request_id.py::test_invalid_request_id_is_replaced PASSED [ 70%]
apps\api\tests\integration\test_system.py::test_system_information PASSED [ 72%]
apps\api\tests\integration\test_transactions.py::test_create_tenant_with_restaurant_success PASSED [ 75%]
apps\api\tests\integration\test_transactions.py::test_failed_operation_rolls_back_atomically PASSED [ 77%]
apps\api\tests\unit\test_config.py::test_default_settings PASSED         [ 80%]
apps\api\tests\unit\test_config.py::test_cors_origins_parsing PASSED     [ 82%]
apps\api\tests\unit\test_config.py::test_empty_cors_origins PASSED       [ 85%]
apps\api\tests\unit\test_config.py::test_database_settings_defaults PASSED [ 87%]
apps\api\tests\unit\test_config.py::test_database_custom_settings PASSED [ 90%]
apps\api\tests\unit\test_lifecycle.py::test_runtime_initialization PASSED [ 92%]
apps\api\tests\unit\test_lifecycle.py::test_runtime_shutdown PASSED      [ 95%]
apps\api\tests\unit\test_lifecycle.py::test_runtime_reinitialization PASSED [ 97%]
apps\api\tests\unit\test_metadata.py::test_metadata_constants PASSED     [100%]

============================= 40 passed in 1.17s ==============================
```
