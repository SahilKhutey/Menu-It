# FCD-15 — 02 Domain Model & Rules

Pure domain models live under `apps/api/src/menu_it/domain/restaurant_configuration/` with zero infrastructure dependencies:
- `HexColor`: Strict `^#[0-9A-Fa-f]{6}$` validation and uppercase normalization.
- `OpeningInterval`: Zero-duration rejection and explicit `closes_next_day` overnight shift modeling.
- `ScheduleExceptionEntry`: `CLOSED`, `SPECIAL_HOURS`, `REDUCED_HOURS`, and `EXTENDED_HOURS`.
- `ServiceModeConfig` & `OperationalSettings`: Validated service modes and prep/advance/capacity bounds.
- `build_effective_configuration` & `resolve_service_modes`: Deterministic precedence with explicit `False` override semantics.
