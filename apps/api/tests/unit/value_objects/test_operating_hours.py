"""Unit tests for operating hours and time range value objects (FCD-06)."""

from datetime import time

import pytest

from menu_it.domain.base.errors import BusinessRuleViolationError, ValidationDomainError
from menu_it.domain.value_objects.operating_hours import (
    DailyOperatingHours,
    Weekday,
    WeeklyOperatingSchedule,
)
from menu_it.domain.value_objects.time_range import TimeRange


def test_time_range_normal() -> None:
    tr = TimeRange(opens_at=time(9, 0), closes_at=time(17, 30))
    assert not tr.crosses_midnight
    assert tr.duration_minutes == 510  # 8.5 hours = 510 mins


def test_time_range_crosses_midnight() -> None:
    tr = TimeRange(opens_at=time(22, 0), closes_at=time(2, 0))
    assert tr.crosses_midnight
    assert tr.duration_minutes == 240  # 4 hours = 240 mins


def test_time_range_identical_raises() -> None:
    with pytest.raises(ValidationDomainError, match="cannot be identical"):
        TimeRange(opens_at=time(9, 0), closes_at=time(9, 0))


def test_time_range_contains_time() -> None:
    normal = TimeRange(opens_at=time(9, 0), closes_at=time(17, 0))
    assert normal.contains_time(time(9, 0))
    assert normal.contains_time(time(12, 30))
    assert not normal.contains_time(time(17, 0))  # exclusive end
    assert not normal.contains_time(time(8, 59))

    overnight = TimeRange(opens_at=time(21, 0), closes_at=time(3, 0))
    assert overnight.contains_time(time(21, 0))
    assert overnight.contains_time(time(23, 59))
    assert overnight.contains_time(time(1, 30))
    assert not overnight.contains_time(time(3, 0))
    assert not overnight.contains_time(time(15, 0))


def test_time_range_overlaps() -> None:
    r1 = TimeRange(opens_at=time(9, 0), closes_at=time(14, 0))
    r2 = TimeRange(opens_at=time(14, 0), closes_at=time(22, 0))
    assert not r1.overlaps_with(r2)  # abut, do not overlap

    r3 = TimeRange(opens_at=time(13, 0), closes_at=time(16, 0))
    assert r1.overlaps_with(r3)

    overnight = TimeRange(opens_at=time(22, 0), closes_at=time(2, 0))
    morning = TimeRange(opens_at=time(1, 0), closes_at=time(5, 0))
    assert overnight.overlaps_with(morning)

    afternoon = TimeRange(opens_at=time(12, 0), closes_at=time(16, 0))
    assert not overnight.overlaps_with(afternoon)


def test_time_range_serialization() -> None:
    tr = TimeRange(opens_at=time(9, 30), closes_at=time(22, 0))
    data = tr.to_dict()
    assert data == {"opens_at": "09:30", "closes_at": "22:00"}
    deserialized = TimeRange.from_dict(data)
    assert deserialized == tr


def test_daily_operating_hours_closed_with_ranges_raises() -> None:
    with pytest.raises(ValidationDomainError, match="cannot have operating time ranges"):
        DailyOperatingHours(
            weekday=Weekday.MONDAY,
            is_closed=True,
            time_ranges=(TimeRange(opens_at=time(9, 0), closes_at=time(17, 0)),),
        )


def test_daily_operating_hours_open_without_ranges_raises() -> None:
    with pytest.raises(ValidationDomainError, match="must have at least one operating time range"):
        DailyOperatingHours(
            weekday=Weekday.MONDAY,
            is_closed=False,
            time_ranges=(),
        )


def test_daily_operating_hours_overlapping_ranges_raises() -> None:
    with pytest.raises(BusinessRuleViolationError, match="overlap"):
        DailyOperatingHours(
            weekday=Weekday.FRIDAY,
            is_closed=False,
            time_ranges=(
                TimeRange(opens_at=time(11, 0), closes_at=time(15, 0)),
                TimeRange(opens_at=time(14, 30), closes_at=time(22, 0)),
            ),
        )


def test_daily_operating_hours_valid_shifts() -> None:
    day = DailyOperatingHours(
        weekday=Weekday.FRIDAY,
        is_closed=False,
        time_ranges=(
            TimeRange(opens_at=time(17, 30), closes_at=time(22, 0)),
            TimeRange(opens_at=time(11, 30), closes_at=time(14, 30)),
        ),
    )
    # Automatically sorted by opens_at
    assert day.time_ranges[0].opens_at == time(11, 30)
    assert day.time_ranges[1].opens_at == time(17, 30)
    assert day.total_operating_minutes == 180 + 270  # 3 hrs + 4.5 hrs = 450 mins
    assert day.is_open_at(time(12, 0))
    assert not day.is_open_at(time(16, 0))


def test_weekly_operating_schedule_requires_7_days() -> None:
    six_days = tuple(
        DailyOperatingHours(
            weekday=w,
            is_closed=False,
            time_ranges=(TimeRange(opens_at=time(9, 0), closes_at=time(17, 0)),),
        )
        for w in [
            Weekday.MONDAY,
            Weekday.TUESDAY,
            Weekday.WEDNESDAY,
            Weekday.THURSDAY,
            Weekday.FRIDAY,
            Weekday.SATURDAY,
        ]
    )
    with pytest.raises(ValidationDomainError, match="exactly 7 days"):
        WeeklyOperatingSchedule(days=six_days)


def test_weekly_operating_schedule_duplicate_day_raises() -> None:
    dup_days = tuple(
        DailyOperatingHours(
            weekday=Weekday.MONDAY,
            is_closed=True,
        )
        for _ in range(7)
    )
    with pytest.raises(ValidationDomainError, match="unique days"):
        WeeklyOperatingSchedule(days=dup_days)


def test_weekly_operating_schedule_valid() -> None:
    schedule = WeeklyOperatingSchedule.create_standard(
        opens_at=time(10, 0),
        closes_at=time(22, 0),
        closed_weekdays=(Weekday.SUNDAY,),
    )
    assert len(schedule.days) == 7
    assert schedule.is_open_on(Weekday.MONDAY)
    assert not schedule.is_open_on(Weekday.SUNDAY)
    assert schedule.is_open_at(Weekday.FRIDAY, time(15, 0))
    assert not schedule.is_open_at(Weekday.SUNDAY, time(15, 0))

    serialized = schedule.to_dict()
    assert len(serialized) == 7
    deserialized = WeeklyOperatingSchedule.from_dict(serialized)
    assert deserialized == schedule
