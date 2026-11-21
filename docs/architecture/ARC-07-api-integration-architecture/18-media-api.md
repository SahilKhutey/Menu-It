# 18. Media API Architecture

## 1. Media Upload Pipeline
1. Client requests upload URL via `POST /api/v1/media/upload-url` with file metadata.
2. Server validates MIME type (`image/jpeg`, `image/png`, `image/webp`) and size limits (< 10 MB).
3. Server returns pre-signed URL.
4. Client uploads directly to object storage.
