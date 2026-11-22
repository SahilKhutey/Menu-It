# Draft Preview & Watermarking Guide

## Overview
Restaurant operators can preview draft menus in real time before publishing to guests.

## Access & Security
- Web Route: `/app/menus/[menuId]/preview`
- Authorized REST API: `POST /api/v1/restaurants/{restaurant_id}/menus/{menu_id}/preview`
- Access requires `verify_restaurant_access` (authenticated tenant user).
- Response headers enforce `Cache-Control: private, no-store, no-cache`.
- Visual preview banner displays `PREVIEW MODE — Unpublished Draft`.
