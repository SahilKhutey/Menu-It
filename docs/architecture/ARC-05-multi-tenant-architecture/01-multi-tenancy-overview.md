# 01 — Multi-Tenancy Overview

## 1. Context and Problem Statement

ModularMenu serves restaurant enterprises ranging from independent single-branch cafes to multi-branch regional restaurant groups. In a shared SaaS environment, multiple organizations coexist on the same compute and database infrastructure.

A single tenant boundary violation—exposing another restaurant's draft menu, pricing strategy, customer analytics, or private imagery—constitutes a critical security failure.

## 2. Core Tenancy Principles

1. **Principle P-04 (Multi-Tenant Isolation):** Total logical data isolation is non-negotiable. One tenant must never observe, modify, or infer another tenant's private assets.
2. **Server-Derived Identity:** Tenant context is resolved strictly from trusted server-side authentication and validated organization membership. Client-supplied organization IDs are selectors, never authorizations.
3. **Defense-in-Depth:** Tenancy is guarded across 8 discrete layers:
   - Layer 1: Identity & Session Authentication
   - Layer 2: Server-Side Tenant Resolution
   - Layer 3: Application Authorization & Role Checking
   - Layer 4: Application Service Context Passing
   - Layer 5: Scoped Repository Persistence
   - Layer 6: PostgreSQL Row-Level Security (RLS)
   - Layer 7: Tenant-Aware Storage & Cache Namespaces
   - Layer 8: Audit Logging & Telemetry Monitoring
4. **Dual-Edition Parity:** Both Managed SaaS and Customer-Hosted Docker appliance share 100% identical domain and authorization code.
