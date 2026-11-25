"""Storage port interface and value objects (FCD-09 WP-02)."""

from dataclasses import dataclass
from typing import BinaryIO, Protocol, runtime_checkable


@dataclass(frozen=True)
class StoredObject:
    """Value object returned after successfully persisting content in storage."""

    storage_key: str
    size_bytes: int
    checksum_sha256: str


@runtime_checkable
class FileStorage(Protocol):
    """Provider-independent storage contract."""

    async def put(
        self,
        *,
        key: str,
        content: BinaryIO,
        content_type: str,
    ) -> StoredObject:
        """Persist a binary stream under the specified storage key."""
        ...

    async def open(self, *, key: str) -> BinaryIO:
        """Open and return a readable binary stream for the given storage key."""
        ...

    async def delete(self, *, key: str) -> None:
        """Delete the object associated with the storage key."""
        ...

    async def exists(self, *, key: str) -> bool:
        """Check whether an object exists at the given storage key."""
        ...
