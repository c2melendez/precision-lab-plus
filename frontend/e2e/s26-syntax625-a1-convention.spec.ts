import { expect, test, type Page } from "@playwright/test";

async function setExpression(page: Page, value: string) {
  await page.evaluate(() => customElements.whenDefined("math-field"));
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  await field.evaluate((node, v) => {
    const el = node as HTMLElement & { value: string };
    el.value = v as string;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

type EvaluateBody = {
  success: boolean;
  result_text?: string | null;
  result_approx?: number | string | null;
  error_message?: string | null;
};

test("EN-FR-13 — fracción sin llaves conserva convención explícita", async ({ page }) => {
  await page.goto("./");
  await setExpression(page, "\\frac123");
  const calculate = page.getByRole("button", { name: /calcular|evaluar/i }).first();
  const responsePromise = page.waitForResponse(
    (r) => r.url().includes("/api/v1/evaluate") && r.request().method() === "POST",
  );
  await calculate.click();
  const body = (await (await responsePromise).json()) as EvaluateBody;

  if (!body.success) {
    expect(body.error_message ?? "").toMatch(/ambig|fracc|sintax|argument|interpret/i);
    return;
  }

  const numeric = Number(body.result_approx ?? body.result_text);
  expect(numeric, `EN-FR-13 debe ser 1.5 o error claro; recibido: ${JSON.stringify(body)}`).toBeCloseTo(1.5, 5);
});
