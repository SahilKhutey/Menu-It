import { test, expect } from '@playwright/test';

test.describe('FCD-14 Organization, Restaurant & Branch UI Journeys', () => {
  test('renders organization onboarding page cleanly', async ({ page }) => {
    const webUrl = process.env.WEB_BASE_URL || 'http://127.0.0.1:3000';
    const resp = await page.goto(`${webUrl}/onboarding/organization`, {
      waitUntil: 'domcontentloaded',
    });
    expect(resp?.status()).toBe(200);
    await expect(page.getByText('Create Your Organization')).toBeVisible();
  });

  test('renders admin organization directory cleanly', async ({ page }) => {
    const adminUrl = process.env.ADMIN_BASE_URL || 'http://127.0.0.1:3001';
    const resp = await page.goto(`${adminUrl}/organizations`, {
      waitUntil: 'domcontentloaded',
    });
    expect(resp?.status()).toBe(200);
    await expect(page.getByText('Organization Directory')).toBeVisible();
  });
});
