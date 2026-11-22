# Devlog-009: ARC-08 Theme & Customization Architecture Baseline

**Date:** 2026-11-22  
**Milestone:** `v1.0.0-arc08` (Theme & Customization Architecture)  
**Author:** Antigravity Engineering & Architecture Team  
**Status:** Released & Certified  

---

## 1. Executive Summary
With **ARC-08 (Theme & Customization Architecture)**, ModularMenu achieves a major engineering milestone: enabling complete, rich visual and structural menu personalization for restaurant operators without writing a single line of code, modifying source templates, or creating tenant code forks.

Customization in ModularMenu is **100% configuration-driven, schema-validated, versioned, portable, and secure**. Whether an operator configures branding via the form-driven **Settings Editor** or visually arranges components using the drag-and-drop **Visual Editor**, both tools operate on the exact same canonical JSON customization document.

The engineering implementation incorporates a deterministic theme engine, design token contracts, platform registries (6 themes, 4 layouts, 13 components), optimistic concurrency control via `If-Match` / `ETag`, immutable revision history, ephemeral previews, and strict tenant isolation. An automated 104-test suite certifies compliance with zero failures.

---

## 2. Key Architecture Pillars Delivered

### 2.1 Configuration-Driven, Code-Free Customization (ADR-0114, ADR-0116)
- **Zero Executable Code:** Prohibits raw CSS injection, `<style>` or `<script>` tags, inline event handlers, and `javascript:` URLs.
- **Strict Bounded Limits:** Max 256 KB document size, max 100 component instances, max 10 levels of nesting depth.
- **Validation Pipeline:** Three-stage validation enforcing payload size/security limits, draft-07 JSON Schema conformance, and semantic catalogue compatibility.

### 2.2 Hierarchical Design Tokens & Deterministic Theme Engine (ADR-0117, ADR-0124, ADR-0125)
- Standardized token taxonomy: `color` (brand, surface, text, border, status), `typography` (fontFamily, fontSize, fontWeight), `spacing` (xs to 2xl), `radius` (none to full), `shadow`, and `elevation`.
- **Pure Resolver Function:** Computes resolved tokens via pure recursive deep-merge. Specifying a token override as `null` or empty string safely resets the token back to the platform theme default.
- **CSS Custom Property Generator:** Emits flat, deterministic CSS variables under `--mm-` (e.g., `--mm-color-brand-primary: #D4AF37;`).
- **Scoped Injection Container (`ThemeScope`):** Scopes variables directly to the menu container, eliminating any CSS leakage into admin dashboards.
- **Dual Implementation Parity:** Tested and certified identical resolution across Python backend (`app.modules.customization.resolver`) and TypeScript frontend (`packages/theme-engine`).

### 2.3 Platform Catalogues & Registry Architecture (ADR-0120, ADR-0121, ADR-0122, ADR-0123)
- **6 Core Themes:** Luxury (obsidian & gold), Minimal (clean high-contrast), Rustic (warm earth & serif), Contemporary (vibrant indigo), Vibrant (high-energy orange), and Editorial (magazine serif).
- **4 Responsive Layouts:** Classic List, Card Grid, Image Cards, Editorial Story. Breakpoints enforce fluid column responsiveness (mobile: 1 column; tablet: 1-2 columns; desktop: 2-4 columns).
- **13 Registered Components:** Header, title, navigation, category heading, item card, item image, price, description, dietary label, allergen label, availability indicator, footer, contact information.
- **Slot Architecture:** Components can only be placed into declared semantic slots (`header`, `navigation`, `category.header`, `category.items`, `footer`).

### 2.4 Optimistic Concurrency & Revision History (ADR-0127, ADR-0128)
- Every read returns an `ETag: "revision-N"`.
- Every save requires `If-Match: "revision-N"`. If a concurrent update occurred, the server rejects with HTTP 409 Conflict (`VERSION_CONFLICT`).
- Every successful update creates an immutable audit record in `customization_revisions`.
- Operators can view historical revisions and restore any past revision in one click, creating a new revision without destroying history.

### 2.5 Ephemeral Previews & Decoupled Public Delivery (ADR-0129, ADR-0130, ADR-0137)
- `POST /menus/{menu_id}/customization/preview` computes live in-memory style resolutions without writing to disk or polluting revision logs.
- When published (ARC-10), the resolved customization is frozen into a static snapshot. Public diners (ARC-09) consume pre-rendered snapshots via CDN edge caches with zero database queries.

### 2.6 Multi-Tenant Security & Accessibility (ADR-0131, ADR-0132, ADR-0136)
- Customization endpoints join `Restaurant` and strictly enforce `Restaurant.organization_id == tenant.organization_id`.
- Cross-tenant requests return HTTP 404 (Not Found) to prevent resource enumeration.
- All 6 platform themes are verified for WCAG 2.1 AA text-to-surface contrast ($\ge 4.5:1$).

---

## 3. Implementation Artifacts

| Layer | Directory / Artifacts | Description |
| :--- | :--- | :--- |
| **Contracts & Schemas** | `packages/contracts/schemas/` | 6 JSON Schemas for tokens, themes, layouts, components, instances, customization |
| **Catalogues** | `packages/contracts/manifests/` | Manifest catalogues for 6 themes, 4 layouts, 13 components, migrations |
| **Generated Types** | `packages/contracts/generated/` | Canonical TypeScript interfaces and types |
| **Shared Libraries** | `packages/design-tokens/`, `packages/theme-engine/`, `packages/component-registry/`, `packages/editor-engine/` | Reusable token, resolution, registry, and history engines |
| **Backend Module** | `backend/app/modules/customization/` | Models, registries, validators, resolver, and service |
| **REST API Routes** | `backend/app/api/v1/customization.py`, `themes.py` | 8 draft lifecycle endpoints, catalogue endpoints, OpenAPI 3.1 |
| **Frontend UI** | `frontend/src/features/customization/` | `SettingsEditor.tsx`, `VisualEditor.tsx`, `ThemeScope.tsx` |
| **Test Matrix** | `tests/customization/test_arc08_customization_catalogue.py` | 104 automated test scenarios covering 10 functional areas |
| **Architecture Docs** | `docs/architecture/ARC-08-theme-customization-architecture/` | 28 comprehensive architecture documents |

---

## 4. Verification & Quality Gate Results
- **ARC-08 Test Suite:** 104 passed / 104 total (100% pass rate in 12.61s).
- **Full Platform Regression Suite:** 378 passed / 378 total (100% pass rate across ARC-01 to ARC-08).
- **Performance Benchmarks:**
  - Token Resolution: $< 1.2\text{ ms}$ (Budget: $< 5\text{ ms}$).
  - CSS Variable Emission: $< 0.15\text{ ms}$ (Budget: $< 1\text{ ms}$).
  - Save Draft Latency: $< 65\text{ ms}$ (Budget: $< 500\text{ ms}$).
- **Accessibility:** 100% WCAG 2.1 AA contrast compliance verified across all base theme tokens.

---

## 5. Next Architectural Horizons
With ARC-08 successfully baselined and certified, the engineering roadmap transitions to:
- **ARC-09: Menu Rendering Architecture** (High-performance public menu delivery, SSR, hydration, dynamic QR code layouts, offline caching).
- **ARC-10: Publishing & Versioning Architecture** (Immutable snapshot releases, scheduled menu transitions, instant rollbacks, multi-location menu synchronization).
