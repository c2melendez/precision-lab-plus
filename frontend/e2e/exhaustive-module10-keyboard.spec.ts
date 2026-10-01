import { expect, test } from "@playwright/test";

async function openKeyboard(page: import("@playwright/test").Page) {
  await page.goto("./");
  const opener = page.getByRole("button", { name: /abrir teclado|expandir teclado/i }).first();
  await expect(opener).toBeVisible();
  await opener.click();
  return page.getByRole("dialog", { name: "Teclado matemático" });
}

async function clearBasic(dialog: import("@playwright/test").Locator) {
  await dialog.getByRole("button", { name: "borrar todo el campo", exact: true }).click();
}

test("módulo 10: la tecla % calcula porcentaje real (50% = 0.5)", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clearBasic(dialog);
  await dialog.getByRole("button", { name: "5", exact: true }).click();
  await dialog.getByRole("button", { name: "0", exact: true }).click();
  await dialog.getByRole("button", { name: "porcentaje", exact: true }).click();

  const responsePromise = page.waitForResponse(r => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST");
  await dialog.getByRole("button", { name: "calcular", exact: true }).click();
  const body = await (await responsePromise).json();
  expect(body.success, JSON.stringify(body)).toBe(true);
  expect(Number(body.result_approx)).toBeCloseTo(0.5, 12);
});

test("módulo 10: ±(5) produce dos ramas matemáticas distintas", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clearBasic(dialog);
  await dialog.getByRole("tab", { name: "Más", exact: true }).click();
  await dialog.getByLabel("Subcategorías de Más").getByRole("button", { name: "Signos", exact: true }).click();
  await dialog.getByRole("button", { name: "más/menos", exact: true }).click();
  await dialog.getByRole("button", { name: "5", exact: true }).click();

  const responsePromise = page.waitForResponse(r => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST");
  await dialog.getByRole("button", { name: "calcular", exact: true }).click();
  const body = await (await responsePromise).json();
  expect(body.success, JSON.stringify(body)).toBe(true);
  const text = String(body.result_text ?? "").replace(/\s/g, "");
  expect(text).toMatch(/(?:\[|\{|,).*5/);
  expect(text).toContain("-5");
});

test("módulo 10: Productoria Π ya no aparece como pendiente", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await dialog.getByRole("tab", { name: "Cálculo", exact: true }).click();
  await dialog.getByLabel("Subcategorías de Cálculo").getByRole("button", { name: "Sumas y productos", exact: true }).click();
  const product = dialog.getByRole("button", { name: "productoria", exact: true });
  await expect(product).toBeVisible();
  await product.click();
  await expect(page.getByText(/productoria: todavía no disponible/i)).toHaveCount(0);
});

test("módulo 10: acciones no aritméticas de Álgebra exponen tooltip", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await dialog.getByRole("tab", { name: "Álgebra", exact: true }).click();
  const subcategories = dialog.getByLabel("Subcategorías de Álgebra");
  await subcategories.getByRole("button", { name: "Ecuaciones", exact: true }).click();

  for (const name of [
    "Resolver ecuación",
    "Resolver inecuación",
    "Resolver sistema de ecuaciones",
    "Resolver sistema de inecuaciones",
    "Simplificar expresión",
    "Factorizar expresión",
    "Evaluar función en un punto",
  ]) {
    const button = dialog.getByRole("button", { name, exact: true }).first();
    await expect(button).toBeVisible();
    const title = await button.getAttribute("title");
    expect(title, `Falta tooltip en ${name}`).toBeTruthy();
  }

  await subcategories.getByRole("button", { name: "Aritmética", exact: true }).click();
  for (const name of ["mínimo común múltiplo", "máximo común divisor"]) {
    const button = dialog.getByRole("button", { name, exact: true }).first();
    await expect(button).toBeVisible();
    const title = await button.getAttribute("title");
    expect(title, `Falta tooltip en ${name}`).toBeTruthy();
  }
});


test("módulo 10 B6: Enter físico evalúa igual que Enter virtual", async ({ page }) => {
  await page.goto("./");
  const field = page.locator('math-field[aria-label="Expresión"]').first();
  await field.evaluate((node) => {
    const mathField = node as HTMLElement & { setValue?: (value: string) => void; value?: string };
    if (typeof mathField.setValue === "function") mathField.setValue("2+2");
    else mathField.value = "2+2";
    node.dispatchEvent(new Event("input", { bubbles: true }));
  });

  const responsePromise = page.waitForResponse(
    r => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST",
  );
  await field.press("Enter");
  const body = await (await responsePromise).json();
  expect(body.success, JSON.stringify(body)).toBe(true);
  expect(Number(body.result_approx)).toBeCloseTo(4, 12);
});
