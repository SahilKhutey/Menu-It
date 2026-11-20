# MOD-02 — Tenant & Organization Module Specification

**Module ID:** MOD-02  
**Tier:** Platform Foundation (P0)  
**Package:** `app.modules.organizations`  

---

## 1. Ownership & Boundaries
- **Owns:** Organization identity, organization lifecycle, membership, invitations.
- **Does Not Own:** User passwords, restaurant menu content, billing processing.

## 2. Domain Model & Invariants
- **Organization Entity:** `Organization(id, name, owner_id, is_active, member_ids)`
  - Owner is automatically added to membership.
  - Ownership transfer requires the new owner to be an existing member.
- **Invitation Entity:** `Invitation(id, organization_id, email, role, expires_at, is_accepted)`
  - Cannot accept expired or already accepted invitations (`assert_can_accept()`).

## 3. Public Contracts & Events
- **Provides:** `OrganizationReader` Protocol (`organization_exists`, `is_user_member`).
- **Consumes:** `IdentityVerifier` Protocol.
- **Emits:** `OrganizationCreated` (EVT-002), `MemberInvited` (EVT-003).
