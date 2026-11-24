"""Repositories package exports (FCD-04 §11)."""

from menu_it.repositories.base import BaseRepository
from menu_it.repositories.restaurants import RestaurantRepository
from menu_it.repositories.tenant_base import TenantScopedRepository
from menu_it.repositories.tenant_restaurants import TenantRestaurantRepository
from menu_it.repositories.tenants import TenantRepository

__all__ = [
    "BaseRepository",
    "RestaurantRepository",
    "TenantRepository",
    "TenantRestaurantRepository",
    "TenantScopedRepository",
]
