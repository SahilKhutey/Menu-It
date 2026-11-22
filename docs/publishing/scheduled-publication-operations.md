# Scheduled Publication Operations (P1)
**Timezone-Aware Scheduling Runbook**

## Schedule Execution
- Stored as UTC timestamp + local timezone string.
- Automatically claims eligible schedules and invokes atomic publish use case.
