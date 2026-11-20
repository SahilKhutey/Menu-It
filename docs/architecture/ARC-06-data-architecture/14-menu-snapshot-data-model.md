# 14 — Menu Snapshot Data Model & Immutability

## 1. Immutable Menu Version

`menu_versions` stores the complete frozen JSON snapshot at publication time:
- Serialized canonically with sorted keys.
- Hashed with SHA-256 (`snapshot_sha256`).
- Guarded by ORM and database triggers preventing UPDATE or DELETE.
- Modifying draft menus in the studio has zero impact on live published snapshots.
