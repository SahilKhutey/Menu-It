# Menu-It — Dependency Management & Security Policy

**Document ID:** FCD01-DOC-09  
**Phase:** FCD-01 Development Environment & Repository Foundation  
**Audience:** All Software Engineers & Security Reviewers  

---

## 1. Principles

External third-party dependencies introduce supply chain risk, bundle bloat, and maintenance overhead. Menu-It enforces strict guidelines before adopting any new library:

1. **Strict Necessity:** Do not introduce a library for functionality easily implemented in standard library code.
2. **Deterministic Locking:** Every dependency must be captured with an exact lockfile (`pnpm-lock.yaml` for frontend, `requirements.txt` / `uv.lock` for backend).
3. **Automated Vulnerability Scanning:** Automated scanning in CI must detect known CVEs before merging.
4. **License Compatibility:** Only permissive licenses (MIT, Apache 2.0, BSD-3-Clause) are permitted. Copyleft licenses (GPL, AGPL) are prohibited in frontend client bundles.

---

## 2. Frontend Dependency Standards

- **Package Manager:** `pnpm` exclusively. Never run `npm install` or `yarn install`.
- **Lockfile Integrity:** CI enforces `--frozen-lockfile`. Modifying dependencies without committing `pnpm-lock.yaml` triggers an immediate build failure.
- **Bundle Budget:** Any dependency added to `frontend/` must be vetted for bundle size impact (target < 120 kB initial gzipped JS).

---

## 3. Backend Dependency Standards

- **Package Manager:** `pip` / `uv` within an isolated Python 3.12 virtual environment.
- **Specification:** Pinned version ranges in `backend/requirements.txt` and `pyproject.toml`.
- **Minimal Core:** Keep core dependencies restricted to FastAPI, SQLAlchemy, Alembic, Pydantic, and verified security utilities (Argon2, Python-Jose).
