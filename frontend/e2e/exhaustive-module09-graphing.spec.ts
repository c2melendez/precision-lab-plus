import { expect, test } from "@playwright/test";

async function setMathField(page: import("@playwright/test").Page, index: number, value: string) {
  const field = page.locator("math-field").nth(index);
  await field.evaluate((node, v) => {
    const el = node as HTMLElement & { value: string };
    el.value = v as string;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

test("suite original módulo 9: modos gráficos están activos y 2D renderiza", async ({ page }) => {
  await page.goto("./");
  await page.getByRole("button", { name: "Gráficas", exact: true }).click();

  for (const name of ["2D", "3D", "Paramétrica", "Polar"]) {
    await expect(page.getByRole("tab", { name, exact: true })).toBeVisible();
  }

  await setMathField(page, 0, "x^2");
  await page.getByRole("button", { name: "Graficar", exact: true }).click();
  await expect(page.locator(".js-plotly-plot").first()).toBeVisible({ timeout: 15000 });
});

test("suite original módulo 9: múltiples curvas 2D se renderizan juntas", async ({ page }) => {
  await page.goto("./");
  await page.getByRole("button", { name: "Gráficas", exact: true }).click();
  await page.getByRole("button", { name: "+ Añadir expresión", exact: true }).click();
  await setMathField(page, 0, "x");
  await setMathField(page, 1, "x^2");
  await page.getByRole("button", { name: "Graficar", exact: true }).click();
  const plot = page.locator(".js-plotly-plot").first();
  await expect(plot).toBeVisible({ timeout: 15000 });
  await expect(plot.locator(".scatterlayer .trace")).toHaveCount(2, { timeout: 15000 });
});
