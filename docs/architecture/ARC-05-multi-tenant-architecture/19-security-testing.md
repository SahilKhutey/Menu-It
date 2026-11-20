# 19 — Security Testing Strategy

## 1. Multi-Tenant Fixture Design

Testing utilizes dual-organization fixtures:
- **Tenant A:** Owner A, Manager A (assigned to Rest A1), Editor A, Menu A1.
- **Tenant B:** Owner B, Manager B (assigned to Rest B1), Editor B, Menu B1.
- **User AB:** Holds distinct memberships in both organizations to verify legitimate switching without leakage.

## 2. Test Execution

All 50 test scenarios (ARC05-T001 through ARC05-T050) are executed automatically in CI via `pytest tests/tenant_isolation/test_arc05_tenant_catalogue.py`.
