# Devlog-003: ARC-02 Architectural Principles, Standards & Constraints
**Date:** 2026-11-19  
**Milestone:** ARC-02 Engineering Standards Baseline  
**Git Tag:** `v1.0.0-arc02`  
**Status:** Approved & Implemented  
**Author:** ModularMenu Architecture Team  

---

## 1. Objective & Scope

ARC-02 converts the high-level architecture from ARC-01 into enforceable engineering standards, design constraints, and automated quality gates. It establishes the rules governing code structure, module imports, error handling, monetary math, and test verification.

---

## 2. Key Architecture Principles (P-01 to P-10)

- **P-01 (Modularity):** Independent business modules exposing public Protocol interfaces.
- **P-02 (Separation of Concerns):** Strict decoupling of API, Application, Domain, and Infrastructure.
- **P-03 (Configuration-Driven Presentation):** Design tokens compiled to CSS custom properties.
- **P-04 (Tenant Isolation):** Multi-layered defense in depth.
- **P-05 (Content/Theme Decoupling):** Schema separation between menu entities and design tokens.
- **P-06 (Renderer Decoupling):** Public mobile renderer isolated from editor studio code.
- **P-07 (WORM Publishing):** Write-Once, Read-Many published snapshots.
- **P-08 (Deployment Portability):** Unified codebase for Managed SaaS and Docker Appliance.
- **P-09 (Secure by Design):** Cryptographic security, least privilege, RFC 7807 error envelopes.
- **P-10 (Extensibility via Registry):** Controlled component allowlist.

---

## 3. Engineering Deliverables & Implementation

1. **Contracts Package (`packages/contracts/`):**
   - `theme_schema.json`: Complete JSON Schema for theme tokens (colors, typography, spacing, card styles).
   - `component_registry.json`: Controlled catalogue of UI components.
2. **RFC 7807 Problem Details:**
   - Standardized error format implemented across backend exception handlers.
3. **Automated AST Boundary Testing:**
   - Implemented `tests/architecture/test_module_boundaries.py` using Python's `ast` module to scan for forbidden imports.
4. **Automated Test Matrix:**
   - 23 initial test suites verified across unit, contract, integration, and architecture layers.
5. **Architecture Decisions:**
   - Recorded `ADR-0001` through `ADR-0012` in `docs/decisions/decision-register.md`.
