# FCD-11 · Document 24: Security, Resilience, Chaos & Recovery Testing Framework

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Multi-Tier Testing Pyramid

Menu-It validates security and reliability through four automated test tiers:

1. **Unit Testing:** Fast, hermetic tests validating config validators, redaction helpers, timeouts, and circuit breaker state transitions (`apps/api/tests/unit/`).
2. **Security Assurance Testing:** Explicit boundary violation tests (`assert_tenant_boundary`), permission denied assertions (`require_permission`), and header injections (`apps/api/tests/security/`).
3. **Integration & Fallback Testing:** Verifying database RLS enforcement, rate limiting fallbacks, audit logging fallback logs, and Prometheus metrics formatting.
4. **Resilience & Chaos Testing:** Simulating network partitions, slow downstream dependencies, sudden Redis disconnections, and database pool saturation.

---

## 2. Test Execution Verification

All tests run in automated CI on every pull request. No PR may merge unless 100% of unit, integration, and security tests pass without warnings or regressions.
