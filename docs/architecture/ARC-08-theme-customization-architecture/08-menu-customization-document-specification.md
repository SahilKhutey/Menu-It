# ARC-08 §8 — Menu Customization Document Specification

## 1. Document Structure
A valid menu customization document conforms to `packages/contracts/schemas/menu-customization.schema.json`:
```json
{
  "configuration_version": "1.0.0",
  "schema_version": "1.0.0",
  "theme": {
    "id": "theme-minimal",
    "version": "1.0.0",
    "overrides": {
      "color": {
        "brand": { "primary": "#E11D48" }
      }
    }
  },
  "layout": {
    "id": "layout-grid",
    "version": "1.0.0",
    "settings": { "card_gap": "1rem" },
    "responsive": {
      "mobile": { "columns": 1, "navigation": "horizontal-scroll" },
      "tablet": { "columns": 2, "navigation": "horizontal-scroll" },
      "desktop": { "columns": 3, "navigation": "inline" }
    }
  },
  "components": [ ... ],
  "metadata": {
    "revision": 2,
    "updated_at": "2026-11-22T14:15:00Z"
  }
}
```

## 2. Boundary Invariants
- **Max Payload Size:** 256 KB.
- **Max Component Instances:** 100 components per menu.
- **Max JSON Nesting Depth:** 10 levels.
- **Instance ID Format:** Alphanumeric with hyphens/underscores (`[a-zA-Z0-9_-]{1,64}`).
