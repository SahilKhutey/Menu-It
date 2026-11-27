# FCD-06 §04 — Shared Value Objects

## 1. Value Object Catalog

Menu-It defines a comprehensive catalog of domain value objects in `apps/api/src/menu_it/domain/value_objects/`:

| Value Object | Responsibility | Key Invariants |
| :--- | :--- | :--- |
| `Currency` | Currency identity & formatting | 3-letter uppercase ISO 4217, validated against supported registry (USD, EUR, GBP, CAD, AUD, JPY, INR, CHF, SGD, AED) |
| `Money` | Exact monetary representation | Enforces Python `Decimal`, non-negative where required, strict currency matching on operations, no floating-point |
| `Percentage` | Fractional rates (0–100%) | Decimal precision between 0.00 and 100.00; provides `.multiplier` |
| `TaxRate` | Applied tax percentages | Validates percentage, calculates tax on Decimal or `Money` |
| `EmailAddress` | Contact email identity | RFC-compliant parsing, casefold normalization, maximum 320 chars |
| `PhoneNumber` | Global telephone contact | Google `phonenumbers` E.164 parsing, international formatting |
| `Slug` | URL-safe identifier | Kebab-case alphanumeric characters, single hyphens, <= 100 chars |
| `Address` | Physical geographic location | Required `line_1`, `locality`, ISO 3166-1 alpha-2 `country_code` |
| `TimeZone` | Temporal localization | Authoritative IANA zone verification via `zoneinfo.ZoneInfo` |
| `TimeRange` | Daily operating interval | Half-open `[opens_at, closes_at)`, midnight-crossing support, interval overlap logic |
| `DailyOperatingHours` | Single weekday schedule | ISO Weekday (1-7), closed day validation, non-overlapping shift check |
| `WeeklyOperatingSchedule` | Full 7-day schedule | Exactly 7 unique weekdays (Monday-Sunday), open-at queries |

## 2. Monetary Safety (ADR-0010)

Floats are strictly forbidden in monetary domains. `Money` guarantees:
1. Addition/subtraction between matching currencies only.
2. Multiplication by integer or Decimal factors only (rejecting floats).
3. Minor unit quantization matching currency decimal precision (e.g., 2 decimal places for USD, 0 for JPY).
