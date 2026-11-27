# FCD-09 §14 — Sensitive Data Redaction

## 1. Redaction Strategy

To prevent credential leakage into centralized logs, terminal dumps, or audit streams, `redact_mapping()` recursively sanitizes dictionary structures before serialization.

### Sensitive Key Catalog
- `password`
- `token`
- `access_token`
- `refresh_token`
- `authorization`
- `cookie`
- `secret`
- `api_key`
- `client_secret`
- `auth_secret_key`
- `private_key`
- `x-api-key`
- `credential`

---

## 2. Recursive Inspection

`redact_mapping()` handles:
1. Root-level key matching (case-insensitive).
2. Deeply nested dictionaries.
3. Lists of dictionaries (e.g. HTTP headers).
Any matching value is replaced with `"[REDACTED]"`.
