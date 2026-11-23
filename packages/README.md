# ModularMenu Shared Packages (`packages/`)

This directory houses cross-cutting, reusable contracts, schemas, and token definitions shared across the **ModularMenu** ecosystem.

## Directory Structure

- `packages/contracts/`: Language-agnostic or JSON Schema definitions for Menu Snapshots, Design Tokens, and Publication payloads.
- `packages/tokens/`: Default design tokens (color palettes, typography scales, spacing density).

All shared packages are strictly decoupled from infrastructure, database drivers, or frontend DOM APIs.
