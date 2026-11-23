# 10 — Storage Architecture & Media Adapters
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Unified Object Storage Abstraction
ModularMenu defines a protocol-based storage abstraction (`backend/app/integrations/storage/service.py`):
```python
class ObjectStorage(Protocol):
    def put_object(self, key: str, data: BinaryIO, mime_type: str) -> str: ...
    def get_object(self, key: str) -> BinaryIO: ...
    def delete_object(self, key: str) -> None: ...
    def create_signed_url(self, key: str, expires_in_seconds: int = 900) -> str: ...
```

## 2. Storage Adapters
- **S3StorageAdapter:** High-throughput cloud storage supporting AWS S3, Cloudflare R2, and MinIO with pre-signed upload/download URLs.
- **LocalStorageAdapter:** Zero-dependency filesystem adapter for Customer-Hosted deployments:
  - Path traversal hardening: Prevents `../` directory escapes.
  - HMAC SHA-256 URL signing: Generates secure, expiring URLs verified via message authentication codes.\n