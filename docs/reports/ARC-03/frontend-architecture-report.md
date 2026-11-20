# ARC-03 Frontend Architecture Report

**Document ID:** REP-ARC03-FE  
**Project:** ModularMenu / Menu-It  
**Governing Specification:** ARC-03 §3 (Frontend Application Architecture)  
**Status:** Approved & Formally Verified  
**Audit Date:** 2026-11-20  

---

## 1. Overview & Technology Stack

The frontend application provides the user interfaces for ModularMenu across three operational surfaces:
1. **Public Diner Menu Experience (`/r/[slug]`):** Ultra-fast, responsive, zero-auth menu display for diners scanning QR codes.
2. **Visual Studio & Management Studio (`/app`):** Dynamic 3-panel visual customizer with instant live preview.
3. **Platform Portal (`/platform`):** Centralized administration and restaurant onboarding.

### Technology Stack Baseline:
- **Framework:** Next.js 14 (App Router)
- **UI Runtime:** React 18 & TypeScript 5
- **Styling:** Tailwind CSS with CSS Custom Properties (`--theme-*`)
- **API Communication:** Decoupled REST (`/api/v1/`) via typed API client

---

## 2. Directory & Feature Organization

The frontend codebase is organized into domain-specific features and shared libraries, following ARC-03 §3.2:

```
frontend/src/
├── app/                      # Next.js App Router route segments
│   ├── page.tsx              # Landing / routing root
│   ├── app/page.tsx          # Restaurant visual management studio
│   ├── platform/page.tsx     # Platform administrative portal
│   └── r/[slug]/page.tsx     # Public customer diner route (SSR/Dynamic)
├── features/                 # Domain-driven feature modules
│   └── menus/                # Menu management & querying feature
│       ├── components/       # Feature-specific React components
│       ├── services/         # Feature API service wrappers (menu-api.ts)
│       ├── hooks/            # Feature custom hooks
│       └── index.ts          # Public feature contract
├── components/               # Shared global UI components
│   ├── ui/                   # Primitive design system components
│   ├── layout/               # Top-level shell layouts
│   └── theme-provider.tsx    # CSS variable injector
└── lib/                      # Cross-cutting utilities and infrastructure
    ├── api/                  # Shared HTTP client infrastructure
    │   ├── client.ts         # RFC 7807 error parser, X-Request-ID handler
    │   └── index.ts          # Module re-exports
    └── api.ts                # Backward-compatible API facade
```

---

## 3. Bundle Size & Performance Budget Verification

In compliance with **CON-12** and **ARC-03 §16**, the customer-facing diner route must not exceed the strict 120 kB First Load JS ceiling.

### Production Build Metrics (Next.js 14.2.35):

```
Route (app)                              Size     First Load JS
┌ ○ /                                    175 B          96.2 kB
├ ○ /_not-found                          873 B          88.2 kB
├ ○ /app                                 5.77 kB         102 kB
├ ○ /platform                            4.22 kB         100 kB
└ ƒ /r/[slug]                            7.9 kB         95.2 kB
+ First Load JS shared by all            87.3 kB
  ├ chunks/2200cc46-9ceb5a2e60a675d7.js  53.6 kB
  ├ chunks/945-738963999e8ae57a.js       31.7 kB
  └ other shared chunks (total)          1.95 kB
```

### Evaluation:
- **Diner Route (`/r/[slug]`):** **95.2 kB** (Ceiling: 120.0 kB) — **20.6% under budget**.
- **Admin Studio (`/app`):** 102 kB.
- **Platform Portal (`/platform`):** 100 kB.
- **Static Landing (`/`):** 96.2 kB.

---

## 4. API Client & RFC 7807 Error Integration

The shared API client (`frontend/src/lib/api/client.ts`) enforces standard HTTP communication rules:
- **Correlation ID Header:** Reads or generates `X-Request-ID` and attaches it to every outgoing request.
- **RFC 7807 Problem Details:** If the server returns an error status (4xx, 5xx), the client automatically parses the `application/problem+json` payload into a structured `ApiError` instance containing `type`, `title`, `status`, `detail`, `instance`, `invalid_params`, and `request_id`.
- **JWT Injection:** Reads authentication tokens from secure storage and sets `Authorization: Bearer <token>` when available.
- **Timeout Management:** Implements an `AbortController` signal with a default 10-second timeout.

---

## 5. Architectural Boundaries & Renderer Independence

Automated AST boundary test `ARCH-ARC03-007` confirms that the public menu renderer (`/r/[slug]`) maintains complete structural isolation from the visual studio editor:
- No visual editor state or drag-and-drop components are loaded by the diner.
- No administrative authentication tokens or credentials are required by the public route.
- Custom styling is applied purely via scoped CSS custom properties injected at the root container.

---

## 6. Frontend Verification Summary

The frontend architecture conforms to all requirements of ARC-03 WP-ARC03-02 and WP-ARC03-05.
