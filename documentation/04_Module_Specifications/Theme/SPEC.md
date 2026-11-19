# Module Specification: Theme Engine (MOD-08) & Visual Presets
**Module ID:** MOD-08  
**Domain:** Design & Customization  
**Priority:** P0

---

## 1. Token Architecture
Themes in ModularMenu are defined as pure JSON objects adhering to the `ThemeTokens` schema.

```typescript
export interface ThemeTokens {
  version: 1;
  id: string;
  name: string;
  key: string; // 'luxury' | 'minimal' | 'rustic' | 'vibrant' | 'contemporary' | 'editorial'
  colors: {
    surface: string;           // Main page background
    surfaceElevated: string;   // Cards and modal surfaces
    surfaceMuted: string;      // Category tags, pills
    textPrimary: string;       // Primary titles & body
    textMuted: string;         // Descriptions & metadata
    primary: string;           // Main brand accent / buttons
    primaryForeground: string; // Text on primary button
    accent: string;            // Highlights & badges
    border: string;            // Dividers & card outlines
    dietaryVeg: string;        // Default: #16A34A (FSSAI Green)
    dietaryNonVeg: string;     // Default: #DC2626 (FSSAI Brown/Red)
    dietaryEgg: string;        // Default: #D97706
  };
  typography: {
    fontHeading: string;       // e.g., 'Playfair Display', 'Inter', 'Cinzel'
    fontBody: string;          // e.g., 'Plus Jakarta Sans', 'Inter'
    fontPrice: string;         // e.g., 'JetBrains Mono', 'Plus Jakarta Sans'
    baseSize: number;          // Default: 16 (in px)
    scaleRatio: number;        // e.g., 1.25 (Major Third)
  };
  layout: {
    borderRadius: 'none' | 'sm' | 'md' | 'lg' | 'full';
    cardStyle: 'flat' | 'bordered' | 'elevated' | 'glass';
    itemSpacing: 'compact' | 'comfortable' | 'spacious';
    imageAspectRatio: 'square' | 'video' | 'portrait' | 'none';
  };
}
```

---

## 2. Six Pre-Built Theme Definitions (Ready for Implementation)

### 1. Luxury (`theme_luxury`)
- **Aesthetic:** Dark, moody, high-end fine dining and cocktail bar ambiance.
- **Palette:** Surface `#0D0E12`, Surface Elevated `#16181F`, Text `#F8F9FA`, Primary `#D4AF37` (Imperial Gold), Accent `#E5C365`.
- **Fonts:** Heading `Cinzel`, Body `Plus Jakarta Sans`.

### 2. Minimal (`theme_minimal`)
- **Aesthetic:** Ultra-clean, Scandinavian, high contrast, pure whitespace.
- **Palette:** Surface `#FFFFFF`, Surface Elevated `#F4F4F5`, Text `#09090B`, Primary `#18181B`, Accent `#71717A`.
- **Fonts:** Heading `Inter`, Body `Inter`.

### 3. Rustic (`theme_rustic`)
- **Aesthetic:** Warm earth tones, artisanal trattoria, farm-to-table bakery.
- **Palette:** Surface `#FBF9F5`, Surface Elevated `#FFFFFF`, Text `#292524`, Primary `#78350F` (Warm Amber), Accent `#B45309`.
- **Fonts:** Heading `Merriweather`, Body `Lora`.

### 4. Vibrant (`theme_vibrant`)
- **Aesthetic:** Playful, bold, street food, smash burger, fast-casual diner.
- **Palette:** Surface `#FFFDF9`, Surface Elevated `#FFFFFF`, Text `#1E1B4B`, Primary `#E11D48` (Vivid Crimson), Accent `#F59E0B`.
- **Fonts:** Heading `Outfit`, Body `Plus Jakarta Sans`.

### 5. Contemporary (`theme_contemporary`)
- **Aesthetic:** Sleek, modern all-day dining, bistros, restro-bars.
- **Palette:** Surface `#F8FAFC`, Surface Elevated `#FFFFFF`, Text `#0F172A`, Primary `#2563EB` (Electric Indigo), Accent `#06B6D4`.
- **Fonts:** Heading `Cabinet Grotesk`, Body `Inter`.

### 6. Editorial (`theme_editorial`)
- **Aesthetic:** High-fashion food photography, tasting menus, chef signatures.
- **Palette:** Surface `#FAFAFA`, Surface Elevated `#FFFFFF`, Text `#171717`, Primary `#262626`, Accent `#A3A3A3`.
- **Fonts:** Heading `Playfair Display`, Body `Source Serif 4`.
