# MOD-14 — Media Management Module Specification

**Module ID:** MOD-14  
**Tier:** Supporting Domains (P1)  
**Package:** `app.modules.media`  

---

## 1. Ownership & Boundaries
- **Owns:** Media assets, MIME validation, storage paths, reference tracking.
- **Does Not Own:** Menu item status, publishing decisions.

## 2. Domain Model & Invariants
- **MediaAsset Entity:** `MediaAsset(asset_id, restaurant_id, filename, content_type, size_bytes, storage_path, reference_count)`
  - MIME type allowlist (`image/webp`, `image/png`, `image/jpeg`).
  - Size budget limit: 5 MB (`MAX_MEDIA_SIZE_BYTES`).
  - Actively referenced media cannot be deleted (`assert_can_delete()`).

## 3. Public Contracts & Events
- **Provides:** `MediaStorage` Protocol (`resolve_media_url`).
- **Consumes:** None.
- **Emits:** `MediaUploaded` (EVT-016).
