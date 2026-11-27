"""Business hours, schedule validation, and open-now evaluation (FCD-15 §6)."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from menu_it.domain.base.errors import BusinessRuleViolationError, ValidationDomainError
from menu_it.domain.restaurant_configuration.value_objects import (
    ExceptionType,
    OpeningInterval,
)


@dataclass(frozen=True, slots=True)
class ScheduleExceptionEntry:
    """Date-specific schedule override (holiday closure or special hours)."""

    exception_date: date
    exception_type: ExceptionType
    reason: str | None = None
    intervals: tuple[OpeningInterval, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.exception_type, ExceptionType):
            object.__setattr__(self, "exception_type", ExceptionType(self.exception_type))
        if self.exception_type == ExceptionType.CLOSED and self.intervals:
            raise ValidationDomainError("CLOSED schedule exception cannot contain intervals.")
        if self.exception_type != ExceptionType.CLOSED and not self.intervals:
            raise ValidationDomainError(
                f"{self.exception_type.value} exception requires at least one interval."
            )
        if self.intervals:
            validated = validate_daily_intervals(self.intervals)
            object.__setattr__(self, "intervals", validated)


@dataclass(frozen=True, slots=True)
class OpenStatusResult:
    """Result of evaluating whether a restaurant/branch is currently open."""

    is_open: bool
    local_time: datetime
    timezone: str
    active_interval: OpeningInterval | None = None
    source: str = "weekly_schedule"


def validate_daily_intervals(intervals: Sequence[OpeningInterval]) -> tuple[OpeningInterval, ...]:
    """Sort and validate that daily opening intervals do not overlap or duplicate."""
    items = sorted(intervals, key=lambda item: (item.opens_at, item.closes_at))
    for idx in range(len(items) - 1):
        if items[idx].overlaps_with(items[idx + 1]):
            raise BusinessRuleViolationError(
                "Opening intervals cannot overlap or duplicate within the same day."
            )
    return tuple(items)


def _intervals_for_date(
    target_date: date,
    weekly_hours: dict[int, tuple[OpeningInterval, ...]],
    exception_map: dict[date, ScheduleExceptionEntry],
) -> tuple[tuple[OpeningInterval, ...], str]:
    exc = exception_map.get(target_date)
    if exc is not None:
        if exc.exception_type == ExceptionType.CLOSED:
            return (), "exception_closed"
        return exc.intervals, "exception_override"
    # Python date.weekday(): 0=Monday .. 6=Sunday
    return weekly_hours.get(target_date.weekday(), ()), "weekly_schedule"


def evaluate_open_status(
    *,
    now_utc: datetime,
    timezone_name: str,
    weekly_hours: dict[int, tuple[OpeningInterval, ...]],
    exceptions: Sequence[ScheduleExceptionEntry] = (),
) -> OpenStatusResult:
    """Evaluate open/closed state in the branch's IANA timezone, including overnight shifts."""
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValidationDomainError(f"Unknown IANA timezone '{timezone_name}'.") from exc

    local_dt = now_utc.astimezone(tz)
    local_date = local_dt.date()
    local_t = local_dt.time().replace(tzinfo=None)
    local_minutes = local_t.hour * 60 + local_t.minute

    exception_map = {item.exception_date: item for item in exceptions}

    # 1. Check yesterday's overnight intervals spilling into today
    yesterday = local_date - timedelta(days=1)
    prev_intervals, prev_source = _intervals_for_date(yesterday, weekly_hours, exception_map)
    for interval in prev_intervals:
        if interval.closes_next_day:
            close_minutes = interval.closes_at.hour * 60 + interval.closes_at.minute
            if local_minutes < close_minutes:
                return OpenStatusResult(
                    is_open=True,
                    local_time=local_dt,
                    timezone=timezone_name,
                    active_interval=interval,
                    source=prev_source,
                )

    # 2. Check today's intervals
    today_intervals, today_source = _intervals_for_date(local_date, weekly_hours, exception_map)
    for interval in today_intervals:
        start_m, end_m = interval.to_minute_span()
        if start_m <= local_minutes < end_m:
            return OpenStatusResult(
                is_open=True,
                local_time=local_dt,
                timezone=timezone_name,
                active_interval=interval,
                source=today_source,
            )

    return OpenStatusResult(
        is_open=False,
        local_time=local_dt,
        timezone=timezone_name,
        active_interval=None,
        source=today_source,
    )
