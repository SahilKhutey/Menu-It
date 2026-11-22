# ARC-08 — Theme & Customization Architecture
MODULARMENU · SYSTEM ARCHITECTURE SERIES · VERSION 1.0
Baseline Architecture Specification
Status: Approved Baseline

## Document Objective
ARC-08 establishes how restaurants customize the appearance and structure of their digital menus without modifying application source code. It supports both the settings-based editor and visual editor while preserving a single shared rendering and configuration foundation.

The central architectural principle is:
> **Restaurant customization must be configuration-driven, schema-validated, versioned, portable, and independent of application code.**

---

## 1. Document Control & Architecture Relationships

### 1.1 Document Metadata
| Attribute | Definition |
| :--- | :--- |
| **Document ID** | ARC-08 |
| **Title** | Theme & Customization Architecture |
| **Product** | ModularMenu (Menu-It) |
| **Version** | 1.0.0-arc08 |
| **Status** | Approved Baseline |
| **Parent Architecture** | ARC-01 through ARC-07 |
| **Primary Dependencies** | ARC-03 (App Arch), ARC-04 (Domain Arch), ARC-05 (Tenancy), ARC-06 (Data Arch), ARC-07 (API Arch) |
| **Downstream Architecture** | ARC-09 (Menu Rendering), ARC-10 (Publishing & Versioning) |
| **Implementation Model** | Modular Monolith (FastAPI + Next.js 14) |
| **Configuration Storage** | PostgreSQL JSONB with validated contracts & immutable revisions |
| **Testing** | Pytest, Vitest, Playwright, axe-core |

### 1.2 Relationship with Other Architecture Documents
- **ARC-03 (Application Architecture):** Shared packages (`packages/contracts`, `packages/design-tokens`, `packages/theme-engine`, `packages/layout-engine`, `packages/component-registry`, `packages/editor-engine`), frontend/backend boundaries.
- **ARC-04 (Domain Architecture):** Bounded contexts for Themes (`MOD-07`), Layouts (`MOD-08`), Components (`MOD-09`), and Editor (`MOD-10`).
- **ARC-05 (Multi-Tenant Architecture):** Server-derived `TenantContext` isolation, strict tenant scoping for all customization drafts and revisions.
- **ARC-06 (Data Architecture):** Persistence, relational foreign keys, composite tenant constraints, JSONB validation, and immutable revision history.
- **ARC-07 (API Architecture):** Versioned REST endpoints under `/api/v1/`, RFC 7807 problem details, ETag/If-Match optimistic concurrency.
- **ARC-09 (Menu Rendering):** Consumes normalized, validated theme/layout/component configuration.
- **ARC-10 (Publishing):** Freezes customization into immutable published snapshots.

### 1.3 Architectural Boundaries
**ARC-08 Owns:**
- Design tokens and token contracts.
- Theme presets and theme customization.
- Theme inheritance and override resolution.
- Layout definitions and layout configuration.
- Component registry metadata and schemas.
- Component-level customization and slot placement.
- Responsive configuration constraints.
- Configuration validation and normalization.
- Settings editor and visual editor configuration contracts.
- Preview configuration lifecycle.
- Theme and configuration compatibility and migrations.

**ARC-08 Does NOT Own:**
- Actual public menu rendering implementation (owned by ARC-09).
- Published snapshot lifecycle and rollback (owned by ARC-10).
- Menu content management (owned by ARC-04 and ARC-06).
- Authentication and tenant authorization (owned by ARC-05 and ARC-07).
- Arbitrary custom JavaScript, executable plugins, or unrestricted CSS uploaded by restaurants.

---

## 2. Architecture Goals & Design Principles

### 2.1 Primary Goals
1. Allow restaurants to customize menu appearance without source-code changes.
2. Provide reusable theme presets (Luxury, Minimal, Rustic, Contemporary, Vibrant, Editorial).
3. Allow independent customization of typography, colors, spacing, borders, backgrounds, and visual elements.
4. Support multiple menu layouts (List, Grid, Image-Cards, Editorial).
5. Provide a registry of approved menu components.
6. Allow configuration of component visibility, order, properties, and supported behaviors.
7. Provide consistent configuration contracts for settings and visual editors.
8. Validate configurations before saving, previewing, or publishing.
9. Preserve compatibility across theme, component, and configuration versions.
10. Ensure one restaurant's customization cannot affect another tenant.
11. Support responsive layouts and accessibility (WCAG AA contrast, reduced motion, keyboard navigation).
12. Ensure self-hosted and SaaS editions use the exact same customization model.

### 2.2 Mandatory Design Principles
- **Configuration over code:** Restaurant customization is declarative data.
- **Content/presentation separation:** Menu content does not contain theme implementation.
- **Schema-first:** Every configurable object has a versioned schema.
- **Allowlisted components:** Only registered components can be configured.
- **Safe extensibility:** No arbitrary executable code in configuration.
- **Predictable inheritance:** Override priority is deterministic.
- **Responsive by design:** Configuration supports defined responsive behavior.
- **Accessible defaults:** Themes must preserve contrast and usable interaction.
- **Version compatibility:** Old configurations must be validated or migrated.
- **Tenant isolation:** All private configuration is tenant-scoped.
- **Renderer independence:** Editors do not implement their own rendering rules.
- **Deployment portability:** No provider-specific theme behavior.

### 2.3 Non-Negotiable Invariants
1. A theme cannot execute code.
2. A layout cannot reference an unregistered component.
3. A component cannot accept unknown properties unless its schema explicitly allows them.
4. Restaurant customization cannot override platform security restrictions.
5. The public menu cannot access draft editor configuration.
6. Preview cannot accidentally publish.
7. A theme update cannot silently corrupt existing restaurant customizations.
8. Invalid configuration cannot be published.
9. All configuration writes must be tenant-authorized.
10. The renderer must receive normalized configuration, not raw untrusted input.

---

## 3. Customization Model & Configuration Hierarchy

### 3.1 Four Primary Configuration Layers
1. **Layer 1 — Design Tokens:** Primitive visual values: colors, typography, spacing, borders, shadows, and sizing.
2. **Layer 2 — Theme Preset:** A coordinated visual identity built from tokens and approved theme-level rules.
3. **Layer 3 — Layout Configuration:** Page structure, category arrangement, item presentation, and responsive layout behavior.
4. **Layer 4 — Component Configuration:** Component selection, ordering, visibility, and schema-defined properties.

### 3.2 Override Resolution Priority
Resolution priority, from lowest to highest:
1. Platform default values.
2. Selected theme preset.
3. Restaurant theme overrides.
4. Selected layout defaults.
5. Restaurant layout overrides.
6. Component definition defaults.
7. Restaurant component instance configuration.
8. Responsive overrides (only where supported by the property).

*Note: Security and accessibility constraints are validation rules that cannot be bypassed by any layer.*

### 3.3 Merge Semantics
- **Scalar:** Higher-priority valid value replaces lower-priority value.
- **Object:** Recursively merge only declared schema properties.
- **Array:** Replace as a complete array unless explicitly configured with identity-based merge.
- **null:** Reset value only if property explicitly supports reset semantics; otherwise invalid.
- **Unknown properties / Component IDs:** Strictly rejected (HTTP 422).

---

## 4. Design Token Architecture

### 4.1 Token Categories
- `color`: brand (primary, secondary, accent), surface (default, subtle, raised), text (primary, secondary, inverse), border (default), status (success, warning, error).
- `typography`: fontFamily (body, heading), fontSize (small, body, heading, display), fontWeight (normal, medium, bold), lineHeight, letterSpacing.
- `spacing`: xs (0.25rem), sm (0.5rem), md (1rem), lg (1.5rem), xl (2rem), 2xl (3rem).
- `radius`: none (0), small (0.25rem), medium (0.75rem), large (1rem), full (9999px).
- `shadow`: none, sm, card, raised, floating.
- `sizing`: contentWidth, cardWidth, imageRatio.
- `motion`: durationFast, durationNormal, durationSlow, easingDefault.
- `breakpoints`: mobile (375px), tablet (768px), desktop (1024px), wide (1440px).

### 4.2 CSS Variable Generation
Design tokens compile deterministically to allowlisted CSS custom properties:
`--mm-color-brand-primary`, `--mm-color-surface-default`, `--mm-color-text-primary`, `--mm-spacing-card`, `--mm-radius-card`.
No arbitrary CSS rules or style injections are permitted.

---

## 5. Theme Presets Catalogue
Six platform presets are provided:
1. **Luxury:** Obsidian surface (`#0D0E12`), Cinzel serif typography, restrained gold accent (`#D4AF37`), elevated card styling.
2. **Minimal:** Clean monochrome (`#FFFFFF`, `#17212B`), Inter typography, low visual density.
3. **Rustic:** Terracotta hues (`#8B4513`, `#E6D5B8`), warm amber highlights, natural comfortable spacing.
4. **Contemporary:** Slate-charcoal palette (`#1E293B`, `#3B82F6`), structured grid layout, modern sans typography.
5. **Vibrant:** Expressive coral and mango tones (`#E11D48`, `#F59E0B`), playful rounded borders, high visual energy.
6. **Editorial:** Large food photography, serif headlines, spacious magazine-style layouts, refined pacing.

---

## 6. Layout Architecture
Four platform layouts:
1. **List Layout (`layout-list`):** Compact, text-led presentation.
2. **Grid Layout (`layout-grid`):** Structured item cards in responsive columns (1-col mobile, 2-col tablet, 3-col desktop).
3. **Image-Card Layout (`layout-image-cards`):** Photography-forward cards with descriptions and prices.
4. **Editorial Layout (`layout-editorial`):** Asymmetrical category sections with editorial hierarchy.

---

## 7. Component Registry Architecture
Authoritative catalog of 13 registered menu components:
1. `restaurant-header` (brand identity, logo, address)
2. `menu-title` (menu headline, operational badge)
3. `category-navigation` (sticky pills, tabs, horizontal scroll)
4. `category-heading` (category name, description)
5. `menu-item-card` (food item container)
6. `menu-item-image` (photo, aspect ratio, zoom)
7. `menu-item-price` (formatted price, portion pricing)
8. `menu-item-description` (item text, truncated/expanded)
9. `dietary-label` (veg, non-veg, vegan, egg, jain badges)
10. `allergen-label` (gluten, nuts, dairy warnings)
11. `availability-indicator` (in stock, sold out badge)
12. `menu-footer` (fssai license, restaurant disclosures)
13. `contact-information` (phone, timings, location link)

Permitted slots: `menu.root`, `header`, `navigation`, `content`, `category.header`, `category.items`, `footer`.

---

## 8. Canonical Customization Document & API
Canonical JSON schema at `packages/contracts/schemas/menu-customization.schema.json`.

### Endpoints:
- `GET /api/v1/menus/{menu_id}/customization` - Retrieve current draft.
- `PUT /api/v1/menus/{menu_id}/customization` - Save complete validated draft with ETag/If-Match concurrency check.
- `POST /api/v1/menus/{menu_id}/customization/validate` - Validate payload without persisting.
- `POST /api/v1/menus/{menu_id}/customization/preview` - Generate ephemeral draft preview.
- `POST /api/v1/menus/{menu_id}/customization/reset` - Reset customization to theme preset defaults.
- `GET /api/v1/menus/{menu_id}/customization/revisions` - List revision history.
- `GET /api/v1/menus/{menu_id}/customization/revisions/{rev}` - Retrieve specific historical revision.
- `POST /api/v1/menus/{menu_id}/customization/revisions/{rev}/restore` - Restore historical revision as new draft.
- `GET /api/v1/themes` - List platform themes catalogue.
- `GET /api/v1/themes/{theme_id}` - Retrieve theme definition.
- `GET /api/v1/layouts` - List layout definitions.
- `GET /api/v1/layouts/{layout_id}` - Retrieve layout definition.
- `GET /api/v1/components` - List registered components.
- `GET /api/v1/components/{component_id}` - Retrieve component definition.

---

## 9. Verification & Acceptance
- 104 automated test scenarios (`ARC08-T001` to `ARC08-T104`).
- 18 verification areas (`ARC08-VF01` to `ARC08-VF18`).
- 8 product validation scenarios (`VAL-01` to `VAL-08`).
- 27 architectural decisions (`ARC08-D01` to `ARC08-D27`).
