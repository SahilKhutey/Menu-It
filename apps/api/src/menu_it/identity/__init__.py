"""Identity package initialization (FCD-05 §4.2)."""

from menu_it.database.models.user import User, UserStatus, normalize_email
from menu_it.identity.exceptions import (
    IdentityError,
    InvalidAccountStatusError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from menu_it.identity.repository import UserRepository
from menu_it.identity.schemas import UserProfileUpdateRequest, UserResponse

__all__ = [
    "IdentityError",
    "InvalidAccountStatusError",
    "User",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "UserProfileUpdateRequest",
    "UserRepository",
    "UserResponse",
    "UserStatus",
    "normalize_email",
]
