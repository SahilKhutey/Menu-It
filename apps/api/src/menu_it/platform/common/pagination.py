"""Platform pagination models and offset calculation (FCD-09 WP-06)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PageRequest:
    """Validated pagination request parameters."""

    page: int = 1
    page_size: int = 20

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("Page must be at least 1.")
        if not 1 <= self.page_size <= 100:
            raise ValueError("Page size must be between 1 and 100.")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
