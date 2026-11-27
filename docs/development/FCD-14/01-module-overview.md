# FCD-14 — 01 Module Overview

## Purpose
FCD-14 introduces the first business-facing module of Menu-It: **Organization, Restaurant & Branch Management**, converting the FCD-01–FCD-13 platform foundations into usable tenant onboarding, restaurant/branch administration, team membership, invitations, and branch-level assignments.

## Core Capabilities
1. **Organization Management**: Self-service onboarding (`POST /api/v1/organizations`), profile updates, regional/operational settings (`organization_settings`), suspension, and ownership transfer.
2. **Restaurant Management**: Restaurant brand creation under an organization, profile/contact management, regional settings (`restaurant_settings`), lifecycle transitions (`draft` → `active` → `suspended` → `archived`), and restaurant-scoped memberships.
3. **Branch Management**: Physical/operational locations under a restaurant with independent timezones, addresses, geo-coordinates, lifecycle transitions (`draft` → `active` → `temporarily_closed` → `archived`), and branch-level staff assignments (`branch_assignments`).
4. **Membership & Invitations**: Organization-level member listing, role updates, removal with atomic final-owner protection, and email invitations using cryptographically random tokens stored as SHA-256 hashes (`organization_invitations`).
5. **Frontend Experiences**: Web onboarding & workspace management (`apps/web/src/app/onboarding/*`, `apps/web/src/app/dashboard/organizations/*`) and platform admin oversight (`apps/admin/src/app/{organizations,restaurants,branches}/*`).

## Out of Scope
Menus, categories, menu items, modifiers, QR menu rendering, orders, payments, and inventory remain deferred to FCD-15+.
