# FCD-09 §03 — Environment & Secret Handling

## 1. Environment File Conventions

```
apps/api/
├── .env.example          # Tracked in git: complete template with non-sensitive defaults
├── .env.development      # Local development overrides (gitignored)
├── .env.test             # Automated testing configuration (gitignored)
└── .env                  # Active runtime environment (gitignored)
```

Only `.env.example` is committed to version control. Real credentials, database passwords, and JWT secret keys are strictly excluded from git.

---

## 2. Secret Redaction in Memory & Logs

The `Settings` class implements a custom `__repr__` method to prevent accidental secret leakage:

```python
def __repr__(self) -> str:
    return (
        f"Settings(app_name={self.app_name!r}, app_env={self.app_env!r}, "
        f"api_port={self.api_port}, auth_secret_key='[REDACTED]')"
    )
```

Additionally, sensitive fields (`password`, `token`, `secret`, `authorization`, `cookie`, `key`) are stripped automatically by `menu_it.platform.common.redaction.redact_mapping()` prior to log serialization or audit event emission.
