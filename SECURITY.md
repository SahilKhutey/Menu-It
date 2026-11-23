# Security Policy

Menu-It takes the security of its modular multi-tenant restaurant platform with the utmost seriousness.

---

## 1. Reporting Vulnerabilities

If you discover a security vulnerability in Menu-It, **please report it privately**. 

Do **not** publish vulnerability details or create public GitHub issues before remediation has been coordinated.

To report a vulnerability:
- Submit details privately to the repository maintainer / security team at `security@modularmenu.in` (or via GitHub Private Vulnerability Reporting).
- Include detailed reproduction steps, impacted versions, and proof of concept if available.

We acknowledge reports within 48 hours and provide a remediation timeline based on severity.

---

## 2. Core Security Invariants

All code within Menu-It is held to the following non-negotiable security requirements:

1. **No Committed Secrets:** Credentials, private keys, API secrets, and tokens must never enter version control.
2. **Tenant Isolation:** Multi-tenant boundaries are defended in depth with PostgreSQL Row-Level Security (`FORCE ROW LEVEL SECURITY`). No query may cross tenant boundaries without authorization.
3. **Strict Input Validation:** All external input must be validated via Pydantic or JSON schemas before processing.
4. **OWASP Top 10 Defense:** All database queries utilize parameterized SQLAlchemy 2.0 ORM expressions to neutralize SQL injection; HTML outputs are strictly sanitized.
5. **Session & Password Security:** Passwords must be hashed using Argon2id; session tokens must use 256-bit CSPRNG generation with automatic rotation.
6. **Supply Chain Defense:** Third-party dependencies are pinned with lockfiles and regularly scanned for known CVEs.

---

## 3. Supported Versions

| Version | Actively Supported | Security Patches |
| :--- | :--- | :--- |
| `1.x` (develop / main) | Yes | Yes |
