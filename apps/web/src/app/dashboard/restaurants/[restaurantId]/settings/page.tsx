'use client';

import Link from 'next/link';
import { Card } from '@menu-it/ui';

const SECTIONS = [
  {
    href: 'profile',
    title: 'Profile & Identity',
    desc: 'Display name, cuisine, description, and public contacts',
  },
  {
    href: 'branding',
    title: 'Branding & Theme',
    desc: 'Logo, cover image, colors, typography, and theme preview',
  },
  {
    href: 'hours',
    title: 'Business Hours',
    desc: 'Weekly shifts, overnight hours, and holiday exceptions',
  },
  {
    href: 'services',
    title: 'Service Modes',
    desc: 'Dine-in, takeaway, pickup, delivery, and curbside',
  },
  {
    href: 'operations',
    title: 'Operational Preferences',
    desc: 'Preparation buffers, advance windows, and capacity',
  },
  {
    href: 'branches',
    title: 'Branch Overrides',
    desc: 'Local branch overrides and effective configuration',
  },
  {
    href: 'public-profile',
    title: 'Public Profile & Publishing',
    desc: 'Preview, publish, unpublish, and revision restore',
  },
];

export default function RestaurantSettingsOverviewPage({
  params,
}: {
  params: { restaurantId: string };
}) {
  return (
    <main className="mx-auto max-w-5xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Restaurant Configuration</h1>
        <p className="text-sm text-neutral-500">
          Centralized identity, branding, hours, service modes, and public profile settings for{' '}
          <code>{params.restaurantId}</code>.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SECTIONS.map((s) => (
          <Link
            key={s.href}
            href={`/dashboard/restaurants/${params.restaurantId}/settings/${s.href}`}
          >
            <Card className="h-full p-4 transition hover:border-neutral-400">
              <h2 className="font-medium">{s.title}</h2>
              <p className="mt-1 text-sm text-neutral-500">{s.desc}</p>
            </Card>
          </Link>
        ))}
      </div>
    </main>
  );
}
