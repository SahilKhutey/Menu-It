'use client';

import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import type { OrganizationInvitationDTO, OrganizationMemberDTO } from '@menu-it/shared-types';
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Container,
  Input,
} from '@menu-it/ui';
import { createOrgInvitation, listOrgInvitations, listOrgMembers } from '@/services/org-api';

export default function OrganizationMembersPage() {
  const params = useParams<{ organizationId: string }>();
  const [members, setMembers] = useState<OrganizationMemberDTO[]>([]);
  const [invitations, setInvitations] = useState<OrganizationInvitationDTO[]>([]);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('manager');
  const [message, setMessage] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!params.organizationId) return;
    const [mRes, iRes] = await Promise.all([
      listOrgMembers(params.organizationId),
      listOrgInvitations(params.organizationId),
    ]);
    setMembers(mRes.data ?? []);
    setInvitations(iRes.data ?? []);
  }, [params.organizationId]);

  useEffect(() => {
    loadData().catch(() => {});
  }, [loadData]);

  async function handleInvite(e: FormEvent) {
    e.preventDefault();
    setMessage(null);
    try {
      await createOrgInvitation(params.organizationId, { email: inviteEmail, role: inviteRole });
      setInviteEmail('');
      setMessage('Invitation sent.');
      await loadData();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Failed to invite member.');
    }
  }

  return (
    <Container size="lg" style={{ padding: '40px 24px', display: 'grid', gap: '24px' }}>
      <Link href={`/dashboard/organizations/${params.organizationId}`}>← Back to Organization</Link>
      <Card>
        <CardHeader>
          <CardTitle>Invite Team Member</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleInvite} style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <Input
              type="email"
              placeholder="teammate@restaurant.com"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              required
            />
            <select value={inviteRole} onChange={(e) => setInviteRole(e.target.value)}>
              <option value="admin">Admin</option>
              <option value="manager">Manager</option>
              <option value="staff">Staff</option>
              <option value="viewer">Viewer</option>
            </select>
            <Button type="submit">Send Invitation</Button>
          </form>
          {message && <p style={{ marginTop: '8px' }}>{message}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Active Members ({members.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <ul style={{ display: 'grid', gap: '8px', listStyle: 'none', padding: 0 }}>
            {members.map((m) => (
              <li key={m.id} style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>User: {m.user_id}</span>
                <span>
                  <Badge variant="primary">{m.role}</Badge>{' '}
                  <Badge variant="default">{m.status}</Badge>
                </span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Invitations ({invitations.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <ul style={{ display: 'grid', gap: '8px', listStyle: 'none', padding: 0 }}>
            {invitations.map((inv) => (
              <li key={inv.id} style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>
                  {inv.email} ({inv.role})
                </span>
                <Badge variant="default">{inv.status}</Badge>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </Container>
  );
}
