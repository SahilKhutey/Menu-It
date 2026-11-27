# FCD-13 · Document 06 — Shared Platform Services Integration

## 1. Objective
Validates that FCD-09 shared platform services (`LocalFileStorage`, `TemplateRenderer`, `NotificationService`, and `AuditEventPublisher`) are integrated consistently and operate through provider-independent abstractions.

---

## 2. Integrated Platform Services

### 2.1 File Storage Service (`LocalFileStorage`)
- **Root-Safe Path Resolution:** Enforces key sandboxing via `_resolve(key)`. Keys attempting path traversal (`../`) raise a `ValueError`.
- **Stream Lifecycle:** Implements asynchronous `put` (BinaryIO stream with SHA-256 computation), `open` (file reader stream), `delete`, and `exists`.

### 2.2 Notification Service & Template Engine (`TemplateRenderer`)
- **Autoescaped Jinja2:** Prevents XSS injection in HTML email bodies by enabling `select_autoescape`.
- **Localized Fallbacks:** Resolves localized templates in `templates/email/<id>/<locale>`, falling back cleanly to English (`en`).
- **Core Templates Verified:** `account-welcome` and `order-status`.

### 2.3 Audit Logging Publisher (`LoggingAuditEventPublisher`)
- **Standardized Audit Schema:** Captures `event_id`, `event_type`, `occurred_at` (UTC), `organization_id`, `actor_user_id`, `resource_type`, `action`, `outcome`, and redacted `metadata`.
- **Secret Redaction:** Passwords, tokens, cookies, and bearer credentials are automatically masked from audit metadata.

---

## 3. Platform Services Test Matrix

| Test ID | Scenario | Expected Outcome | Verification Status |
| :--- | :--- | :--- | :---: |
| `PLAT-T01` | File storage put & read | Byte stream uploaded and verified via SHA-256 | **PASSED** |
| `PLAT-T02` | File storage delete | File unlinked, `exists` returns False | **PASSED** |
| `PLAT-T03` | Path traversal prevention | Directory escaping rejected with ValueError | **PASSED** |
| `PLAT-T04` | Localized email rendering | Template rendered with variable substitution | **PASSED** |
| `PLAT-T05` | Audit event contract | Required audit properties present and valid | **PASSED** |
| `PLAT-T06` | IANA timezone validation | Valid zones accepted; unknown identifiers rejected | **PASSED** |
| `PLAT-T07` | Monetary arithmetic | Currency safety and decimal precision preserved | **PASSED** |

---

## 4. Verification Evidence
Verified by: `apps/api/tests/integration/test_platform_services_integration.py` (all tests passing).
