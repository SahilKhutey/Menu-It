# MOD-10 — Component Registry Module Specification

**Module ID:** MOD-10  
**Tier:** Experience Configuration (P0)  
**Package:** `app.modules.components`  

---

## 1. Ownership & Boundaries
- **Owns:** Component definitions, versions, property schemas, layout compatibility.
- **Does Not Own:** Menu data, dynamic executable code uploads.

## 2. Domain Model & Invariants
- **ComponentDefinition Entity:** `ComponentDefinition(component_id, version, schema, supported_layouts, enabled, is_deprecated)`
  - Schema property validation blocks unknown or script-injected properties.
  - Safe allowlisted component catalogue.

## 3. Public Contracts & Events
- **Provides:** `ComponentRegistryReader` Protocol (`get_component`).
- **Consumes:** None.
- **Emits:** `ComponentRegistered` (EVT-012).
