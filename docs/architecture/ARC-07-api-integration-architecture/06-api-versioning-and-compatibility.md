# 06. API Versioning and Compatibility

## 1. Versioning Strategy
- ModularMenu uses URI path versioning: `/api/v1/`.
- Breaking changes require a major version increment (e.g., `/api/v2/`).
- Additive changes (new optional fields, new endpoints) occur within `v1` without breaking existing consumers.

## 2. Sunset and Deprecation Policy
- Deprecated endpoints include `Deprecation: true` and `Sunset: <date>` HTTP headers.
- Support policy mandates minimum 6 months deprecation window before sunset.
