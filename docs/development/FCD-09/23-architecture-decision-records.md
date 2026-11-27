# FCD-09 §23 — Architecture Decision Records (ADRs)

## ADR-09-001: Centralized Typed Configuration
- **Status:** Accepted
- **Context:** Multiple modules accessing environment variables via raw `os.getenv()` leads to missing validation and runtime crashes.
- **Decision:** Consolidate all configuration into a frozen, validated `pydantic_settings.BaseSettings` singleton (`apps/api/src/menu_it/core/config.py`).
- **Consequences:** Startup fails fast if invalid configurations exist; runtime code cannot mutate settings; zero scattered `os.getenv()` calls.

---

## ADR-09-002: Provider-Independent File Storage Abstraction
- **Status:** Accepted
- **Context:** Coupling business code to a specific filesystem or AWS S3 SDK prevents flexible deployment across appliances and cloud providers.
- **Decision:** Introduce `FileStorage` protocol with `put`, `open`, `delete`, `exists` methods, backed initially by `LocalFileStorage`.
- **Consequences:** Business modules request file operations via `FileService` without knowing storage topology or SDK details.

---

## ADR-09-003: Non-Predictable Internal Storage Keys
- **Status:** Accepted
- **Context:** Storing files by their original name or sequential IDs allows enumeration and path traversal attacks.
- **Decision:** Generate internal storage keys partitioned by organization and UUIDs with random hex suffixes (`organizations/{org_id}/files/{file_id}/{hash}.ext`).
- **Consequences:** Eliminates filename collisions and prevents storage path enumeration.

---

## ADR-09-004: Replaceable Notification Channel Adapters
- **Status:** Accepted
- **Context:** Sending messages directly through third-party APIs ties business logic to external vendors.
- **Decision:** Decouple delivery behind `NotificationChannelAdapter` and `EmailProvider` protocols, providing `ConsoleEmailProvider` and `InMemoryEmailProvider` for local environments.
- **Consequences:** Delivery providers can be swapped or tested with zero business logic changes.

---

## ADR-09-005: Autoescaped Jinja2 Notification Templates
- **Status:** Accepted
- **Context:** String interpolation in notification emails opens HTML injection vulnerabilities.
- **Decision:** Use Jinja2 with autoescaping enabled by default for HTML templates, plain-text alternatives, and English locale fallback.
- **Consequences:** Prevents XSS/HTML injection attacks in transactional emails while supporting localized delivery.
