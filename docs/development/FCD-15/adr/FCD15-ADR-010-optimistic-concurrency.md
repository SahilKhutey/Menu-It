# FCD15-ADR-010: Optimistic Concurrency on Profile & Branding Edits

- **Status**: Accepted
- **Decision**: Support `expected_version` / `expected_revision` checks raising `ConcurrencyConflictError` (HTTP 409) to prevent silent lost updates during concurrent dashboard edits.
