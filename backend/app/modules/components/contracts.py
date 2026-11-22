"""
Public Contracts for Component Registry Module (ARC-04 §8, MOD-10).
"""

from typing import Protocol

from app.modules.components.domain.entities import ComponentDefinition


class ComponentRegistryReader(Protocol):
    def get_component(self, component_id: str, version: int = 1) -> ComponentDefinition | None: ...
