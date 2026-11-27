"""Operating schedule domain value objects (FCD-06 §7.8, §7.9)."""

import enum
from dataclasses import dataclass
from datetime import time
from typing import Any

from menu_it.domain.base.errors import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    ValidationDomainError,
)
from menu_it.domain.value_objects.time_range import TimeRange


class Weekday(enum.IntEnum):
    """ISO weekday numbers (Monday=1 through Sunday=7)."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    @classmethod
    def from_value(cls, val: Any) -> "Weekday":
        """Resolve weekday from integer (1-7) or case-insensitive string name."""
        if isinstance(val, Weekday):
            return val
        if isinstance(val, int):
            try:
                return cls(val)
            except ValueError as err:
                raise ValidationDomainError(
                    f"Invalid weekday integer: {val}. Must be 1 (Monday) to 7 (Sunday)."
                ) from err
        if isinstance(val, str):
            clean = val.strip().upper()
            try:
                return cls[clean]
            except KeyError as err:
                raise ValidationDomainError(f"Invalid weekday name: '{val}'.") from err
        raise ValidationDomainError(f"Unsupported weekday representation: {type(val)}")


@dataclass(frozen=True, slots=True)
class DailyOperatingHours:
    """Operating hours for a single day of the week."""

    weekday: Weekday
    is_closed: bool = False
    time_ranges: tuple[TimeRange, ...] = ()

    def __post_init__(self) -> None:
        # Normalize weekday enum
        normalized_weekday = Weekday.from_value(self.weekday)
        if self.weekday is not normalized_weekday:
            object.__setattr__(self, "weekday", normalized_weekday)

        # Normalize time_ranges to tuple
        if not isinstance(self.time_ranges, tuple):
            object.__setattr__(self, "time_ranges", tuple(self.time_ranges))

        if self.is_closed:
            if self.time_ranges:
                raise ValidationDomainError(
                    f"Closed day ({self.weekday.name}) cannot have operating time ranges."
                )
        else:
            if not self.time_ranges:
                raise ValidationDomainError(
                    f"Open day ({self.weekday.name}) must have at least one operating time range."
                )

            # Check for overlaps between ranges on the same day
            ranges = self.time_ranges
            for i in range(len(ranges)):
                for j in range(i + 1, len(ranges)):
                    if ranges[i].overlaps_with(ranges[j]):
                        r1_o = ranges[i].opens_at.strftime("%H:%M")
                        r1_c = ranges[i].closes_at.strftime("%H:%M")
                        r2_o = ranges[j].opens_at.strftime("%H:%M")
                        r2_c = ranges[j].closes_at.strftime("%H:%M")
                        raise BusinessRuleViolationError(
                            f"Operating time ranges overlap on {self.weekday.name}: "
                            f"{r1_o}-{r1_c} and {r2_o}-{r2_c}."
                        )

            # Sort ranges by opens_at
            sorted_ranges = tuple(sorted(self.time_ranges, key=lambda r: r.opens_at))
            if sorted_ranges != self.time_ranges:
                object.__setattr__(self, "time_ranges", sorted_ranges)

    @property
    def total_operating_minutes(self) -> int:
        """Calculate total operating minutes across all shifts for the day."""
        if self.is_closed:
            return 0
        return sum(r.duration_minutes for r in self.time_ranges)

    def is_open_at(self, t: time) -> bool:
        """Check if restaurant is open at a given time on this day."""
        if self.is_closed:
            return False
        return any(r.contains_time(t) for r in self.time_ranges)

    def to_dict(self) -> dict[str, Any]:
        """Serialize daily schedule to dictionary."""
        return {
            "weekday": self.weekday.value,
            "weekday_name": self.weekday.name,
            "is_closed": self.is_closed,
            "time_ranges": [r.to_dict() for r in self.time_ranges],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DailyOperatingHours":
        """Deserialize daily schedule from dictionary."""
        weekday_raw = data.get("weekday") or data.get("weekday_name")
        if weekday_raw is None:
            raise ValidationDomainError("DailyOperatingHours dict missing 'weekday'")
        weekday = Weekday.from_value(weekday_raw)
        is_closed = bool(data.get("is_closed", False))
        ranges_raw = data.get("time_ranges", [])
        time_ranges = tuple(TimeRange.from_dict(r) for r in ranges_raw)
        return cls(weekday=weekday, is_closed=is_closed, time_ranges=time_ranges)


@dataclass(frozen=True, slots=True)
class WeeklyOperatingSchedule:
    """Full 7-day operating schedule invariant boundary."""

    days: tuple[DailyOperatingHours, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.days, tuple):
            object.__setattr__(self, "days", tuple(self.days))

        if len(self.days) != 7:
            raise ValidationDomainError(
                f"WeeklyOperatingSchedule must contain exactly 7 days, got {len(self.days)}."
            )

        weekdays = [d.weekday for d in self.days]
        unique_weekdays = set(weekdays)
        if len(unique_weekdays) != 7:
            raise ValidationDomainError(
                "WeeklyOperatingSchedule must contain unique days with no duplicates."
            )

        expected = set(Weekday)
        if unique_weekdays != expected:
            missing = [m.name for m in expected - unique_weekdays]
            raise ValidationDomainError(
                f"WeeklyOperatingSchedule is missing required weekdays: {missing}."
            )

        # Sort days deterministically from Monday (1) to Sunday (7)
        sorted_days = tuple(sorted(self.days, key=lambda d: d.weekday.value))
        if sorted_days != self.days:
            object.__setattr__(self, "days", sorted_days)

    def get_day(self, weekday: Weekday | int | str) -> DailyOperatingHours:
        """Lookup schedule for a specific weekday."""
        normalized = Weekday.from_value(weekday)
        for day in self.days:
            if day.weekday == normalized:
                return day
        raise EntityNotFoundError(f"Day '{normalized.name}' not found in schedule.")

    def is_open_on(self, weekday: Weekday | int | str) -> bool:
        """Check whether restaurant is open on the specified weekday."""
        return not self.get_day(weekday).is_closed

    def is_open_at(self, weekday: Weekday | int | str, t: time) -> bool:
        """Check whether restaurant is open at a given weekday and time."""
        return self.get_day(weekday).is_open_at(t)

    def to_dict(self) -> list[dict[str, Any]]:
        """Serialize weekly schedule to list of daily dictionaries."""
        return [day.to_dict() for day in self.days]

    @classmethod
    def from_dict(cls, data: list[dict[str, Any]] | dict[str, Any]) -> "WeeklyOperatingSchedule":
        """Deserialize weekly schedule from list or dict containing 'days'."""
        if isinstance(data, dict):
            days_raw = data.get("days", [])
        elif isinstance(data, list):
            days_raw = data
        else:
            raise ValidationDomainError("Invalid weekly schedule data format.")

        daily_list = [DailyOperatingHours.from_dict(d) for d in days_raw]
        return cls(days=tuple(daily_list))

    @classmethod
    def create_standard(
        cls,
        opens_at: time = time(9, 0),
        closes_at: time = time(22, 0),
        closed_weekdays: tuple[Weekday, ...] = (),
    ) -> "WeeklyOperatingSchedule":
        """Factory helper creating a standard weekly schedule."""
        days = []
        for w in Weekday:
            if w in closed_weekdays:
                days.append(DailyOperatingHours(weekday=w, is_closed=True))
            else:
                days.append(
                    DailyOperatingHours(
                        weekday=w,
                        is_closed=False,
                        time_ranges=(TimeRange(opens_at=opens_at, closes_at=closes_at),),
                    )
                )
        return cls(days=tuple(days))
