"""Domain and database persistence exceptions (FCD-03 §14.3)."""


class DatabaseUnavailableError(Exception):
    """Raised when the database service is unreachable or connection pool is exhausted."""

    pass


class ResourceConflictError(Exception):
    """Raised when an operation violates a unique constraint or logical domain rule."""

    pass


class PersistenceError(Exception):
    """Raised when an unexpected lower-level database or ORM persistence failure occurs."""

    pass
