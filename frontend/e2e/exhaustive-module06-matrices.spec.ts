import { expect, test } from "@playwright/test";

test("suite original módulo 6: matrices expone rango, traza y eigen y calcula rango", async ({ page }) => {
  await page.goto("./");
  await page.getByRole("button", { name: "Matrices", exact: true }).click();

  const op = page.locator("#matrix-operation");
  await expect(op).toBeVisible();
  await expect(op.locator("option")).toContainText([
    "Eigenvalores y eigenvectores",
    "Traza (tr A)",
    "Rango (rango A)",
  ]);

  await op.selectOption("rank");
  const cells = page.getByRole("group", { name: "Celdas de Matriz A" }).getByRole("textbox");
  await cells.nth(0).fill("1");
  await cells.nth(1).fill("2");
  await cells.nth(2).fill("2");
  await cells.nth(3).fill("4");
  await page.getByRole("button", { name: /calcular/i }).click();

  const result = page.getByRole("region", { name: "Resultado", exact: true });
  await expect(result).toContainText("1", { timeout: 12000 });
});
