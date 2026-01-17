import { chromium } from "playwright";

async function captureUI() {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 400, height: 700 },
    colorScheme: "dark",
  });
  const page = await context.newPage();

  try {
    await page.goto("http://localhost:5173", { waitUntil: "networkidle" });

    // Force dark theme
    await page.evaluate(() => {
      localStorage.removeItem("claudeminder-theme");
      document.documentElement.setAttribute("data-theme", "dark");
    });

    await page.reload({ waitUntil: "networkidle" });
    await page.waitForTimeout(1500);

    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");

    // Capture main UI
    await page.screenshot({
      path: `screenshots/ui-main-${timestamp}.png`,
      fullPage: false,
    });
    console.log(`Screenshot saved: screenshots/ui-main-${timestamp}.png`);

    // Click settings button to open panel
    const settingsBtn = page.locator('button[title="Settings"]');
    if (await settingsBtn.isVisible()) {
      await settingsBtn.click();
      await page.waitForTimeout(500);

      await page.screenshot({
        path: `screenshots/ui-settings-${timestamp}.png`,
        fullPage: false,
      });
      console.log(`Screenshot saved: screenshots/ui-settings-${timestamp}.png`);
    }
  } catch (error) {
    console.error("Error capturing UI:", error);
  } finally {
    await browser.close();
  }
}

captureUI();
