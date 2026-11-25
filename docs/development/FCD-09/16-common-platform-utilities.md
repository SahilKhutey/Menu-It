# FCD-09 §16 — Common Platform Utilities

## 1. Inventory of Utilities

| Utility Module | Primary Functions / Types | Responsibility |
| :--- | :--- | :--- |
| `clock.py` | `Clock`, `SystemClock`, `FrozenClock` | Deterministic UTC time source |
| `identifiers.py` | `new_uuid()`, `parse_uuid()` | Cryptographic UUID generation and parsing |
| `timezone.py` | `get_timezone()`, `to_local_time()`, `now_in_timezone()` | Safe IANA timezone conversions |
| `serialization.py` | `serialize_value()` | Safe serialization of Decimal, UUID, aware Datetime |
| `pagination.py` | `PageRequest` | Standard page, page size, and offset calculation |
| `localization.py` | `resolve_locale()`, `SUPPORTED_LOCALES` | Language resolution and fallback handling |

---

## 2. Invariants

1. **UTC Everywhere:** Datetimes stored in the database or returned in API envelopes must be UTC-aware instants.
2. **Exact Money Serialization:** Decimal monetary values are serialized as exact fixed strings (`format(val, "f")`) to eliminate IEEE 754 floating-point inaccuracies.
3. **No Domain Duplication:** Platform utilities provide raw primitive functions and protocols, reusing FCD-06 domain models for business value objects.
