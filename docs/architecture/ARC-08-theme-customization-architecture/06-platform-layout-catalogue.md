# ARC-08 §6 — Platform Layout Catalogue

ModularMenu provides 4 platform-approved responsive layouts in `packages/contracts/manifests/layout-catalogue.json`:

| Layout ID | Name | Description | Default Mobile Cols | Default Tablet Cols | Default Desktop Cols |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `layout-list` | Classic List | Compact linear presentation for high-density menus | 1 | 1 | 2 |
| `layout-grid` | Card Grid | Visual card grid optimal for modern casual dining | 1 | 2 | 3 |
| `layout-image-cards` | Image Cards | Media-forward design highlighting high-res photography | 1 | 2 | 3 |
| `layout-editorial` | Editorial Story | Asymmetric storytelling layout for tasting menus | 1 | 1 | 2 |

### Responsive Breakpoints
- `mobile`: `< 640px` (Enforces 1 column layout, horizontal scrolling categories)
- `tablet`: `640px - 1023px` (1-2 columns)
- `desktop`: `>= 1024px` (2-4 columns)
