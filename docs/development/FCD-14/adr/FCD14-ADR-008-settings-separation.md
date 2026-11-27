# FCD14-ADR-008: Dedicated Organization and Restaurant Settings Tables

## Status
Accepted

## Context
Operational settings (currency, timezone, locale, feature flags, contact preferences) evolve more frequently than core identity/slug columns.

## Decision
Separate `organization_settings` and `restaurant_settings` into dedicated 1:1 tables linked to `organizations` and `restaurants`.

## Consequences
- Keeps core entity tables compact and allows settings schemas to evolve without locking or bloating primary entity rows.
