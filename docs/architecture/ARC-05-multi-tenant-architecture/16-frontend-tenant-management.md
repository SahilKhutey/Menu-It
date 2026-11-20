# 16 — Frontend Tenant Management & UI Isolation

## 1. Multi-Tenant Organization Switcher

The Next.js dashboard provides an authoritative organization selector:
- Active organization is stored in application state and reflected in `X-Organization-Id` request headers.
- Switching organizations triggers an immediate cache invalidation in TanStack Query.
- Route guards verify user membership before rendering branch management views.
