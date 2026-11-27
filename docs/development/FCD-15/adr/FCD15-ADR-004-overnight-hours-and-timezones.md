# FCD15-ADR-004: Explicit Overnight Hours & IANA Timezone Evaluation

- **Status**: Accepted
- **Decision**: Require explicit `closes_next_day=True` for shifts crossing midnight and evaluate `evaluate_open_status` using `ZoneInfo(timezone_name)` with an injected UTC clock rather than server-local time.
