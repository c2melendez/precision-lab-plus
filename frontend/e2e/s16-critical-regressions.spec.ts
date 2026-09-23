import { expect, test, type Locator, type Page, type APIResponse } from "@playwright/test";

type EvaluateBody = {
  success: boolean;
  result_text?: string | null;
  result_approx?: number | string | null;
  error_code?: string | null;
  error_message?: string | null;
};

async function openKeyboard(page: Page): Promise<Locator> {
  await page.goto("./");
  const opener = page.getByRole("button", { name: /abrir teclado|expandir teclado/i }).first();
  await expect(opener).toBeVisible();
  await opener.click();
  const dialog = page.getByRole("dialog", { name: "Teclado matemático" });
  await expect(dialog).toBeVisible();
  return dialog;
}

async function category(dialog: Locator, name: string) {
  const tab = dialog.getByRole("tab", { name, exact: true });
  await expect(tab).toBeVisible();
  await tab.click();
  await expect(tab).toHaveAttribute("aria-selected", "true");
}

async function press(dialog: Locator, name: string) {
  let button = dialog.getByRole("button", { name, exact: true }).first();
  if (await button.isVisible().catch(() => false)) {
    await button.click();
    return;
  }

  // En V5 el contenido del panel cambia con la categoría. Las teclas de
  // escritura/control viven en Básico: volver ahí reproduce el recorrido
  // normal del usuario después de insertar una plantilla temática.
  await category(dialog, "Básico");
  button = dialog.getByRole("button", { name, exact: true }).first();
  await expect(button).toBeVisible();
  await button.click();
}

async function clear(dialog: Locator) {
  await category(dialog, "Básico");
  await press(dialog, "borrar todo el campo");
}

async function calculate(page: Page, dialog: Locator): Promise<EvaluateBody> {
  await category(dialog, "Básico");
  const responsePromise: Promise<APIResponse> = page.waitForResponse(
    (r) => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST",
  );
  await press(dialog, "calcular");
  const response = await responsePromise;
  const body = (await response.json()) as EvaluateBody;

  // Además de validar la respuesta de backend, exige que el frontend haya
  // renderizado un resultado utilizable para el usuario.
  await expect(page.getByRole("button", { name: "Copiar resultado", exact: true })).toBeVisible();
  return body;
}

function expectSuccess(body: EvaluateBody) {
  expect(body.success, JSON.stringify(body)).toBe(true);
}

function approx(body: EvaluateBody): number {
  expectSuccess(body);
  const n = Number(body.result_approx ?? body.result_text);
  expect(Number.isFinite(n), JSON.stringify(body)).toBe(true);
  return n;
}

test("S16 REG-001 Plus: 1.5+2.25 => 3.75 por UI -> API -> resultado", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  for (const key of ["1", "punto decimal", "5", "sumar", "2", "punto decimal", "2", "5"]) {
    await press(dialog, key);
  }
  expect(approx(await calculate(page, dialog))).toBeCloseTo(3.75, 12);
});

test("S16 REG-002 Plus: log(100) => 2 desde plantilla real", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Álgebra");
  await press(dialog, "logaritmo base 10");
  await press(dialog, "1");
  await press(dialog, "0");
  await press(dialog, "0");
  expect(approx(await calculate(page, dialog))).toBeCloseTo(2, 12);
});

test("S16 REG-003 Plus: ln(e) => 1 desde plantilla y constante reales", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Álgebra");
  await press(dialog, "logaritmo natural");
  await category(dialog, "Símbolos");
  await press(dialog, "e");
  expect(approx(await calculate(page, dialog))).toBeCloseTo(1, 12);
});

test("S16 REG-004 Plus: log base 2 de 8 => 3", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Álgebra");
  await press(dialog, "logaritmo base 2");
  await press(dialog, "8");
  expect(approx(await calculate(page, dialog))).toBeCloseTo(3, 12);
});

test("S16 REG-005 Plus: entero > MAX_SAFE_INTEGER conserva exactitud", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  for (const digit of "9007199254740993") await press(dialog, digit);
  const body = await calculate(page, dialog);
  expectSuccess(body);
  const text = String(body.result_text ?? "").replace(/[\s,]/g, "");
  expect(text).not.toContain("9007199254740992");
  expect(text).toContain("9007199254740993");
});

test("S16 REG-006 Plus: 50% => 0.5", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await press(dialog, "5");
  await press(dialog, "0");
  await press(dialog, "porcentaje");
  expect(approx(await calculate(page, dialog))).toBeCloseTo(0.5, 12);
});

test("S16 REG-007 Plus: exp(1) => e", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Álgebra");
  await press(dialog, "exponencial");
  await press(dialog, "1");
  expect(approx(await calculate(page, dialog))).toBeCloseTo(Math.E, 10);
});

test("S16 REG-008 Plus: sin(90°) => 1 usando tecla grados", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Trigonométricas");
  await press(dialog, "sin");
  await press(dialog, "9");
  await press(dialog, "0");
  await press(dialog, "grados");
  expect(approx(await calculate(page, dialog))).toBeCloseTo(1, 10);
});

test("S16 REG-009 Plus: |-3| => 3 desde plantilla valor absoluto", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Álgebra");
  await press(dialog, "valor absoluto de a");
  await press(dialog, "restar");
  await press(dialog, "3");
  expect(approx(await calculate(page, dialog))).toBeCloseTo(3, 12);
});

test("S16 REG-010 Plus: sin inversa de 0 => 0", async ({ page }) => {
  const dialog = await openKeyboard(page);
  await clear(dialog);
  await category(dialog, "Trigonométricas");
  await press(dialog, "sin inversa");
  await press(dialog, "0");
  expect(approx(await calculate(page, dialog))).toBeCloseTo(0, 12);
});
