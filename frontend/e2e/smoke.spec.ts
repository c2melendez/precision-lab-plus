import { expect, test } from "@playwright/test";

function collectBrowserProblems(page: import("@playwright/test").Page) {
  const problems: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") problems.push(`console.error: ${message.text()}`);
  });
  page.on("pageerror", (error) => problems.push(`pageerror: ${error.message}`));
  page.on("response", (response) => {
    if (response.status() >= 500) problems.push(`HTTP ${response.status()}: ${response.url()}`);
  });
  return problems;
}

test("frontend y backend cargan sin errores críticos", async ({ page, request }) => {
  const health = await request.get("http://127.0.0.1:8000/api/v1/health");
  expect(health.ok()).toBeTruthy();

  const problems = collectBrowserProblems(page);
  await page.goto("./", { waitUntil: "networkidle" });
  await expect(page.locator("body")).toContainText(/Precision Lab|Calculadora|Teclado/i);
  expect(problems).toEqual([]);
});

test("no produce desbordamiento horizontal importante", async ({ page }) => {
  await page.goto("./");
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport + 2);
});
