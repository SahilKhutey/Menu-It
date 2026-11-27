"""Argon2id password hashing and verification (FCD-05 §6.2)."""

import contextlib

from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

# Argon2id password hasher configured per FCD-05 §6.2 specification
password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)

# Precomputed dummy hash for constant-time comparison when email is not found
_DUMMY_HASH = password_hasher.hash("dummy-nonexistent-user-timing-mitigation-password")


def hash_password(password: str) -> str:
    """Hash plaintext password with Argon2id and unique cryptographic salt."""
    return password_hasher.hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
    """Verify plaintext password against stored Argon2id hash."""
    try:
        return password_hasher.verify(stored_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(stored_hash: str) -> bool:
    """Check if hash parameters are outdated and require upgrading."""
    try:
        return password_hasher.check_needs_rehash(stored_hash)
    except Exception:
        return False


def perform_dummy_verification(password: str) -> None:
    """Perform dummy hash verification work to mitigate timing-based account enumeration."""
    with contextlib.suppress(Exception):
        password_hasher.verify(_DUMMY_HASH, password)
