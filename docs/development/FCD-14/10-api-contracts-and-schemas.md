# FCD-14 — 10 API Contracts & Schemas

## Endpoints Registered
All routes are registered under `/api/v1` in `apps/api/src/menu_it/api/v1/router.py` (57 total OpenAPI paths verified via `create_application().openapi()`):

- **Organizations (`api/v1/endpoints/organizations.py`)**:
  - `POST /api/v1/organizations` — Create/onboard organization
  - `GET /api/v1/organizations` — List user's organizations
  - `GET /api/v1/organizations/{organization_id}` — Get organization details
  - `PATCH /api/v1/organizations/{organization_id}` — Update organization
  - `GET /api/v1/organizations/{organization_id}/settings` & `PUT .../settings` — Organization settings
  - `POST /api/v1/organizations/{organization_id}/suspend` — Suspend organization
  - `GET /api/v1/organizations/{organization_id}/members`, `PATCH .../members/{user_id}`, `DELETE .../members/{user_id}`
  - `POST /api/v1/organizations/{organization_id}/transfer-ownership`
  - `POST /api/v1/organizations/{organization_id}/invitations`, `GET .../invitations`, `DELETE .../invitations/{invitation_id}`, `POST /api/v1/organizations/invitations/accept`
- **Restaurants (`api/v1/modules/restaurants/router.py`)**:
  - CRUD, status transitions, restaurant settings, and restaurant membership assignment under `/api/v1/organizations/{organization_id}/restaurants` and `/api/v1/restaurants`.
- **Branches (`api/v1/endpoints/branches.py`)**:
  - `POST /api/v1/restaurants/{restaurant_id}/branches`, `GET /api/v1/restaurants/{restaurant_id}/branches`
  - `GET /api/v1/branches/{branch_id}`, `PATCH /api/v1/branches/{branch_id}`, `POST /api/v1/branches/{branch_id}/status`
  - `GET /api/v1/branches/{branch_id}/assignments`, `PUT /api/v1/branches/{branch_id}/assignments/{user_id}`, `DELETE /api/v1/branches/{branch_id}/assignments/{user_id}`
