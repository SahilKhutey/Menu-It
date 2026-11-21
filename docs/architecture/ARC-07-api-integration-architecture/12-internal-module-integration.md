# 12. Internal Module Integration

## 1. Monolith Boundary Preservation
Internal modules communicate via explicit Python interfaces (`ModuleService`) and published domain events, never through cross-module direct table joins.
