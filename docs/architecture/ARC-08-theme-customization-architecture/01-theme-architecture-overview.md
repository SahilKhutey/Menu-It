# ARC-08 §1 — Theme & Customization Architecture Overview

## 1. Purpose & Scope
ARC-08 establishes how restaurant operators customize the visual aesthetics, responsive typography, spacing, color palette, component layout, and structural slots of their digital menus without requiring source code modifications, arbitrary CSS injections, or tenant-specific deployments.

It enforces a **configuration-driven, schema-validated, versioned, portable, and secure** customization architecture across both deployment editions:
1. **Managed SaaS Edition:** Multi-tenant shared PostgreSQL database with strict tenant isolation, row-level boundaries, and CDN edge caching.
2. **Customer-Hosted Edition:** Self-contained, single-tenant deployment utilizing identical configuration schemas and deterministic resolvers without platform dependencies.

## 2. Core Architectural Objectives
- **OBJ-01 (Zero Executable Code):** Prohibit custom JavaScript, external script tags, style injection, or unvalidated CSS. All customizations are pure JSON data structures.
- **OBJ-02 (Schema-Validated Configuration):** Every draft and published customization conforms strictly to canonical JSON Schemas with bounded depth and size limits (max 256 KB, max 100 components, max depth 10).
- **OBJ-03 (Deterministic Theme Resolution):** Theme resolution is a pure, idempotent function ($f(\text{Theme}, \text{Overrides}) \to \text{ResolvedTokens}$) guaranteeing identical output in Python backend and TypeScript frontend.
- **OBJ-04 (Dual-Editor Parity):** Settings-based editor and visual drag-and-drop editor manipulate the exact same underlying customization document with full bi-directional state synchronization.
- **OBJ-05 (Immutable Revision History):** All draft updates create immutable revision records with optimistic concurrency control (`If-Match` / `ETag`), supporting audit trails and one-click rollback.
- **OBJ-06 (Strict Multi-Tenancy):** Customization documents, revisions, and previews are isolated to their owner organization; cross-tenant reads or writes are rejected with 404/403.
