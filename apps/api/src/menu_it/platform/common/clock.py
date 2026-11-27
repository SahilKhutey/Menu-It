"""Deterministic clock abstraction for platform services (FCD-09 WP-06)."""

from datetime import UTC, datetime, timedelta
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """Protocol for UTC time retrieval."""

    def now(self) -> datetime:
        """Return the current UTC datetime."""
        ...


class SystemClock:
    """Production clock using real system UTC time."""

    def now(self) -> datetime:
        return datetime.now(UTC)


class FrozenClock:
    """Test clock with fixed or manipulable time for deterministic testing."""

    def __init__(self, initial_time: datetime | None = None) -> None:
        if initial_time is not None:
            if initial_time.tzinfo is None or initial_time.utcoffset() is None:
                raise ValueError("Initial time must be timezone-aware (UTC).")
            self._current = initial_time.astimezone(UTC)
        else:
            self._current = datetime.now(UTC)

    def now(self) -> datetime:
        return self._current

    def set(self, target: datetime) -> None:
        if target.tzinfo is None or target.utcoffset() is None:
            raise ValueError("Target time must be timezone-aware (UTC).")
        self._current = target.astimezone(UTC)

    def advance(self, delta: timedelta) -> datetime:
        self._current += delta
        return self._current
