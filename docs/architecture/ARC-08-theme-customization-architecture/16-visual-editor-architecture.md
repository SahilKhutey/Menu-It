# ARC-08 §16 — Visual Editor Architecture

The Visual Editor (`frontend/src/features/customization/VisualEditor.tsx`) provides a WYSIWYG editing canvas:
- **Component Tree:** Hierarchical slot representation (`header`, `navigation`, `category.header`, `category.items`, `footer`).
- **Interactive Canvas:** Live rendering inside a simulated mobile (375px), tablet (768px), or desktop (1280px) viewport.
- **Property Inspector:** Contextual sidebar exposing schema-validated props for the selected component instance.
- **Slot Boundaries:** Enforces slot compatibility during component moves and prevents illegal drops.
