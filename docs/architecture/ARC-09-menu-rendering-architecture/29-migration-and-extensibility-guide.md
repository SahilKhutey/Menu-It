# ARC-09 §29 — Migration & Extensibility Guide

## 1. Backwards Compatibility Policy
ARC-09 maintains full backwards compatibility with:
- ARC-04 domain concepts (accepting legacy snapshot dictionaries).
- ARC-07 public menu endpoints (`/api/v1/public/restaurants/{slug}/menu`).
- ARC-08 theme presets and design configuration tokens.

## 2. Extensibility Rules
- **Adding Components**: Register new component definitions in the central catalogue manifest (`packages/contracts/manifests/render-component-map.json`) and implement them in both frontend and renderer packages.
- **Adding Layouts**: Define new layout schemas with required slot definitions in `packages/contracts/manifests/render-layout-compatibility.json`.
- **Custom Currencies**: Add symbol formatting mappings to `RenderInputBuilder.format_price`.
