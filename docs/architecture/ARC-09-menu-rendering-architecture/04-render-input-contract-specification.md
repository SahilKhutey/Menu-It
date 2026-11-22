# ARC-09 §04 — Render Input Contract Specification

## 1. Specification Overview
The `RenderInput` contract serves as the canonical DTO consumed by all rendering components. It is defined in `packages/contracts/schemas/menu-render-input.schema.json` and mirrored in both TypeScript (`packages/contracts/generated/rendering.ts`) and Python (`app.modules.rendering.domain.render_input`).

## 2. Core Schema Structure
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MenuRenderInput",
  "type": "object",
  "required": ["restaurant", "menu", "categories", "theme", "layout", "metadata"],
  "properties": {
    "restaurant": { "$ref": "#/$defs/RenderRestaurant" },
    "menu": { "$ref": "#/$defs/RenderMenu" },
    "categories": { "type": "array", "items": { "$ref": "#/$defs/RenderCategory" } },
    "theme": { "$ref": "#/$defs/RenderTheme" },
    "layout": { "$ref": "#/$defs/RenderLayout" },
    "metadata": { "$ref": "#/$defs/RenderMetadata" }
  }
}
```

## 3. Strict Domain Invariants
- `categories` and `items` must maintain strict numeric `sort_order`.
- `price` amounts must be non-negative decimals.
- `currency_code` must default to the restaurant's operational currency (e.g., `INR`, `USD`).
- `theme.tokens` must supply valid hex or design token strings.
