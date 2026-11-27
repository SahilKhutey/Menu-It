# FCD-09 §05 — File Validation & Security

## 1. Defensive Validation Chain

Menu-It validates files through a five-stage defensive pipeline before persisting bytes to disk:

1. **Filename Sanitization:** Path separators (`/`, `\`) and traversal tokens (`..`) are stripped. Filenames are capped at 180 characters.
2. **Size Bounds Verification:** Content size must satisfy $0 < \text{size} \le \text{FILE\_MAX\_UPLOAD\_BYTES}$ (default 10MB).
3. **Extension Whitelist:** Only approved extensions (`.jpg`, `.jpeg`, `.png`, `.webp`, `.pdf`) are processed.
4. **Magic-Byte Sniffing:** File headers are inspected for authentic byte signatures:
   - JPEG: `\xFF\xD8\xFF`
   - PNG: `\x89PNG\r\n\x1a\n`
   - WebP: `RIFF....WEBP`
   - PDF: `%PDF-`
   If the sniffed MIME type disagrees with the extension, the upload is rejected.
5. **Integrity Checksum:** The complete byte stream is hashed using SHA-256 for tamper detection and deduplication.

---

## 2. Path Traversal Defense in Local Storage

The `LocalFileStorage` adapter resolves absolute filesystem paths and enforces that the target is strictly contained within the storage root:
```python
target = (self.root / clean_key).resolve()
if not target.is_relative_to(self.root):
    raise ValueError(f"Storage key '{key}' escapes root storage directory.")
```
Any attempt to traverse directories (e.g. `../../etc/passwd`) raises a `ValueError` immediately.
