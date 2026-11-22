import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getPublishedMenu, PublicMenuRenderer } from "@/features/public-menu";

interface PageProps {
  params: {
    slug: string;
    menuSlug: string;
  };
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const restaurantSlug = params.slug;
  const menuSlug = params.menuSlug;
  const menuInput = await getPublishedMenu({ restaurantSlug, menuSlug });

  if (!menuInput) {
    return {
      title: "Menu Not Found | ModularMenu",
      robots: { index: false, follow: false },
    };
  }

  const title = `${menuInput.menu.title} | ${menuInput.restaurant.name}`;
  const description =
    menuInput.menu.description || menuInput.restaurant.description || "Digital restaurant menu";

  return {
    title,
    description,
    alternates: {
      canonical: `/r/${restaurantSlug}/${menuSlug}`,
    },
    openGraph: {
      title,
      description,
      type: "website",
      images: menuInput.restaurant.cover_image?.url
        ? [menuInput.restaurant.cover_image.url]
        : undefined,
    },
  };
}

export default async function PublicMenuPage({ params }: PageProps) {
  const restaurantSlug = params.slug;
  const menuSlug = params.menuSlug;
  const menuInput = await getPublishedMenu({ restaurantSlug, menuSlug });

  if (!menuInput) {
    notFound();
  }

  return <PublicMenuRenderer input={menuInput} />;
}
