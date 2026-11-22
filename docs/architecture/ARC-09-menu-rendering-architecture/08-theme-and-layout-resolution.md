# ARC-09 §08 — Theme & Layout Resolution

## 1. Theme Token Hierarchy
Themes are resolved hierarchically:
1. **Base Preset Tokens**: Standard tokens defined in `THEME_PRESETS` (e.g. Classic Slate, Warm Bistro).
2. **Restaurant Custom Tokens**: Overrides chosen by the operator via the settings or visual editor.
3. **CSS Variable Mapping**: Tokens are converted into scoped CSS variables:
   ```css
   --menu-color-primary: #475569;
   --menu-color-background: #F8FAFC;
   --menu-color-surface: #FFFFFF;
   --menu-font-family-heading: "Playfair Display", serif;
   --menu-font-family-body: "Inter", sans-serif;
   ```

## 2. Layout Rules
Supported layout paradigms:
- `category_first`: Vertical scrolling with sticky horizontal category pills.
- `item_first`: Curated highlights followed by categorized courses.
- `tabbed`: Full tabbed view switching categories with zero scroll jumping.
- `grid`: 2 or 3 column presentation optimized for larger tablet/desktop displays.
