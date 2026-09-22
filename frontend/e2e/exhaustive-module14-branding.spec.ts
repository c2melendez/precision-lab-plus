import { expect, test } from "@playwright/test";

test("M14: branding visible e icono de Precision Lab Plus son consistentes", async ({ page }) => {
  await page.goto("./");
  await expect(page).toHaveTitle("Precision Lab Plus");
  await expect(page.getByRole("heading", { name: "Precision Lab Plus", exact: true })).toBeVisible();

  const iconHref = await page.locator('link[rel="icon"]').getAttribute("href");
  expect(iconHref).toBe("/icon-192.png");
  const icon = await page.request.get(new URL(iconHref!, page.url()).toString());
  expect(icon.ok()).toBeTruthy();

  await expect(page.locator("body")).not.toContainText("PowerRule");
  await expect(page.locator("body")).not.toContainText("ChainRule");
  await expect(page.locator("body")).not.toContainText("MatrixMultiply");
});
