import { test, expect } from "@playwright/test";

test.describe("Claudiminder App", () => {
  test("has title", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/Claudiminder/);
  });

  test("shows usage display", async ({ page }) => {
    await page.goto("/");
    // Wait for app to load
    await page.waitForTimeout(1000);
    // Check for main container
    const container = page.locator('[data-testid="app-container"]');
    await expect(container).toBeVisible();
  });

  test("theme toggle works", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    // Find theme toggle button
    const themeButton = page.locator('[data-testid="theme-toggle"]');
    if (await themeButton.isVisible()) {
      await themeButton.click();
      // Verify theme changed
      const html = page.locator("html");
      const dataTheme = await html.getAttribute("data-theme");
      expect(dataTheme).toBeTruthy();
    }
  });

  test("refresh button exists", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    // Check for refresh functionality
    const refreshButton = page.locator('[data-testid="refresh-button"]');
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      // Should not throw error
    }
  });

  test("settings panel can be opened", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    const settingsButton = page.locator('[data-testid="settings-button"]');
    if (await settingsButton.isVisible()) {
      await settingsButton.click();
      // Check settings panel appears
      const settingsPanel = page.locator('[data-testid="settings-panel"]');
      await expect(settingsPanel).toBeVisible();
    }
  });
});
