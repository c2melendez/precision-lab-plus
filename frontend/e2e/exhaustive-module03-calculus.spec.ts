import { expect, test } from "@playwright/test";

async function openCalculus(page: import("@playwright/test").Page) {
  await page.goto("./");
  const opener = page.getByRole("button", { name: /abrir teclado|expandir teclado/i }).first();
  await expect(opener).toBeVisible();
  await opener.click();
  await page.getByRole("tab", { name: "Cálculo", exact: true }).click();
}

async function setExpression(page: import("@playwright/test").Page, value: string) {
  const field = page.locator("math-field").first();
  await field.evaluate((node, v) => {
    const el = node as HTMLElement & { value: string };
    el.value = v as string;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

test("suite original módulo 3: inventario de Cálculo refleja capacidades actuales", async ({ page }) => {
  await openCalculus(page);
  const subcategories = page.getByLabel("Subcategorías de Cálculo");

  await subcategories.getByRole("button", { name: "Integrales", exact: true }).click();
  for (const name of ["integral indefinida", "integral definida"]) {
    await expect(page.getByRole("button", { name, exact: true }).first()).toBeVisible();
  }

  await subcategories.getByRole("button", { name: "Sumas y productos", exact: true }).click();
  for (const name of ["sumatoria", "productoria"]) {
    await expect(page.getByRole("button", { name, exact: true }).first()).toBeVisible();
  }
  const product = page.getByRole("button", { name: "productoria", exact: true }).first();
  await product.click();
  await expect(page.getByText(/productoria: todavía no disponible/i)).toHaveCount(0);

  await subcategories.getByRole("button", { name: "Derivadas", exact: true }).click();
  for (const name of ["derivada", "derivada segunda"]) {
    await expect(page.getByRole("button", { name, exact: true }).first()).toBeVisible();
  }
  await expect(page.getByRole("button", { name: /derivada de orden n/i }).first()).toBeVisible();

  await subcategories.getByRole("button", { name: "Límites", exact: true }).click();
  for (const name of [
    "límite",
    "límite al infinito",
    "límite lateral por la izquierda",
    "límite lateral por la derecha",
  ]) {
    await expect(page.getByRole("button", { name, exact: true }).first()).toBeVisible();
  }
});

test("suite original módulo 3: productoria de 1 a 5 se evalúa a 120 desde la UI", async ({ page }) => {
  await page.goto("./");
  await setExpression(page, "\\prod_{i=1}^{5}i");

  const calculate = page.getByRole("button", { name: /calcular|evaluar/i }).first();
  await expect(calculate).toBeEnabled();
  await calculate.click();

  const result = page.getByRole("region", { name: "Resultado", exact: true });
  await expect(result).toContainText("120", { timeout: 12000 });
});

test("suite original módulo 3: sumatoria de 1 a 5 se evalúa a 15 desde la UI", async ({ page }) => {
  await page.goto("./");
  await setExpression(page, "\\sum_{i=1}^{5}i");

  const calculate = page.getByRole("button", { name: /calcular|evaluar/i }).first();
  await expect(calculate).toBeEnabled();
  await calculate.click();

  const result = page.getByRole("region", { name: "Resultado", exact: true });
  await expect(result).toContainText("15", { timeout: 12000 });
});
