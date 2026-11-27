# FCD-12 · Document 02: Backend Testing Infrastructure

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Backend Pytest Architecture

Backend testing is configured in `apps/api/pyproject.toml` with strict options:
- `testpaths = ["tests"]`
- `asyncio_mode = "auto"`
- Custom markers:
  - `unit`: Isolated, in-memory domain and service tests.
  - `integration`: Tests requiring external infrastructure (database, cache, workers).
  - `api`: API endpoint, middleware, and router tests.
  - `security`: Authentication, authorization, and tenant isolation tests.
  - `database`: PostgreSQL schema, transaction, and migration tests.
  - `tenant`: Multi-tenant isolation and boundary tests.
  - `slow`: Long-running or performance-sensitive tests.

---

## 2. Test Execution Commands

```bash
# Run unit and security tests (fast)
python -m pytest apps/api/tests/unit apps/api/tests/security -v

# Run complete test suite with coverage report
python -m pytest apps/api/tests -v --cov=menu_it --cov-report=term-missing --cov-report=xml:coverage.xml

# Run excluding slow tests
python -m pytest apps/api/tests -m "not slow" -v
```
