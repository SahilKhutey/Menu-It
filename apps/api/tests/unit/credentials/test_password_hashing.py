"""Unit tests for Argon2id password hashing and verification (FCD-05 §21.2)."""

from menu_it.credentials.hashing import (
    hash_password,
    needs_rehash,
    perform_dummy_verification,
    verify_password,
)


def test_password_hash_is_not_plaintext():
    """Verify password hash does not expose raw plaintext."""
    password = "A-long-and-unique-password-2026"
    hashed = hash_password(password)
    assert hashed != password
    assert password not in hashed
    assert hashed.startswith("$argon2id$")


def test_correct_password_verifies():
    """Verify correct password matches Argon2id hash."""
    password = "A-long-and-unique-password-2026"
    hashed = hash_password(password)
    assert verify_password(hashed, password) is True


def test_incorrect_password_fails():
    """Verify incorrect password fails verification cleanly without raising exceptions."""
    password = "A-long-and-unique-password-2026"
    hashed = hash_password(password)
    assert verify_password(hashed, "Incorrect-password-1234") is False
    assert verify_password(hashed, "") is False


def test_unique_salts_create_different_hashes():
    """Verify identical passwords generate unique hashes due to cryptographic salting."""
    password = "A-long-and-unique-password-2026"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2
    assert verify_password(hash1, password) is True
    assert verify_password(hash2, password) is True


def test_needs_rehash_returns_false_for_current_parameters():
    """Verify newly generated hashes match current algorithm parameters."""
    password = "A-long-and-unique-password-2026"
    hashed = hash_password(password)
    assert needs_rehash(hashed) is False


def test_dummy_verification_executes_safely():
    """Verify dummy verification work completes safely for timing attack mitigation."""
    perform_dummy_verification("any-arbitrary-password")
