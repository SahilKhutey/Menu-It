# Engineering Work Packages (WP-01 to WP-12)
**Project:** ModularMenu  
**Tracking Model:** Strict Engineering Workflow with Verification Gates

---

### WP-01: Project Foundation & Repository Architecture (Priority: P0)
- **Scope:** Root repository setup, `.gitignore`, Docker Compose development environment, unified `.env.example`, Next.js 14+ frontend boilerplate, FastAPI backend structure, Alembic baseline, and automated test runners.
- **Exit Criteria:** Reproducible local build across frontend and backend; CI passes clean lint and smoke tests.

### WP-02: Identity & Multi-Tenancy Engine (Priority: P0)
- **Scope:** Users, Organizations, Restaurants, and Restaurant Members models. Argon2id password hashing, session tokens, tenant context middleware, role-based authorization dependencies (`owner`, `manager`, `menu_editor`, `viewer`).
- **Exit Criteria:** Multi-tenant security test suite passes with zero unauthorized access.

### WP-03: Restaurant & Menu Management Engine (Priority: P0)
- **Scope:** Restaurant profile settings (contact, hours, currency, taxes), Menus CRUD, Categories (N-level nested), Food Items CRUD, Variants (portion sizes), Addons.
- **Exit Criteria:** Complete CRUD lifecycle verified via automated API tests.

### WP-04: Pricing, Availability & Media Pipeline (Priority: P0/P1)
- **Scope:** High-precision monetary calculations (`NUMERIC(12,2)`), 86 / Out-of-Stock toggles, dietary tags (Veg, Non-Veg, Egg, Vegan, Jain), spice level rating, media asset uploads with WebP optimization.
- **Exit Criteria:** Accurate item rendering and validated image optimization pipeline.

### WP-05: Design System & 6 Theme Presets (Priority: P0)
- **Scope:** Token system (colors, typography, spacing, radius, shadows). Implementation of the 6 core themes: Luxury, Minimal, Rustic, Vibrant, Contemporary, Editorial. CSS variable generator.
- **Exit Criteria:** Theme token validation schema passing and 6 visual presets rendering accurately.

### WP-06: Menu Rendering Engine (Public Mobile Menu) (Priority: P0)
- **Scope:** High-performance public customer menu page (`/r/[restaurantSlug]`), instant category jump bar, fast search & dietary filter pills, item detail bottom sheets, allergen alerts.
- **Exit Criteria:** Sub-1.5s LCP on simulated 4G mobile, 95+ Mobile Lighthouse score.

### WP-07: Administration Dashboard (Priority: P0)
- **Scope:** Secure manager portal (`/app`): menu builder, category reordering, quick item 86ing, restaurant operational settings.
- **Exit Criteria:** Intuitive, responsive dashboard for restaurant operators.

### WP-08: Visual Menu Editor (Priority: P0)
- **Scope:** 3-panel interactive studio: Left structure tree, Center live responsive viewport (mobile/tablet/desktop preview), Right property inspector for themes and components. Undo/redo history.
- **Exit Criteria:** Real-time visual updates on canvas without direct production DB mutation.

### WP-09: Publishing Engine & Version Snapshots (Priority: P0)
- **Scope:** Atomic snapshot generator, JSON serialization, SHA-256 checksums, immutable version archives in `menu_versions`, active pointer in `publications`, dynamic QR code generator (SVG/PNG).
- **Exit Criteria:** One-click publish, zero-downtime cache invalidation, and instant rollback.

### WP-10: Hybrid Deployment Package (Priority: P0)
- **Scope:** Managed Cloud configuration vs. Customer-Hosted Docker package (`docker-compose.yml`, `install.sh`, `backup.sh`, `restore.sh`), offline license verifier.
- **Exit Criteria:** Standalone customer deployment runs in a single `docker compose up` command.

### WP-11: Security & Quality Audit (Priority: P0)
- **Scope:** Full cross-tenant penetration tests, WCAG 2.1 AA accessibility audit, performance benchmarking, automated E2E customer journey test.
- **Exit Criteria:** All 8 critical security tests pass; zero P0/P1 bugs.

### WP-12: Commercial MVP Launch & Customer Onboarding (Priority: P0)
- **Scope:** Initial demo restaurant seed datasets (Fine Dining, Pizzeria, Cafe, Street Food), marketing onboarding flow, documentation pack.
- **Exit Criteria:** Platform is commercially live and ready for first paying restaurant.
