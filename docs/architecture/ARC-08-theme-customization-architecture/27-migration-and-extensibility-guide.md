# ARC-08 §27 — Migration & Extensibility Guide

## 1. Version Migrations (v0.9 $\to$ v1.0)
Legacy configurations (`theme_preset: "minimal"`) are seamlessly migrated to v1.0 canonical format (`theme: { "id": "theme-minimal", "version": "1.0.0" }`) via `packages/contracts/manifests/configuration-migrations.json`.

## 2. Introducing New Platform Themes
1. Add theme definition into `packages/contracts/manifests/theme-catalogue.json`.
2. Validate against `theme-definition.schema.json`.
3. Verify WCAG 2.1 AA contrast ratios across all token combinations.
4. Regenerate TypeScript contracts and run regression test suite.
