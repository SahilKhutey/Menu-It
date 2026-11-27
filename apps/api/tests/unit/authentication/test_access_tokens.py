"""Unit tests for JWT access token issuance, claims, and verification (FCD-05 §21.3)."""

from uuid import uuid4

import pytest

from menu_it.authentication.tokens import (
    InvalidTokenClaimsError,
    InvalidTokenSignatureError,
    TokenExpiredError,
    create_access_token,
    decode_access_token,
    generate_opaque_token,
    generate_refresh_token,
    hash_opaque_token,
    hash_refresh_token,
)

TEST_SECRET = "test-secret-key-for-jwt-signing-minimum-32-bytes"
ALT_SECRET = "alternative-secret-key-that-does-not-match-signature"


def test_create_and_decode_access_token():
    """Verify standard access token round-trip issuance and decode."""
    user_id = uuid4()
    session_id = uuid4()

    token = create_access_token(
        user_id=user_id,
        session_id=session_id,
        signing_key=TEST_SECRET,
        issuer="menu-it-test",
        audience="menu-it-api-test",
        ttl_seconds=300,
    )

    payload = decode_access_token(
        token=token,
        verification_key=TEST_SECRET,
        issuer="menu-it-test",
        audience="menu-it-api-test",
    )

    assert payload["sub"] == str(user_id)
    assert payload["sid"] == str(session_id)
    assert payload["iss"] == "menu-it-test"
    assert payload["aud"] == "menu-it-api-test"
    assert payload["token_use"] == "access"
    assert "jti" in payload
    assert "exp" in payload
    assert "iat" in payload


def test_invalid_signature_rejected():
    """Verify token signed with different key raises InvalidTokenSignatureError."""
    user_id = uuid4()
    session_id = uuid4()

    token = create_access_token(
        user_id=user_id,
        session_id=session_id,
        signing_key=TEST_SECRET,
    )

    with pytest.raises(InvalidTokenSignatureError):
        decode_access_token(
            token=token,
            verification_key=ALT_SECRET,
        )


def test_expired_token_rejected():
    """Verify expired token raises TokenExpiredError."""
    user_id = uuid4()
    session_id = uuid4()

    token = create_access_token(
        user_id=user_id,
        session_id=session_id,
        signing_key=TEST_SECRET,
        ttl_seconds=-10,  # Negative TTL simulates past expiry
    )

    with pytest.raises(TokenExpiredError):
        decode_access_token(
            token=token,
            verification_key=TEST_SECRET,
        )


def test_invalid_issuer_rejected():
    """Verify mismatched token issuer raises InvalidTokenClaimsError."""
    token = create_access_token(
        user_id=uuid4(),
        session_id=uuid4(),
        signing_key=TEST_SECRET,
        issuer="wrong-issuer",
    )

    with pytest.raises(InvalidTokenClaimsError, match="claim validation failed"):
        decode_access_token(
            token=token,
            verification_key=TEST_SECRET,
            issuer="expected-issuer",
        )


def test_invalid_audience_rejected():
    """Verify mismatched token audience raises InvalidTokenClaimsError."""
    token = create_access_token(
        user_id=uuid4(),
        session_id=uuid4(),
        signing_key=TEST_SECRET,
        audience="wrong-audience",
    )

    with pytest.raises(InvalidTokenClaimsError, match="claim validation failed"):
        decode_access_token(
            token=token,
            verification_key=TEST_SECRET,
            audience="expected-audience",
        )


def test_refresh_token_and_opaque_helpers():
    """Verify opaque token and refresh token generation and cryptographic hashing."""
    raw_refresh = generate_refresh_token()
    raw_opaque = generate_opaque_token()

    assert len(raw_refresh) >= 64
    assert len(raw_opaque) >= 48

    hash_ref1 = hash_refresh_token(raw_refresh)
    hash_ref2 = hash_refresh_token(raw_refresh)
    assert hash_ref1 == hash_ref2
    assert len(hash_ref1) == 64  # SHA-256 hex string

    hash_op = hash_opaque_token(raw_opaque)
    assert len(hash_op) == 64
