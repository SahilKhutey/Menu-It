# FCD-14 — 18 Testing Strategy & Coverage

## Test Pyramid
1. **Domain Unit Tests (`apps/api/tests/unit/test_fcd14_domain_models.py`)**:
   - Organization country code validation, branch entity & lifecycle transitions, final owner protection, cross-organization scope guard, and invitation acceptance invariants.
2. **Service Integration Tests (`apps/api/tests/integration/test_fcd14_org_restaurant_branch.py`)**:
   - Organization onboarding + transactional outbox atomicity, restaurant/branch hierarchy & cross-tenant isolation, invitation token hashing & reuse rejection, owner protection, ownership transfer, and branch staff assignments.
3. **API Endpoint Tests (`apps/api/tests/api/test_fcd14_endpoints.py`)**:
   - Full HTTP workflow from user session creation through organization onboarding, restaurant creation, branch creation, and retrieval.
4. **Frontend Unit & E2E Tests**:
   - `apps/web/tests/unit/org-api.test.ts`: Validates `org-api.ts` request construction and response unwrapping.
   - `tests/e2e/fcd14-journeys.spec.ts`: Playwright journey specification covering onboarding, restaurant/branch creation, and member management.
