"""
Visual Menu Editor Domain Entities (ARC-04 §6.12, MOD-12).
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class EditorDraft:
    draft_id: UUID
    restaurant_id: UUID
    configuration: dict[str, Any] = field(default_factory=dict)
    revision: int = 1
    history: list[dict[str, Any]] = field(default_factory=list)
    redo_stack: list[dict[str, Any]] = field(default_factory=list)

    def update_configuration(self, new_config: dict[str, Any]) -> None:
        # Save previous state to history
        self.history.append(dict(self.configuration))
        self.redo_stack.clear()
        self.configuration = new_config
        self.revision += 1

    def undo(self) -> None:
        if not self.history:
            return
        previous_state = self.history.pop()
        self.redo_stack.append(dict(self.configuration))
        self.configuration = previous_state
        self.revision += 1

    def redo(self) -> None:
        if not self.redo_stack:
            return
        next_state = self.redo_stack.pop()
        self.history.append(dict(self.configuration))
        self.configuration = next_state
        self.revision += 1


@dataclass
class EditorSession:
    session_id: UUID
    user_id: UUID
    draft_id: UUID
    is_active: bool = True

    def close(self) -> None:
        self.is_active = False
