"""Time range value object representing an operating interval (FCD-06 §7.8)."""

from dataclasses import dataclass
from datetime import time
from typing import Any

from menu_it.domain.base.errors import ValidationDomainError


@dataclass(frozen=True, slots=True)
class TimeRange:
    """Operating hours interval within a day, supporting overnight hours."""

    opens_at: time
    closes_at: time

    def __post_init__(self) -> None:
        if not isinstance(self.opens_at, time):
            raise ValidationDomainError("opens_at must be an instance of datetime.time")
        if not isinstance(self.closes_at, time):
            raise ValidationDomainError("closes_at must be an instance of datetime.time")
        if self.opens_at == self.closes_at:
            raise ValidationDomainError(
                "Operating hours opens_at and closes_at cannot be identical."
            )

    @property
    def crosses_midnight(self) -> bool:
        """Return True if closing time is on the next calendar day."""
        return self.opens_at > self.closes_at

    @property
    def duration_minutes(self) -> int:
        """Calculate total operating duration in minutes."""
        open_minutes = self.opens_at.hour * 60 + self.opens_at.minute
        close_minutes = self.closes_at.hour * 60 + self.closes_at.minute
        if not self.crosses_midnight:
            return close_minutes - open_minutes
        return (24 * 60 - open_minutes) + close_minutes

    def _intervals(self) -> list[tuple[time, time]]:
        """Return half-open interval(s) representing this range on a day's timeline."""
        if not self.crosses_midnight:
            return [(self.opens_at, self.closes_at)]
        return [
            (self.opens_at, time(23, 59, 59, 999999)),
            (time(0, 0, 0), self.closes_at),
        ]

    def overlaps_with(self, other: "TimeRange") -> bool:
        """Check if two time ranges overlap on the same business day timeline."""
        if not isinstance(other, TimeRange):
            raise ValidationDomainError("Can only compare overlap with another TimeRange")
        for s1, e1 in self._intervals():
            for s2, e2 in other._intervals():
                if max(s1, s2) < min(e1, e2):
                    return True
        return False

    def contains_time(self, t: time) -> bool:
        """Check if a specific time falls within the half-open operating interval."""
        if not self.crosses_midnight:
            return self.opens_at <= t < self.closes_at
        return t >= self.opens_at or t < self.closes_at

    def to_dict(self) -> dict[str, str]:
        """Serialize time range to ISO string dictionary."""
        return {
            "opens_at": self.opens_at.strftime("%H:%M"),
            "closes_at": self.closes_at.strftime("%H:%M"),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TimeRange":
        """Deserialize from dictionary."""
        opens_raw = data["opens_at"]
        closes_raw = data["closes_at"]

        opens_val = time.fromisoformat(opens_raw) if isinstance(opens_raw, str) else opens_raw
        closes_val = time.fromisoformat(closes_raw) if isinstance(closes_raw, str) else closes_raw
        return cls(opens_at=opens_val, closes_at=closes_val)
