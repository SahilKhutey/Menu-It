# ARC-09 §02 — Architecture Principles & Standards

## 1. Fundamental Engineering Invariants
All menu rendering components adhere strictly to seven P0 principles:

1. **Pure Rendering Engine (P0-01)**: The core rendering logic executes with zero database calls, zero filesystem reads, and zero network queries. Given an identical `RenderInput`, it must return an identical `RenderPlan`.
2. **Draft Isolation & Public Safety (P0-02)**: Anonymous public consumers may only access immutable, verified published snapshots. Unsaved drafts, draft revisions, internal tenant identifiers, and billing details are strictly purged from public DTOs.
3. **Deterministic Output (P0-03)**: Sort orders for categories, food items, and layout slots are strictly preserved and normalized across server and client execution.
4. **Schema-First Contracts (P0-04)**: All input and output payloads are governed by versioned JSON Schemas (`menu-render-input`, `public-menu-response`, `draft-preview-response`).
5. **Zero Raw Code Execution (P0-05)**: No arbitrary JavaScript or user-supplied CSS strings are evaluated. Customizations must conform to typed design tokens and registered components.
6. **Graceful Fallback Resilience (P0-06)**: Missing images, long text strings, or corrupted secondary slots degrade gracefully to standard placeholders without causing white-screen crashes.
7. **Accessibility First (P0-07)**: All rendered markup strictly complies with WCAG 2.1 Level AA standards, semantic heading hierarchies, minimum touch targets (44x44px), and ARIA attributes.
