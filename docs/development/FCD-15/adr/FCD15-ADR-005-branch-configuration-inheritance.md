# FCD15-ADR-005: Explicit Branch Override Inheritance Semantics

- **Status**: Accepted
- **Decision**: Distinguish absent (`None`, inherits restaurant default) from explicitly disabled (`enabled=False`, stops inheritance) via `BranchConfiguration` and `BranchServiceConfiguration`.
