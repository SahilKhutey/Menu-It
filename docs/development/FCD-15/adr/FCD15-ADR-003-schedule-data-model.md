# FCD15-ADR-003: Normalized Weekly Schedule Data Model

- **Status**: Accepted
- **Decision**: Store weekly schedules in normalized `restaurant_weekly_hours` and `branch_weekly_hours` rows (supporting multiple shifts per day) plus `restaurant_schedule_exceptions` for date-specific overrides.
