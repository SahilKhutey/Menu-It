# 05 — Organization Membership & Multi-Tenancy

## 1. Multi-Tenant Identities

A single human user (`user_id`) can belong to multiple organizations:
- In Organization A: Role = `Owner`, unrestricted branch access.
- In Organization B: Role = `Restaurant Manager`, restricted to `[rest_b1_id]`.

## 2. Membership Invariants

- **Explicit Revocation:** Inactivating or deleting a membership immediately invalidates all active sessions attempting to resolve that organization.
- **No Implicit Cross-Over:** Having owner permissions in Organization A confers zero permissions in Organization B.
- **Invitation Boundary:** Invitations are cryptographic, time-limited, and bound to a specific organization and email address.
