# FCD15-ADR-002: Branding & FCD-09 Asset Storage Integration

- **Status**: Accepted
- **Decision**: Store asset UUIDs (`logo_asset_id`, `alternate_logo_asset_id`, `cover_asset_id`, `favicon_asset_id`) in `restaurant_branding` referencing FCD-09 `FileService` assets, and validate all colors via `HexColor` to prevent arbitrary CSS injection.
