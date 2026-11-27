# FCD14-ADR-002: Independent Branch Timezone Configuration

## Status
Accepted

## Context
A restaurant brand operating under one organization may span multiple cities or time zones.

## Decision
Store `timezone` directly on `branches` (`BranchEntity` / `Branch`), defaulting from the parent restaurant/organization on creation if omitted, while allowing per-branch overrides.

## Consequences
- Operating hours, order timestamps, and daily analytics rollups can operate accurately in each branch's local timezone.
