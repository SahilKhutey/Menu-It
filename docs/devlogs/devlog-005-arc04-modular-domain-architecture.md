# Devlog-005: ARC-04 Modular Domain Architecture & Bounded Contexts
**Date:** 2026-11-20  
**Milestone:** ARC-04 Modular Domain Architecture  
**Git Tag:** `v1.0.0-arc04`  
**Status:** Approved & Implemented  
**Author:** ModularMenu Architecture Team  

---

## 1. Domain Decomposition: 16 Discrete Business Modules

ARC-04 decomposed ModularMenu into 16 discrete, cohesive business modules across 5 capability groups:
- **Core Identity & Tenancy:**
  - `MOD-01`: Identity & Access Management
  - `MOD-02`: Organization & Tenancy Boundary
  - `MOD-03`: Restaurant & Location Management
- **Menu Catalog & Structure:**
  - `MOD-04`: Menu Catalog Structure
  - `MOD-05`: Category Management
  - `MOD-06`: Food Item Catalog
- **Pricing & Presentation:**
  - `MOD-07`: Pricing, Portion & Variant Engine
  - `MOD-08`: Dietary, Allergen & FSSAI Classification
  - `MOD-09`: Theme Token & Style Engine
  - `MOD-10`: Layout Preset & Slot Composition
  - `MOD-11`: Component Allowlist Registry
- **Authoring & Publishing:**
  - `MOD-12`: Visual Studio & Menu Authoring Engine
  - `MOD-13`: Publishing, Snapshot & Rollback Lifecycle
  - `MOD-14`: Public Diner Delivery & Resolution Engine
- **Cross-Cutting Operations:**
  - `MOD-15`: Media Asset Management
  - `MOD-16`: Licensing, Subscription & Entitlements

---

## 2. Module Autonomy & AST Enforcement

- Each module contains an authoritative `module.yaml` manifest declaring its owned entities, exposed protocols, permitted dependencies, and consumed domain events.
- **Automated AST Boundary Verification:** `tests/architecture/test_arc04_boundaries.py` parses the Python AST across all modules to guarantee:
  1. Zero circular dependencies.
  2. Zero private cross-module imports.
  3. Zero cross-module direct ORM access.

---

## 3. Standardized Domain Events & Primitives

- **18 Standardized Domain Events:** `EVT-001` through `EVT-018` with correlation IDs and UTC timestamps.
- **Domain Value Objects:** `Money` (finite non-negative Decimal), `EmailAddress`, `RestaurantSlug`, `MenuSlug`, `DisplayOrder`.
- **50-Test Catalogue (ARC04-T001 to ARC04-T050):** Expanded total test count to **94 passing tests**.
- **Decision Records:** `ADR-0028` through `ADR-0043` recorded in `docs/decisions/decision-register.md`.
