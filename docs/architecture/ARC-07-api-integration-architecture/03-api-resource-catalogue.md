# 03. API Resource Catalogue

## 1. Endpoint Inventory
The ModularMenu API exposes 66 production endpoints across 10 resource groups:

### 1. Authentication & Identity (`/api/v1/auth`)
- `POST /api/v1/auth/register` - Create user, tenant organization, and default restaurant.
- `POST /api/v1/auth/login` - Authenticate credentials and issue session cookie.
- `POST /api/v1/auth/logout` - Invalidate session and clear cookies.
- `POST /api/v1/auth/refresh` - Refresh session credentials.
- `GET /api/v1/auth/me` - Retrieve authenticated actor profile and memberships.

### 2. Organizations & Tenancy (`/api/v1/organizations`)
- `GET /api/v1/organizations` - List user's organizations.
- `POST /api/v1/organizations` - Create organization tenant.
- `GET /api/v1/organizations/{id}` - Retrieve organization details.
- `PATCH /api/v1/organizations/{id}` - Update organization profile.
- `GET /api/v1/organizations/{id}/members` - List organization members.
- `POST /api/v1/organizations/{id}/invitations` - Invite member.
- `DELETE /api/v1/organizations/{id}/members/{user_id}` - Revoke membership.

### 3. Restaurants & Branches (`/api/v1/restaurants`)
- `GET /api/v1/restaurants` - List user's restaurants.
- `POST /api/v1/restaurants` - Create restaurant branch.
- `GET /api/v1/restaurants/{id}` - Get restaurant branch details.
- `PATCH /api/v1/restaurants/{id}` - Update restaurant details.
- `GET /api/v1/restaurants/{id}/settings` - Get restaurant operational settings.
- `PATCH /api/v1/restaurants/{id}/settings` - Update operational settings.
- `GET /api/v1/restaurants/{id}/design-config` - Get visual design configuration.
- `PUT /api/v1/restaurants/{id}/design-config` - Save visual design configuration.
- `POST /api/v1/restaurants/{id}/design-config/validate` - Validate token overrides.

### 4. Menus & Categories (`/api/v1/menus`, `/api/v1/categories`)
- `GET /api/v1/restaurants/{id}/menus` - List menus.
- `POST /api/v1/restaurants/{id}/menus` - Create menu.
- `GET /api/v1/menus/{id}` - Get menu draft details.
- `PATCH /api/v1/menus/{id}` - Update menu metadata.
- `DELETE /api/v1/menus/{id}` - Delete menu.
- `GET /api/v1/menus/{id}/categories` - List categories under menu.
- `POST /api/v1/menus/{id}/categories` - Create category.
- `POST /api/v1/menus/{id}/categories/reorder` - Reorder categories.
- `PATCH /api/v1/categories/{id}` - Update category.
- `DELETE /api/v1/categories/{id}` - Delete category.
- `GET /api/v1/categories/{id}/items` - List food items.
- `POST /api/v1/categories/{id}/items` - Create food item.

### 5. Items, Pricing & Availability (`/api/v1/items`)
- `GET /api/v1/items/{id}` - Get item details.
- `PATCH /api/v1/items/{id}` - Update item properties.
- `DELETE /api/v1/items/{id}` - Delete item.
- `POST /api/v1/items/{id}/prices` - Create price tier.
- `PATCH /api/v1/items/{id}/availability` - Quick-toggle item availability.

### 6. Themes & Layouts (`/api/v1/themes`)
- `GET /api/v1/themes` - List platform theme presets.
- `GET /api/v1/themes/{theme_key}` - Get theme tokens.

### 7. Editor, Preview & Publication (`/api/v1/menus/{id}/...`)
- `GET /api/v1/menus/{id}/editor-state` - Full composite editor state.
- `POST /api/v1/menus/{id}/preview` - Ephemeral preview generation.
- `POST /api/v1/menus/{id}/validate` - Pre-publication validation rules.
- `POST /api/v1/menus/{id}/publish` - Publish snapshot with immutable SHA-256 hash.
- `POST /api/v1/menus/{id}/rollback` - Revert to previous published version.
- `GET /api/v1/menus/{id}/publications` - List version history.

### 8. Public Diners (`/api/v1/public`)
- `GET /api/v1/public/{restaurant_slug}/{menu_slug}` - Resolve active published menu snapshot.
- `GET /api/v1/public/{restaurant_slug}/{menu_slug}/health` - Diners route heartbeat.

### 9. Media & Uploads (`/api/v1/media`)
- `POST /api/v1/media/upload-url` - Request pre-signed image upload URL.
- `GET /api/v1/media/{id}` - Get media asset metadata.
- `DELETE /api/v1/media/{id}` - Remove media asset.

### 10. Platform & Observability (`/api/v1/platform`, `/health`)
- `GET /health` - Comprehensive system and dependency health check.
- `GET /api/v1/platform/overview` - Platform administrative metrics.
