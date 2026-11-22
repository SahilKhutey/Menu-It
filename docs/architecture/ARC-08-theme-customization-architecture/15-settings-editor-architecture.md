# ARC-08 §15 — Settings Editor Architecture

The Settings Editor (`frontend/src/features/customization/SettingsEditor.tsx`) provides a guided form interface for rapid branding:
- **Theme Selector:** Cards displaying theme name, description, and thumbnail previews.
- **Layout Selector:** Radio pills for switching between List, Grid, Image Cards, and Editorial layouts.
- **Color Accent Picker:** Color swatch inputs restricting inputs to valid hexadecimal colors (`^#([A-Fa-f0-9]{6})$`).
- **Component Visibility Toggles:** Clean switches enabling or disabling platform components without altering slot structures.
- **Real-Time Synchronous Validation:** Disables save button if any property violates contract rules.
