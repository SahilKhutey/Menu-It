# ARC-08 §13 — Customization API Specification

All endpoints are versioned under `/api/v1` and enforce tenant-scoped authorization:

| Method | Endpoint | Permission | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/menus/{id}/customization` | `menu.customization.read` | Retrieve active customization draft & ETag |
| `PUT` | `/menus/{id}/customization` | `menu.customization.update`| Update draft with optimistic concurrency (`If-Match`) |
| `POST` | `/menus/{id}/customization/validate`| `menu.customization.validate`| Validate customization payload without saving |
| `POST` | `/menus/{id}/customization/preview` | `menu.preview` | Generate ephemeral preview with resolved tokens |
| `POST` | `/menus/{id}/customization/reset` | `menu.customization.update`| Reset draft back to clean theme/layout defaults |
| `GET` | `/menus/{id}/customization/revisions`| `menu.customization.read` | List historical revision metadata |
| `GET` | `/menus/{id}/customization/revisions/{rev}`| `menu.customization.read`| Fetch full historical revision document |
| `POST` | `/menus/{id}/customization/revisions/{rev}/restore`| `menu.customization.restore`| Restore historical revision as new draft revision |
| `GET` | `/themes` | Public / Authenticated | List platform themes catalogue |
| `GET` | `/themes/{id}` | Public / Authenticated | Fetch theme token definition |
| `GET` | `/layouts` | Public / Authenticated | List platform layouts catalogue |
| `GET` | `/layouts/{id}` | Public / Authenticated | Fetch layout responsive grid definition |
| `GET` | `/components` | Public / Authenticated | List platform registered components |
| `GET` | `/components/{id}` | Public / Authenticated | Fetch component prop schema & slots |
