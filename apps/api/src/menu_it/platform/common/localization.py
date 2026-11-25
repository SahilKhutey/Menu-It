"""Language and locale resolution with fallback handling (FCD-09 WP-06)."""

SUPPORTED_LOCALES: frozenset[str] = frozenset({"en", "hi"})
DEFAULT_LOCALE: str = "en"


def resolve_locale(requested: str | None, *, default: str = DEFAULT_LOCALE) -> str:
    """Resolve an incoming language or locale string against supported system locales."""
    if not requested or not isinstance(requested, str):
        return default
    normalized = requested.replace("_", "-").strip().lower()
    # Check primary language subtag (e.g., 'en-US' -> 'en', 'hi-IN' -> 'hi')
    lang = normalized.split("-", maxsplit=1)[0]
    if lang in SUPPORTED_LOCALES:
        return lang
    return default
