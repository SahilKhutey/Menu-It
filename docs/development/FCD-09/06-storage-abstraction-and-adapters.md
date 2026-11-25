# FCD-09 §06 — Storage Abstraction & Adapters

## 1. Storage Interface Protocol

Menu-It defines a provider-independent storage protocol in `menu_it.platform.files.domain.storage.FileStorage`:

```python
class FileStorage(Protocol):
    async def put(self, *, key: str, content: BinaryIO, content_type: str) -> StoredObject: ...
    async def open(self, *, key: str) -> BinaryIO: ...
    async def delete(self, *, key: str) -> None: ...
    async def exists(self, *, key: str) -> bool: ...
```

---

## 2. Local Filesystem Adapter

`LocalFileStorage` implements `FileStorage` for local development, test automation, and appliance deployments:
- **Root Directory:** Configured via `FILE_STORAGE_ROOT` (`./storage`).
- **Directory Hierarchy:** Directories (`organizations/...`, `platform/...`) are created on demand.
- **Atomic Read Streams:** `open()` returns an in-memory `io.BytesIO` buffer, ensuring non-blocking async execution.
- **Fail-Safe Cleanup:** When a file is deleted, `unlink()` removes the file without throwing if already absent.

---

## 3. Future S3-Compatible Object Storage Adapter

The `FileStorage` protocol enables seamless swapping to AWS S3, Cloudflare R2, MinIO, or Google Cloud Storage in production without modifying business services or repository code.
