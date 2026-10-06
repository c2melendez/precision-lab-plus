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
  await dialog.getByRole("tab", { name: "Básico", exact: true }).click();
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
  await dialog.getByRole("tab", { name: "Básico", exact: true }).click();
  await clearBasic(dialog);
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
  const product = dialog.getByRole("button", { name: "productoria", exact: true });
  await expect(product).toBeVisible();
  await product.click();
  await expect(page.getByText(/productoria: todavía no disponible/i)).toHaveCount(0);
});

test("módulo 10: acciones no aritméticas de Álgebra exponen tooltip", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await dialog.getByRole("tab", { name: "Álgebra", exact: true }).click();

  for (const name of [
    "Resolver ecuación",
    "Resolver inecuación",
    "Resolver sistema de ecuaciones",
    "Simplificar expresión",
    "Mínimo común múltiplo",
    "Máximo común divisor",
  ]) {
    const button = dialog.getByRole("button", { name, exact: true }).first();
    await expect(button).toBeVisible();
    const title = await button.getAttribute("title");
    expect(title, `Falta tooltip en ${name}`).toBeTruthy();
  }
});



async function valueOfMainField(page: import("@playwright/test").Page) {
  const field = page.locator("math-field").first();
  return String(await field.evaluate((el) => (el as HTMLElement & { value?: string }).value ?? ""));
}

async function pressVirtualPowerSequence(
  page: import("@playwright/test").Page,
  base: string,
  exponentDigits: string[],
  suffix: string[] = [],
) {
  const dialog = await openKeyboard(page);
  await dialog.getByRole("tab", { name: "Básico", exact: true }).click();
  await clearBasic(dialog);
  await dialog.getByRole("button", { name: base, exact: true }).click();

  await dialog.getByRole("tab", { name: "Símbolos", exact: true }).click();
  await dialog.getByRole("button", { name: "potencia general", exact: true }).click();

  await dialog.getByRole("tab", { name: "Básico", exact: true }).click();
  for (const d of exponentDigits) {
    await dialog.getByRole("button", { name: d, exact: true }).click();
  }
  for (const key of suffix) {
    if (key === "+") await dialog.getByRole("button", { name: "sumar", exact: true }).click();
    else await dialog.getByRole("button", { name: key, exact: true }).click();
  }
  return valueOfMainField(page);
}

test("IN625 G1b EN-TC-01: teclado virtual conserva 10 completo en el exponente", async ({ page }) => {
  await page.goto("./");
  const latex = await pressVirtualPowerSequence(page, "2", ["1","0"]);
  expect(latex.replace(/\s/g, "")).toMatch(/2\^\{?10\}?/);
});

test("IN625 G1b EN-TC-02: teclado virtual saca + del exponente", async ({ page }) => {
  await page.goto("./");
  const dialog = await openKeyboard(page);
  await dialog.getByRole("tab", { name: "Básico", exact: true }).click();
  await clearBasic(dialog);
  const field = page.locator("math-field").first();
  await field.evaluate((el) => { (el as HTMLElement & { value?: string }).value = "x"; });
  await dialog.getByRole("tab", { name: "Símbolos", exact: true }).click();
  await dialog.getByRole("button", { name: "potencia general", exact: true }).click();
  await dialog.getByRole("tab", { name: "Básico", exact: true }).click();
  await dialog.getByRole("button", { name: "2", exact: true }).click();
  await dialog.getByRole("button", { name: "sumar", exact: true }).click();
  await dialog.getByRole("button", { name: "1", exact: true }).click();
  const latex = await valueOfMainField(page);
  expect(latex.replace(/\s/g, "")).toMatch(/x\^\{?2\}?\+1/);
});

test("IN625 G1b EN-TC-03: teclado virtual conserva x^10 y luego suma", async ({ page }) => {
  await page.goto("./");
  const dialog = await openKeyboard(page);
  await dialog.getByRole("tab", { name: "Básico", exact: true }).click();
  await clearBasic(dialog);
  const field = page.locator("math-field").first();
  await field.evaluate((el) => { (el as HTMLElement & { value?: string }).value = "x"; });
  await dialog.getByRole("tab", { name: "Símbolos", exact: true }).click();
  await dialog.getByRole("button", { name: "potencia general", exact: true }).click();
  await dialog.getByRole("tab", { name: "Básico", exact: true }).click();
  await dialog.getByRole("button", { name: "1", exact: true }).click();
  await dialog.getByRole("button", { name: "0", exact: true }).click();
  await dialog.getByRole("button", { name: "sumar", exact: true }).click();
  await dialog.getByRole("button", { name: "1", exact: true }).click();
  const latex = await valueOfMainField(page);
  expect(latex.replace(/\s/g, "")).toMatch(/x\^\{?10\}?\+1/);
});
