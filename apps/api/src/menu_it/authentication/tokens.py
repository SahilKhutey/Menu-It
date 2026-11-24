"""Cryptographic token issuance and verification (FCD-05 §8)."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    ImmatureSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    PyJWTError,
)


class TokenError(Exception):
    """Base exception for JWT processing errors."""


class TokenExpiredError(TokenError):
    """Raised when access token has expired."""


class InvalidTokenSignatureError(TokenError):
    """Raised when token signature is invalid or tampered with."""


class InvalidTokenClaimsError(TokenError):
    """Raised when token claims (iss, aud, token_use, nbf) are invalid."""


def create_access_token(
    *,
    user_id: UUID,
    session_id: UUID,
    signing_key: str,
    algorithm: str = "HS256",
    key_id: str = "menu-it-k1",
    issuer: str = "menu-it",
    audience: str = "menu-it-api",
    ttl_seconds: int = 600,
) -> str:
    """Issue a signed JWT access token with standardized claims."""
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "sid": str(session_id),
        "iss": issuer,
        "aud": audience,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
        "jti": str(uuid4()),
        "token_use": "access",
    }
    headers = {"kid": key_id}
    return jwt.encode(
        payload,
        signing_key,
        algorithm=algorithm,
        headers=headers,
    )


def decode_access_token(
    *,
    token: str,
    verification_key: str,
    allowed_algorithms: list[str] | None = None,
    issuer: str = "menu-it",
    audience: str = "menu-it-api",
) -> dict[str, object]:
    """Decode and cryptographically verify an access token."""
    if allowed_algorithms is None:
        allowed_algorithms = ["HS256", "RS256", "EdDSA"]

    try:
        payload = jwt.decode(
            token,
            verification_key,
            algorithms=allowed_algorithms,
            issuer=issuer,
            audience=audience,
            options={
                "require": [
                    "sub",
                    "sid",
                    "iss",
                    "aud",
                    "iat",
                    "nbf",
                    "exp",
                    "jti",
                ],
            },
        )
    except ExpiredSignatureError as exc:
        raise TokenExpiredError("Access token has expired.") from exc
    except InvalidSignatureError as exc:
        raise InvalidTokenSignatureError("Token signature validation failed.") from exc
    except (InvalidIssuerError, InvalidAudienceError, ImmatureSignatureError) as exc:
        raise InvalidTokenClaimsError(f"Token claim validation failed: {exc}") from exc
    except PyJWTError as exc:
        raise TokenError(f"Malformed or invalid token: {exc}") from exc

    if payload.get("token_use") != "access":
        raise InvalidTokenClaimsError("Invalid token use; expected 'access'.")

    return payload


def generate_refresh_token() -> str:
    """Generate high-entropy cryptographically secure opaque refresh token."""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """Hash raw refresh token with SHA-256 for secure database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_opaque_token() -> str:
    """Generate secure opaque token for email verification or password reset."""
    return secrets.token_urlsafe(48)


def hash_opaque_token(token: str) -> str:
    """Hash opaque token with SHA-256 for secure database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
