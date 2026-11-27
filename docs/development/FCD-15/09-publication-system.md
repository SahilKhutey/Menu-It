# FCD-15 — 09 Publication System

`RestaurantPublicationService` manages `publish`, `unpublish`, `restore_revision`, `list_publications`, and `get_public_profile_by_slug`. Published snapshots are stored as immutable `RestaurantConfigurationRevision` records and strictly allowlist public fields without exposing internal `organization_id` or `restaurant_id`.
