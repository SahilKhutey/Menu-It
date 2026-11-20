# Devlog-002: ARC-01 System Architecture Overview
**Date:** 2026-11-19  
**Milestone:** ARC-01 System Architecture Overview  
**Git Tag:** `v1.0.0-arc01`  
**Status:** Approved Baseline  
**Author:** ModularMenu Architecture Team  

---

## 1. Scope & System Definition

ARC-01 established the high-level architecture baseline for ModularMenu, codifying the product identity, external actors, operational boundaries, 7-layer architecture, and 10 non-negotiable invariants.

---

## 2. System Context & External Actors

The platform formally identifies and isolates 7 external actors:
1. **Platform Owner:** Global multi-tenant administration, licensing, system telemetry.
2. **Platform Staff / Support:** Time-bounded, audited support access.
3. **Restaurant Owner / Brand Manager:** Organizational account administration, branch management, billing.
4. **Restaurant Manager / Chef:** Menu creation, real-time item availability toggles, price updates.
5. **Marketing & Brand Designer:** Visual theme customization, typography selection, layout configuration.
6. **Dining Guest (Diner):** Frictionless mobile browsing, dietary filtering, portion selection.
7. **External Consumer / Aggregator:** Read-only access to published menu versions via API.

---

## 3. Seven Architectural Layers

ModularMenu is organized into 7 distinct structural layers:
1. **Presentation & Studio Layer:** Responsive Next.js 14 web application hosting the 3-panel visual studio and restaurant administrative dashboard.
2. **Public Diner Delivery Layer:** Ultra-lean, edge-cacheable mobile webview rendering frozen JSON menu snapshots.
3. **Application & Use Case Layer:** Orchestrates business operations, tenant resolution, and authorization.
4. **Domain Capabilities Layer:** Pure Python domain entities, aggregates, and value objects.
5. **Persistence & Relational Layer:** PostgreSQL relational storage with composite foreign key ownership chains.
6. **Media & Asset Storage:** S3-compatible object storage with tenant-prefixed key paths.
7. **Infrastructure & Deployment Adapter Layer:** Abstracts environment specifics between Managed SaaS and Customer-Hosted Docker containers.

---

## 4. Ten Non-Negotiable Architectural Invariants

ARC-01 locked 10 invariants governing all future development:
- **INV-01 (Zero-Fork Customization):** Custom branding occurs exclusively through data configuration.
- **INV-02 (Strict Tenant Sovereignty):** No cross-tenant data access, queries, or entity linkages.
- **INV-03 (Content & Presentation Independence):** Menu catalog items are strictly decoupled from visual themes.
- **INV-04 (Immutable Snapshot Publishing):** Public diners browse immutable, SHA-256 verified snapshots; never mutable draft tables.
- **INV-05 (Infrastructure Neutrality):** 100% binary and schema parity across cloud and on-premise appliances.
- **INV-06 (CQRS-Lite Pathways):** Relational transactional write path; pre-compiled static read path.
- **INV-07 (Diner Ergonomics):** <120 kB JS bundle, zero login friction, WCAG 2.1 AA accessible.
- **INV-08 (Monetary Correctness):** Integer minor units or exact Decimals; floating point is prohibited.
- **INV-09 (Temporal Clarity):** UTC TIMESTAMPTZ across all entities, logs, and events.
- **INV-10 (Progressive Extensibility):** Whitelisted component registry; no arbitrary script injection.
