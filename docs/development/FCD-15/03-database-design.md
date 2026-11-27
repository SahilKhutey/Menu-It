# FCD-15 — 03 Database Design

Alembic migration `0010_create_fcd15_restaurant_configuration.py` extends `restaurant_profiles` and creates:
- `restaurant_branding`
- `restaurant_weekly_hours`
- `restaurant_schedule_exceptions`
- `restaurant_service_configurations`
- `restaurant_operational_settings`
- `branch_configurations`, `branch_weekly_hours`, `branch_service_configurations`
- `restaurant_publications`, `restaurant_configuration_revisions`

All tables enforce tenant-aware composite foreign keys and PostgreSQL `ENABLE` + `FORCE ROW LEVEL SECURITY` isolation policies.
