"""Authentication package initialization (FCD-05 §7, §8)."""

from menu_it.authentication.exceptions import (
    AccountLockedError,
    AccountNotActiveError,
    AccountNotVerifiedError,
    AccountSuspendedError,
    AuthenticationError,
    InvalidCredentialsError,
)
from menu_it.authentication.schemas import (
    AuthenticationResponse,
    EmailVerificationRequest,
    LoginRequest,
    PasswordChangeRequest,
    PasswordForgotRequest,
    PasswordResetRequest,
    RegisterRequest,
    ResendVerificationRequest,
    SessionResponse,
    TokenRefreshRequest,
    TokenResponse,
)
from menu_it.authentication.service import AuthenticationService
from menu_it.authentication.tokens import (
    create_access_token,
    decode_access_token,
    generate_opaque_token,
    generate_refresh_token,
    hash_opaque_token,
    hash_refresh_token,
)

__all__ = [
    "AccountLockedError",
    "AccountNotActiveError",
    "AccountNotVerifiedError",
    "AccountSuspendedError",
    "AuthenticationError",
    "AuthenticationResponse",
    "AuthenticationService",
    "EmailVerificationRequest",
    "InvalidCredentialsError",
    "LoginRequest",
    "PasswordChangeRequest",
    "PasswordForgotRequest",
    "PasswordResetRequest",
    "RegisterRequest",
    "ResendVerificationRequest",
    "SessionResponse",
    "TokenRefreshRequest",
    "TokenResponse",
    "create_access_token",
    "decode_access_token",
    "generate_opaque_token",
    "generate_refresh_token",
    "hash_opaque_token",
    "hash_refresh_token",
]
