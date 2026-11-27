# FCD-08 §09 — Theme Configuration & Validation

## 1. Contrast Calculation Algorithm

To protect accessibility, the Theme Engine implements the standard WCAG relative luminance formula (`packages/theme-engine/src/resolvers/contrast.ts`):

$$L = 0.2126 \times R + 0.7152 \times G + 0.0722 \times B$$

Where $R, G, B$ are sRGB components linearised according to:
$$C_{\text{linear}} = \begin{cases} \frac{C_{\text{sRGB}}}{12.92} & \text{if } C_{\text{sRGB}} \le 0.04045 \\ \left(\frac{C_{\text{sRGB}} + 0.055}{1.055}\right)^{2.4} & \text{if } C_{\text{sRGB}} > 0.04045 \end{cases}$$

The contrast ratio between two relative luminances $L_1$ (lighter) and $L_2$ (darker) is:
$$\text{Ratio} = \frac{L_1 + 0.05}{L_2 + 0.05}$$

A pair passes WCAG 2.2 Level AA for normal body text if:
$$\text{Ratio} \ge 4.5$$

---

## 2. Validation Engine (`validateTheme`)

The validation function performs systematic syntactic and semantic checks on any theme object:
```typescript
const result = validateTheme(candidateTheme);
if (!result.valid) {
  console.error("Theme validation failed:", result.errors);
}
```

### Checks Performed
1. **Structural Integrity:** Ensures `id`, `name`, `version`, `colors`, `typography`, and `radii` objects exist and conform to their schemas.
2. **Color Hex Validation:** Ensures all 23 color tokens are valid 6-character hexadecimal strings (`^#[0-9A-Fa-f]{6}$`).
3. **Typography Constraints:** Restricts base font sizes to approved steps (`14px`, `15px`, `16px`, `17px`, `18px`).
4. **Radii Constraints:** Restricts button, card, and input border radii to standard approved token values.
5. **Mandatory Contrast Pairs:**
   - `foreground` on `background` must achieve $\ge 4.5:1$.
   - `primaryForeground` on `primary` must achieve $\ge 4.5:1$.
   - `destructiveForeground` on `destructive` must achieve $\ge 4.5:1$.

If any check fails, `validateTheme` returns `{ valid: false, errors: string[] }` and `applyTheme()` refuses to mount the invalid theme to the DOM.
