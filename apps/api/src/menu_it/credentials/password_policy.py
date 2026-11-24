"""Password complexity and policy validation (FCD-05 §6.4)."""

import re

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128


def validate_password(password: str) -> None:
    """Validate password against security policy requirements.

    Requirements:
    - At least 12 characters
    - At most 128 characters
    - No leading or trailing whitespace
    - No unsupported ASCII control characters
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must contain at least {MIN_PASSWORD_LENGTH} characters.")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password must not exceed {MAX_PASSWORD_LENGTH} characters.")
    if password.strip() != password:
        raise ValueError("Password must not contain surrounding whitespace.")
    if re.search(r"[\x00-\x1f\x7f]", password):
        raise ValueError("Password contains unsupported control characters.")
