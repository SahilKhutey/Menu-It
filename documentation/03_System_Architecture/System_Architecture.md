# System & Technical Architecture Specification
**Architecture Pattern:** Modular Monolith with Domain-Driven Boundaries  
**Target Environment:** Shared Multi-Tenant Managed SaaS + Standalone Docker Self-Hosted

---

## 1. Architectural Principles
1. **Zero Data Leakage:** Tenant boundary isolation enforced at routing, query-building, and DB Row-Level Security (RLS) layers.
2. **Read-Heavy Optimization:** Public customer menus serve pre-compiled, immutable JSON snapshot payloads directly from memory/cache or CDN edge. The main relational database is completely shielded during peak dining rushes.
3. **Configuration over Custom Code:** A single rendering engine interprets declarative JSON configurations for themes, layouts, and components.
4. **Environment-Driven Polymorphism:** Business logic is identical across Cloud and Self-Hosted editions; differences exist solely at infrastructure boundary adapters.

---

## 2. Component Diagram

```mermaid
graph TD
    subgraph Client Layer
        MobileGuest["Mobile Guest (QR Scanner / Web Browser)"]
        RestOwner["Restaurant Manager (Desktop / Tablet)"]
        SuperAdmin["Platform Admin (Desktop Browser)"]
    end

    subgraph Edge & Routing Layer
        ReverseProxy["Reverse Proxy / Nginx / Caddy / Cloudflare"]
    end

    subgraph NextJS Frontend Service
        PublicMenu["Customer Menu Renderer (/r/[slug])"]
        DashApp["Restaurant Dashboard & Visual Builder (/app)"]
        AdminApp["Platform Admin Panel (/platform)"]
    end

    subgraph FastAPI Application Core
        AuthMiddleware["Tenant & Session Auth Middleware"]
        RouterHub["API v1 Gateway (/api/v1)"]
        
        subgraph Domain Modules
            IdentityMod["Identity & RBAC (MOD-01)"]
            TenantMod["Tenant & Org Engine (MOD-02, 03)"]
            CatalogMod["Menu & Item Catalog (MOD-04, 05, 06, 07)"]
            ThemeMod["Theme & Layout Engine (MOD-08, 09, 10)"]
            EditorMod["Visual Editor State Engine (MOD-12)"]
            PublishMod["Publishing & Snapshot Compiler (MOD-13)"]
            LicenseMod["Licensing Engine (MOD-15)"]
        end
    end

    subgraph Storage & Infrastructure
        PostgresDB[("PostgreSQL 16 (Multi-Tenant Relational Store)")]
        SnapshotStore[("Immutable Snapshot Store (JSONB / Redis)")]
        MediaStorage[("Media Storage (S3 / Local Filesystem)")]
    end

    MobileGuest --> ReverseProxy
    RestOwner --> ReverseProxy
    SuperAdmin --> ReverseProxy

    ReverseProxy --> NextJS Frontend Service
    NextJS Frontend Service --> RouterHub
    RouterHub --> AuthMiddleware
    AuthMiddleware --> Domain Modules
    
    Domain Modules --> PostgresDB
    PublishMod --> SnapshotStore
    PublicMenu -.->|"Read Fast Snapshot"| SnapshotStore
    CatalogMod --> MediaStorage
```

---

## 3. Request Flow Lifecycles

### A. Public QR Menu Reading
1. Diner scans physical QR code: `https://modularmenu.in/r/the-bombay-canteen`.
2. Edge / Next.js catches `/r/[slug]` route.
3. Server Component fetches the latest active published snapshot from `/api/v1/public/restaurants/the-bombay-canteen/menu`.
4. The API queries the `publications` table joining `menu_versions` for `snapshot_data`.
5. The Next.js Menu Renderer feeds the snapshot into the theme-engine CSS variable injector and component registry.
6. Rendered HTML + dehydrated JSON returns to mobile viewport in under 1 second. Zero database joins on catalog tables.

### B. Menu Authoring, Styling & Publishing
1. Restaurant manager enters `/app/editor`.
2. Changes items, colors, or category ordering in the Visual Editor.
3. Changes update local state with undo/redo capability.
4. User clicks **Publish Menu**:
   - Client sends draft configuration to `POST /api/v1/restaurants/{id}/publish`.
   - Backend creates an atomic transaction:
     - Assembles the complete menu, category, item, variant, addon, theme, and layout graph.
     - Validates against Pydantic `PublishedMenuSnapshot` schema.
     - Computes SHA-256 hash.
     - Inserts a new row into `menu_versions`.
     - Updates `publications.active_version_id` atomically.
   - Cache invalidation signal dispatched.
   - Diner requests now receive the new version instantly.
