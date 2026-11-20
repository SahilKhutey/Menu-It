# 20 — Verification & Validation Plan

## 1. Release Verification Gates

1. **Gate 1: Architecture Manifest Compliance:** All tenant tables match `tenant_owned_resources.yaml`.
2. **Gate 2: RLS DDL Verification:** All required tables enforce `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY`.
3. **Gate 3: Security Test Suite:** 100% pass rate on `tests/tenant_isolation/test_arc05_tenant_catalogue.py`.
4. **Gate 4: Runtime Role Safety:** DB runtime user validated with `NOSUPERUSER` and `NOBYPASSRLS`.
