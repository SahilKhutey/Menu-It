# ARC-09 §06 — Deterministic Composition & Render Plan

## 1. Composition Concept
Composition is the deterministic process of mapping raw normalized content to structural display sections and registered component slots.

## 2. Render Plan DTO
The composition engine outputs a `RenderPlan`:
```typescript
export interface RenderPlan {
  layout_type: string;
  slots: Record<string, string>;
  active_components: string[];
  responsive_breakpoints: {
    mobile: string;
    tablet: string;
    desktop: string;
  };
}
```

## 3. Structural Slots
ModularMenu defines five mandatory structural slots:
1. `header`: Displays restaurant branding, cover hero, and contact info (e.g., `RestaurantHeroHeader`).
2. `navigation`: Displays category jumping pills or sticky tabs (e.g., `CategoryPillNav`).
3. `category_section`: Groups items within each category header (e.g., `CategorySection`).
4. `item_card`: Individual item presentation with pricing and badges (e.g., `FoodItemCard`).
5. `footer`: Compliance badges, FSSAI licence numbers, and legal disclaimers (e.g., `MenuFooter`).
