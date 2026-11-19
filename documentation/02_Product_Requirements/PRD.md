# Product Requirements Document (PRD) — ModularMenu
**Status:** Approved Baseline  
**Target Release:** MVP v1.0.0  
**Focus Market:** India-First, Web-First, Mobile-First Customer Rendering

---

## 1. Scope & Target Personas

### Personas
1. **Diner / Guest (Customer):** Anonymous mobile browser user scanning table QR code. Wants instantaneous loading (<1.5s), intuitive filtering by dietary preference (Pure Veg, Jain, Halal/Non-Veg), clear pricing, item imagery, and allergen transparency. Zero login friction.
2. **Restaurant Staff / Manager:** Fast-paced floor manager needing to 86 (mark out of stock) an item in 3 taps, change daily special prices, or toggle from Lunch to Dinner menu.
3. **Restaurant Owner / Brand Lead:** Visual perfectionist configuring brand palette, uploading logo, selecting typography, and aligning digital menu with physical restaurant ambiance using the Visual Editor.
4. **Platform Operator (Super Admin):** Platform owner monitoring multi-tenant health, managing SaaS subscriptions, approving customer accounts, and issuing customer-hosted license keys.

---

## 2. In-Scope vs Out-of-Scope (MVP Boundary)

### Strictly In-Scope (MVP v1.0)
- Multi-tenant Organization & Restaurant management.
- Complete Catalog CRUD: Menus, Categories (N-level), Food Items, Variants (portion sizes), Add-ons.
- Indian dining essentials: Dietary tags (Veg, Non-Veg, Egg, Vegan, Jain), Spice Indicators (1-4 peppers), Taxes & Service Charge display toggles.
- Theme Engine with 6 pre-built presets and token overrides.
- Dual-mode customization: Settings Editor + 3-Panel Visual Editor with live mobile preview.
- Versioned Publishing Engine: atomic snapshot publication, SHA-256 checksums, one-click rollback.
- Public Responsive Menu Renderer with instant category scrolling and search.
- Dynamic high-resolution QR code generator (PNG / SVG).
- Hybrid deployment profiles (Managed SaaS profile and Docker self-hosted profile).

### Out-of-Scope (Post-MVP Roadmap)
- Online payment processing & payment gateway integration (Razorpay/Stripe checkout).
- Real-time customer cart and kitchen order ticketing (KOT) / POS integration.
- Delivery courier dispatch / logistics aggregator integrations.
- Native iOS / Android store apps (PWA capabilities cover mobile requirements).
