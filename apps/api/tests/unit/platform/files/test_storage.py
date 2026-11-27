"""Unit tests for local file storage adapter (FCD-09 WP-02)."""

import io
from pathlib import Path

import pytest

from menu_it.platform.files.infrastructure.local_storage import LocalFileStorage


@pytest.mark.asyncio
async def test_local_storage_lifecycle(tmp_path: Path):
    """Storage adapter successfully puts, opens, checks existence, and deletes objects."""
    storage = LocalFileStorage(root=tmp_path)
    key = "organizations/org-1/files/file-1/abc.png"
    content = b"fake-png-binary-stream-12345"

    # Put
    stream = io.BytesIO(content)
    stored = await storage.put(key=key, content=stream, content_type="image/png")
    assert stored.storage_key == key
    assert stored.size_bytes == len(content)

    # Exists
    assert await storage.exists(key=key) is True

    # Open
    read_stream = await storage.open(key=key)
    read_bytes = read_stream.read()
    assert read_bytes == content

    # Delete
    await storage.delete(key=key)
    assert await storage.exists(key=key) is False

    with pytest.raises(FileNotFoundError):
        await storage.open(key=key)


@pytest.mark.asyncio
async def test_local_storage_prevents_path_traversal(tmp_path: Path):
    """Keys attempting directory traversal outside root raise ValueError."""
    storage = LocalFileStorage(root=tmp_path)
    with pytest.raises(ValueError, match="escapes root storage directory"):
        await storage.exists(key="../../etc/shadow")
