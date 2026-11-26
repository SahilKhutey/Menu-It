"""Recurrence calculation and timezone handling for scheduled jobs (FCD-10 WP-07)."""

import zoneinfo
from datetime import UTC, datetime, time, timedelta


def compute_next_run_at(
    schedule_type: str,
    expression: str | None,
    tz_name: str = "UTC",
    from_time: datetime | None = None,
) -> datetime:
    """Compute the next UTC execution instant based on schedule type and IANA timezone."""
    try:
        tz = zoneinfo.ZoneInfo(tz_name)
    except Exception:
        tz = zoneinfo.ZoneInfo("UTC")

    now_utc = from_time or datetime.now(UTC)
    local_now = now_utc.astimezone(tz)

    if schedule_type == "interval":
        # expression format: e.g. "60s", "5m", "1h", "1d" or integer seconds
        if not expression:
            return now_utc + timedelta(minutes=5)
        expr = expression.strip().lower()
        if expr.endswith("s"):
            seconds = int(expr[:-1])
        elif expr.endswith("m"):
            seconds = int(expr[:-1]) * 60
        elif expr.endswith("h"):
            seconds = int(expr[:-1]) * 3600
        elif expr.endswith("d"):
            seconds = int(expr[:-1]) * 86400
        else:
            seconds = int(expr)
        return now_utc + timedelta(seconds=max(seconds, 1))

    elif schedule_type == "daily":
        # expression format: "HH:MM", e.g. "04:00" in local timezone
        if not expression or ":" not in expression:
            target_time = time(4, 0)
        else:
            parts = expression.split(":")
            target_time = time(int(parts[0]), int(parts[1]))

        candidate = local_now.replace(
            hour=target_time.hour,
            minute=target_time.minute,
            second=0,
            microsecond=0,
        )
        if candidate <= local_now:
            candidate += timedelta(days=1)
        return candidate.astimezone(UTC)

    elif schedule_type == "once":
        # Run once in 5 minutes by default if no expression given
        if expression:
            dt = datetime.fromisoformat(expression)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            return dt.astimezone(UTC)
        return now_utc + timedelta(minutes=5)

    # Fallback default
    return now_utc + timedelta(hours=1)
