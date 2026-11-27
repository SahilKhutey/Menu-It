# FCD-12 · Document 07: Security Testing & Quality Gates

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Automated Security Scanning Stack

Menu-It integrates multiple automated security scanners in the CI workflow (`.github/workflows/security.yml`):

| Scanner | Target | Policy / Gate |
| :--- | :--- | :--- |
| **Gitleaks** | Repository commits & diffs | Blocks any committed API keys, tokens, or private certificates |
| **Bandit** | Python backend codebase (`apps/api/src`) | Blocks high-severity AST security vulnerabilities |
| **pip-audit** | Python package dependencies | Scans against Python Packaging Advisory Database for CVEs |
| **pnpm audit** | Node frontend dependencies | Scans production dependencies for high/critical advisories |

---

## 2. Security Test Scenarios

- Boundary verification (`test_tenant_isolation_assurance.py`).
- Production settings enforcement (`test_config_validation.py`).
- Security header injection (`test_security_headers.py`).
- Rate limiting quotas and fallbacks (`test_rate_limit.py`).
- Sensitive data masking and log scrubbing (`test_logging_and_redaction.py`).
