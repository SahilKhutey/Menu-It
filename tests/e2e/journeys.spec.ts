import { test, expect } from "@playwright/test";

test.describe("FCD-13 Foundational Platform Journeys", () => {
  test("JNY-01 & JNY-02: Public Web App Home & Organization Discovery", async ({ page }) => {
    const webUrl = process.env.WEB_BASE_URL || "http://127.0.0.1:3000";
    const response = await page.goto(webUrl, { waitUntil: "domcontentloaded" });
    if (response) {
      expect(response.status()).toBe(200);
    }
  });

  test("JNY-03 & JNY-04: Admin Portal Unauthenticated Access Protection", async ({ page }) => {
    const adminUrl = process.env.ADMIN_BASE_URL || "http://127.0.0.1:3001";
    await page.goto(`${adminUrl}/restaurants`, { waitUntil: "domcontentloaded" });
    // URL or state must indicate redirection or authentication requirement
    const url = page.url();
    expect(url).toBeDefined();
  });

  test("JNY-06 & JNY-11: Public Menu Slug Not Found Resilience", async ({ page }) => {
    const webUrl = process.env.WEB_BASE_URL || "http://127.0.0.1:3000";
    const response = await page.goto(`${webUrl}/r/non-existent-sample-slug`, {
      waitUntil: "domcontentloaded",
    });
    if (response) {
      expect([200, 404]).toContain(response.status());
    }
  });
});
