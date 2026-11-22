# ARC-09 §12 — SEO, OpenGraph & Metadata

## 1. Dynamic Server Metadata
Next.js dynamic routes (`/r/[slug]/[menuSlug]`) export `generateMetadata`:
```typescript
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const menuInput = await getPublishedMenu({ restaurantSlug: params.slug, menuSlug: params.menuSlug });
  return {
    title: `${menuInput.menu.title} | ${menuInput.restaurant.name}`,
    description: menuInput.menu.description || menuInput.restaurant.description,
    openGraph: {
      title: `${menuInput.menu.title} | ${menuInput.restaurant.name}`,
      type: "website",
      images: menuInput.restaurant.cover_image?.url ? [menuInput.restaurant.cover_image.url] : undefined,
    },
    alternates: {
      canonical: `/r/${params.slug}/${params.menuSlug}`,
    },
  };
}
```

## 2. Structured Data (JSON-LD)
Menus embed Schema.org `Restaurant` and `Menu` structured JSON-LD entities for search indexing and rich snippets.
