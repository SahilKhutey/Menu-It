# FCD-15 — 06 Business Hours & Scheduling

`validate_daily_intervals` rejects overlapping or duplicate shifts within a day while supporting multiple shifts per weekday. `evaluate_open_status` converts injected UTC instants into the branch's IANA timezone (`ZoneInfo`), evaluates date-specific `ScheduleExceptionEntry` overrides first, and handles overnight shifts spilling from the previous day.
