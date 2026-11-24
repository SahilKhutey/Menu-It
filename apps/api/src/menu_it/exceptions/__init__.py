"""Exceptions package exports (FCD-03 §14)."""

from menu_it.exceptions.domain import (
    DatabaseUnavailableError,
    PersistenceError,
    ResourceConflictError,
)
from menu_it.exceptions.handlers import register_exception_handlers

__all__ = [
    "DatabaseUnavailableError",
    "PersistenceError",
    "ResourceConflictError",
    "register_exception_handlers",
]
