# 18 — Data Lifecycle, Retention and Deletion

## 1. Lifecycle State Machine

- Organizations: `pending` -> `active` -> `suspended` -> `deletion_pending` -> `deleted`
- Restaurants: `active` -> `inactive` -> `suspended` -> `archived`
- Menus: `draft` -> `active` -> `archived`

Deletion requests observe a mandatory retention window, preventing accidental loss of financial or audit history.
