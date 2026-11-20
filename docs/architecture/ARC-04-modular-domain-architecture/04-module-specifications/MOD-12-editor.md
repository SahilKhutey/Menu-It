# MOD-12 — Visual Menu Editor Module Specification

**Module ID:** MOD-12  
**Tier:** Experience Configuration (P0)  
**Package:** `app.modules.editor`  

---

## 1. Ownership & Boundaries
- **Owns:** Editing sessions, draft revisions, undo/redo stacks, canvas coordination.
- **Does Not Own:** Direct mutation of published snapshots, public menu routing.

## 2. Domain Model & Invariants
- **EditorDraft Entity:** `EditorDraft(draft_id, restaurant_id, configuration, revision, history, redo_stack)`
  - Reversible revisions with `undo()` and `redo()`.
- **EditorSession Entity:** `EditorSession(session_id, user_id, draft_id, is_active)`

## 3. Public Contracts & Events
- **Provides:** `EditorDraftManager` Protocol (`get_draft_configuration`).
- **Consumes:** `ThemeResolver`, `LayoutResolver`, `ComponentRegistryReader`, `MenuReader`.
- **Emits:** `DraftSaved` (EVT-013).
