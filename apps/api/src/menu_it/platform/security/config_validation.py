"""Production configuration security validation (FCD-11 WP-01 / WP-02)."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from menu_it.core.config import Settings


class SecurityConfigurationError(Exception):
    """Raised when application configuration violates production security standards."""

    def __init__(self, violations: list[str]) -> None:
        self.violations = violations
        msg = (
            f"Production security configuration validation failed with {len(violations)} "
            f"violations: {'; '.join(violations)}"
        )
        super().__init__(msg)


class SecurityConfigValidator:
    """Validator that audits runtime settings against security baselines."""

    INSECURE_SECRET_SUBSTRINGS: tuple[str, ...] = (
        "dev-insecure",
        "insecure",
        "changeme",
        "change_me",
        "replace_me",
        "placeholder",
        "default_secret",
        "test_secret",
    )

    @classmethod
    def validate(cls, settings: "Settings") -> list[str]:
        """Validate settings and return a list of security violations."""
        violations: list[str] = []

        # 1. Debug mode in production
        if settings.app_debug:
            violations.append(
                "DEBUG mode must be disabled in production environment (app_debug=False)."
            )

        # 2. Secret Key strength
        secret = settings.auth_secret_key or ""
        if len(secret) < 32:
            violations.append(
                f"AUTH_SECRET_KEY too short ({len(secret)} chars); minimum required is 32 bytes."
            )
        secret_lower = secret.lower()
        if any(substr in secret_lower for substr in cls.INSECURE_SECRET_SUBSTRINGS):
            violations.append(
                "AUTH_SECRET_KEY contains known insecure development placeholder strings."
            )

        # 3. Cookie security in production
        if not settings.auth_cookie_secure:
            violations.append(
                "AUTH_COOKIE_SECURE must be True in production for HTTPS-only cookie transmission."
            )
        if settings.auth_cookie_samesite.lower() not in ("lax", "strict"):
            violations.append(
                f"AUTH_COOKIE_SAMESITE='{settings.auth_cookie_samesite}' is insecure; "
                "must be 'lax' or 'strict'."
            )

        # 4. CORS wildcards
        cors_origins = [o.strip() for o in settings.cors_origins_raw.split(",") if o.strip()]
        if "*" in cors_origins:
            violations.append(
                "CORS_ORIGINS contains wildcard '*' which is forbidden in production."
            )

        # 5. Database credentials
        db_url_lower = settings.database_url.lower()
        if "change_this_local_password" in db_url_lower:
            violations.append(
                "DATABASE_URL uses the default development password 'change_this_local_password'."
            )

        # 6. JWT Algorithm integrity
        if settings.auth_jwt_algorithm.lower() == "none":
            violations.append("AUTH_JWT_ALGORITHM cannot be 'none'.")

        return violations


def validate_production_config(settings: "Settings") -> list[str]:
    """Audit settings and return any production security violations."""
    return SecurityConfigValidator.validate(settings)


def ensure_production_config(settings: "Settings") -> None:
    """Enforce production security configuration; raises SecurityConfigurationError if invalid."""
    if settings.app_env == "production":
        violations = validate_production_config(settings)
        if violations:
            raise SecurityConfigurationError(violations)
