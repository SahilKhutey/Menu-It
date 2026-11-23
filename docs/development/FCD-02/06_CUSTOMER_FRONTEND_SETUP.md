# FCD-02 — Customer Frontend Application Setup (`apps/web`)

## 1. Overview
The customer-facing application shell provides a modern Next.js 14 App Router web application on port 3000.

## 2. Directory Structure
```
apps/web/
├── public/
│   └── icons/                    # icon-192.png, icon-512.png (PWA assets)
├── src/
│   ├── app/
│   │   ├── layout.tsx            # Root layout with responsive Viewport & Metadata
│   │   ├── page.tsx              # Customer homepage shell
│   │   ├── globals.css           # Fluid styling, design tokens, safe-area insets
│   │   ├── loading.tsx           # Standardized loading state
│   │   ├── error.tsx             # Client error boundary
│   │   ├── not-found.tsx         # Custom 404 page
│   │   └── manifest.ts           # Web application manifest (/manifest.webmanifest)
│   └── services/
│       ├── api-client.ts         # Generic type-safe enveloped API fetch client
│       └── health-service.ts     # Operational backend health polling service
├── package.json                  # @menu-it/web package definition
├── tsconfig.json                 # Strict TypeScript configuration
└── next.config.mjs               # Next.js configuration
```

## 3. Production Build Validation
- **Status:** Verified passing
- **Static Pages:** 5/5 static pages pre-rendered
- **Bundle Size:** Initial shared First Load JS is 87.2 kB (home route total: 96.1 kB), comfortably below the 120 kB production budget.
