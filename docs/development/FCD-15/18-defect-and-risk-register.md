# FCD-15 — 18 Defect & Risk Register

- **Inheritance ambiguity**: Mitigated by explicit `BranchConfiguration.service_override_enabled` / `BranchServiceConfiguration.enabled = False` rather than Python truthiness.
- **Public data leakage**: Mitigated by allowlisted `published_snapshot` omitting internal `organization_id` and `restaurant_id`.
- **Concurrent overwrites**: Mitigated by `expected_version` / `expected_revision` optimistic concurrency checks returning HTTP 409.
