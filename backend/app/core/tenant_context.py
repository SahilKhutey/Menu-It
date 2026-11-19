import uuid
from contextvars import ContextVar
from typing import Optional

# Request-scoped tenant context variable
_current_restaurant_id: ContextVar[Optional[uuid.UUID]] = ContextVar("current_restaurant_id", default=None)
_current_user_id: ContextVar[Optional[uuid.UUID]] = ContextVar("current_user_id", default=None)


def set_current_restaurant_id(restaurant_id: Optional[uuid.UUID]) -> None:
    _current_restaurant_id.set(restaurant_id)


def get_current_restaurant_id() -> Optional[uuid.UUID]:
    return _current_restaurant_id.get()


def set_current_user_id(user_id: Optional[uuid.UUID]) -> None:
    _current_user_id.set(user_id)


def get_current_user_id() -> Optional[uuid.UUID]:
    return _current_user_id.get()
