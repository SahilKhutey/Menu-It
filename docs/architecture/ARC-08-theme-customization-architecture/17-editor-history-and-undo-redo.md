# ARC-08 §17 — Editor History & Undo/Redo

Implemented via the Command Pattern in `packages/editor-engine/src/history.ts`:
- Bounded history stack (maximum 50 entries to conserve memory).
- `pushState(document)`: Pushes new immutable state, clearing any redo forward branch.
- `undo()`: Pops current state and restores previous document.
- `redo()`: Advances forward along previously undone actions.
- `isDirty()`: Compares current state against last persisted revision baseline.
- `canUndo` / `canRedo` boolean flags drive keyboard shortcut enablement (`Ctrl+Z`, `Ctrl+Y`, `Ctrl+Shift+Z`).
