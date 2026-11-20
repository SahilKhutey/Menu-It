"""
Theme Domain Entities (ARC-04 §6.8, MOD-08).
"""
from dataclasses import dataclass, field
import re
from typing import Any


@dataclass
class ThemeDefinition:
    theme_id: str
    name: str
    tokens: dict[str, Any] = field(default_factory=dict)
    schema_version: int = 1

    def __post_init__(self) -> None:
        if not self.theme_id or not self.theme_id.strip():
            raise ValueError("Theme ID is required")
        self.validate_tokens()

    def validate_tokens(self) -> None:
        colors = self.tokens.get("colors", {})
        hex_regex = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
        for key, color in colors.items():
            if isinstance(color, str) and not hex_regex.match(color):
                raise ValueError(f"Invalid hex color '{color}' for token '{key}'")

    def resolve_tokens(self) -> dict[str, Any]:
        """Returns normalized, resolved token dictionary."""
        return {
            "schema_version": self.schema_version,
            "theme_id": self.theme_id,
            "tokens": self.tokens,
        }
