"""Currency value object and supported currency registry (FCD-06 §7.1, §22.2)."""

import re
from dataclasses import dataclass

from menu_it.domain.base.errors import ValidationDomainError

# Authoritative supported currency registry defining minor-unit precision and symbol
SUPPORTED_CURRENCIES: dict[str, dict[str, object]] = {
    "INR": {"name": "Indian Rupee", "minor_units": 2, "symbol": "₹"},
    "USD": {"name": "US Dollar", "minor_units": 2, "symbol": "$"},
    "EUR": {"name": "Euro", "minor_units": 2, "symbol": "€"},
    "GBP": {"name": "British Pound", "minor_units": 2, "symbol": "£"},
    "AED": {"name": "UAE Dirham", "minor_units": 2, "symbol": "د.إ"},
    "SAR": {"name": "Saudi Riyal", "minor_units": 2, "symbol": "﷼"},
    "SGD": {"name": "Singapore Dollar", "minor_units": 2, "symbol": "S$"},
    "AUD": {"name": "Australian Dollar", "minor_units": 2, "symbol": "A$"},
    "CAD": {"name": "Canadian Dollar", "minor_units": 2, "symbol": "C$"},
    "JPY": {"name": "Japanese Yen", "minor_units": 0, "symbol": "¥"},
    "KWD": {"name": "Kuwaiti Dinar", "minor_units": 3, "symbol": "د.ك"},
}


@dataclass(frozen=True, slots=True)
class Currency:
    """ISO 4217 three-letter currency code value object."""

    code: str

    def __post_init__(self) -> None:
        if not isinstance(self.code, str):
            raise ValidationDomainError("Currency code must be a string.")
        normalized = self.code.strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", normalized):
            raise ValidationDomainError("Currency must be a three-letter uppercase code.")
        object.__setattr__(self, "code", normalized)

    @property
    def is_supported(self) -> bool:
        """Check if currency is present in the platform's supported registry."""
        return self.code in SUPPORTED_CURRENCIES

    @property
    def minor_unit_precision(self) -> int:
        """Minor-unit decimal precision (e.g. 2 for INR/USD, 0 for JPY, 3 for KWD)."""
        info = SUPPORTED_CURRENCIES.get(self.code)
        if info:
            return int(info["minor_units"])
        return 2  # Default standard decimal precision for unrecognized valid ISO codes

    @property
    def symbol(self) -> str:
        """Display symbol for currency."""
        info = SUPPORTED_CURRENCIES.get(self.code)
        if info:
            return str(info["symbol"])
        return self.code
