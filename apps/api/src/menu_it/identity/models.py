"""Identity models interface (FCD-05 §5.1)."""

from menu_it.database.models.user import User, UserStatus, normalize_email

__all__ = ["User", "UserStatus", "normalize_email"]
