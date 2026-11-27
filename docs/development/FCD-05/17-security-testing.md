# FCD-05 — Security Testing & Attack Verification

## 1. Security Test Suite Matrix

Phase FCD-05 incorporates extensive automated security tests located in `apps/api/tests/security/` and `apps/api/tests/integration/`:

| Test Suite | File Link | Attacks & Scenarios Verified |
|---|---|---|
| **Authentication Security** | [test_authentication_security.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/tests/security/test_authentication_security.py) | Tampered JWT signature rejection, expired token rejection, untrusted issuer/audience rejection, brute-force rate limiting, account lockout after 5 failed attempts |
| **Platform Boundary** | [test_platform_boundary.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/tests/security/test_platform_boundary.py) | Separation of tenant and platform roles, rejection of organization owner trying to access platform admin endpoints, rejection of suspended platform admin |
| **Refresh Rotation & Reuse** | [test_refresh_rotation.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/tests/integration/test_refresh_rotation.py) | Automatic token rotation, immediate detection of token reuse, automatic token family revocation, session revocation upon replay attack |
| **Password Policy & Hashing** | [test_password_hashing.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/tests/unit/credentials/test_password_hashing.py) | Argon2id parameter correctness, constant-time dummy verification, password complexity validation |
| **Tenant Auth Integration** | [test_tenant_auth_integration.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/tests/integration/test_tenant_auth_integration.py) | Bearer JWT tenant resolution, rejection of non-member with 404 (anti-probing), rejection when session revoked |

---

## 2. Test Execution Verification

```bash
python -m pytest apps/api/tests/security -v
```
All security and boundary test cases execute cleanly and pass 100%.
