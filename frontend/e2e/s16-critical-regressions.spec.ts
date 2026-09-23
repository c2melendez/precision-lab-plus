import { expect, test, type Locator, type Page } from "@playwright/test";

async function openKeyboard(page: Page): Promise<Locator> {
  await page.goto("./");
  const opener = page.getByRole("button", { name: /abrir teclado|expandir teclado/i }).first();
  await expect(opener).toBeVisible();
  await opener.click();
  const dialog = page.getByRole("dialog", { name: "Teclado matemático" });
  await expect(dialog).toBeVisible();
  return dialog;
}

async function clickVisibleButton(page: Page, name: string): Promise<boolean> {
  const matches = page.getByRole("button", { name, exact: true });
  for (let i = 0; i < await matches.count(); i += 1) {
    const candidate = matches.nth(i);
    if (await candidate.isVisible()) {
      await candidate.click();
      return true;
    }
  }
  return false;
}

async function press(dialog: Locator, name: string) {
  const page = dialog.page();
  if (await clickVisibleButton(page, name)) return;

  const basicTab = page.getByRole("tab", { name: "Básico", exact: true }).first();
  if (await basicTab.isVisible().catch(() => false)) {
    await basicTab.click();
    await expect(basicTab).toHaveAttribute("aria-selected", "true");
    if (await clickVisibleButton(page, name)) return;
  }

  const opener = page.getByRole("button", { name: /abrir teclado|expandir teclado/i }).first();
  if (await opener.isVisible().catch(() => false)) {
    await opener.click();
    await expect(page.getByRole("dialog", { name: "Teclado matemático" })).toBeVisible();
    const reopenedBasic = page.getByRole("tab", { name: "Básico", exact: true }).first();
    if (await reopenedBasic.isVisible().catch(() => false)) {
      await reopenedBasic.click();
      await expect(reopenedBasic).toHaveAttribute("aria-selected", "true");
    }
    if (await clickVisibleButton(page, name)) return;
  }

  throw new Error(`No se encontró una tecla visible con aria-label "${name}"`);
}

async function category(dialog: Locator, name: string) {
  const page = dialog.page();
  let tab = page.getByRole("tab", { name, exact: true }).first();
  if (!(await tab.isVisible().catch(() => false))) {
    const opener = page.getByRole("button", { name: /abrir teclado|expandir teclado/i }).first();
    await expect(opener).toBeVisible();
    await opener.click();
    await expect(page.getByRole("dialog", { name: "Teclado matemático" })).toBeVisible();
    tab = page.getByRole("tab", { name, exact: true }).first();
  }
  await tab.click();
  await expect(tab).toHaveAttribute("aria-selected", "true");
}

async function clear(dialog: Locator) {
  await press(dialog, "borrar todo el campo");
}

async function calculate(page: Page, dialog: Locator): Promise<Record<string, unknown>> {
  const responsePromise = page.waitForResponse(
    (r) => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST",
  );
  await press(dialog, "calcular");
  const response = await responsePromise;
  const body = await response.json();
  return body as Record<string, unknown>;
}

function expectSuccess(body: Record<string, unknown>) {
  expect(body.success, JSON.stringify(body)).toBe(true);
}

function approx(body: Record<string, unknown>): number {
  const value = body.result_approx;
  expect(value, JSON.stringify(body)).not.toBeNull();
  expect(value, JSON.stringify(body)).not.toBeUndefined();
  return Number(value);
}

test("S16 REG-001 Plus: 1.5+2.25 => 3.75 desde teclado real", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  for (const key of ["1", "punto decimal", "5", "sumar", "2", "punto decimal", "2", "5"]) await press(dialog, key);
  const body = await calculate(page, dialog);
  expectSuccess(body);
  expect(approx(body)).toBeCloseTo(3.75, 12);
});

test("S16 REG-002 Plus: log(100) => 2 desde plantilla real", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Álgebra");
  await press(dialog, "logaritmo base 10");
  for (const key of ["1", "0", "0"]) await press(dialog, key);
  const body = await calculate(page, dialog);
  expectSuccess(body);
  expect(approx(body)).toBeCloseTo(2, 12);
});

test("S16 REG-003 Plus: ln(e) => 1", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Álgebra");
  await press(dialog, "logaritmo natural");
  await category(dialog, "Símbolos");
  await press(dialog, "e");
  const body = await calculate(page, dialog);
  expectSuccess(body);
  expect(approx(body)).toBeCloseTo(1, 12);
});

test("S16 REG-004 Plus: log base 2 de 8 => 3", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Álgebra");
  await press(dialog, "logaritmo base 2");
  await press(dialog, "8");
  const body = await calculate(page, dialog);
  expectSuccess(body);
  expect(approx(body)).toBeCloseTo(3, 12);
});

test("S16 REG-005 Plus: entero > MAX_SAFE_INTEGER exacto o rechazo explícito", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  for (const digit of "9007199254740993") await press(dialog, digit);
  const body = await calculate(page, dialog);

  if (body.success === true) {
    const exact = String(body.result_text ?? body.result_exact ?? "").replace(/[\s,]/g, "");
    expect(exact, JSON.stringify(body)).toContain("9007199254740993");
    expect(exact, JSON.stringify(body)).not.toContain("9007199254740992");
  } else {
    expect(String(body.error_code ?? body.error ?? ""), JSON.stringify(body)).not.toBe("");
  }
});

test("S16 REG-006 Plus: 50% => 0.5", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await press(dialog, "5");
  await press(dialog, "0");
  await press(dialog, "porcentaje");
  const body = await calculate(page, dialog);
  expectSuccess(body);
  expect(approx(body)).toBeCloseTo(0.5, 12);
});

test("S16 REG-007 Plus: exp(1) => e", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Álgebra");
  await press(dialog, "exponencial");
  await press(dialog, "1");
  const body = await calculate(page, dialog);
  expectSuccess(body);
  expect(approx(body)).toBeCloseTo(Math.E, 10);
});

test("S16 REG-008 Plus: sin(90°) => 1", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Trigonométricas");
  await press(dialog, "sin");
  await press(dialog, "9");
  await press(dialog, "0");
  await press(dialog, "grados");
  const body = await calculate(page, dialog);
  expectSuccess(body);
  expect(approx(body)).toBeCloseTo(1, 10);
});

test("S16 REG-009 Plus: |-3| => 3", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Álgebra");
  await press(dialog, "valor absoluto de a");
  await press(dialog, "restar");
  await press(dialog, "3");
  const body = await calculate(page, dialog);
  expectSuccess(body);
  expect(approx(body)).toBeCloseTo(3, 12);
});

test("S16 REG-010 Plus: sin inversa de 0 => 0", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Trigonométricas");
  await press(dialog, "sin inversa");
  await press(dialog, "0");
  const body = await calculate(page, dialog);
  expectSuccess(body);
  expect(approx(body)).toBeCloseTo(0, 12);
});
