# ARC-10 §18: Scheduled Publishing (P1 Capability)
**Timezone-Aware Future Activations**

## 1. Architecture
- Schedules store exact UTC activation instants alongside the restaurant's local timezone.
- Schedules bind to an immutable draft revision or pre-built candidate.
- At execution time, the scheduler validates that the candidate is still valid and atomically activates it.
