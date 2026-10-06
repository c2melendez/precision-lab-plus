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




async function preparePhysicalMathField(page: import("@playwright/test").Page) {
  const field = page.locator("math-field").first();
  await field.waitFor({ state: "visible" });
  await field.evaluate((el) => {
    const mf = el as HTMLElement & { value?: string; setValue?: (v: string) => void };
    if (typeof mf.setValue === "function") mf.setValue("");
    else mf.value = "";
  });
  await field.click();
  await page.waitForTimeout(100);
  return field;
}

async function physicalSequence(
  page: import("@playwright/test").Page,
  sequence: string,
) {
  const field = await preparePhysicalMathField(page);
  for (const key of sequence) {
    await page.keyboard.press(key);
    await page.waitForTimeout(35);
  }
  return String(await field.evaluate((el) => (el as HTMLElement & { value?: string }).value ?? ""));
}

test("IN625 G1b EN-TC-01: 2 ^ 1 0 conserva 10 completo en el exponente", async ({ page }) => {
  await page.goto("./");
  const latex = await physicalSequence(page, "2^10");
  expect(latex.replace(/\s/g, "")).toMatch(/2\^\{?10\}?/);
});

test("IN625 G1b EN-TC-02: x ^ 2 + 1 saca + del exponente", async ({ page }) => {
  await page.goto("./");
  const latex = await physicalSequence(page, "x^2+1");
  expect(latex.replace(/\s/g, "")).toMatch(/x\^\{?2\}?\+1/);
});

test("IN625 G1b EN-TC-03: x ^ 1 0 + 1 conserva x^10 y luego suma", async ({ page }) => {
  await page.goto("./");
  const latex = await physicalSequence(page, "x^10+1");
  expect(latex.replace(/\s/g, "")).toMatch(/x\^\{?10\}?\+1/);
});


test("IN625 G1b EN-TC-04: 2 ^ - 3 + 1 conserva exponente negativo y sale al +", async ({ page }) => {
  await page.goto("./");
  const latex = await physicalSequence(page, "2^-3+1");
  expect(latex.replace(/\s/g, "")).toMatch(/2\^\{?-3\}?\+1/);
});

test("IN625 G1b EN-TC-05: x ^ 2 y saca la variable del exponente", async ({ page }) => {
  await page.goto("./");
  const latex = await physicalSequence(page, "x^2y");
  expect(latex.replace(/\s/g, "")).toMatch(/x\^\{?2\}?y/);
});

test("IN625 G1b EN-TC-06: e ^ x + 1 mantiene un eco matemático coherente", async ({ page }) => {
  await page.goto("./");
  const latex = (await physicalSequence(page, "e^x+1")).replace(/\s/g, "");
  expect([
    /^e\^\{?x\}?\+1$/,
    /^e\^\{?x\+1\}?$/,
  ].some((re) => re.test(latex))).toBe(true);
});
