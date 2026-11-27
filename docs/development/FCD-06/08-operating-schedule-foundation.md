# FCD-06 §08 — Operating Schedule Foundation

## 1. Domain Modeling of Time

Restaurants have unique temporal requirements:
- Split shifts (e.g. lunch 11:30–14:30 and dinner 17:30–22:00).
- Late-night operations crossing midnight (e.g. 22:00 to 02:00).
- Complete closures on specific weekdays (e.g. closed Mondays).

## 2. Component Models

Located in `apps/api/src/menu_it/domain/value_objects/`:

### 2.1 `TimeRange`
Represents an interval `[opens_at, closes_at)`:
- `crosses_midnight: bool`: True when `opens_at > closes_at`.
- `duration_minutes: int`: Accurately handles both standard intervals and overnight spans.
- `overlaps_with(other: TimeRange) -> bool`:
  Splits overnight spans into two timeline intervals `[opens_at, 23:59:59.999999]` and `[00:00:00, closes_at]`. Any intersection between range interval pairs signals an overlap.
- `contains_time(t: time) -> bool`: Half-open inclusion logic.

### 2.2 `DailyOperatingHours`
Governs hours for a single ISO weekday:
- `weekday: Weekday`: Enum from `MONDAY` (1) to `SUNDAY` (7).
- `is_closed: bool`: If true, `time_ranges` must be empty. If false, at least one range must be present.
- Invariant: Automatically checks for overlapping ranges on the same day and maintains them sorted by opening time.

### 2.3 `WeeklyOperatingSchedule`
The weekly aggregate schedule:
- Invariant: Must contain exactly 7 unique days from Monday through Sunday.
- Methods: `get_day()`, `is_open_on()`, `is_open_at()`, `to_dict()`, `from_dict()`.
- Standard factory: `WeeklyOperatingSchedule.create_standard(opens_at, closes_at, closed_weekdays)`.
