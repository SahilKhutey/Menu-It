# 15 — Tenant Lifecycle & Offboarding

## 1. Lifecycle States

1. **Pending Provisioning:** Account initialized; default restaurant and initial draft generated.
2. **Active:** Fully operational; menus editable and publishable.
3. **Suspended:** Account locked due to non-payment or policy violation. Editing and publishing blocked.
4. **Offboarded:** Tenant marked for deletion; access revoked across all paths.

## 2. Suspension Grace Policy

During suspension, live diners can continue viewing the last published menu snapshot for a documented grace period (e.g. 7 days), preventing immediate diner disruption, while blocking all administrative actions.
