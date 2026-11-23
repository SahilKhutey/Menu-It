# FCD-02 — Mobile-Ready Application Foundation

## 1. Scope
FCD-02 provides responsive web foundations and PWA installability preparation, intentionally distinguishing responsive web experiences from native mobile applications (Android/iOS).

## 2. Responsive Breakpoint Taxonomy
CSS design tokens defined in `globals.css`:
```css
:root {
  --breakpoint-mobile: 640px;
  --breakpoint-tablet: 768px;
  --breakpoint-desktop: 1024px;
  --breakpoint-wide: 1440px;
}
```

## 3. Viewport Profiles Validated
| Device Profile | Width x Height | Layout Behavior |
| :--- | :--- | :--- |
| **Small Mobile** | 320 x 640 | Single-column, stacked hero actions, 44px min touch target |
| **Standard Mobile** | 375 x 812 | Fluid typography clamp, compact header |
| **Large Mobile** | 430 x 932 | High-density fluid scaling |
| **Tablet Portrait** | 768 x 1024 | Expanded padding, inline navigation |
| **Tablet Landscape**| 1024 x 768 | Desktop header navigation, multi-column actions |
| **Laptop / Desktop**| 1366–1920 | Constrained max-width layout (760px hero, 900px admin) |

## 4. Safe-Area Inset Support
Header and footer spacing adapts dynamically to modern notched mobile displays:
```css
.app-header {
  padding-top: max(12px, env(safe-area-inset-top));
  padding-left: max(5%, env(safe-area-inset-left));
  padding-right: max(5%, env(safe-area-inset-right));
}
.app-footer {
  padding-bottom: max(18px, env(safe-area-inset-bottom));
}
```

## 5. Web Application Manifest
- Served dynamically from `apps/web/src/app/manifest.ts` at `/manifest.webmanifest`.
- Configured with `display: "standalone"`, `theme_color: "#ffffff"`, and verified icon references (`/icons/icon-192.png`, `/icons/icon-512.png`).
