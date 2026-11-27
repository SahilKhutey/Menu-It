'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Button, Card, CardContent, CardHeader, CardTitle, Container, Input } from '@menu-it/ui';
import { getOrganization, updateOrganization } from '@/services/org-api';

export default function OrganizationSettingsPage() {
  const params = useParams<{ organizationId: string }>();
  const [name, setName] = useState('');
  const [legalName, setLegalName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!params.organizationId) return;
    getOrganization(params.organizationId).then((res) => {
      if (res.data) {
        setName(res.data.name);
        setLegalName(res.data.legal_name ?? '');
        setEmail(res.data.email ?? '');
        setPhone(res.data.phone ?? '');
      }
    });
  }, [params.organizationId]);

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    setStatusMsg(null);
    try {
      await updateOrganization(params.organizationId, {
        name: name.trim(),
        legal_name: legalName.trim() || null,
        email: email.trim() || null,
        phone: phone.trim() || null,
      });
      setStatusMsg('Organization profile saved.');
    } catch (err) {
      setStatusMsg(err instanceof Error ? err.message : 'Failed to save changes.');
    }
  }

  return (
    <Container size="sm" style={{ padding: '40px 24px' }}>
      <Link href={`/dashboard/organizations/${params.organizationId}`}>← Back to Organization</Link>
      <Card style={{ marginTop: '16px' }}>
        <CardHeader>
          <CardTitle>Organization Profile & Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSave} style={{ display: 'grid', gap: '16px' }}>
            {statusMsg && <p>{statusMsg}</p>}
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>Display Name</span>
              <Input value={name} onChange={(e) => setName(e.target.value)} required />
            </label>
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>Legal Name</span>
              <Input value={legalName} onChange={(e) => setLegalName(e.target.value)} />
            </label>
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>Business Email</span>
              <Input value={email} onChange={(e) => setEmail(e.target.value)} type="email" />
            </label>
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>Phone</span>
              <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
            </label>
            <Button type="submit">Save Settings</Button>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
}
