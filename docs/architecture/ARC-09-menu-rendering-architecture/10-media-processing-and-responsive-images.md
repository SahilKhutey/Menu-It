# ARC-09 §10 — Media Processing & Responsive Images

## 1. Media Assets Specification
All rendered images (logos, covers, item photos) are served from optimized CDN origins with strict HTTPS enforcement.

## 2. Image Loading Policies
1. **Hero Cover Image**:
   - `priority = true` (Next.js image priority flag).
   - Eagerly fetched to ensure maximum Core Web Vitals LCP (Largest Contentful Paint) score.
2. **Food Item Images**:
   - `loading = "lazy"` (applied to all images below the fold).
   - `aspect-ratio: 16/9` or `1/1` defined explicitly to avoid Cumulative Layout Shift (CLS).
3. **Missing Images**:
   - Automatically fall back to SVG vector placeholders or clean text-only card styles.
4. **Alt Text Accessibility**:
   - Screen reader alt text is automatically generated: `Photo of {item_name}`.
