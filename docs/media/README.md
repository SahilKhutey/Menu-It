# Media & Responsive Images Guide

## Overview
Guidelines for handling imagery across ModularMenu digital menus.

## Image Best Practices
1. **Hero Cover Image**: Preloaded using priority flag to optimize Largest Contentful Paint (LCP).
2. **Food Item Photos**: Lazy-loaded below the fold with fixed aspect ratio containers (`16/9` or `1/1`).
3. **Alt Text**: Automated accessible alt text generation: `Photo of {item_name}`.
4. **Placeholders**: Graceful SVG fallbacks when items lack photos.
