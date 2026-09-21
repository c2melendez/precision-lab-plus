import { expect, test } from "@playwright/test";

test("suite original módulo 7: Estadística calcula media y expone submodos", async ({ page }) => {
  await page.goto("./");
  await page.getByRole("button", { name: "Estadística", exact: true }).click();

  await expect(page.getByRole("button", { name: "Descriptiva", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Distribución", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Correlación", exact: true })).toBeVisible();

  const data = page.getByLabel("Datos (separados por coma)");
  await data.fill("1,2,3,4,5");
  await page.getByRole("button", { name: "x̄", exact: true }).click();

  const result = page.getByRole("region", { name: "Resultado", exact: true });
  await expect(result).toContainText("3", { timeout: 12000 });
});
