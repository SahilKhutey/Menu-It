# Menu Rendering Engine Guide

## Overview
The menu rendering engine (`@modularmenu/menu-renderer`) provides deterministic composition of digital restaurant menus from normalized `RenderInput` payloads.

## Key Capabilities
- Pure functional normalization of prices, dietary classifications, allergens, and availability.
- Deterministic layout slot resolution (`header`, `navigation`, `category_section`, `item_card`, `footer`).
- Scoped CSS variable generation for custom theme styling.
- Responsive breakpoints calculation for mobile, tablet, and desktop viewports.
