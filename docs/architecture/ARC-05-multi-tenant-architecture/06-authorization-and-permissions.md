# 06 — Authorization & Permissions Architecture

## 1. Role Hierarchy

- **Owner:** Unrestricted administrative, financial, and branch authority.
- **Org Admin:** Organizational administration (members, branches, configuration); cannot delete organization.
- **Restaurant Manager:** Operates assigned branches (menus, prices, hours, publishing).
- **Menu Editor:** Edits menu drafts, categories, items, and design themes for assigned branches.
- **Viewer:** Read-only dashboard and analytics observation.

## 2. Branch Assignment Rule

```python
def has_restaurant_access(self, restaurant_id: UUID) -> bool:
    if self.allowed_restaurant_ids is None:
        return True  # Organization-wide access
    return restaurant_id in self.allowed_restaurant_ids
```

If a manager attempts to access an unassigned branch in the same organization, `TenantAccessDeniedException` is thrown.
