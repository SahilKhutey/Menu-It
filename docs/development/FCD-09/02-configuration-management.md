# FCD-09 §02 — Configuration Management

## 1. Centralized Typed Settings

Menu-It uses `pydantic-settings` to load and validate all runtime configuration in `apps/api/src/menu_it/core/config.py`:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env" if (PROJECT_ROOT / ".env").exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )
```

---

## 2. Setting Domains

| Group | Key Settings | Validation Constraints |
| :--- | :--- | :--- |
| **Application** | `app_name`, `app_env`, `app_debug`, `app_version` | If `app_env == "production"`, `app_debug` must be `False` |
| **API Server** | `api_host`, `api_port`, `api_prefix`, `docs_enabled` | `1 <= api_port <= 65535` |
| **CORS** | `cors_origins_raw` -> `cors_origins` | Wildcard `*` is strictly forbidden |
| **Localization** | `default_locale`, `default_timezone`, `default_currency` | Currency must be 3-character uppercase ISO code |
| **File Storage** | `file_storage_backend`, `file_storage_root`, `file_max_upload_bytes` | Max upload bytes bounded between 1KB and 100MB |
| **Notifications** | `notification_email_enabled`, `notification_email_provider` | `console`, `memory`, `smtp` |
| **Logging** | `log_level`, `log_format` | `text` or `json` |

---

## 3. Dependency Injection

Settings are injected via FastAPI dependencies (`get_settings`) or passed directly to infrastructure constructors during startup:

```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```
Global `os.getenv()` calls across business services are strictly forbidden.
