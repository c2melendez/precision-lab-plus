import { expect, test } from "@playwright/test";

test("M14: Plus conserva identidad PL+ y sidebar contractual", async ({ page }) => {
  await page.goto("./");
  await expect(page).toHaveTitle("Precision Lab Plus");

  const sidebar = page.locator('aside[aria-label="Navegación principal"]');
  await expect(sidebar).toHaveAttribute("data-sidebar-state", "expanded");
  await expect(sidebar).toHaveCSS("background-color", "rgb(5, 43, 82)");

  await expect(page.getByRole("heading", { name: "Precision Lab Plus", exact: true })).toBeVisible();

  const iconHref = await page.locator('link[rel="icon"]').getAttribute("href");
  expect(iconHref).toBe("/precision-lab-plus.svg");
  const icon = await page.request.get(new URL(iconHref!, page.url()).toString());
  expect(icon.ok()).toBeTruthy();

  const brandImage = sidebar.locator('img[src*="precision-lab-plus.svg"]');
  await expect(brandImage).toBeVisible();

  await expect(page.getByRole("button", { name: "Gráficas", exact: true }).locator("svg path").nth(1))
    .toHaveAttribute("d", "m6 15 4-5 3 3 5-7");
  await expect(page.getByRole("button", { name: "Geometría", exact: true }).locator("svg path").first())
    .toHaveAttribute("d", "m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z");

  await page.getByRole("button", { name: "Contraer navegación", exact: true }).click();
  await expect(sidebar).toHaveAttribute("data-sidebar-state", "compact");
  await expect(brandImage).toBeVisible();
  await expect(page.getByRole("heading", { name: "Precision Lab Plus", exact: true })).toHaveCount(0);

  await expect(page.locator("body")).not.toContainText("PowerRule");
  await expect(page.locator("body")).not.toContainText("ChainRule");
  await expect(page.locator("body")).not.toContainText("MatrixMultiply");
});
