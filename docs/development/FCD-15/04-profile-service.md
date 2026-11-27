# FCD-15 — 04 Profile Service

`RestaurantConfigurationService.get_profile` and `update_profile` manage `RestaurantProfileRecord` with optimistic concurrency (`expected_version` -> `ConcurrencyConflictError`), outbox events (`restaurant.profile.updated`), and audit logging.
