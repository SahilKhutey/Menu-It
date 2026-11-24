# FCD-06 §09 — Business Rules & Invariants Catalog

## 1. Catalog of Core Domain Invariants

| Invariant ID | Rule Description | Enforced By | Error Raised |
| :--- | :--- | :--- | :--- |
| `INV-MONEY-01` | Floating-point numbers are strictly forbidden in monetary operations | `Money.__post_init__` | `ValidationDomainError` |
| `INV-MONEY-02` | Monetary values must be finite (no NaN or Infinity) | `Money.__post_init__` | `ValidationDomainError` |
| `INV-MONEY-03` | Currency operations require identical currency codes | `Money.add()`, `Money.subtract()` | `ValidationDomainError` |
| `INV-CURR-01` | Currencies must exist in the supported ISO 4217 registry | `Currency.__post_init__` | `ValidationDomainError` |
| `INV-ADDR-01` | Physical addresses must specify `line_1`, `locality`, and 2-letter ISO country code | `Address.__post_init__` | `ValidationDomainError` |
| `INV-TZ-01` | Timezone strings must resolve to valid IANA names | `TimeZone.__post_init__` | `ValidationDomainError` |
| `INV-TIME-01` | Opening and closing times within a range cannot be identical | `TimeRange.__post_init__` | `ValidationDomainError` |
| `INV-SCHED-01` | Operating time ranges on the same day cannot overlap | `DailyOperatingHours.__post_init__` | `BusinessRuleViolationError` |
| `INV-SCHED-02` | A closed operating day cannot define time ranges | `DailyOperatingHours.__post_init__` | `ValidationDomainError` |
| `INV-SCHED-03` | An open operating day must specify at least one time range | `DailyOperatingHours.__post_init__` | `ValidationDomainError` |
| `INV-SCHED-04` | A weekly schedule must contain exactly 7 unique weekdays | `WeeklyOperatingSchedule.__post_init__` | `ValidationDomainError` |
| `INV-STATE-01` | Archived restaurants cannot transition to active or inactive | `validate_restaurant_transition()` | `InvalidStateTransitionError` |
| `INV-STATE-02` | Inactive restaurants cannot jump directly to suspended | `validate_restaurant_transition()` | `InvalidStateTransitionError` |
| `INV-TENANT-01` | Restaurant resources must belong to authorized tenant organization | `assert_restaurant_belongs_to_organization()` | `BusinessRuleViolationError` |
| `INV-CONCURR-01`| Stale version updates must be rejected on save | `SQLAlchemyRestaurantProfileRepository.save()` | `ConcurrencyConflictError` |
