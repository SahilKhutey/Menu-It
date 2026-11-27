# FCD-15 — 08 Configuration Resolution

`RestaurantConfigurationService.resolve_effective_configuration` delegates to `build_effective_configuration` with strict precedence: `BranchOverride` -> `RestaurantDefault` -> `OrganizationDefault` -> `SystemDefault`. An explicit branch override with `enabled=False` disables inheritance.
