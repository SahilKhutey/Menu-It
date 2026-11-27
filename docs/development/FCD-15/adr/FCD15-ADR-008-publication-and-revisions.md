# FCD15-ADR-008: Atomic Publication Pointers & Immutable Revisions

- **Status**: Accepted
- **Decision**: Store immutable allowlisted snapshots in `restaurant_configuration_revisions` and switch the public pointer atomically in `restaurant_publications`, supporting `unpublish` and `restore_revision`.
