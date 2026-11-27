import { expect, test } from '@playwright/test';

test.describe('FCD-15 Restaurant Configuration Journeys', () => {
  test('renders restaurant configuration overview and settings pages', async ({ page }) => {
    await page.goto('/dashboard/restaurants/demo-rest/settings');
    await expect(page.getByRole('heading', { name: 'Restaurant Configuration' })).toBeVisible();

    await page.goto('/dashboard/restaurants/demo-rest/settings/branding');
    await expect(page.getByRole('heading', { name: 'Branding & Theme' })).toBeVisible();

    await page.goto('/dashboard/restaurants/demo-rest/settings/public-profile');
    await expect(page.getByRole('heading', { name: 'Public Profile & Publishing' })).toBeVisible();
  });
});
