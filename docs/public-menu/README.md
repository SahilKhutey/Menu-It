# Public Menu Delivery Guide

## Overview
ModularMenu delivers fast, mobile-first, QR-accessible digital menus for dining guests.

## URLs & Routing
- Web View: `/r/[slug]/[menuSlug]`
- Canonical REST API: `GET /api/v1/public/restaurants/{restaurant_slug}/menus/{menu_slug}/render`
- Lightweight Metadata: `GET /api/v1/public/restaurants/{restaurant_slug}/menus/{menu_slug}/metadata`

## Caching Strategy
- `Cache-Control: public, max-age=60, s-maxage=300, stale-while-revalidate=86400`
- `ETag: "{checksum}"`
- Supports HTTP 304 Not Modified for high-concurrency QR code scanning.
