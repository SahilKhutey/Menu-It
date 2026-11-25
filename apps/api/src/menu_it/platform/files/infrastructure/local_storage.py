"""Local filesystem storage adapter (FCD-09 WP-02)."""

import hashlib
import io
from pathlib import Path
from typing import BinaryIO

from menu_it.platform.files.domain.storage import StoredObject


class LocalFileStorage:
    """Stores files on the local filesystem within a designated root directory."""

    def __init__(self, root: str | Path = "./storage") -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        """Resolve storage key to absolute path and verify it stays inside root."""
        clean_key = key.lstrip("/").lstrip("\\")
        target = (self.root / clean_key).resolve()
        if not target.is_relative_to(self.root):
            raise ValueError(f"Storage key '{key}' escapes root storage directory.")
        return target

    async def put(
        self,
        *,
        key: str,
        content: BinaryIO,
        content_type: str,
    ) -> StoredObject:
        """Persist a binary stream to local disk."""
        target = self._resolve(key)
        target.parent.mkdir(parents=True, exist_ok=True)

        digest = hashlib.sha256()
        total_bytes = 0

        # Read content from stream and write to file
        with target.open("wb") as dest:
            while chunk := content.read(64 * 1024):
                dest.write(chunk)
                digest.update(chunk)
                total_bytes += len(chunk)

        return StoredObject(
            storage_key=key,
            size_bytes=total_bytes,
            checksum_sha256=digest.hexdigest(),
        )

    async def open(self, *, key: str) -> BinaryIO:
        """Open an existing file for reading."""
        target = self._resolve(key)
        if not target.is_file():
            raise FileNotFoundError(f"Object with key '{key}' does not exist.")
        # Return in-memory buffer or open file handle
        with target.open("rb") as f:
            return io.BytesIO(f.read())

    async def delete(self, *, key: str) -> None:
        """Delete an object from local storage if present."""
        target = self._resolve(key)
        if target.is_file():
            target.unlink()

    async def exists(self, *, key: str) -> bool:
        """Check if an object exists on disk."""
        target = self._resolve(key)
        return target.is_file()
