'use client';

import { useState } from 'react';
import { Badge, Button, Card, Input } from '@menu-it/ui';
import { restaurantConfigApi } from '@/services/restaurant-config-api';

export default function RestaurantPublicProfilePage({
  params,
}: {
  params: { restaurantId: string };
}) {
  const [publicSlug, setPublicSlug] = useState('');
  const [pubStatus, setPubStatus] = useState<string>('draft');
  const [revision, setRevision] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handlePublish = async () => {
    setMessage(null);
    try {
      const res = await restaurantConfigApi.publishProfile(params.restaurantId, {
        public_slug: publicSlug || undefined,
      });
      if (res.data) {
        setPubStatus(res.data.status);
        setRevision(res.data.published_revision ?? null);
        setMessage(`Published revision ${res.data.published_revision}.`);
      }
    } catch {
      setMessage('Unable to publish restaurant profile.');
    }
  };

  const handleUnpublish = async () => {
    setMessage(null);
    try {
      const res = await restaurantConfigApi.unpublishProfile(params.restaurantId);
      if (res.data) setPubStatus(res.data.status);
      setMessage('Public profile unpublished.');
    } catch {
      setMessage('Unable to unpublish restaurant profile.');
    }
  };

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Public Profile & Publishing</h1>
        <Badge variant={pubStatus === 'published' ? 'success' : 'outline'}>{pubStatus}</Badge>
      </div>
      <Card className="space-y-4 p-6">
        <Input
          label="Public Slug (optional override)"
          value={publicSlug}
          onChange={(e) => setPublicSlug(e.target.value)}
        />
        {revision !== null && (
          <p className="text-sm text-neutral-600">Published Revision: v{revision}</p>
        )}
        {message && <p className="text-sm text-neutral-600">{message}</p>}
        <div className="flex gap-3">
          <Button onClick={handlePublish}>Publish Profile</Button>
          <Button variant="secondary" onClick={handleUnpublish}>
            Unpublish
          </Button>
        </div>
      </Card>
    </main>
  );
}
