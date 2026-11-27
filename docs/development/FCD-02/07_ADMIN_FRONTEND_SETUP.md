# FCD-02 — Platform Administration Application Setup (`apps/admin`)

## 1. Overview
The administration frontend shell provides a dedicated platform console runtime on port 3001.

## 2. Directory Structure
```
apps/admin/
├── src/
│   ├── app/
│   │   ├── layout.tsx            # Admin layout with noindex/nofollow robots directive
│   │   ├── page.tsx              # Platform console dashboard card
│   │   ├── globals.css           # Neutral admin design variables
│   │   ├── loading.tsx           # Admin loading state
│   │   ├── error.tsx             # Admin error boundary
│   │   └── not-found.tsx         # Admin 404 handler
│   └── services/
│       ├── api-client.ts         # Enveloped API client
│       └── health-service.ts     # Health monitoring client
├── package.json                  # @menu-it/admin package definition
├── tsconfig.json                 # Strict TypeScript configuration
└── next.config.mjs               # Next.js configuration
```

## 3. Security Boundary
- The admin application has `robots: { index: false, follow: false }` configured to prevent search engine indexing.
- Actual data isolation is enforced server-side through backend authentication, authorization guards, and row-level security (FCD-04/05).
- Production build verified passing with 87.4 kB First Load JS.
