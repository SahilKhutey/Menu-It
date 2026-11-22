export interface ResponsiveGridRules {
  columns: number;
  gap: string;
  cssClass: string;
}

export function resolveResponsiveGrid(
  layoutId: string,
  viewport: "mobile" | "tablet" | "desktop" = "desktop",
  customCols?: number
): ResponsiveGridRules {
  let columns = 1;
  let gap = "1rem";

  switch (viewport) {
    case "mobile":
      columns = 1;
      gap = "0.75rem";
      break;
    case "tablet":
      columns = customCols && customCols <= 2 ? customCols : 2;
      gap = "1rem";
      break;
    case "desktop":
    default:
      if (layoutId === "layout-grid") columns = customCols && customCols <= 4 ? customCols : 3;
      else if (layoutId === "layout-image-cards") columns = customCols && customCols <= 3 ? customCols : 3;
      else columns = customCols && customCols <= 2 ? customCols : 2;
      gap = "1.5rem";
      break;
  }

  return {
    columns,
    gap,
    cssClass: `menu-layout--${layoutId} menu-layout--cols-${columns}`,
  };
}
