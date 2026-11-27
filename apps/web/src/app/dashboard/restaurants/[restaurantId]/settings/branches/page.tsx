'use client';

import { Card } from '@menu-it/ui';

export default function RestaurantBranchOverridesPage({
  params,
}: {
  params: { restaurantId: string };
}) {
  return (
    <main className="mx-auto max-w-4xl space-y-6 p-6">
      <h1 className="text-2xl font-semibold">Branch Configuration Overrides</h1>
      <Card className="space-y-2 p-6">
        <p className="text-sm text-neutral-600">
          Restaurant <code>{params.restaurantId}</code> branches inherit restaurant-wide hours,
          service modes, and operational preferences unless explicit overrides are configured via{' '}
          <code>/api/v1/branches/:branchId/configuration</code>.
        </p>
        <p className="text-sm text-neutral-500">
          Explicitly disabling a service (for example setting <code>DELIVERY: false</code>) prevents
          inheritance from the parent restaurant configuration.
        </p>
      </Card>
    </main>
  );
}
