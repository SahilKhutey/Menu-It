"""
ModularMenu — Password Hashing Architecture (ARC-12 §4.2, ADR-0225).
Standardizes on Argon2id for secure password hashing with unique salts.
"""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

# Production-calibrated Argon2id hasher
_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
)


def hash_password(password: str) -> str:
    """Hash plaintext password using Argon2id with unique salt."""
    if not password:
        raise ValueError("Password cannot be empty")
    return _hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against Argon2id hash with timing attack resistance."""
    if not password or not stored_hash:
        return False
    try:
        return _hasher.verify(stored_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(stored_hash: str) -> bool:
    """Determine if password hash needs migration to updated parameters."""
    try:
        return _hasher.check_needs_rehash(stored_hash)
    except Exception:
        return True
