# Devlog-001: Project Initialization & Blueprint Baseline
**Date:** 2026-11-19  
**Milestone:** Pre-Development & Architectural Foundation  
**Status:** Completed  
**Author:** ModularMenu Architecture Team  

---

## 1. Product Genesis & Vision

The digital restaurant menu ecosystem has historically suffered from extreme fragmentation: either inflexible, generic QR SaaS products that restrict brand identity, or bespoke agency web apps that require independent code forks, separate repositories, and untenable maintenance overhead.

**ModularMenu** (commercial name **Menu-It**) was conceived to eliminate this dichotomy:
- An enterprise-grade, configurable, multi-tenant digital restaurant menu platform.
- Delivers rich, brand-specific diner experiences from a **single, unified application codebase**.
- Operates under a **hybrid deployment model**: Managed Multi-Tenant Cloud SaaS alongside an on-premises Customer-Hosted Docker appliance.

---

## 2. Core Strategic Decisions

During the initial architecture phase, four fundamental architectural decisions were established:
1. **Menu Deployment Architecture:** Shared multi-tenant platform with logical tenant boundaries.
2. **Customization Engine:** Dual-mode editing — settings-based form controls alongside a real-time 3-panel visual studio with 60fps CSS token compilation.
3. **Hosting Ownership:** Hybrid delivery model (Profile A: Managed SaaS; Profile B: Customer-Hosted container appliance) sharing 100% binary and schema parity.
4. **Product Naming:** `ModularMenu` as the architectural system identifier; `Menu-It` as the commercial brand.

---

## 3. Market Context: India-First & Web-First Constraints

The platform is designed around real-world restaurant conditions in India and emerging markets:
- **Mobile Web-First:** Diners must never be forced to download a native mobile app or authenticate to view a menu. Access is instantaneous upon scanning a table QR code.
- **Bandwidth Constraints:** Sub-second LCP (<1.5s) on 3G/4G connections; strict client JavaScript bundle budget (<120 kB First Load JS).
- **Regulatory & Cultural Requirements:** Mandatory FSSAI dietary classifications:
  - Green dot in green square (Vegetarian)
  - Red dot in red square (Non-Vegetarian)
  - Amber dot in amber square (Egg)
  - Explicit badges for Vegan and Jain preparations.
- **Currency Standards:** Fixed-precision Indian Rupee (INR) calculations in minor units (paise) with zero floating-point representation.

---

## 4. Initial Repository & Legal Baseline

- **Repository Created:** Structured monorepo layout containing `backend/`, `frontend/`, `packages/contracts/`, and `docs/`.
- **Licensing:** Commercial Proprietary License ([LICENSE](file:///c:/Users/ASUS/Documents/Menu-it/LICENSE)) with explicit source-available clauses for customer-hosted enterprise licensees.
- **Initial Engineering Blueprint:** Master artifact `ModularMenu_Engineering_Blueprint_v1.md` established.
