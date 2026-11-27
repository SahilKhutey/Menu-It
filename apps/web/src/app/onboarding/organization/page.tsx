'use client';

import { useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button, Card, CardContent, CardHeader, CardTitle, Container, Input } from '@menu-it/ui';
import { createOrganization } from '@/services/org-api';
import { APIClientError } from '@/services/api-client';

export default function OrganizationOnboardingPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [currencyCode, setCurrencyCode] = useState('INR');
  const [timezone, setTimezone] = useState('Asia/Kolkata');
  const [countryCode, setCountryCode] = useState('IN');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!name.trim() || !slug.trim()) {
      setError('Organization name and URL slug are required.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await createOrganization({
        name: name.trim(),
        slug: slug.trim().toLowerCase(),
        currency_code: currencyCode.trim().toUpperCase(),
        timezone: timezone.trim(),
        country_code: countryCode.trim().toUpperCase(),
      });
      if (res.data) {
        router.push(`/dashboard/organizations/${res.data.id}`);
      }
    } catch (err) {
      if (err instanceof APIClientError) {
        setError(`${err.message} (Request ID: ${err.requestId ?? 'n/a'})`);
      } else {
        setError('Unable to create organization. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Container size="sm" style={{ padding: '48px 24px' }}>
      <Card>
        <CardHeader>
          <CardTitle>Create Your Organization</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '16px' }}>
            {error && (
              <div role="alert" style={{ color: 'var(--color-danger, #b91c1c)', fontSize: '14px' }}>
                {error}
              </div>
            )}
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>Organization Name</span>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="ABC Hospitality Pvt. Ltd."
                required
              />
            </label>
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>URL Slug</span>
              <Input
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                placeholder="abc-hospitality"
                required
              />
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <label style={{ display: 'grid', gap: '6px' }}>
                <span>Country (ISO-2)</span>
                <Input
                  value={countryCode}
                  onChange={(e) => setCountryCode(e.target.value)}
                  maxLength={2}
                  required
                />
              </label>
              <label style={{ display: 'grid', gap: '6px' }}>
                <span>Currency (ISO-3)</span>
                <Input
                  value={currencyCode}
                  onChange={(e) => setCurrencyCode(e.target.value)}
                  maxLength={3}
                  required
                />
              </label>
            </div>
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>IANA Time Zone</span>
              <Input
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                placeholder="Asia/Kolkata"
                required
              />
            </label>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <Link href="/dashboard/organizations">Cancel</Link>
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Creating...' : 'Create Organization'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
}
