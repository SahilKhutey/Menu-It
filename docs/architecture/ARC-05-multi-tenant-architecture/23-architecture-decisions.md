# 23 — Architecture Decisions (ADR-0044 through ADR-0063)

## Summary of Decisions (ARC05-D01 – ARC05-D20)

- **ADR-0044 (ARC05-D01):** Organization is the primary tenant boundary.
- **ADR-0045 (ARC05-D02):** Restaurant is a subordinate resource boundary.
- **ADR-0046 (ARC05-D03):** SaaS uses shared PostgreSQL database/schema.
- **ADR-0047 (ARC05-D04):** Tenant-owned resources carry authoritative organization ownership.
- **ADR-0048 (ARC05-D05):** Membership and role validation are server-side.
- **ADR-0049 (ARC05-D06):** Tenant context is immutable and request-scoped.
- **ADR-0050 (ARC05-D07):** Tenant context is explicitly passed to application services.
- **ADR-0051 (ARC05-D08):** Repository queries enforce tenant scope.
- **ADR-0052 (ARC05-D09):** PostgreSQL RLS provides defense in depth.
- **ADR-0053 (ARC05-D10):** Runtime DB role cannot bypass RLS.
- **ADR-0054 (ARC05-D11):** Tenant context uses transaction-local PostgreSQL settings.
- **ADR-0055 (ARC05-D12):** Tenant-owned parent-child relationships enforce matching ownership via composite keys.
- **ADR-0056 (ARC05-D13):** Storage object keys include tenant scope.
- **ADR-0057 (ARC05-D14):** Tenant-specific cache keys include tenant identity.
- **ADR-0058 (ARC05-D15):** Public menu access uses published data only.
- **ADR-0059 (ARC05-D16):** Background jobs carry explicit tenant context.
- **ADR-0060 (ARC05-D17):** Platform roles are separate from tenant roles.
- **ADR-0061 (ARC05-D18):** Tenant lifecycle includes suspension and offboarding policies.
- **ADR-0062 (ARC05-D19):** Support access is separately authorized and audited.
- **ADR-0063 (ARC05-D20):** SaaS and self-hosted editions share domain authorization rules.
