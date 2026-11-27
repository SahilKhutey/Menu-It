"""Application service result container (FCD-07 WP-12)."""

from typing import Generic, TypeVar

T = TypeVar("T")


class ApplicationResult(Generic[T]):
    """Standardized result wrapper for internal application services."""

    def __init__(
        self,
        value: T | None = None,
        error: str | None = None,
        error_code: str | None = None,
        is_success: bool = True,
    ) -> None:
        self._value = value
        self._error = error
        self._error_code = error_code
        self._is_success = is_success

    @classmethod
    def ok(cls, value: T) -> "ApplicationResult[T]":
        """Factory for successful result."""
        return cls(value=value, is_success=True)

    @classmethod
    def fail(cls, error: str, error_code: str | None = None) -> "ApplicationResult[T]":
        """Factory for failed result."""
        return cls(value=None, error=error, error_code=error_code, is_success=False)

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    @property
    def value(self) -> T:
        if not self._is_success:
            raise ValueError(f"Cannot get value of failed ApplicationResult: {self._error}")
        return self._value  # type: ignore

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def error_code(self) -> str | None:
        return self._error_code

    def unwrap(self) -> T:
        """Unwrap value or raise ValueError."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Unwrap value or return default."""
        return self._value if self._is_success else default
